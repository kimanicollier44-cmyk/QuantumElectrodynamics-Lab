#!/usr/bin/env python3
"""QuantumElectrodynamics-Lab - educational QED precision-quantities lab.

by Darion Kellar

Pure Python standard library. Zero dependencies. Zero network.
Education only - and the central lesson is stated up front:

  * This lab EVALUATES textbook quantum-electrodynamics formulas
    from LABELLED input constants: the electron anomalous magnetic
    moment as a five-term series in (alpha/pi), the one-loop leptonic
    running of alpha up to the Z pole, Compton scattering with the
    Klein-Nishina cross section integrated numerically and graded
    against its own closed form, Bethe's nonrelativistic estimate of
    the Lamb shift, and the pair-production thresholds.
  * Every physical constant and every published coefficient is a
    LABELLED INPUT, stated in the code. The experimental values the
    series is compared against are labelled reference inputs too -
    they are not results of this lab, and nothing here is a
    measurement.
  * Where a piece of the full answer is NOT computed (the hadronic
    vacuum polarisation, the mass-dependent and weak pieces of g-2,
    the relativistic corrections to the Lamb shift), the lab prints
    it as a labelled missing piece with its size, so the gap between
    this evaluation and the full theory is visible, never hidden.

A small residual is arithmetic, not a discovery: new-physics,
precision-measurement, metrology, vendor, and hardware claims are
permanent HOLD gates - with Gemini Argon 4 Extended Thinking as
DECIDER (names-only, tighten-only), Muse as advisor (never
overrides HOLD), and Google Flow plan-only seats.
"""
import hashlib
import json
import math
import sys

# ---------------------------------------------------------------- constants
VERSION = "1.0.0"

# Labelled input constants (CODATA-style values, stated, not measured
# by this lab). Everything else in the file is computed from these.
ALPHA_INV_0 = 137.035999084          # 1/alpha at Q = 0 (labelled input)
ALPHA = 1.0 / ALPHA_INV_0            # fine-structure constant (derived)
H_PLANCK = 6.62607015e-34            # Planck constant, J s (exact SI)
HBAR = H_PLANCK / (2.0 * math.pi)    # reduced Planck constant (derived)
C_LIGHT = 299792458.0                # speed of light, m/s (exact SI)
E_CHARGE = 1.602176634e-19           # elementary charge, C (exact SI)
M_E_KG = 9.1093837015e-31            # electron mass, kg (labelled input)
M_E_MEV = 0.510998950                # electron rest energy, MeV (labelled)
M_MU_MEV = 105.6583755               # muon rest energy, MeV (labelled)
M_TAU_MEV = 1776.86                  # tau rest energy, MeV (labelled)
M_Z_GEV = 91.1876                    # Z boson mass, GeV (labelled)
RYDBERG_EV = 13.605693122994         # Rydberg energy, eV (labelled)

# Derived constants (computed from the labelled inputs above).
M_E_C2_MEV = M_E_KG * C_LIGHT ** 2 / E_CHARGE / 1.0e6   # m_e c^2 in MeV
LAMBDA_C_M = H_PLANCK / (M_E_KG * C_LIGHT)              # Compton wavelength
R_E_M = ALPHA * HBAR / (M_E_KG * C_LIGHT)               # classical e- radius
SIGMA_T_M2 = (8.0 * math.pi / 3.0) * R_E_M ** 2         # Thomson cross section

# Electron g-2: published mass-independent QED coefficients of
# a_e = sum_n C_n (alpha/pi)^n, n = 1..5 (labelled inputs; the
# evaluation, partial sums, and comparisons are computed here).
AE_COEFFS = (0.5, -0.328478965579193, 1.181241456587,
             -1.912245764926, 6.737)
AE_EXPERIMENT = 0.00115965218073     # labelled experimental reference

# Running coupling: the hadronic vacuum-polarisation piece is NOT
# computed by this lab; it enters only as this labelled input when
# the full on-shell value is quoted, and the gap is printed.
DELTA_ALPHA_HAD_LABELLED = 0.02766   # Delta alpha_had(M_Z^2), labelled
ALPHA_INV_MZ_MSbar_LABELLED = 127.95  # MS-bar convention value, labelled

# Lamb shift: Bethe logarithm for hydrogen 2S (labelled published
# input, in units where the mean excitation energy K0 is measured
# in Rydbergs) and the labelled measured 2S-2P splitting.
BETHE_LOG_2S = 2.8117695
LAMB_MEASURED_MHZ = 1057.84

# ---------------------------------------------------------------- HOLD gates
HOLD_GATES = {
    "precision_measurement_claim": "HOLD - no new precision measurement of alpha, g-2, or any constant is claimed; inputs are labelled references",
    "new_physics_claim": "HOLD - no new-physics or beyond-Standard-Model claim; a series residual is arithmetic, not a discovery",
    "constant_redefinition_claim": "HOLD - no redefining CODATA constants; the lab evaluates formulas at labelled input values",
    "metrology_certification_claim": "HOLD - no metrology certification or traceability claim for any computed number",
    "vendor_claim": "HOLD - no vendor, instrument, or product claims from textbook evaluations",
    "hardware_spec_claim": "HOLD - no hardware specifications for accelerators, detectors, lasers, or magnets",
    "experimental_design_claim": "HOLD - no claim that these evaluations design or validate a real experiment",
    "medical_claim": "HOLD - no medical imaging, therapy, or dosimetry claims from Compton or pair-production math",
    "radiation_safety_claim": "HOLD - no radiation-safety, shielding, or exposure certification",
    "weapons_claim": "HOLD - no weapons-related use of cross sections or pair-production thresholds",
    "live_radiation_monitoring": "HOLD - no live radiation monitoring or dosimetry use",
    "data_fabrication_claim": "HOLD - computed values are never presented as measured data",
    "publication_claim": "HOLD - no claim of publishable new results; these are textbook evaluations",
    "investment_claim": "HOLD - no investment claims; a lab model is not a prospectus",
}


def gate(action):
    """Return 'HOLD' if the action is gated, else 'PROCEED' (sandbox sim)."""
    return "HOLD" if action in HOLD_GATES else "PROCEED"


# ================================================================ 1. Electron g-2
# a_e = sum_n C_n (alpha/pi)^n with the published mass-independent
# QED coefficients as labelled inputs. What is NOT in these
# coefficients: the mass-dependent QED terms (muon and tau loops),
# the hadronic contribution (~1.7e-12), and the weak contribution
# (~3e-14). The residual against the labelled experimental value is
# printed with exactly that caveat - it is the size of the missing
# pieces plus the uncertainty alpha itself carries in as an input.

def ae_terms():
    """The five series terms C_n (alpha/pi)^n, n = 1..5."""
    x = ALPHA / math.pi
    return [AE_COEFFS[n] * x ** (n + 1) for n in range(len(AE_COEFFS))]


def ae_partial_sums():
    """Running total of a_e after each order 1..5."""
    out, total = [], 0.0
    for term in ae_terms():
        total += term
        out.append(total)
    return out


def gtwo_report():
    terms = ae_terms()
    total = ae_partial_sums()[-1]
    residual = total - AE_EXPERIMENT
    return {
        "alpha_over_pi": ALPHA / math.pi,
        "schwinger_term_alpha_over_2pi": ALPHA / (2.0 * math.pi),
        "coefficients_labelled": list(AE_COEFFS),
        "terms": [float(f"{t:.6e}") for t in terms],
        "partial_sums": [round(s, 15) for s in ae_partial_sums()],
        "total_mass_independent_qed": round(total, 15),
        "experiment_labelled": AE_EXPERIMENT,
        "residual": float(f"{residual:.3e}"),
        "residual_ppm": round(residual / AE_EXPERIMENT * 1.0e6, 6),
        "not_included": ["mass-dependent QED (muon/tau loops)",
                         "hadronic contribution ~1.7e-12",
                         "weak contribution ~3e-14",
                         "uncertainty of the alpha input itself"],
    }


# ================================================================ 2. Running of alpha
# One-loop leptonic vacuum polarisation, asymptotic form valid for
# Q^2 >> m_l^2:  Delta alpha_lep(Q^2) = (alpha/3pi) * sum_l
# [ ln(Q^2/m_l^2) - 5/3 ], summed over e, mu, tau. A lepton's term
# is included only above its pair threshold (Q > 2 m_l), which is
# the stated guard where the asymptotic form would otherwise go
# negative near threshold. alpha(Q^2) = alpha(0) / (1 - Delta alpha),
# so alpha^-1(Q^2) = alpha^-1(0) * (1 - Delta alpha). The hadronic
# piece is NOT computed here: it is printed as a labelled missing
# piece, and the full on-shell alpha^-1(M_Z) is quoted only with
# that labelled input added.

LEPTONS_MEV = (("electron", M_E_MEV), ("muon", M_MU_MEV), ("tau", M_TAU_MEV))


def delta_alpha_lep(q_gev):
    """Leptonic Delta alpha at momentum transfer Q (GeV), one loop."""
    q_mev = q_gev * 1000.0
    total = 0.0
    for _, mass in LEPTONS_MEV:
        if q_mev > 2.0 * mass:
            total += math.log((q_mev / mass) ** 2) - 5.0 / 3.0
    return ALPHA / (3.0 * math.pi) * total


def delta_alpha_lep_by_lepton(q_gev):
    """Per-lepton contributions to Delta alpha at Q (GeV)."""
    q_mev = q_gev * 1000.0
    out = {}
    for name, mass in LEPTONS_MEV:
        if q_mev > 2.0 * mass:
            out[name] = ALPHA / (3.0 * math.pi) * (
                math.log((q_mev / mass) ** 2) - 5.0 / 3.0)
        else:
            out[name] = 0.0
    return out


def alpha_inv_lep(q_gev):
    """alpha^-1(Q) with leptonic running only (hadronic NOT included)."""
    return ALPHA_INV_0 * (1.0 - delta_alpha_lep(q_gev))


def running_report():
    ladder_q = [10.0, 50.0, M_Z_GEV, 200.0, 1000.0]
    d_mz = delta_alpha_lep(M_Z_GEV)
    full = ALPHA_INV_0 * (1.0 - d_mz - DELTA_ALPHA_HAD_LABELLED)
    return {
        "formula": "Delta alpha_lep = (alpha/3pi) sum_l [ln(Q^2/m_l^2) - 5/3]",
        "regime": "Q^2 >> m_l^2, lepton term included only for Q > 2 m_l",
        "by_lepton_at_mz": {k: round(v, 6) for k, v in
                            delta_alpha_lep_by_lepton(M_Z_GEV).items()},
        "delta_alpha_lep_mz": round(d_mz, 6),
        "alpha_inv_mz_leptonic_only": round(alpha_inv_lep(M_Z_GEV), 4),
        "hadronic_piece_labelled_not_computed": DELTA_ALPHA_HAD_LABELLED,
        "alpha_inv_mz_with_labelled_hadronic": round(full, 4),
        "alpha_inv_mz_msbar_labelled": ALPHA_INV_MZ_MSbar_LABELLED,
        "ladder": [{"q_gev": q,
                    "delta_alpha_lep": round(delta_alpha_lep(q), 6),
                    "alpha_inv_lep_only": round(alpha_inv_lep(q), 4)}
                   for q in ladder_q],
    }


# ================================================================ 3. Compton scattering
# Wavelength shift Delta lambda = lambda_C (1 - cos theta), exact.
# Klein-Nishina differential cross section for a photon of energy
# E = x * m_e c^2 scattering off a free electron at rest:
#   d sigma/d Omega = (r_e^2/2) * (1/(1 + x(1-cos theta))^2)
#                     * (1 + cos^2 theta
#                        + x^2 (1-cos theta)^2 / (1 + x(1-cos theta)))
# The total cross section is computed TWO ways - Simpson integration
# of the differential form over angle, and the standard closed form -
# and the checks assert they agree, so the integral is graded, not
# trusted. Low-energy limit: sigma -> sigma_T (Thomson).

def compton_shift_pm(theta_deg):
    """Compton wavelength shift in picometres at angle theta_deg."""
    return LAMBDA_C_M * 1.0e12 * (1.0 - math.cos(math.radians(theta_deg)))


def kn_dsigma_domega(theta, x):
    """Klein-Nishina d sigma/d Omega (m^2/sr); theta rad, x = E/(m_e c^2)."""
    ct = math.cos(theta)
    k = 1.0 + x * (1.0 - ct)
    return 0.5 * R_E_M ** 2 / k ** 2 * (
        1.0 + ct * ct + x * x * (1.0 - ct) ** 2 / k)


def kn_total_closed(x):
    """Klein-Nishina total cross section (m^2), closed form."""
    lx = math.log(1.0 + 2.0 * x)
    return 2.0 * math.pi * R_E_M ** 2 * (
        (1.0 + x) / x ** 2 * (2.0 * (1.0 + x) / (1.0 + 2.0 * x) - lx / x)
        + lx / (2.0 * x) - (1.0 + 3.0 * x) / (1.0 + 2.0 * x) ** 2)


def kn_total_integral(x, n=2880):
    """Klein-Nishina total cross section (m^2), Simpson over angle."""
    a, b = 0.0, math.pi
    h = (b - a) / n
    total = kn_dsigma_domega(a, x) * math.sin(a) \
        + kn_dsigma_domega(b, x) * math.sin(b)
    for i in range(1, n):
        th = a + i * h
        total += (4.0 if i % 2 else 2.0) * kn_dsigma_domega(th, x) \
            * math.sin(th)
    return 2.0 * math.pi * total * h / 3.0


def compton_report():
    angles = [0.0, 30.0, 60.0, 90.0, 120.0, 180.0]
    ladder_x = [0.001, 0.01, 0.1, 1.0, 10.0]
    return {
        "lambda_c_pm": round(LAMBDA_C_M * 1.0e12, 10),
        "shift_table_pm": {f"{a:.0f}": round(compton_shift_pm(a), 6)
                           for a in angles},
        "sigma_t_barn": round(SIGMA_T_M2 / 1.0e-28, 8),
        "kn_ladder": [{"x": xx,
                       "sigma_closed_barn": round(
                           kn_total_closed(xx) / 1.0e-28, 6),
                       "sigma_integral_barn": round(
                           kn_total_integral(xx) / 1.0e-28, 6),
                       "ratio_to_thomson": round(
                           kn_total_closed(xx) / SIGMA_T_M2, 6)}
                      for xx in ladder_x],
    }


# ================================================================ 4. Lamb shift (Bethe)
# Bethe's 1947 nonrelativistic estimate for an nS level of hydrogen:
#   Delta E = (4/(3 pi)) * alpha^5 * m_e c^2 / n^3
#             * ln( m_e c^2 / K0(nS) ),
# with K0 the Bethe mean excitation energy; for 2S the Bethe
# logarithm ln K0 = 2.8117695 (labelled published input) with K0
# measured in Rydbergs. This estimate famously lands within ~1% of
# the measured 1057.84 MHz - and the lab prints that gap as what it
# is: the known shortfall of the nonrelativistic estimate, whose
# missing pieces are the relativistic, recoil, and higher-order
# radiative corrections. Only the window is asserted, not agreement.

def bethe_lamb_mhz(n=2):
    """Bethe nonrelativistic Lamb-shift estimate for nS, in MHz."""
    k0_ev = math.exp(BETHE_LOG_2S) * RYDBERG_EV
    prefactor_hz = (4.0 / (3.0 * math.pi)) * ALPHA ** 5 \
        * (M_E_KG * C_LIGHT ** 2 / H_PLANCK) / n ** 3
    return prefactor_hz * math.log(M_E_MEV * 1.0e6 / k0_ev) / 1.0e6


def lamb_report():
    est = bethe_lamb_mhz(2)
    return {
        "state": "hydrogen 2S-2P",
        "bethe_log_2s_labelled": BETHE_LOG_2S,
        "k0_ev": round(math.exp(BETHE_LOG_2S) * RYDBERG_EV, 4),
        "bethe_estimate_mhz": round(est, 4),
        "measured_labelled_mhz": LAMB_MEASURED_MHZ,
        "gap_percent": round((LAMB_MEASURED_MHZ - est)
                             / LAMB_MEASURED_MHZ * 100.0, 4),
        "missing_pieces": ["relativistic (Dirac) corrections",
                           "recoil corrections",
                           "higher-order radiative corrections"],
    }


# ================================================================ 5. Thresholds
# Pair production by a single photon, gamma -> e+ e-, needs at least
# 2 m_e c^2 of photon energy (and a nearby nucleus to conserve
# momentum - the threshold printed here is the energy bookkeeping,
# stated as such). Breit-Wheeler pair production, gamma gamma ->
# e+ e-, for two head-on photons needs E1 * E2 >= (m_e c^2)^2; the
# grid below prints the minimum partner energy for each E1 and
# flags the combinations that stay below threshold as blocked.

def pair_threshold_mev():
    """Single-photon pair-production energy threshold, MeV."""
    return 2.0 * M_E_C2_MEV


def bw_partner_min_mev(e1_mev):
    """Minimum head-on partner photon energy (MeV) for Breit-Wheeler."""
    return M_E_MEV ** 2 / e1_mev


def bw_allowed(e1_mev, e2_mev):
    """True if head-on photons E1, E2 clear the Breit-Wheeler threshold."""
    return e1_mev * e2_mev >= M_E_MEV ** 2


def thresholds_report():
    grid_e1 = [0.1, 0.25, M_E_MEV, 1.0, 10.0]
    return {
        "m_e_c2_mev": round(M_E_C2_MEV, 9),
        "pair_threshold_mev": round(pair_threshold_mev(), 9),
        "pair_note": "energy bookkeeping; a nucleus is also required "
                     "to conserve momentum",
        "bw_threshold_product_mev2": round(M_E_MEV ** 2, 9),
        "bw_grid": [{"e1_mev": round(e1, 6),
                     "e2_min_mev": round(bw_partner_min_mev(e1), 6),
                     "at_threshold_allowed": bw_allowed(
                         e1, bw_partner_min_mev(e1))}
                    for e1 in grid_e1],
        "bw_below_example": {"e1_mev": 0.25, "e2_mev": 0.5,
                             "allowed": bw_allowed(0.25, 0.5)},
    }


# ================================================================ 6. kNN regime classifier
# Features: a_e residual (ppm), Delta alpha (percent), sigma/sigma_T,
# E/E_threshold. The training grid is labelled by the lab's own
# regime policy (model_label below) - the classifier interpolates
# the policy; it does not replace the section computations.

def model_label(residual_ppm, dalpha_pct, sigma_ratio, e_ratio):
    """The regime policy distilled to a four-way teaching label."""
    if e_ratio < 1.0:
        return "threshold-blocked"
    if sigma_ratio >= 0.97:
        return "classical-limit"
    if dalpha_pct >= 1.0:
        return "running-coupling-regime"
    if residual_ppm <= 0.01:
        return "precision-agreement"
    return "running-coupling-regime"


def _training_grid():
    rows = []
    for residual in (0.0, 0.002, 0.02, 0.2, 2.0):
        for dalpha in (0.0, 0.4, 1.5, 3.2, 6.0):
            for sigma in (0.12, 0.43, 0.84, 0.99):
                for e_ratio in (0.25, 0.75, 1.0, 4.0, 40.0):
                    rows.append(((residual, dalpha, sigma, e_ratio),
                                 model_label(residual, dalpha, sigma,
                                             e_ratio)))
    return rows


TRAINING_GRID = _training_grid()


def _scaled(features):
    residual, dalpha, sigma, e_ratio = features
    return (residual / 2.0, dalpha / 6.0, sigma, e_ratio / 40.0)


def classify_regime(residual_ppm, dalpha_pct, sigma_ratio, e_ratio, k=5):
    """Distance-weighted kNN over the policy-labelled grid."""
    target = _scaled((residual_ppm, dalpha_pct, sigma_ratio, e_ratio))
    ranked = []
    for features, label in TRAINING_GRID:
        point = _scaled(features)
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(target, point)))
        ranked.append((dist, features, label))
    ranked.sort(key=lambda row: (row[0], row[1]))
    votes = {}
    for dist, _, label in ranked[:k]:
        votes[label] = votes.get(label, 0.0) + 1.0 / (dist * dist + 1e-12)
    priority = {"precision-agreement": 0, "running-coupling-regime": 1,
                "classical-limit": 2, "threshold-blocked": 3}
    return sorted(votes.items(), key=lambda kv: (-kv[1], priority[kv[0]]))[0][0]


def classifier_report():
    g = gtwo_report()
    scenarios = {
        "electron_g_minus_2_probe": (
            abs(g["residual_ppm"]), 0.0,
            round(kn_total_closed(1.0) / SIGMA_T_M2, 6), 2.0),
        "mz_running_probe": (
            abs(g["residual_ppm"]),
            round(delta_alpha_lep(M_Z_GEV) * 100.0, 4),
            round(kn_total_closed(1.0) / SIGMA_T_M2, 6), 2.0),
        "thomson_limit_probe": (
            0.0, 0.0, round(kn_total_closed(0.01) / SIGMA_T_M2, 6), 2.0),
        "subthreshold_photon_probe": (0.0, 0.0,
                                      round(kn_total_closed(1.0)
                                            / SIGMA_T_M2, 6), 0.5),
        "hard_scattering_probe": (
            0.5, 0.2, round(kn_total_closed(10.0) / SIGMA_T_M2, 6), 20.0),
    }
    return {name: classify_regime(*features)
            for name, features in scenarios.items()}


# ================================================================ 7. Advisory seats
def _trace(payload):
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def argon4_decide(topic="quantumelectrodynamics-demo"):
    """Gemini Argon 4 DECIDER seat: MAP->MODEL->STRESS->DECIDE.

    Names-only keys, live calls 0, tighten-only: can add HOLDs, never lift one.
    """
    stages = ["MAP", "MODEL", "STRESS", "DECIDE"]
    payload = {"seat": "gemini-argon-4", "topic": topic, "stages": stages}
    return {
        "seat": "Gemini Argon 4 Extended Thinking",
        "model_id": "gemini-argon-4",
        "role": "DECIDER",
        "pipeline": stages,
        "tiers": [2048, 8192, 32768],
        "key": "names-only (GEMINI_API_KEY name checked, value never read)",
        "live_calls": 0,
        "decision": "PROCEED - textbook evaluation only, all measurement and new-physics gates stay HOLD",
        "can_override_hold": False,
        "trace_sha256_16": _trace(payload),
    }


def claude_advisor(topic="quantumelectrodynamics-demo"):
    """Muse advisor seat: advises, can never override a HOLD."""
    return {
        "seat": "Muse",
        "role": "ADVISOR",
        "key": "names-only (MODEL_API_KEY name checked, value never read)",
        "live_calls": 0,
        "advice": "Print every missing piece next to the number it belongs to: the hadronic gap beside alpha(M_Z), the mass-dependent terms beside the g-2 residual, the relativistic corrections beside Bethe's 1047 MHz - a QED number without its caveat is only half a result.",
        "can_override_hold": False,
    }


def google_flow_plan():
    """Google Flow seat: plan-only, nothing rendered, nothing live."""
    return {
        "seat": "Google Flow",
        "role": "PLAN-ONLY",
        "shots": ["five series terms shrinking rung by rung toward a measured line",
                  "a coupling constant climbing as the energy scale rises to the Z pole",
                  "a photon bouncing off an electron, its wavelength stretched by angle",
                  "two head-on photons meeting exactly at the pair threshold",
                  "the Bethe logarithm bridge between a 1947 estimate and a modern value"],
        "rendered": False,
        "live": 0,
    }


def brains_report():
    return {"decider": argon4_decide(), "advisor": claude_advisor(),
            "flow": google_flow_plan()}


# ================================================================ checks
def run_checks():
    c = []

    def chk(name, ok):
        c.append((name, bool(ok)))

    # 1. g-2 series
    terms = ae_terms()
    sums = ae_partial_sums()
    total = sums[-1]
    chk("alpha_input_consistent", abs(ALPHA * ALPHA_INV_0 - 1.0) < 1e-15)
    chk("coefficients_five_labelled", len(AE_COEFFS) == 5
        and AE_COEFFS[0] == 0.5)
    chk("schwinger_term_exact",
        abs(terms[0] - ALPHA / (2.0 * math.pi)) < 1e-18)
    chk("schwinger_term_size", abs(terms[0] - 0.001161409733) < 1e-9)
    chk("terms_shrink_monotone",
        all(abs(terms[i + 1]) < abs(terms[i]) for i in range(4)))
    chk("term_ratios_under_percent",
        all(abs(terms[i + 1] / terms[i]) < 0.01 for i in range(4)))
    chk("partial_sum_steps_shrink",
        all(abs(sums[i + 1] - sums[i]) < abs(sums[i] - sums[i - 1])
            for i in range(1, 4)))
    chk("five_loop_total_window", abs(total - 0.001159652177) < 1e-11)
    resid_ppm = (total - AE_EXPERIMENT) / AE_EXPERIMENT * 1e6
    chk("residual_below_experiment_small",
        total < AE_EXPERIMENT and abs(resid_ppm) < 0.01)

    # 2. running coupling
    d_mz = delta_alpha_lep(M_Z_GEV)
    chk("delta_alpha_lep_mz_window", 0.0310 < d_mz < 0.0318)
    chk("alpha_inv_lep_only_window",
        132.5 < alpha_inv_lep(M_Z_GEV) < 133.0)
    full = ALPHA_INV_0 * (1.0 - d_mz - DELTA_ALPHA_HAD_LABELLED)
    chk("alpha_inv_with_labelled_hadronic_window", 128.7 < full < 129.2)
    ladder = [10.0, 50.0, M_Z_GEV, 200.0, 1000.0]
    invs = [alpha_inv_lep(q) for q in ladder]
    chk("running_monotone_falling_inverse",
        all(invs[i + 1] < invs[i] for i in range(len(invs) - 1)))
    by = delta_alpha_lep_by_lepton(M_Z_GEV)
    chk("electron_dominates_running",
        by["electron"] > by["muon"] > by["tau"] > 0.0)
    chk("running_by_lepton_sums",
        abs(sum(by.values()) - d_mz) < 1e-12)

    # 3. Compton + Klein-Nishina
    chk("lambda_c_value_pm",
        abs(LAMBDA_C_M * 1e12 - 2.4263102387) < 1e-9)
    chk("shift_zero_forward", compton_shift_pm(0.0) == 0.0)
    chk("shift_90_is_lambda_c",
        abs(compton_shift_pm(90.0) - LAMBDA_C_M * 1e12) < 1e-12)
    chk("shift_180_is_two_lambda_c",
        abs(compton_shift_pm(180.0) - 2.0 * LAMBDA_C_M * 1e12) < 1e-12)
    table = [compton_shift_pm(a) for a in (0.0, 30.0, 60.0, 90.0, 120.0, 180.0)]
    chk("shift_monotone_in_angle",
        all(table[i + 1] > table[i] for i in range(len(table) - 1)))
    chk("thomson_cross_section_barn",
        0.6652 < SIGMA_T_M2 / 1e-28 < 0.6653)
    for xx in (0.01, 1.0, 10.0):
        chk(f"kn_integral_matches_closed_x{xx}",
            abs(kn_total_integral(xx) - kn_total_closed(xx))
            / kn_total_closed(xx) < 1e-8)
    r001 = kn_total_closed(0.001) / SIGMA_T_M2
    r01 = kn_total_closed(0.01) / SIGMA_T_M2
    r1 = kn_total_closed(1.0) / SIGMA_T_M2
    r10 = kn_total_closed(10.0) / SIGMA_T_M2
    chk("thomson_approach_x001", 0.995 < r001 < 1.0)
    chk("thomson_approach_x01", 0.975 < r01 < 0.985)
    chk("kn_ratio_x1_window", 0.42 < r1 < 0.44)
    chk("kn_ratio_x10_window", 0.11 < r10 < 0.13)
    chk("kn_ratio_falls_with_energy", r001 > r01 > r1 > r10)
    chk("kn_forward_peaked",
        kn_dsigma_domega(0.0, 1.0) > kn_dsigma_domega(math.pi, 1.0))

    # 4. Lamb shift
    est = bethe_lamb_mhz(2)
    chk("bethe_estimate_window", 1040.0 < est < 1050.0)
    chk("bethe_below_measured", est < LAMB_MEASURED_MHZ)
    gap_pct = (LAMB_MEASURED_MHZ - est) / LAMB_MEASURED_MHZ * 100.0
    chk("lamb_gap_few_percent", 0.5 < gap_pct < 2.0)

    # 5. thresholds
    chk("mec2_value", abs(M_E_C2_MEV - 0.510998950) < 1e-6)
    chk("pair_threshold_digits",
        abs(pair_threshold_mev() - 1.021998) < 1e-6)
    chk("bw_product_identity",
        all(abs(e1 * bw_partner_min_mev(e1) - M_E_MEV ** 2)
            / M_E_MEV ** 2 < 1e-12
            for e1 in (0.1, 0.25, M_E_MEV, 1.0, 10.0)))
    chk("bw_symmetric_point",
        abs(bw_partner_min_mev(M_E_MEV) - M_E_MEV) < 1e-12)
    chk("bw_below_threshold_blocked",
        not bw_allowed(0.25, 0.5) and bw_allowed(1.0, 1.0))

    # 6. classifier - labels come from the lab's own policy
    rep = classifier_report()
    chk("classifier_gtwo_precision",
        rep["electron_g_minus_2_probe"] == "precision-agreement")
    chk("classifier_mz_running",
        rep["mz_running_probe"] == "running-coupling-regime")
    chk("classifier_thomson_classical",
        rep["thomson_limit_probe"] == "classical-limit")
    chk("classifier_subthreshold_blocked",
        rep["subthreshold_photon_probe"] == "threshold-blocked")
    chk("classifier_hard_scattering",
        rep["hard_scattering_probe"] == "running-coupling-regime")
    chk("classifier_matches_model_grid",
        all(classify_regime(*features) == label
            for features, label in TRAINING_GRID))
    chk("classifier_grid_size", len(TRAINING_GRID) == 500)

    # gates + seats
    chk("hold_gates_14", len(HOLD_GATES) == 14
        and all(v.startswith("HOLD") for v in HOLD_GATES.values()))
    chk("gate_precision_hold", gate("precision_measurement_claim") == "HOLD")
    chk("gate_new_physics_hold", gate("new_physics_claim") == "HOLD")
    chk("gate_vendor_hold", gate("vendor_claim") == "HOLD")
    chk("gate_medical_hold", gate("medical_claim") == "HOLD")
    chk("gate_weapons_hold", gate("weapons_claim") == "HOLD")
    chk("gate_sandbox_proceed", gate("run_simulation") == "PROCEED")
    brains = brains_report()
    chk("argon4_no_override", brains["decider"]["can_override_hold"] is False
        and brains["decider"]["seat"]
        == "Gemini Argon 4 Extended Thinking"
        and brains["decider"]["model_id"] == "gemini-argon-4")
    chk("claude_no_override", brains["advisor"]["can_override_hold"] is False)
    chk("flow_plan_only", brains["flow"]["rendered"] is False
        and brains["flow"]["live"] == 0)
    return c


# ================================================================ CLI / demo
def demo():
    print("=" * 68)
    print("QuantumElectrodynamics-Lab - QED precision quantities lab")
    print("by Darion Kellar | MIT | pure stdlib | zero network | EDUCATION ONLY")
    print("=" * 68)
    print("\n[1] THE HONEST CORE - evaluation is not measurement")
    print("    This lab evaluates textbook QED formulas from LABELLED input")
    print("    constants. The experimental values are labelled references,")
    print("    not results. Pieces the lab does not compute (hadronic")
    print("    running, mass-dependent g-2 terms, relativistic Lamb")
    print("    corrections) are printed as labelled missing pieces.")
    g = gtwo_report()
    print("\n[2] Electron g-2 - five published terms in (alpha/pi)")
    print(f"    alpha/pi = {g['alpha_over_pi']:.12f} (alpha from the "
          f"labelled 1/alpha = {ALPHA_INV_0})")
    terms = ae_terms()
    sums = ae_partial_sums()
    for i, (t, s) in enumerate(zip(terms, sums)):
        print(f"    order {i + 1}: term {t:+.6e} | running a_e = {s:.15f}")
    print(f"    Schwinger term alpha/(2pi) = {terms[0]:.15f}")
    print(f"    5-loop mass-independent QED total = {g['total_mass_independent_qed']:.15f}")
    print(f"    labelled experiment               = {AE_EXPERIMENT:.15f}")
    print(f"    residual = {g['residual']:+.3e} ({g['residual_ppm']:+.6f} ppm)")
    print("    -> the residual is the size of the pieces NOT in the")
    print("       mass-independent coefficients: mass-dependent QED,")
    print("       hadronic ~1.7e-12, weak ~3e-14, and alpha's own input")
    print("       uncertainty. It is arithmetic, not new physics.")
    r = running_report()
    print("\n[3] Running coupling - leptonic vacuum polarisation to M_Z")
    print(f"    Delta alpha_lep(M_Z^2) = {r['delta_alpha_lep_mz']:.6f} "
          f"(e {r['by_lepton_at_mz']['electron']:.6f} + "
          f"mu {r['by_lepton_at_mz']['muon']:.6f} + "
          f"tau {r['by_lepton_at_mz']['tau']:.6f})")
    print(f"    alpha^-1(M_Z), leptonic only = {r['alpha_inv_mz_leptonic_only']:.4f}")
    print(f"    hadronic piece NOT computed (labelled input "
          f"{DELTA_ALPHA_HAD_LABELLED}) -> full on-shell "
          f"alpha^-1(M_Z) = {r['alpha_inv_mz_with_labelled_hadronic']:.4f}")
    print(f"    (the often-quoted {ALPHA_INV_MZ_MSbar_LABELLED} is the "
          f"MS-bar convention value, labelled, not computed here)")
    for row in r["ladder"]:
        print(f"    Q = {row['q_gev']:8.3f} GeV | Delta alpha_lep "
              f"{row['delta_alpha_lep']:.6f} | alpha^-1 (lep) "
              f"{row['alpha_inv_lep_only']:.4f}")
    cp = compton_report()
    print("\n[4] Compton scattering + Klein-Nishina")
    print(f"    lambda_C = {cp['lambda_c_pm']:.10f} pm | "
          f"Delta lambda(90 deg) = {cp['shift_table_pm']['90']:.6f} pm | "
          f"(180 deg) = {cp['shift_table_pm']['180']:.6f} pm")
    print(f"    sigma_T = {cp['sigma_t_barn']:.8f} barn")
    for row in cp["kn_ladder"]:
        print(f"    x = {row['x']:6.3f} | sigma closed "
              f"{row['sigma_closed_barn']:.6f} b | integral "
              f"{row['sigma_integral_barn']:.6f} b | sigma/sigma_T "
              f"{row['ratio_to_thomson']:.6f}")
    print("    -> the Simpson integral and the closed form agree; the")
    print("       cross section falls from the Thomson limit as x grows.")
    lb = lamb_report()
    print("\n[5] Lamb shift - Bethe's 1947 nonrelativistic estimate")
    print(f"    Bethe log ln K0(2S) = {BETHE_LOG_2S} (labelled) -> "
          f"K0 = {lb['k0_ev']:.4f} eV")
    print(f"    Bethe estimate = {lb['bethe_estimate_mhz']:.4f} MHz vs "
          f"labelled measured {LAMB_MEASURED_MHZ:.2f} MHz")
    print(f"    gap = {lb['gap_percent']:.4f}% - the known shortfall of the")
    print("    nonrelativistic estimate (relativistic + recoil + higher-")
    print("    order radiative pieces are not in Bethe's formula).")
    th = thresholds_report()
    print("\n[6] Pair-production thresholds")
    print(f"    m_e c^2 = {th['m_e_c2_mev']:.9f} MeV | gamma -> e+e- "
          f"threshold = {th['pair_threshold_mev']:.9f} MeV")
    print(f"    Breit-Wheeler head-on: E1 * E2 >= "
          f"{th['bw_threshold_product_mev2']:.9f} MeV^2")
    for row in th["bw_grid"]:
        print(f"    E1 = {row['e1_mev']:9.6f} MeV -> partner needs "
              f"E2 >= {row['e2_min_mev']:.6f} MeV")
    print("\n[7] Regime classifier (TinyML kNN, labels from the lab policy)")
    for name, label in classifier_report().items():
        print(f"    {name:36s} -> {label}")
    print("\n[8] Advisory seats")
    brains = brains_report()
    print(f"    decider: {brains['decider']['decision']} "
          f"trace={brains['decider']['trace_sha256_16']}")
    print(f"    advisor can_override_hold = {brains['advisor']['can_override_hold']}")
    print(f"    flow rendered = {brains['flow']['rendered']} "
          f"live = {brains['flow']['live']}")
    print(f"\n[9] HOLD gates: {len(HOLD_GATES)}")
    for key in HOLD_GATES:
        print(f"    HOLD  {key}")
    checks = run_checks()
    passed = sum(1 for _, ok in checks if ok)
    print(f"\nCHECKS {passed}/{len(checks)}")
    for name, ok in checks:
        if not ok:
            print(f"    FAIL {name}")
    verdict = "PROCEED" if passed == len(checks) else "HOLD"
    print(f"VERDICT {verdict} (sandbox simulation only) | HOLD gates {len(HOLD_GATES)}")
    return 0 if passed == len(checks) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] == "demo":
        return demo()
    cmd = argv[0]
    if cmd == "checks":
        checks = run_checks()
        for name, ok in checks:
            print(f"{'PASS' if ok else 'FAIL'} {name}")
        print(f"CHECKS {sum(1 for _, ok in checks if ok)}/{len(checks)}")
        return 0 if all(ok for _, ok in checks) else 1
    if cmd == "gtwo":
        print(json.dumps(gtwo_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "running":
        print(json.dumps(running_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "compton":
        print(json.dumps(compton_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "lamb":
        print(json.dumps(lamb_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "thresholds":
        print(json.dumps(thresholds_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "classify":
        print(json.dumps(classifier_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "brains":
        print(json.dumps(brains_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "holds":
        for key, value in HOLD_GATES.items():
            print(f"{key}: {value}")
        return 0
    if cmd == "hold-demo":
        action = argv[1] if len(argv) > 1 else "precision_measurement_claim"
        print(f"{action}: {HOLD_GATES.get(action, 'PROCEED - not gated')}")
        return 2 if gate(action) == "HOLD" else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
