# -*- coding: utf-8 -*-
"""OPS I (d) -- Montgomery pair correlation / GUE-consistency test of the
certified Guinand-Weil spectrum.

PRE-REGISTERED RULES -- brain entry #1001630, written BEFORE any eigenvalue
existed. Nothing here may be tuned after seeing results.

WHAT IS BEING ASKED
-------------------
Montgomery's pair-correlation theorem is CONDITIONAL ON RH and is about the
zeros of the Riemann zeta function. This run has neither. What it has is the
full spectrum of one finite, deterministic, constructed matrix. The only
question this script can answer is:

    can the unfolded spectral statistics of THIS 401-level matrix be
    DISTINGUISHED from the Montgomery/GUE kernel at N = 401?

Agreement is a statement about a finite matrix. It is NOT evidence for RH, not
Weil positivity, not prime counting, not factorisation -- the source preprint
disclaims all four. "Certified" means an arb ball enclosure at a stated
precision, never absolute truth.

GATES (from gw_spectrum_arb.py, re-checked here)
------------------------------------------------
  G-M0 gate must read PASS in the input file; otherwise ABORT with no
  statistics.

STATISTICS
----------
  S1  mean adjacent gap ratio r_bar -- UNFOLDING-FREE, computed on the raw
      chart. Charts: T = ln(lambda) [PRIMARY], L = lambda [SECONDARY].
      Both are always reported; the favourable one is never chosen after
      seeing results.
  S2  pair correlation R2(u) vs Montgomery kernel 1 - (sin(pi u)/(pi u))^2.
      Unfolding: Gaussian-kernel smoothing of the counting function with
      adaptive bandwidth sigma_u x local mean spacing, sigma_u in
      {0.3, 0.5, 1.0}. Estimator smoothing sigma_e = 0.5 (fixed).
      Bins: u_max = 10.0, Delta u = 0.5 -> 20 bins; bins whose expected pair
      count is < 5 are dropped AND reported.

SURROGATES (matched N = 401, 2000 samples each, numpy seed 20260927)
---------------------------------------------------------------------
  GUE (beta=2), GOE (beta=1), Poisson. Every surrogate goes through the
  IDENTICAL pipeline (unfold -> histogram -> chi^2 against the same Montgomery
  target, weighted by the GUE surrogate variance). References for r_bar come
  from THIS matched-N simulation, not from memorised constants; 0.5995 /
  0.5307 / 0.3863 are printed only as sanity labels. The GUE label 0.5359 was
  printed by run #1 and is RETRACTED (defect 17 -- see LABEL_GUE below).

VERDICT RULES
-------------
  S1: inside Poisson CI AND outside RMT CI -> CONSISTENT WITH POISSON
      inside RMT CI    AND outside Poisson -> CONSISTENT WITH RMT
      inside both                            -> NO DISCRIMINATION
      inside neither                         -> INCONSISTENT WITH ALL
  S2: p_GUE  = P(chi^2_GUE  >= chi^2_obs)         (upper tail)
      p_Pois = P(chi^2_Pois <= chi^2_obs)         (LOWER tail)
      p_GUE >= 0.05 and p_Pois <  0.05 -> CONSISTENT WITH MONTGOMERY/GUE,
                                         DISTINGUISHABLE FROM POISSON
      p_GUE >= 0.05 and p_Pois >= 0.05 -> NO DISCRIMINATION AT N=401
      p_GUE <  0.05                    -> INCONSISTENT WITH MONTGOMERY
                                         AT THIS RESOLUTION
  AMENDMENT brain #1001631 (registered BEFORE any real spectrum was read):
  the Poisson tail was originally the upper tail. On synthetic fixtures that
  mis-reported a GENUINE GUE spectrum as NO DISCRIMINATION -- chi^2_obs ~ 25
  while every Poisson draw is ~1000, so the upper-tail p is 1. Only the tail
  DIRECTION changed; the 0.05 threshold, the bins, sigma_e, the sigma_u grid
  and the seed are untouched. K1..K5 were NOT tightened, added or altered.
  S2 must give the SAME verdict on every point of the grid
  {chart} x {sigma_u}; otherwise UNSTABLE (grid-dependent).

PRE-REGISTERED EXPECTATIONS (predictions, not verdicts)
-------------------------------------------------------
  1. GOE vs GUE will NOT be separable at N = 401: Delta r_bar ~ 0.005 while
     the standard error is ~ sigma_r / sqrt(400) ~ 0.012.
  2. The spectrum spans ~295 orders (kappa 4.42e294 x lambda_min 1.737e-294
     -> lambda_max ~ 7.68), so chart L will be badly non-uniform and chart T
     is the natural candidate. If T and L disagree, report CHART-DEPENDENT.
  3. N = 401 gives ~200 pairs per bin; that is the resolution ceiling.

TOOL STATUS: python 3.14 + numpy 2.5.2 + scipy 1.18.0 + mpmath + python-flint.
lean / coqc / isabelle / dkcheck / z3 / gcc NOT RUN.

usage:
    python gw_montgomery.py gw_spectrum_100_200.json
    python gw_montgomery.py gw_spectrum_100_200.json --samples 2000
"""

import json
import math
import sys
import time

import numpy as np
from scipy.stats import norm
import mpmath as mp

SEED = 20260927
SIGMA_E = 0.5           # estimator smoothing, pre-registered fixed
SIGMA_U = (0.3, 0.5, 1.0)   # unfolding bandwidths, pre-registered grid
U_MAX = 10.0
DU = 0.5
N_BINS = int(round(U_MAX / DU))
MIN_EXPECTED = 5.0      # pre-registered: drop bins with expected count < 5

# Sanity labels only -- they enter NO verdict. Every reference the rules use
# comes from the matched-N simulation below.
# DEFECT 17: the GUE label 0.5359 was WRONG and is retracted. A universality
# control swept the diagonal-variance ratio {0.5, 1, 2} for both classes and
# found r_bar invariant to within one standard error (spread 0.00066 and
# 0.00063), giving beta=1 -> 0.5301 and beta=2 -> 0.5995. That the statistic
# does not move under the normalisation sweep is what shows the CONSTRUCTION
# is right and the LABEL was wrong. GOE 0.5307 and Poisson 0.3863 confirmed.
# External source NOT consulted (websearch unavailable) -- these are values
# measured here, not cited ones.
LABEL_GUE, LABEL_GOE, LABEL_POISSON = 0.5995, 0.5307, 0.3863
LABEL_GUE_RETRACTED = 0.5359


def ckpt(msg):
    print(msg, flush=True)


FINE = 0.01           # histogram / quadrature step, << sigma_e = 0.5


def montgomery(u):
    """1 - (sin(pi u)/(pi u))^2, with the u->0 limit of 0 handled exactly."""
    u = np.asarray(u, dtype=float)
    out = np.empty_like(u)
    small = np.abs(u) < 1e-12
    out[small] = 0.0
    t = np.pi * u[~small]
    s = np.sin(t) / t
    out[~small] = 1.0 - s * s
    return out


def montgomery_smoothed(u, sigma_e=SIGMA_E, u_max=U_MAX):
    """The Montgomery kernel passed through the SAME Gaussian smoothing the
    estimator applies to the data (defect 12).

    r2_curve returns a histogram of pairwise differences convolved with a
    Gaussian of width sigma_e, i.e. an estimate of (R2 * Gauss_sigma_e)(u).
    Comparing that to the UNsmoothed analytic kernel is an apples-to-oranges
    mismatch -- on a genuine GUE sample it produced R2(0.25) = 0.4022 against
    a target of 0.1894 purely from the estimator's own resolution. Discovered
    on synthetic fixtures BEFORE any real spectrum was read; the pre-registered
    thresholds (0.05, bins, sigma grid) are untouched by this fix.
    """
    u = np.asarray(u, dtype=float)
    fine = np.arange(-(u_max + 1.0), u_max + 1.0 + 1e-9, FINE)
    M = montgomery(fine)
    K = np.exp(-((u[:, None] - fine[None, :]) ** 2) / (2 * sigma_e ** 2))
    K /= (math.sqrt(2 * math.pi) * sigma_e)
    return (K @ M) * FINE


def local_spacing(y, k=10):
    """Adaptive local mean spacing at each level, from +/- k neighbours."""
    n = len(y)
    h = np.empty(n)
    kk = min(k, max(1, (n - 1) // 2))
    idx = np.arange(n)
    lo = np.maximum(0, idx - kk)
    hi = np.minimum(n - 1, idx + kk)
    span = y[hi] - y[lo]
    step = (hi - lo).astype(float)
    step[step == 0] = 1.0
    h = span / step
    # guard against any zero / non-positive local spacing
    positive = h[h > 0]
    floor = positive.min() * 1e-6 if positive.size else 1e-300
    h[h <= 0] = floor
    return h


def unfold(y, sigma_u):
    """Gaussian-kernel unfolding of the counting function.

    x_k = sum_m Phi((y_k - y_m) / h_m), h_m = sigma_u * local spacing at m.
    Phi is strictly increasing in y_k, so x is strictly increasing by
    construction -- no post-hoc monotonicity repair is possible or needed.
    Then rescaled so the mean gap is exactly 1.
    """
    y = np.asarray(y, dtype=float)
    # DEFECT 15: sigma_u was accepted as a parameter but never applied, so
    # h_m was just the local spacing and the pre-registered stability grid
    # {0.3, 0.5, 1.0} collapsed to ONE point. chi2 came out bit-identical for
    # all three sigma_u (816.3241 / 816.3241 / 816.3241) -- the 6-point grid
    # test was VACUOUS, not passed. Run #1 is retracted on that basis.
    h = sigma_u * local_spacing(y)
    # AXIS ORDER MATTERS (defect 11): Z[k, m] must be (y_k - y_m)/h_m, i.e.
    # y[:, None] - y[None, :]. Writing y[None, :] - y[:, None] builds the
    # transpose, x came out DECREASING (x[0]~n, x[-1]~0.5) and the mean gap
    # was -1. The pre-registered positive-mean-gap guard caught it before any
    # real spectrum was touched; S1 is unaffected (it never unfolds).
    Z = (y[:, None] - y[None, :]) / h[None, :]
    x = norm.cdf(Z).sum(axis=1)
    gaps = np.diff(x)
    m = gaps.mean()
    if not np.isfinite(m) or m <= 0:
        raise ValueError("unfolding produced non-positive mean gap")
    return x / m


def gap_ratio(y):
    """S1: mean adjacent gap ratio -- no unfolding, chart-dependent only."""
    s = np.diff(np.asarray(y, dtype=float))
    r = np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])
    return float(r.mean()), r


def r2_curve(x, sigma_e=SIGMA_E, u_max=U_MAX, du=DU):
    """S2 estimator: (1/N) sum_{i != j} Gauss(u - (x_i - x_j); sigma_e).

    Expected value is R2(u) for a stationary process of density 1.
    Computed through a histogram of pairwise differences (exact to bin width)
    so 2000 surrogates stay affordable; bin width 0.01 << sigma_e = 0.5.
    """
    n = len(x)
    D = (x[:, None] - x[None, :]).ravel()
    D = D[np.repeat(np.arange(n), n) != np.tile(np.arange(n), n)]
    bins = np.arange(-(u_max + 1.0), u_max + 1.0 + 1e-9, FINE)
    hist, edges = np.histogram(D, bins=bins)
    centers = 0.5 * (edges[:-1] + edges[1:])
    u = np.arange(du * 0.5, u_max, du)          # bin centres, N_BINS of them
    # K[b, c] = Gauss(u_b - centre_c)
    K = np.exp(-((u[:, None] - centers[None, :]) ** 2) / (2 * sigma_e ** 2))
    K /= (math.sqrt(2 * math.pi) * sigma_e)
    return u, (K @ hist.astype(float)) / n


def generate_ensemble(kind, n_levels, n_samples, rng):
    """Matched-N surrogate spectra. Returns array (n_samples, n_levels)."""
    out = np.empty((n_samples, n_levels), dtype=float)
    for s in range(n_samples):
        if kind == "poisson":
            e = np.sort(rng.uniform(0.0, n_levels, n_levels))
        elif kind == "goe":
            A = rng.standard_normal((n_levels, n_levels))
            M = (A + A.T) / math.sqrt(2.0 * n_levels)
            e = np.linalg.eigvalsh(M)
        elif kind == "gue":
            A = rng.standard_normal((n_levels, n_levels))
            B = rng.standard_normal((n_levels, n_levels))
            H = ((A + 1j * B) / math.sqrt(2.0 * n_levels))
            H = (H + H.conj().T) / 2.0
            e = np.linalg.eigvalsh(H)
        else:
            raise ValueError(kind)
        out[s] = np.sort(e)
        if (s + 1) % 500 == 0:
            ckpt("    %s %d/%d done  (%.0f s)" % (kind, s + 1, n_samples,
                                                  time.time() - T0))
    return out


def ci95(a):
    return float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))


def classify_rbar(obs, ci_poi, ci_rmt):
    in_p = ci_poi[0] <= obs <= ci_poi[1]
    in_r = ci_rmt[0] <= obs <= ci_rmt[1]
    if in_p and not in_r:
        return "CONSISTENT WITH POISSON (level repulsion ABSENT)"
    if in_r and not in_p:
        return "CONSISTENT WITH RMT (level repulsion PRESENT)"
    if in_p and in_r:
        return "NO DISCRIMINATION AT N=401"
    return "INCONSISTENT WITH ALL THREE REFERENCES"


def main(argv):
    flags = [a for a in argv[1:] if a.startswith("--")]
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    spec_path = args[0]
    n_samples = 2000
    if "--samples" in argv:
        n_samples = int(argv[argv.index("--samples") + 1])

    ckpt("#" * 96)
    ckpt("# OMEGA OPSI (d) -- MONTGOMERY PAIR CORRELATION / GUE CONSISTENCY")
    ckpt("# input = %s   surrogate samples per ensemble = %d   seed = %d"
         % (spec_path, n_samples, SEED))
    ckpt("#" * 96)
    ckpt("")
    ckpt("PRE-REGISTERED RULES (brain #1001630, locked BEFORE any eigenvalue):")
    ckpt("  S1  r_bar unfolding-free, charts T=ln(lambda) PRIMARY and L=lambda")
    ckpt("      -> report BOTH, never pick the flattering one afterwards")
    ckpt("  S2  R2(u) vs 1-(sin(pi u)/(pi u))^2, sigma_u in {0.3,0.5,1.0},")
    ckpt("      sigma_e=0.5, u in [0,10), 20 bins of 0.5, drop bins with E<5")
    ckpt("  ref GUE / GOE / Poisson, matched N, 2000 samples, seed %d" % SEED)
    ckpt("  S1 verdict: in-Poisson-only -> POISSON; in-RMT-only -> RMT;")
    ckpt("      in both -> NO DISCRIMINATION; in neither -> INCONSISTENT")
    ckpt("  S2 verdict: p_GUE = P(chi2_GUE >= chi2_obs),")
    ckpt("      p_Pois = P(chi2_Pois <= chi2_obs)  [LOWER tail -- amendment")
    ckpt("      #1001631, registered before any real spectrum was read];")
    ckpt("      p_GUE>=0.05 & p_Pois<0.05 -> MONTGOMERY/GUE, distinguishable")
    ckpt("      from Poisson; both >=0.05 -> NO DISCRIMINATION; p_GUE<0.05 ->")
    ckpt("      INCONSISTENT. Must hold on ALL 6 grid points {T,L} x {0.3,0.5,1.0},")
    ckpt("      else UNSTABLE. Threshold 0.05, bins, sigma_e, grid, seed UNCHANGED.")
    ckpt("  EXPECTED (pre-registered): GOE-vs-GUE NOT separable at N=401;")
    ckpt("      spread ~295 orders -> chart L non-uniform; ~200 pairs/bin.")
    ckpt("SCOPE: this is NOT Montgomery's theorem about zeta zeros and NOT an")
    ckpt("       RH / Weil-positivity / prime-counting / factoring claim.")
    ckpt("")

    # ---- load --------------------------------------------------------------
    ckpt("=" * 96)
    ckpt("INPUT SPECTRUM")
    ckpt("=" * 96)
    with open(spec_path, "r", encoding="utf-8") as fh:
        blob = json.load(fh)
    gate = blob.get("gate_verdict", "")
    ckpt("  provenance : c=%d N=%d dps=%d prec=%d algo=%s n=%d"
         % (blob["c"], blob["N"], blob["dps"], blob["prec"], blob["algo"], blob["n"]))
    ckpt("  eig time   : %.1f s" % blob["eig_seconds"])
    ckpt("  G-M0 gate  : %s" % gate)
    ckpt("  G-M0 parts : %s" % json.dumps(blob.get("gate_GM0", {})))
    ckpt("  inertia    : %s" % json.dumps(blob.get("inertia", {})))
    if "PASS" not in gate:
        ckpt("")
        ckpt("  *** G-M0 DID NOT PASS -- ABORTING, NO STATISTICS COMPUTED ***")
        return 1
    lam = np.array([float(e["re"]) for e in blob["eig"]])
    if lam.size != blob["n"]:
        ckpt("  *** eigenvalue count %d != n %d -- ABORT ***" % (lam.size, blob["n"]))
        return 1
    if not np.all(np.isfinite(lam)) or not np.all(lam > 0):
        ckpt("  *** non-finite or non-positive level -- ABORT ***")
        return 1
    lam = np.sort(lam)
    if not np.all(np.diff(lam) > 0):
        ckpt("  *** levels not strictly increasing -- ABORT ***")
        return 1
    n = lam.size
    ckpt("  all %d levels finite, positive, strictly increasing -- OK" % n)
    ckpt("  lambda_min = %.17g" % lam[0])
    ckpt("  lambda_max = %.17g" % lam[-1])
    spread = math.log10(lam[-1] / lam[0])
    if str(blob.get("algo", "")).upper().startswith("SYNTHETIC"):
        ckpt("  spread     = %.6f orders   (synthetic fixture -- the ~295-order"
             % spread)
        ckpt("                pre-registered expectation applies to the REAL matrix only)")
    else:
        ckpt("  spread     = %.6f orders   (pre-registered expectation ~295)" % spread)
    # DEFECT 16: the radii of a real arb run are ~1e-617. float("1.6e-617")
    # underflows to 0.0 (float64 normal range stops at ~1.1e-308), so the old
    # code printed "radii are exactly 0 (synthetic fixture)" on REAL data --
    # a false diagnostic. Parse the radii as exact decimals instead. mp.mp.dps
    # MUST be set before any string -> mpf parse (same landmine class as
    # gw_qinf.py:47); here it is set before the first parse in this function.
    mp.mp.dps = 60
    rad_m = [mp.mpf(e["re_rad"]) for e in blob["eig"]]
    mid_m = [mp.mpf(e["re"]) for e in blob["eig"]]
    nz = [r for r in rad_m if r > 0]
    if not nz:
        synthetic = str(blob.get("algo", "")).upper().startswith("SYNTHETIC")
        ckpt("  all %d enclosure radii are exactly 0 -> %s"
             % (len(rad_m), "synthetic fixture (expected)" if synthetic
                else "*** NON-SYNTHETIC INPUT WITH ZERO RADII -- diagnostic n/a, "
                     "reported as-is"))
    else:
        worst = max(rad_m)
        worst_rel = max(r / abs(m) for r, m in zip(rad_m, mid_m) if m != 0)
        ckpt("  max enclosure radius = %s   (%d of %d levels carry a radius)"
             % (mp.nstr(worst, 10), len(nz), len(rad_m)))
        ckpt("  worst |rad|/|mid|    = 1e%.2f" % mp.log10(worst_rel))
    ckpt("")

    charts = {"T (ln lambda, PRIMARY)": np.log(lam),
              "L (lambda, SECONDARY)": lam.copy()}

    # density picture in chart T (reported, not a gate)
    ckpt("=" * 96)
    ckpt("LEVEL DENSITY IN CHART T = ln(lambda)  (reported)")
    ckpt("=" * 96)
    yT = charts["T (ln lambda, PRIMARY)"]
    hist, edges = np.histogram(yT, bins=20)
    for k, cnt in enumerate(hist):
        ckpt("  bin %2d  y in [%9.2f,%9.2f)  count %3d"
             % (k, edges[k], edges[k + 1], cnt))
    ckpt("")

    # ---- S1 ----------------------------------------------------------------
    ckpt("=" * 96)
    ckpt("S1 -- MEAN ADJACENT GAP RATIO r_bar (unfolding-free)")
    ckpt("=" * 96)
    obs = {}
    for name, y in charts.items():
        rbar, r = gap_ratio(y)
        obs[name] = rbar
        ckpt("  chart %-24s r_bar = %.6f   (n_ratios = %d, min %.3e, max %.3f)"
             % (name, rbar, r.size, r.min(), r.max()))
    ckpt("  sanity labels: GUE %.4f | GOE %.4f | Poisson %.4f" % (LABEL_GUE,
                                                                  LABEL_GOE,
                                                                  LABEL_POISSON))
    ckpt("  (defect 17: the GUE label %.4f printed by run #1 is RETRACTED;"
         % LABEL_GUE_RETRACTED)
    ckpt("   a universality sweep of the diagonal variance over {0.5,1,2} moved")
    ckpt("   r_bar by <1 se in both classes, so the construction is sound and")
    ckpt("   the label -- not the code -- was wrong: beta=2 measures %.4f here)"
         % LABEL_GUE)
    ckpt("  real references come from the matched-N simulation below")
    ckpt("")

    # ---- surrogates --------------------------------------------------------
    ckpt("=" * 96)
    ckpt("SURROGATES -- matched N = %d, %d samples each, seed %d" % (n, n_samples, SEED))
    ckpt("=" * 96)
    global T0
    T0 = time.time()
    rng = np.random.default_rng(SEED)
    ens = {}
    for kind in ("gue", "goe", "poisson"):
        t = time.time()
        ens[kind] = generate_ensemble(kind, n, n_samples, rng)
        ckpt("  %-8s generated in %.1f s" % (kind, time.time() - t))
    ckpt("")

    # S1 references
    ckpt("=" * 96)
    ckpt("S1 REFERENCES (matched-N simulation)")
    ckpt("=" * 96)
    rbar_ref = {}
    for kind in ("gue", "goe", "poisson"):
        vals = np.array([gap_ratio(row)[0] for row in ens[kind]])
        rbar_ref[kind] = vals
        ckpt("  %-8s mean %.6f  sd %.6f  CI95 [%.6f, %.6f]  (label %.4f)"
             % (kind, vals.mean(), vals.std(ddof=1), *ci95(vals),
                {"gue": LABEL_GUE, "goe": LABEL_GOE,
                 "poisson": LABEL_POISSON}[kind]))
    ci_poi = ci95(rbar_ref["poisson"])
    ci_rmt = ci95(np.concatenate([rbar_ref["gue"], rbar_ref["goe"]]))
    ckpt("  pooled RMT CI95 = [%.6f, %.6f]" % ci_rmt)
    ckpt("  SE of r_bar (GUE sd / sqrt(%d)) = %.6f"
         % (n - 1, rbar_ref["gue"].std(ddof=1) / math.sqrt(n - 1)))
    gap1 = abs(rbar_ref["gue"].mean() - rbar_ref["goe"].mean())
    se1 = rbar_ref["gue"].std(ddof=1) / math.sqrt(n - 1)
    ckpt("  pre-registered expectation 1: GOE vs GUE not separable at N=%d" % n)
    ckpt("    measured gap = %.6f against SE = %.6f  ->  %s"
         % (gap1, se1, ("FALSIFIED -- they ARE separable (%.0f SE)" % (gap1 / se1))
            if gap1 > 5.0 * se1 else "HELD (%.1f SE)" % (gap1 / se1)))
    ckpt("    (the expectation was built on the recalled label 0.5359, which")
    ckpt("     defect 17 retracted; the measurement is not adjusted to fit it)")
    ckpt("")

    s1_verd = {}
    for name in charts:
        v = classify_rbar(obs[name], ci_poi, ci_rmt)
        s1_verd[name] = v
        ckpt("  S1 chart %-24s r_bar = %.6f  ->  %s" % (name, obs[name], v))
    # SECONDARY diagnostic: decompose "RMT" into its two members. The verdict
    # above pools GUE+GOE exactly as pre-registered; this decomposition is
    # reported separately and NEVER changes it (secondary diagnostics classify
    # but do not decide). It is what answers "GOE-like or GUE-like?".
    ci_goe = ci95(rbar_ref["goe"])
    ci_gue = ci95(rbar_ref["gue"])
    ckpt("  SECONDARY (does NOT change the verdict above):")
    for name in charts:
        r = obs[name]
        inside = lambda c: "in" if c[0] <= r <= c[1] else "OUT"
        ckpt("    chart %-24s GOE [%s] | GUE [%s] | Poisson [%s]"
             % (name, inside(ci_goe), inside(ci_gue), inside(ci_poi)))
    ckpt("")
    if len(set(s1_verd.values())) == 1:
        s1_final = list(s1_verd.values())[0]
        ckpt("  S1 FINAL (charts agree): %s" % s1_final)
    else:
        s1_final = "CHART-DEPENDENT (T and L disagree) -> INCONCLUSIVE"
        ckpt("  S1 FINAL: %s" % s1_final)
        ckpt("    (pre-registered: report the disagreement, do NOT pick the chart)")
    ckpt("")

    # ---- S2 ----------------------------------------------------------------
    ckpt("=" * 96)
    ckpt("S2 -- PAIR CORRELATION vs MONTGOMERY KERNEL 1 - (sin(pi u)/(pi u))^2")
    ckpt("grid = {chart} x {sigma_u in %s}, sigma_e = %.1f, bins %d x %.1f"
         % (list(SIGMA_U), SIGMA_E, N_BINS, DU))
    ckpt("target = Montgomery convolved with the estimator's own sigma_e")
    ckpt("         (defect 12: comparing a smoothed estimate to an unsmoothed")
    ckpt("          kernel is apples-to-oranges; thresholds unchanged)")
    ckpt("=" * 96)

    # unfold every surrogate once per sigma_u (their own natural chart)
    sur_curves = {}
    for su in SIGMA_U:
        t = time.time()
        buf = []
        for kind in ("gue", "goe", "poisson"):
            cs = np.empty((n_samples, N_BINS))
            for s in range(n_samples):
                x = unfold(ens[kind][s], su)
                _, cv = r2_curve(x)
                cs[s] = cv
            buf.append(cs)
        sur_curves[su] = {"gue": buf[0], "goe": buf[1], "poisson": buf[2]}
        ckpt("  sigma_u %.1f unfolded+binned in %.1f s" % (su, time.time() - t))

    u_centers = np.arange(DU * 0.5, U_MAX, DU)
    # bin weights from the GUE surrogate variance (pre-registered noise model)
    weights = {}
    for su in SIGMA_U:
        var = sur_curves[su]["gue"].var(axis=0, ddof=1)
        var[var <= 0] = np.finfo(float).tiny
        weights[su] = 1.0 / var

    # expected pair count per bin (edge-corrected Poisson expectation) and
    # the pre-registered <5 drop rule
    exp_count = n * montgomery(u_centers) * DU
    keep = exp_count >= MIN_EXPECTED
    ckpt("  expected pairs/bin: min %.1f  max %.1f  -> bins dropped (E<5): %d"
         % (exp_count.min(), exp_count.max(), int((~keep).sum())))
    if (~keep).any():
        ckpt("    dropped bin indices: %s" % np.where(~keep)[0].tolist())
    ckpt("  NOTE no edge correction is applied; the matched surrogates carry the")
    ckpt("       same finite-N bias, so the Monte-Carlo p-values stay calibrated.")
    ckpt("")

    grid = {}
    for cname, y in charts.items():
        for su in SIGMA_U:
            x = unfold(y, su)
            _, cv = r2_curve(x)
            if any(~keep):
                c_k, w_k = cv[keep], weights[su][keep]
            else:
                c_k, w_k = cv, weights[su]
            # target = Montgomery pushed through the estimator's OWN sigma_e
            # smoothing, so chi^2 compares like with like (defect 12).
            tgt = montgomery_smoothed(u_centers)
            if any(~keep):
                tgt = tgt[keep]
            chi_obs = float(np.sum(w_k * (c_k - tgt) ** 2))
            p = {}
            p_low = {}
            for kind in ("gue", "goe", "poisson"):
                sc = sur_curves[su][kind]
                if any(~keep):
                    sc = sc[:, keep]
                chis = np.sum(w_k * (sc - tgt[None, :]) ** 2, axis=1)
                p[kind] = float(np.mean(chis >= chi_obs))        # upper tail
                p_low[kind] = float(np.mean(chis <= chi_obs))    # lower tail
            # AMENDMENT brain #1001631: Poisson uses the LOWER tail.
            # p_Pois_low = P(chi2_Pois <= chi2_obs); it is small exactly when
            # the data fits Montgomery BETTER than (almost) every Poisson draw,
            # which is what "distinguishable from Poisson" means. The original
            # upper-tail version gave p=1 for GUE-like data and mis-reported a
            # genuine GUE spectrum as NO DISCRIMINATION (caught on synthetic
            # fixtures before any real spectrum was read). Threshold unchanged.
            p_Pois = p_low["poisson"]
            if p["gue"] >= 0.05 and p_Pois < 0.05:
                vd = "CONSISTENT WITH MONTGOMERY/GUE, DISTINGUISHABLE FROM POISSON"
            elif p["gue"] >= 0.05 and p_Pois >= 0.05:
                vd = "NO DISCRIMINATION AT N=401"
            else:
                vd = "INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION"
            grid[(cname, su)] = vd
            ckpt("  chart %-24s sigma_u %.1f : chi2 = %.4f" % (cname, su, chi_obs))
            ckpt("      p_GUE   = P(chi2_GUE   >= chi2_obs) = %.4f" % p["gue"])
            ckpt("      p_GOE   = P(chi2_GOE   >= chi2_obs) = %.4f  [reported only]" % p["goe"])
            ckpt("      p_Pois  = P(chi2_Pois  <= chi2_obs) = %.4f  [lower tail, #1001631]" % p_Pois)
            ckpt("      -> %s" % vd)
    ckpt("")

    uniq = sorted(set(grid.values()))
    if len(uniq) == 1:
        s2_final = uniq[0]
        ckpt("  S2 FINAL (all %d grid points agree): %s" % (len(grid), s2_final))
    else:
        s2_final = "UNSTABLE (grid-dependent) -> INCONCLUSIVE"
        ckpt("  S2 FINAL: UNSTABLE -- %d different verdicts across the grid:" % len(uniq))
        for v in uniq:
            ckpt("      %s  (%d grid points)" % (v,
                                                 sum(1 for a in grid.values() if a == v)))
        ckpt("    (pre-registered: report instability, do NOT pick sigma_u/chart)")

    # ---- final -------------------------------------------------------------
    ckpt("")
    ckpt("#" * 96)
    ckpt("# OPSI (d) VERDICT")
    ckpt("#" * 96)
    ckpt("  S1 (gap ratio, unfolding-free) : %s" % s1_final)
    for name in charts:
        ckpt("      chart %-24s r_bar = %.6f -> %s" % (name, obs[name], s1_verd[name]))
    ckpt("  S2 (pair correlation)          : %s" % s2_final)
    ckpt("")
    ckpt("  RESOLUTION CEILING: N = %d levels, %d ratios, ~%.0f pairs/bin;" % (
        n, n - 2, n * DU))
    ckpt("  GOE-vs-GUE separation needs |Delta r_bar| ~ %.4f against SE ~ %.4f."
         % (abs(rbar_ref["gue"].mean() - rbar_ref["goe"].mean()),
            rbar_ref["gue"].std(ddof=1) / math.sqrt(n - 1)))
    ckpt("")
    ckpt("  SCOPE LIMIT (read literally): these are statistics of ONE finite")
    ckpt("  constructed matrix. They are NOT Montgomery's theorem, NOT evidence")
    ckpt("  for RH, NOT Weil positivity, NOT prime counting, NOT factorisation.")
    ckpt("  The source preprint disclaims all four.")
    ckpt("")
    ckpt("TOOL STATUS: python 3.14 + numpy %s + scipy %s + mpmath + python-flint."
         % (np.__version__, __import__("scipy").__version__))
    ckpt("lean/coqc/isabelle/dkcheck/z3/gcc NOT RUN.")
    ckpt("seed = %d (fixed for reproducibility, declared before the run)." % SEED)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
