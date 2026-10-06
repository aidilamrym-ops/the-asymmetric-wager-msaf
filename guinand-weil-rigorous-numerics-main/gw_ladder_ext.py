# -*- coding: utf-8 -*-
"""
Does lambda_min(Q_inf) converge to a positive gap, or to zero?

Statement under test: arXiv:2607.02828v3 (PREPRINT; LLM-assisted; the paper
explicitly disclaims RH / Weil-positivity / prime-counting results).

What the earlier run (gw_degeneracy.py) established, at c = 13:

    N      lambda_min
    4      9.6792619e-15
    8      7.6743926e-23
    16     8.5686275e-35
    24     3.0745569e-43
    32     2.25893e-49
    40     9.46281e-54

The drop per unit N was 2.03, 1.50, 1.05, 0.76, 0.55 -- decelerating, and two
competing models still fit:

    geometric   increments ratio ~0.71 per dN=8  ->  converges to lambda_* > 0
    power law   increments ~ N^-p                 ->  diverges, lambda_min -> 0

These are distinguishable only at larger N.  This script extends the ladder to
N = 48, 64, 80, 96 with adaptive precision, and prints the diagnostic that
decides between the two models.

RESOLUTION PROTOCOL (this is the point of the whole exercise):
  for each N the ladder is evaluated at two working precisions separated by
  >= 40 decimal digits; the value is called RESOLVED only when the two agree
  to 1e-12 relative.  A value below the working floor is reported as NOISE and
  never as a negative -- on dps=40 the earlier run produced the "negative"
  eigenvalues -1.066e-41 (N=32) and -1.258e-41 (N=40), both of which resolved
  to positive at dps=80.

No RH claim is made or implied.
"""

import sys
import time

import mpmath as mp

import gw_qinf as G


def spectrum_at(c, N, dps):
    mp.mp.dps = dps
    t0 = time.time()
    bl = G.build_blocks(c, N)
    t1 = time.time()
    M = G.even_matrix(bl, N, block="all")
    w, _ = mp.eigsy(M)
    t2 = time.time()
    return min(w), max(w), t1 - t0, t2 - t1


def ladder(c, N, seq, out):
    """Two successive precisions must agree ON THE EXPONENT being measured.

    The ladder measures y = -log10(lambda_min), not lambda_min.  A relative
    difference of 1e-12 on lambda is a difference of 4e-13 decades on y -- far
    below anything the model fit can see -- while a relative difference of 9e-2
    (seen at dps=60 vs 100 for N=40) is 0.038 DECADES and would move the fit.
    So the criterion is dy < 1e-4 decades between successive precisions, with
    lambda_min > 0 and above the working floor.  Both figures are printed.
    """
    rows = []
    resolved = False
    for dps in seq:
        lmin, lmax, tb, te = spectrum_at(c, N, dps)
        rows.append((dps, lmin, lmax))
        print("      dps=%-4d lambda_min = %-22s lambda_max = %-22s build %.1fs eig %.1fs"
              % (dps, mp.nstr(lmin, 12), mp.nstr(lmax, 12), tb, te), flush=True)
        if len(rows) >= 2:
            a, b = rows[-2][1], rows[-1][1]
            rel = abs(a - b) / abs(b) if b != 0 else mp.mpf("inf")
            dy = abs(-mp.log10(abs(a)) - -mp.log10(abs(b))) if a != 0 else mp.mpf("inf")
            floor = lmax * mp.mpf(10) ** (-(dps - 10))
            above_floor = (b > 0) and (b > floor)
            ok = (dy < mp.mpf("1e-4")) and above_floor
            print("      stability dps %d vs %d: |dlambda|/lambda = %-12s  dy = %-12s"
                  "  lambda_min > floor = %s  -> %s"
                  % (rows[-2][0], dps, mp.nstr(rel, 6), mp.nstr(dy, 6),
                     above_floor, "RESOLVED" if ok else "not yet"), flush=True)
            if ok:
                resolved = True
                break
    out.append((N, rows, resolved))
    return rows, resolved


def decide(c, table):
    """Print the model-discriminating diagnostic.

    geometric model:  s_i / s_{i-1} = r < 1 constant per interval
                      -> -log10 lambda_min converges, lambda_* > 0
    power model:      s_i ~ N^-p, p > 0
                      -> -log10 lambda_min diverges like N^(1-p) or log N,
                         lambda_min -> 0
    p is recovered from  r = (Nmid_i / Nmid_{i-1})^-p.
    """
    print("=" * 96, flush=True)
    print("MODEL DIAGNOSTIC: geometric (-> lambda_* > 0)  vs  power law (-> 0)")
    print("=" * 96, flush=True)
    pts = []
    for N, rows, ok in table:
        if ok:
            pts.append((N, -mp.log10(abs(rows[-1][1]))))
    if len(pts) < 3:
        print("  too few resolved points (%d)" % len(pts), flush=True)
        return

    print("   interval   Nmid     -log10(lmin)   slope s/dN   s_i/s_{i-1}   implied p",
          flush=True)
    slopes = []          # (Nmid, slope)
    for i in range(1, len(pts)):
        Nmid = mp.mpf(pts[i - 1][0] + pts[i][0]) / 2
        dN = mp.mpf(pts[i][0] - pts[i - 1][0])
        slopes.append((Nmid, (pts[i][1] - pts[i - 1][1]) / dN))

    for i, (Nmid, s) in enumerate(slopes):
        ratio, p = "-", "-"
        if i > 0:
            r = s / slopes[i - 1][1]
            ratio = mp.nstr(r, 6)
            if 0 < r != 1 and slopes[i - 1][0] != Nmid:
                p = mp.nstr(-mp.log(r) / mp.log(Nmid / slopes[i - 1][0]), 6)
        print("   [%2d,%3d]  %6.1f   %-14s %-12s %-13s %s"
              % (pts[i - 1][0], pts[i][0], float(Nmid), mp.nstr(pts[i][1], 8),
                 mp.nstr(s, 6), ratio, p), flush=True)

    if len(slopes) >= 2:
        r = slopes[-1][1] / slopes[-2][1]
        last_drop = pts[-1][1] - pts[-2][1]
        print(flush=True)
        print("  last interval: drop = %s decades over dN = %d"
              % (mp.nstr(last_drop, 6), pts[-1][0] - pts[-2][0]), flush=True)
        print("  last slope ratio r = %s" % mp.nstr(r, 6), flush=True)
        if 0 < r < 1:
            extra = last_drop * r / (1 - r)
            print("  geometric extrapolation: remaining drop = %s decades" % mp.nstr(extra, 6),
                  flush=True)
            print("  => predicted limit  -log10(lambda_min) ~ %s,  lambda_* ~ 1e-%s"
                  % (mp.nstr(pts[-1][1] + extra, 6), mp.nstr(pts[-1][1] + extra, 6)),
                  flush=True)
            print("  => VERDICT: GEOMETRIC, converges to a POSITIVE gap", flush=True)
        else:
            print("  slope ratio r >= 1: increments are NOT decaying geometrically",
                  flush=True)
            print("  => VERDICT: POWER LAW / undecayed, lambda_min -> 0", flush=True)


def main():
    c = 13
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    print("#" * 96, flush=True)
    print("# EXTENDED lambda_min LADDER FOR THE CUTOFF-FREE GUINAND-WEIL MATRIX")
    print("# c = %d ;  statement: arXiv:2607.02828v3 (PREPRINT, LLM-assisted, no RH claim)" % c)
    print("#" * 96, flush=True)
    print(flush=True)

    configs = {
        "base": [(4, [60, 100]), (8, [60, 100]), (16, [60, 100]),
                 (24, [60, 100]), (32, [60, 100]), (40, [60, 100])],
        "new": [(48, [100, 150]), (64, [110, 160])],
        "far": [(80, [140, 190]), (96, [170, 220])],
        # N=40 needs a third precision: dps 60 vs 100 differ by 0.038 decades
        "fix": [(40, [100, 140])],
    }

    table = []
    if stage in ("all", "base", "new", "far", "bn", "fix"):
        if stage == "all":
            todo = configs["base"] + configs["new"] + configs["far"]
        elif stage == "bn":
            todo = configs["base"] + configs["new"]
        else:
            todo = configs[stage]
        for N, seq in todo:
            print("=" * 96, flush=True)
            print("LADDER  (c, N) = (%d, %d)   dps sequence %s" % (c, N, seq), flush=True)
            print("=" * 96, flush=True)
            rows, ok = ladder(c, N, seq, table)
            print(flush=True)

    if stage in ("all", "base", "new", "far", "bn", "fix"):
        decide(c, table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
