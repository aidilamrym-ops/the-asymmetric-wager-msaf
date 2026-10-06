# -*- coding: utf-8 -*-
"""Measure the ACTUAL absolute entry error of the corrected Q_inf matrix by
dps-doubling, to compare against the certified tolerance rho* from
gw_arb_sweep.py.

WHY THIS IS THE LOAD-BEARING LINK
---------------------------------
gw_arb_sweep established, rigorously over the matrix as handed to flint:

    lambda_min > 0 is certified while every entry's absolute error < rho*
    (rho* = lam_min(parse)/n)

and it also established that flint CANNOT check the other direction:
python-flint 0.9.0 exposes no psi/digamma/polygamma/hyp2f1/lerchphi, so the
archimedean block arrives as decimal text and its distance from the true
values is invisible to arb.  That distance must be measured, and the only
measurement available is dps-doubling:

    |M_dps - M_2*dps|  estimates the error of M_dps

The matrix is built by the SAME code path at both precisions (the corrected
build, beta_L via the defining series), so the difference isolates the
rounding/truncation error of the lower precision rather than a code change.

This is an ESTIMATE, not a proof: mpmath is not interval arithmetic, and
dps-doubling can miss errors that are stable across both precisions.  It is
reported as an estimate throughout.

usage:  python gw_entry_error.py <c> <N> <dps_low> <dps_high> <saved.json>

    saved.json  the dps_low matrix written by gw_corrected_eig.py phase 5

SCOPE: a measurement on one preprint's matrix.  Not an RH, Weil-positivity,
prime-counting or factoring result; the source preprint disclaims all four.
"""
import json
import sys
import time

import mpmath as mp

# imports before mp.mp.dps is assigned -- gw_qinf sets 40 at module level
from gw_corrected_eig import build_blocks_corrected
from gw_full_vs_even import full_matrix


def main(argv):
    if len(argv) < 6:
        print(__doc__)
        return 2
    c, N = int(argv[1]), int(argv[2])
    dps_lo, dps_hi = int(argv[3]), int(argv[4])
    path = argv[5]

    # LANDMINE ORDER -- gw_qinf.py:47 sets mp.mp.dps = 40 at module level, and
    # this module imports it transitively.  mp.mpf(DECIMAL_STRING) rounds the
    # string to the CURRENT dps, so parsing the 180-digit JSON before setting
    # dps would silently truncate every entry to 40 digits.  That produced a
    # false "entry error = 4.2e-41" reading; the real value is ~5.4e-179.
    # Set the precision BEFORE any string becomes a number.
    mp.mp.dps = dps_lo

    with open(path, encoding="utf-8") as fh:
        meta = json.load(fh)
    if meta.get("dps") != dps_lo:
        print("WARNING: saved matrix is dps=%s, not dps=%d as declared"
              % (meta.get("dps"), dps_lo))
    M_lo = [[mp.mpf(x) for x in row] for row in meta["M"]]
    n = len(M_lo)

    print("#" * 100)
    print("# ENTRY ERROR BY dps-DOUBLING   (c, N) = (%d, %d)   dps %d -> %d"
          % (c, N, dps_lo, dps_hi))
    print("# corrected build at both precisions -- only difference is precision")
    print("#" * 100)
    print()
    print("  saved matrix          : %s  (%dx%d, dps %s)"
          % (path.split("\\")[-1], n, n, meta.get("dps")))
    sys.stdout.flush()

    mp.mp.dps = dps_hi
    t = time.time()
    bl = build_blocks_corrected(c, N)
    M_hi = full_matrix(bl, N, "all")
    print("  rebuilt at dps %d     : %.1f s" % (dps_hi, time.time() - t))
    sys.stdout.flush()

    # ---- entrywise difference ---------------------------------------------
    t = time.time()
    dmax = mp.mpf(0)
    at = (0, 0)
    mmax = mp.mpf(0)
    rat = mp.mpf(0)
    rat_at = (0, 0)
    for i in range(n):
        for j in range(n):
            # M_lo came from JSON (list of lists), M_hi is an mpmath matrix
            a, b = M_lo[i][j], M_hi[i, j]
            d = abs(a - b)
            if d > dmax:
                dmax, at = d, (i, j)
            if abs(b) > mmax:
                mmax = abs(b)
            if abs(b) > 0:
                r = d / abs(b)
                if r > rat:
                    rat, rat_at = r, (i, j)
    print("  differencing           : %.1f s" % (time.time() - t))
    print()

    print("=" * 100)
    print("MEASURED ENTRY ERROR")
    print("=" * 100)
    print("  entries compared                 : %d" % (n * n))
    print("  max |M(%d) - M(%d)| = %s   at (i,j) = %s" % (dps_lo, dps_hi,
                                                        mp.nstr(dmax, 12), at))
    print("  max |entry|                      = %s" % mp.nstr(mmax, 12))
    print("  max RELATIVE entry difference    = %s   at %s" % (mp.nstr(rat, 8), rat_at))
    print("  (index -> row is i - N, col is j - N)")
    print()

    # ---- compare against the certified tolerance ---------------------------
    lam = mp.mpf(meta["lam_corrected"])
    rho_star = lam / n          # as derived in gw_arb_sweep.py
    print("=" * 100)
    print("AGAINST THE CERTIFIED TOLERANCE")
    print("=" * 100)
    print("  measured rho_actual (absolute)   = %s" % mp.nstr(dmax, 18))
    print("  certified tolerance rho*         = %s" % mp.nstr(rho_star, 18))
    print("  rho_actual / rho*                = %s" % mp.nstr(dmax / rho_star, 8))
    print()
    verdict = "CERTIFIED (subject to the dps-doubling estimate)" if dmax < rho_star \
        else "NOT CERTIFIED -- measured entry error exceeds the tolerance"
    print("  VERDICT                          : %s" % verdict)
    print("  orders of margin                 = %s" % mp.nstr(mp.log10(rho_star / dmax), 8))
    print()
    print("  the dps-doubling figure above is an ESTIMATE: mpmath is not interval")
    print("  arithmetic, so an error stable across both precisions would not appear.")
    print()
    print("TOOL STATUS: mpmath.  lean/coqc/isabelle/z3/dkcheck NOT RUN.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
