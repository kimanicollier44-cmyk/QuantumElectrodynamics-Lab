"""Tests for QuantumElectrodynamics-Lab (main.py)."""
import json
import math

import main


# ------------------------------------------------------------ g-2 series
def test_schwinger_term_exact():
    assert abs(main.ae_terms()[0] - main.ALPHA / (2.0 * math.pi)) < 1e-18


def test_terms_shrink_monotone():
    terms = main.ae_terms()
    assert all(abs(terms[i + 1]) < abs(terms[i]) for i in range(4))
    assert all(abs(terms[i + 1] / terms[i]) < 0.01 for i in range(4))


def test_five_loop_total_window():
    total = main.ae_partial_sums()[-1]
    assert abs(total - 0.001159652177) < 1e-11


def test_residual_below_experiment():
    rep = main.gtwo_report()
    assert rep["total_mass_independent_qed"] < rep["experiment_labelled"]
    assert abs(rep["residual_ppm"]) < 0.01
    assert rep["residual"] < 0


def test_gtwo_report_lists_missing_pieces():
    rep = main.gtwo_report()
    assert len(rep["not_included"]) == 4
    assert rep["coefficients_labelled"][0] == 0.5


# ------------------------------------------------------------ running
def test_delta_alpha_lep_mz():
    assert 0.0310 < main.delta_alpha_lep(main.M_Z_GEV) < 0.0318


def test_alpha_inv_windows():
    assert 132.5 < main.alpha_inv_lep(main.M_Z_GEV) < 133.0
    full = main.ALPHA_INV_0 * (1.0 - main.delta_alpha_lep(main.M_Z_GEV)
                               - main.DELTA_ALPHA_HAD_LABELLED)
    assert 128.7 < full < 129.2


def test_running_monotone():
    invs = [main.alpha_inv_lep(q)
            for q in (10.0, 50.0, main.M_Z_GEV, 200.0, 1000.0)]
    assert all(invs[i + 1] < invs[i] for i in range(len(invs) - 1))


def test_running_by_lepton_order_and_sum():
    by = main.delta_alpha_lep_by_lepton(main.M_Z_GEV)
    assert by["electron"] > by["muon"] > by["tau"] > 0.0
    assert abs(sum(by.values())
               - main.delta_alpha_lep(main.M_Z_GEV)) < 1e-12


# ------------------------------------------------------------ Compton
def test_lambda_c_value():
    assert abs(main.LAMBDA_C_M * 1e12 - 2.4263102387) < 1e-9


def test_compton_shift_landmarks():
    lam = main.LAMBDA_C_M * 1e12
    assert main.compton_shift_pm(0.0) == 0.0
    assert abs(main.compton_shift_pm(90.0) - lam) < 1e-12
    assert abs(main.compton_shift_pm(180.0) - 2.0 * lam) < 1e-12


def test_thomson_cross_section():
    assert 0.6652 < main.SIGMA_T_M2 / 1e-28 < 0.6653


def test_kn_integral_matches_closed():
    for x in (0.01, 1.0, 10.0):
        closed = main.kn_total_closed(x)
        assert abs(main.kn_total_integral(x) - closed) / closed < 1e-8


def test_kn_ratios():
    t = main.SIGMA_T_M2
    assert 0.975 < main.kn_total_closed(0.01) / t < 0.985
    assert 0.42 < main.kn_total_closed(1.0) / t < 0.44
    assert 0.11 < main.kn_total_closed(10.0) / t < 0.13


# ------------------------------------------------------------ Lamb shift
def test_bethe_estimate_window():
    est = main.bethe_lamb_mhz(2)
    assert 1040.0 < est < 1050.0
    assert est < main.LAMB_MEASURED_MHZ


def test_lamb_gap_few_percent():
    rep = main.lamb_report()
    assert 0.5 < rep["gap_percent"] < 2.0
    assert len(rep["missing_pieces"]) == 3


# ------------------------------------------------------------ thresholds
def test_pair_threshold_digits():
    assert abs(main.pair_threshold_mev() - 1.021998) < 1e-6


def test_bw_product_identity():
    for e1 in (0.1, 0.25, main.M_E_MEV, 1.0, 10.0):
        prod = e1 * main.bw_partner_min_mev(e1)
        assert abs(prod - main.M_E_MEV ** 2) / main.M_E_MEV ** 2 < 1e-12


def test_bw_allowed_flags():
    assert not main.bw_allowed(0.25, 0.5)
    assert main.bw_allowed(1.0, 1.0)
    assert abs(main.bw_partner_min_mev(main.M_E_MEV)
               - main.M_E_MEV) < 1e-12


# ------------------------------------------------------------ classifier
def test_classifier_scenarios():
    rep = main.classifier_report()
    assert rep["electron_g_minus_2_probe"] == "precision-agreement"
    assert rep["mz_running_probe"] == "running-coupling-regime"
    assert rep["thomson_limit_probe"] == "classical-limit"
    assert rep["subthreshold_photon_probe"] == "threshold-blocked"
    assert rep["hard_scattering_probe"] == "running-coupling-regime"


def test_classifier_matches_policy_grid():
    assert len(main.TRAINING_GRID) == 500
    assert all(main.classify_regime(*f) == label
               for f, label in main.TRAINING_GRID)


# ------------------------------------------------------------ gates + seats
def test_hold_gates_14():
    assert len(main.HOLD_GATES) == 14
    assert all(v.startswith("HOLD") for v in main.HOLD_GATES.values())


def test_specific_gates_hold():
    for action in ("precision_measurement_claim", "new_physics_claim",
                   "vendor_claim", "medical_claim", "weapons_claim"):
        assert main.gate(action) == "HOLD"
    assert main.gate("run_simulation") == "PROCEED"


def test_seats_never_override():
    brains = main.brains_report()
    assert brains["decider"]["can_override_hold"] is False
    assert brains["decider"]["model_id"] == "gemini-argon-4"
    assert brains["advisor"]["can_override_hold"] is False
    assert brains["flow"]["rendered"] is False
    assert brains["flow"]["live"] == 0


# ------------------------------------------------------------ CLI + checks
def test_run_checks_all_pass():
    checks = main.run_checks()
    assert all(ok for _, ok in checks)
    assert len(checks) == 55


def test_cli_checks_exit_zero(capsys):
    assert main.main(["checks"]) == 0
    out = capsys.readouterr().out
    assert "CHECKS 55/55" in out


def test_cli_hold_demo_exit_two(capsys):
    assert main.main(["hold-demo"]) == 2
    assert "HOLD" in capsys.readouterr().out


def test_cli_topic_commands_json(capsys):
    for cmd in ("gtwo", "running", "compton", "lamb", "thresholds",
                "classify", "brains"):
        assert main.main([cmd]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert isinstance(payload, dict) and payload


def test_demo_deterministic(capsys):
    assert main.main(["demo"]) == 0
    first = capsys.readouterr().out
    assert main.main(["demo"]) == 0
    second = capsys.readouterr().out
    assert first == second
    assert "CHECKS 55/55" in first
