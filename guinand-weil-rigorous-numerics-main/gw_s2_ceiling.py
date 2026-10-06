# -*- coding: utf-8 -*-
"""S2 CEILING DIAGNOSTIC -- does the S2 instrument fail to REACH
"CONSISTENT WITH MONTGOMERY/GUE" on a genuine GUE fixture because of an
ALGORITHM/ESTIMATOR DEFECT, or because of a finite-N power ceiling at N=401?

ASKED AFTER the audited run ke-2.  Nothing here changes gw_montgomery.py, no
audited log is touched, and no pre-registered rule of #1001630/#1001631 is
altered.  This script only MEASURES and prints.

WHY THE ANSWER IS NOT OBVIOUS (the structural prior, stated before measuring)
---------------------------------------------------------------------------
A Monte-Carlo p-value is valid only if observation and reference surrogates
are pushed through the SAME coordinate transformation (exchangeability).
Audited code path, gw_montgomery.py main():

    charts   = {"T": np.log(lam), "L": lam}          # observation
    surrogates:  x = unfold(ens[kind][s], su)         # line 498 -- LINEAR chart
    chart L obs : x = unfold(lam, su)                 # same transform  -> OK
    chart T obs : x = unfold(np.log(lam), su)         # DIFFERENT       -> ?

`unfold()` is affine-invariant (local_spacing uses differences only, then
mean gap is rescaled), so a constant fixture shift does not matter -- TEST 0
measures that rather than asserting it.  A LOG transform is not affine, so
chart T is the candidate defect.  That is TEST A.

Even with a perfectly calibrated instrument, verdict "CONSISTENT..." needs BOTH

    p_GUE  = P(chi2_GUE  >= chi2_obs) >= 0.05      (do not reject GUE)
    p_Pois = P(chi2_Pois <= chi2_obs) <  0.05      (reject Poisson)

i.e. chi2_obs must lie below  min( q95(chi2_GUE), q05(chi2_Pois) ).
How tight that window is depends on N through the pairs-per-bin count.
That is TEST B: power and calibration as functions of N.

TEST 0  affine invariance of unfold()            -> justifies chart-L analysis
TEST A  exchangeability audit, chart T           -> "algorithm defect?"
TEST B  power + calibration vs N                 -> "N=401 ceiling?"

READ THE OUTPUT AS: numbers, not verdicts.  A rate that should be 0.05 and is
0.05 proves calibration; a rate that should be 0.05 and is 0.000 does not.

SEED is declared here, before any draw: 20260928 (deliberately NOT 20260927,
so this diagnostic can never be confused with an audited run).

Tool status: python 3.14 + numpy + scipy. lean/coqc/isabelle/dkcheck/z3/gcc
NOT RUN.  Not a claim about RH, Weil positivity, prime counting or factoring.
"""

import argparse
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gw_montgomery as G  # reuse the audited pipeline functions unchanged

# gw_montgomery defines T0 only INSIDE main() (line 416: `global T0`), so the
# progress printer in generate_ensemble (line 255) and ckpt() raise NameError
# when the module is IMPORTED rather than run as a script. Inject it from here
# instead of editing the audited module -- that file is evidence.
G.T0 = time.time()

T0 = time.time()
SEED = 20260928
N_REF_SUF = 1200          # Poisson reference size at N=401 (scaled down for big N)


def log(msg):
    print("[%7.1f s] %s" % (time.time() - T0, msg), flush=True)


def fixture_shift(e):
    """Exactly the shift gw_mont_pipeline_check.make_spectrum applies."""
    e = np.asarray(e, dtype=float)
    return e - e.min() + abs(e.min()) * 1e-3 + 1e-3


def u_centers():
    return np.arange(G.DU * 0.5, G.U_MAX, G.DU)


def curves(spectra, sigma_u, use_log):
    """(n, N_BINS) R2 curves, one row per spectrum, via the audited estimator."""
    uc = u_centers()
    out = np.empty((len(spectra), uc.size))
    for i, s in enumerate(spectra):
        y = np.log(fixture_shift(s)) if use_log else np.asarray(s, dtype=float)
        out[i] = G.r2_curve(G.unfold(y, sigma_u))[1]
    return out


def weights_from(ref_curves):
    v = ref_curves.var(axis=0, ddof=1)
    v[v <= 0] = np.finfo(float).tiny
    return 1.0 / v


def chi2_of(c, w, tgt):
    return np.sum(w[None, :] * (c - tgt[None, :]) ** 2, axis=1)


def rate(x):
    """mean + Wilson-free simple SE, printed as percentage +- SE."""
    p = float(np.mean(x))
    n = len(x)
    se = float(np.sqrt(max(p * (1 - p), 1e-12) / n))
    return "%6.2f%% +-%4.2f" % (100 * p, 100 * se)


def psummary(name, p):
    p = np.asarray(p, dtype=float)
    log("    %-34s mean=%.3f med=%.3f  p<0.05: %-15s  p>0.95: %s"
        % (name, p.mean(), np.median(p), rate(p < 0.05), rate(p > 0.95)))


# --------------------------------------------------------------------------- #
def test0(rng, n_levels=401):
    """unfold() must be unchanged by the fixture's constant shift (chart L)."""
    log("TEST 0 -- affine invariance of unfold()  (why chart L is exchangeable)")
    worst = 0.0
    for _ in range(5):
        A = rng.standard_normal((n_levels, n_levels))
        B = rng.standard_normal((n_levels, n_levels))
        H = ((A + 1j * B) / np.sqrt(2.0 * n_levels))
        H = (H + H.conj().T) / 2.0
        e = np.sort(np.linalg.eigvalsh(H))
        for su in G.SIGMA_U:
            d = np.abs(G.unfold(e, su) - G.unfold(fixture_shift(e), su)).max()
            worst = max(worst, float(d))
    log("    max |unfold(e) - unfold(shift(e))| over 5 draws x %d sigma_u = %.3e"
        % (len(G.SIGMA_U), worst))
    log("    -> chart L: fixture shift is invisible to the estimator: %s"
        % ("EXCHANGEABLE" if worst < 1e-9 else "NOT exchangeable"))
    return worst


# --------------------------------------------------------------------------- #
def test_a(n_ref, n_test, n_levels=401, n_pois=1200):
    """Is chart T's p-value calibrated?  Compare 3 constructions."""
    log("TEST A -- exchangeability audit for chart T (log) vs chart L (linear)")
    log("         N=%d, n_ref=%d, n_test=%d, seed=%d" % (n_levels, n_ref, n_test, SEED))
    rng = np.random.default_rng(SEED + 1)
    ref = G.generate_ensemble("gue", n_levels, n_ref, rng)
    test = G.generate_ensemble("gue", n_levels, n_test, rng)
    uc = u_centers()
    tgt = G.montgomery_smoothed(uc)

    # pre-registration note: the audited code computes ONE weight vector per
    # sigma_u, from the LINEAR-chart GUE surrogates, and uses it for BOTH charts.
    w_lin = {}
    w_log = {}
    ref_lin = {}
    ref_log = {}
    for su in G.SIGMA_U:
        ref_lin[su] = curves(ref, su, use_log=False)
        ref_log[su] = curves(ref, su, use_log=True)
        w_lin[su] = weights_from(ref_lin[su])
        w_log[su] = weights_from(ref_log[su])
        log("    sigma_u %.1f  ref curves built (linear + log)" % su)

    pois = G.generate_ensemble("poisson", n_levels, n_pois, rng)

    for su in G.SIGMA_U:
        obs_lin = curves(test, su, use_log=False)
        obs_log = curves(test, su, use_log=True)
        pois_lin = curves(pois, su, use_log=False)
        pois_log = curves(pois, su, use_log=True)

        # control: chart L, every side linear -> must be ~U(0,1)
        chi_obs_lin = chi2_of(obs_lin, w_lin[su], tgt)
        chi_ref_lin = chi2_of(ref_lin[su], w_lin[su], tgt)
        chi_pois_lin = chi2_of(pois_lin, w_lin[su], tgt)
        # chart T exactly as audited: log-chart OBSERVATION against the
        # LINEAR-chart reference and LINEAR weights (gw_montgomery.py:498
        # unfolds every surrogate on its own linear eigenvalue chart).
        chi_obs_log_as = chi2_of(obs_log, w_lin[su], tgt)
        # chart T exchangeable: every side in the log chart, weights from the
        # log-chart reference (what a valid Monte-Carlo p-value requires).
        chi_obs_log_ex = chi2_of(obs_log, w_log[su], tgt)
        chi_ref_log_ex = chi2_of(ref_log[su], w_log[su], tgt)
        chi_pois_ex = chi2_of(pois_log, w_log[su], tgt)

        p_ctrl = np.mean(chi_ref_lin[:, None] >= chi_obs_lin[None, :], axis=1)
        p_as_is = np.mean(chi_ref_lin[:, None] >= chi_obs_log_as[None, :], axis=1)
        p_exch = np.mean(chi_ref_log_ex[:, None] >= chi_obs_log_ex[None, :], axis=1)

        log("  -- sigma_u %.1f --" % su)
        log("     chi2  obs_L=%.1f   obs_T=%.1f   ref_L[med,q95]=%.1f,%.1f   "
            "ref_T[med,q95]=%.1f,%.1f"
            % (np.median(chi_obs_lin), np.median(chi_obs_log_as),
               np.median(chi_ref_lin), np.quantile(chi_ref_lin, 0.95),
               np.median(chi_ref_log_ex), np.quantile(chi_ref_log_ex, 0.95)))
        psummary("CONTROL chart L (must be ~U(0,1))", p_ctrl)
        psummary("chart T AS AUDITED (log obs, lin ref)", p_as_is)
        psummary("chart T EXCHANGEABLE (log obs, log ref)", p_exch)

        # acceptance power of each construction (window = below both gates)
        thr_l = min(float(np.quantile(chi_ref_lin, 0.95)),
                    float(np.quantile(chi_pois_lin, 0.05)))
        thr_t_as = thr_l                       # audited chart T shares both gates
        thr_t_ex = min(float(np.quantile(chi_ref_log_ex, 0.95)),
                       float(np.quantile(chi_pois_ex, 0.05)))
        log("     power chart L (control)          = %s" % rate(chi_obs_lin < thr_l))
        log("     power chart T AS AUDITED          = %s" % rate(chi_obs_log_as < thr_t_as))
        log("     power chart T EXCHANGEABLE        = %s" % rate(chi_obs_log_ex < thr_t_ex))
        log("     gates chart L  q95_GUE=%.1f  q05_Pois=%.1f   |   chart T exch  "
            "q95_GUE=%.1f  q05_Pois=%.1f"
            % (np.quantile(chi_ref_lin, 0.95), np.quantile(chi_pois_lin, 0.05),
               np.quantile(chi_ref_log_ex, 0.95), np.quantile(chi_pois_ex, 0.05)))


# --------------------------------------------------------------------------- #
def test_b(sweep, n_ref_map, n_test_map, n_levels_list, n_pois_map=None):
    """Power and calibration of the ACCEPT side as a function of N."""
    uc = u_centers()
    tgt = G.montgomery_smoothed(uc)
    log("TEST B -- power vs N   (seed=%d, chart L, exchangeable by TEST 0)" % SEED)
    rows = {}
    for idx, N in enumerate(n_levels_list):
        n_ref, n_test = n_ref_map[N], n_test_map[N]
        n_pois = (n_pois_map or {}).get(N) or \
            max(250, min(N_REF_SUF, N_REF_SUF * 401 // N))
        log("  N=%d : n_ref=%d n_test=%d n_pois=%d" % (N, n_ref, n_test, n_pois))
        rng = np.random.default_rng(SEED + 100 + N)
        gue_ref = G.generate_ensemble("gue", N, n_ref, rng)
        gue_test = G.generate_ensemble("gue", N, n_test, rng)
        pois = G.generate_ensemble("poisson", N, n_pois, rng)

        for su in G.SIGMA_U:
            c_ref = curves(gue_ref, su, use_log=False)
            c_test = curves(gue_test, su, use_log=False)
            c_pois = curves(pois, su, use_log=False)
            w = weights_from(c_ref)
            chi_r = chi2_of(c_ref, w, tgt)
            chi_t = chi2_of(c_test, w, tgt)
            chi_p = chi2_of(c_pois, w, tgt)

            q95g = float(np.quantile(chi_r, 0.95))
            q05p = float(np.quantile(chi_p, 0.05))
            thr = min(q95g, q05p)
            calib = float(np.mean(chi_t > q95g))     # must be ~0.05
            power = float(np.mean(chi_t < thr))
            rows.setdefault((su, N), dict(
                mu_g=float(chi_r.mean()), sd_g=float(chi_r.std(ddof=1)),
                mu_p=float(chi_p.mean()), sd_p=float(chi_p.std(ddof=1)),
                q95g=q95g, q05p=q05p, sep=q05p / q95g,
                calib=calib, power=power, n_test=n_test))
            log("    su %.1f  mu_GUE=%.1f+-%.1f  mu_Pois=%.1f+-%.1f  "
                "q05_Pois=%.1f  q95_GUE=%.1f  sep=%.2f  calib=%s  power=%s"
                % (su, chi_r.mean(), chi_r.std(ddof=1), chi_p.mean(),
                   chi_p.std(ddof=1), q05p, q95g, q05p / q95g,
                   rate(chi_t > q95g), rate(chi_t < thr)))

    log("")
    log("=" * 100)
    log("TEST B SUMMARY -- verdict window  [ , min(q95_GUE, q05_Pois) )")
    log("=" * 100)
    log("  sigma_u      N  n_test   mu_GUE   sd_GUE  mu_Pois   sep=q05P/q95G  calib(is 0.05)  power")
    for su in G.SIGMA_U:
        for N in n_levels_list:
            r = rows[(su, N)]
            log("    %.1f  %5d  %6d  %8.1f %8.1f %8.1f     %6.2f      %8.2f%%  %8.1f%%"
                % (su, N, r["n_test"], r["mu_g"], r["sd_g"], r["mu_p"],
                   r["sep"], 100 * r["calib"], 100 * r["power"]))
        log("")


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tests", default="0,A,B", help="any of 0,A,B")
    ap.add_argument("--sweep", default="401,801,1601")
    ap.add_argument("--n-ref", default="500,300,100")
    ap.add_argument("--n-test", default="250,150,60")
    ap.add_argument("--n-ref-a", type=int, default=400)
    ap.add_argument("--n-test-a", type=int, default=250)
    ap.add_argument("--n-pois-a", type=int, default=1200)
    ap.add_argument("--n-pois-b", default="",
                    help="override Poisson reference size per N (comma list)")
    a = ap.parse_args()

    which = set(x.strip() for x in a.tests.split(","))
    Ns = [int(x) for x in a.sweep.split(",")]
    n_ref_map = dict(zip(Ns, [int(x) for x in a.n_ref.split(",")]))
    n_test_map = dict(zip(Ns, [int(x) for x in a.n_test.split(",")]))
    n_pois_map = dict(zip(Ns, [int(x) for x in a.n_pois_b.split(",")])) \
        if a.n_pois_b else None
    rng = np.random.default_rng(SEED)

    log("S2 CEILING DIAGNOSTIC -- seed %d declared BEFORE any draw" % SEED)
    log("SIGMA_U=%s SIGMA_E=%.1f U_MAX=%.1f DU=%.1f N_BINS=%d"
        % (list(G.SIGMA_U), G.SIGMA_E, G.U_MAX, G.DU, G.N_BINS))
    log("tool: python %s + numpy %s + scipy; lean/coqc/isabelle/z3 NOT RUN"
        % (sys.version.split()[0], np.__version__))
    log("")

    if "0" in which:
        test0(rng)
        log("")
    if "A" in which:
        test_a(a.n_ref_a, a.n_test_a, n_pois=a.n_pois_a)
        log("")
    if "B" in which:
        test_b(None, n_ref_map, n_test_map, Ns, n_pois_map)
        log("")
    log("DONE in %.1f s" % (time.time() - T0))


if __name__ == "__main__":
    main()
