# -*- coding: utf-8 -*-
"""Decisive comparison: shipped build vs corrected build, both at full working
precision, with build cost TIMED.

Why a dedicated script
----------------------
gw_corrected_eig.py compared the corrected eigenvalue against a hard-coded

    BUGGY_LAM = mp.mpf("1.32105051975e-102")

which carries only 12 significant digits, so its own uncertainty is ~1e-114.
The reported "shift" of 1.74632728899314595e-114 sits inside that rounding and
proves nothing.  The shipped build must be re-run so both eigenvalues are
produced by the same code path at the same dps and differ ONLY in the single
lerchphi call site.

This script also times both builds.  gw_corrected_eig.py reported the
corrected build at 2.5 s against a recorded 679 s for the shipped one -- a
270x gap that must be measured, not explained.

usage:  python gw_compare_builds.py <c> <N> <dps>

SCOPE: a measurement on one preprint's matrix.  Not an RH, Weil-positivity,
prime-counting or factoring result; the source preprint disclaims all four.
"""
import sys
import time

import mpmath as mp

# imports before mp.mp.dps is assigned -- gw_qinf sets 40 at module level
import gw_qinf as G
from gw_full_vs_even import full_matrix
from gw_corrected_eig import build_blocks_corrected


def lam_of(bl, N):
    t = time.time()
    M = full_matrix(bl, N, "all")
    t_mat = time.time() - t
    t = time.time()
    w = sorted(mp.eigsy(M)[0])
    t_eig = time.time() - t
    return +w[0], t_mat, t_eig, len(M)


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    c, N, dps = int(argv[1]), int(argv[2]), int(argv[3])
    mp.mp.dps = dps

    print("#" * 100)
    print("# SHIPPED vs CORRECTED build, same code path, same dps = %d, (c,N) = (%d,%d)"
          % (dps, c, N))
    print("# only difference: beta_L t2 = mp.lerchphi  vs  V3.lerchphi_series")
    print("#" * 100)
    print()

    # ---- shipped -----------------------------------------------------------
    t = time.time()
    old = G.build_blocks(c, N)
    t_old = time.time() - t
    lam_old, t_mat_o, t_eig_o, dim = lam_of(old, N)
    print("  SHIPPED   build %8.1f s   matrix %5.1f s   eigsy %5.1f s   (%dx%d)"
          % (t_old, t_mat_o, t_eig_o, dim, dim))
    print("            lambda_min = %s" % mp.nstr(lam_old, 30))
    sys.stdout.flush()

    # ---- corrected ---------------------------------------------------------
    t = time.time()
    new = build_blocks_corrected(c, N)
    t_new = time.time() - t
    lam_new, t_mat_n, t_eig_n, _ = lam_of(new, N)
    print("  CORRECTED build %8.1f s   matrix %5.1f s   eigsy %5.1f s"
          % (t_new, t_mat_n, t_eig_n))
    print("            lambda_min = %s" % mp.nstr(lam_new, 30))
    sys.stdout.flush()

    print()
    print("=" * 100)
    print("COMPARISON")
    print("=" * 100)
    d = lam_new - lam_old
    print("  lambda_min shipped    = %s" % mp.nstr(lam_old, 30))
    print("  lambda_min corrected  = %s" % mp.nstr(lam_new, 30))
    print("  difference            = %s" % mp.nstr(d, 30))
    print("  |difference|          = %s" % mp.nstr(abs(d), 30))
    print("  |difference| / |lam|  = %s" % mp.nstr(abs(d) / abs(lam_old), 12))
    print("  sign shipped          : %s" % ("+" if lam_old > 0 else "-"))
    print("  sign corrected        : %s" % ("+" if lam_new > 0 else "-"))
    print("  SIGN CHANGED?         : %s" % ("YES" if (lam_old > 0) != (lam_new > 0) else "no"))
    print()
    print("  build cost shipped    : %.1f s" % t_old)
    print("  build cost corrected  : %.1f s" % t_new)
    print("  ratio                 : %.1fx" % (t_old / t_new if t_new else float('inf')))
    print()

    # ---- entry-level delta, directly --------------------------------------
    print("=" * 100)
    print("ENTRY LEVEL (max |delta P0d| over the index range)")
    print("=" * 100)
    dm = mp.mpf(0)
    at = 0
    prof = []
    for n in old["idx"]:
        dd = abs(old["P0d"][n] - new["P0d"][n])
        prof.append((n, dd))
        if dd > dm:
            dm, at = dd, n
    print("  max |delta P0d| = %s at n=%+d" % (mp.nstr(dm, 20), at))
    print("  lambda_min      = %s" % mp.nstr(lam_old, 20))
    print("  ratio           = %s" % mp.nstr(dm / abs(lam_old), 12))
    print()
    print("  profile (every 5th index):")
    for n, dd in prof:
        if n % 5 == 0:
            print("     n=%+4d  |delta| = %s" % (n, mp.nstr(dd, 8)))
    print()
    print("  WHY the eigenvalue barely moved despite a 2.57x entry error:")
    print("    lambda_min shift = sum_i v_i^2 * delta_i ; the measured value above")
    print("    tells you where the eigenvector sits relative to delta's profile.")
    print()
    print("TOOL STATUS: mpmath.  lean/coqc/isabelle/z3/dkcheck NOT RUN.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
