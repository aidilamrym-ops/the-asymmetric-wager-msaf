# -*- coding: utf-8 -*-
"""
Independent cross-check of lambda_min via the determinant identity.

    lambda_min = det(M) / prod_{i >= 2} lambda_i

WHY THIS EXISTS
---------------
At (100, 40) the eigenvalue routine (mp.eigsy) produced -4.183251e-71 at
dps = 100 and +1.32105051975e-102 at dps = 140 and 180.  The smallest
eigenvalue is therefore in the regime where the routine has already been
observed to be wrong by 31 orders of magnitude while the reported value
sat "above the floor".  Before that number is used for anything, it must be
confirmed by a route that does not ask the eigenvalue routine for the small
eigenvalue at all.

The right-hand side uses
  * mp.det, an LU-based determinant at the working precision, and
  * the 80 LARGE eigenvalues, which are orders of magnitude away from
    lambda_min and hence accurately computed.
Only lambda_min enters through det, whose absolute error is inherited from
the entrywise error of M -- the same error that ruined dps = 100.

Sensitivity note: d(det)/dM_ij = C_ij (cofactor) and C_ij/det = (M^-1)_ji,
so an entrywise error delta moves det by about delta * O(prod_{i>=2} lambda_i),
i.e. lambda_min carries absolute error about delta ~ 10^-dps.  That is why
dps = 100 (error 1e-100 > 1.3e-102) failed and dps = 140 (error 1e-140) need
not.  It also shows the printed floor test is SELF-REFERENTIAL: it compares
the *reported* value against the floor, so a noise value that happens to land
above the floor passes.  Only the successive-precision dy rule detects that.

usage:  python gw_det_check.py <c> <N> <dps>

SCOPE: a measurement on one preprint's matrix.  Not an RH, Weil-positivity,
prime-counting or factoring result; the source preprint disclaims all four.
"""

import sys
import time

import mpmath as mp

import gw_qinf as G
from gw_full_vs_even import full_matrix


def check(c, N, dps):
    mp.mp.dps = dps
    t0 = time.time()
    bl = G.build_blocks(c, N)
    t_build = time.time() - t0

    M = full_matrix(bl, N, "all")

    t1 = time.time()
    w = sorted(mp.eigsy(M)[0])
    t_eig = time.time() - t1

    t1 = time.time()
    det = mp.det(M)
    t_det = time.time() - t1

    lam_eig = +w[0]
    prod_rest = mp.mpf(1)
    for x in w[1:]:
        prod_rest *= x
    lam_det = det / prod_rest

    ratio = lam_det / lam_eig if lam_eig != 0 else mp.mpf("nan")

    return dict(dps=dps, lam_eig=lam_eig, lam_det=lam_det, ratio=ratio,
                det=det, w=w, t_build=t_build, t_eig=t_eig, t_det=t_det,
                t=time.time() - t0)


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    c, N, dps = int(argv[1]), int(argv[2]), int(argv[3])

    print("#" * 100)
    print("# INDEPENDENT lambda_min CHECK at (c, N) = (%d, %d), dps = %d"
          % (c, N, dps))
    print("# route A: mp.eigsy  (eigenvalue routine)")
    print("# route B: mp.det / prod_{i>=2} lambda_i   (LU determinant)")
    print("#" * 100)
    print()

    r = check(c, N, dps)

    print("  build %.1f s   eigsy %.1f s   det %.1f s   total %.1f s"
          % (r["t_build"], r["t_eig"], r["t_det"], r["t"]))
    print()
    print("  route A  lambda_min (eigsy)      = %s" % mp.nstr(r["lam_eig"], 25))
    print("  route B  lambda_min (det ratio)  = %s" % mp.nstr(r["lam_det"], 25))
    print("  ratio B/A                        = %s" % mp.nstr(r["ratio"], 12))
    print("  log10|det|                       = %s"
          % mp.nstr(mp.log10(abs(r["det"])), 12))
    print()

    w = r["w"]
    print("  5 smallest eigenvalues:")
    for x in w[:5]:
        print("      %s" % mp.nstr(x, 18))
    print("  3 largest eigenvalues:")
    for x in w[-3:]:
        print("      %s" % mp.nstr(x, 18))
    print()

    for thr in ("1e-60", "1e-80", "1e-100", "1e-110"):
        k = sum(1 for x in w if abs(x) < mp.mpf(thr))
        print("      # eigenvalues with |lambda| < %-8s = %d" % (thr, k))
    print()

    agree = abs(r["ratio"] - 1) < mp.mpf("1e-40")
    print("  VERDICT: det-route and eigsy-route agree to 1e-40 ?  %s"
          % ("YES" if agree else "NO"))
    if not agree:
        print("           -> the smallest eigenvalue is NOT trustworthy;"
              " do not use it.")
    print()
    print("SCOPE: a measurement on one preprint's matrix.  Not an RH,")
    print("Weil-positivity, prime-counting or factoring result.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
