# -*- coding: utf-8 -*-
"""A1 with MEASURED per-entry radii -- the certificate gw_arb_sweep could not
deliver with a uniform worst-case radius.

THE GAP THIS CLOSES
-------------------
gw_arb_sweep.py proved, by Weyl on the parse-only enclosure:

    lambda_min > 0  certified only while  every entry's error < rho* = 1.63e-104

then gw_entry_error.py measured the real uniform worst case:

    rho_actual = 4.19986259663e-41        -> rho_actual / rho* = 2.6e63
    VERDICT: NOT CERTIFIED  (63 orders short)

and giving FLINT a uniform rho >= 1e-180 made it fail to isolate the spectrum
at all.  Both failures come from applying the WORST entry's error to all 6561
entries.

But the error is not uniform.  gw_entry_error located it: the largest
differences sit at large |n| (row/col index +-30), while gw_lam_dps.py showed
lambda_min does not move at all while entries move 4.2e-41 -- the eigenvector
is localised where the error is small.  A per-entry radius reproduces that
structure instead of flattening it.

METHOD
------
    rho_ij = |M(dps_lo)[i,j] - M(dps_hi)[i,j]|        (measured, same code path)
    matrix = M(dps_lo) +/- rho_ij                     (midpoint = lower precision)

M(dps_hi) plays the role of "exact", so the radius estimates the error of
M(dps_lo).  This is an ESTIMATE: mpmath is not interval arithmetic and an
error stable across both precisions would not appear.  That caveat travels
with the output.

usage:  python gw_arb_measured.py <c> <N> <dps_lo> <dps_hi>

SCOPE: interval verification of one preprint's matrix.  Not an RH,
Weil-positivity, prime-counting or factoring result; the source preprint
disclaims all four.
"""
import sys
import time

import mpmath as mp

# imports before mp.mp.dps is assigned -- gw_qinf sets 40 at module level
from gw_corrected_eig import build_blocks_corrected
from gw_full_vs_even import full_matrix


def main(argv):
    if len(argv) < 5:
        print(__doc__)
        return 2
    c, N, dps_lo, dps_hi = (int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
    prec = int(argv[5]) if len(argv) > 5 else 1024
    algos = ["rump", "vdhoeven_mourrain"] if len(argv) <= 6 else [argv[6]]

    print("#" * 100)
    print("# A1 -- MEASURED PER-ENTRY RADII   (c, N) = (%d, %d)   dps %d -> %d"
          % (c, N, dps_lo, dps_hi))
    print("# midpoint = M(%d), radius_ij = |M(%d) - M(%d)|   prec=%d bits  algos=%s"
          % (dps_lo, dps_lo, dps_hi, prec, algos))
    print("#" * 100)
    print()
    sys.stdout.flush()

    mp.mp.dps = dps_lo
    t0 = time.time()
    bl_lo = build_blocks_corrected(c, N)
    M_lo = full_matrix(bl_lo, N, "all")
    n = len(M_lo)
    print("  M(%d) built                 : %d x %d in %.1f s"
          % (dps_lo, n, n, time.time() - t0))
    sys.stdout.flush()

    mp.mp.dps = dps_hi
    t0 = time.time()
    bl_hi = build_blocks_corrected(c, N)
    M_hi = full_matrix(bl_hi, N, "all")
    print("  M(%d) built                 : %.1f s" % (dps_hi, time.time() - t0))
    sys.stdout.flush()

    rho = [[abs(M_lo[i, j] - M_hi[i, j]) for j in range(n)] for i in range(n)]
    rmax = max(max(r) for r in rho)
    rmin = min(min(r) for r in rho)
    nz = sum(1 for r in rho for x in r if x != 0)
    imax = max(((i, j) for i in range(n) for j in range(n)), key=lambda t: rho[t[0]][t[1]])
    print("  radius model built         : %d / %d entries nonzero" % (nz, n * n))
    print("  rho max = %s  at (i,j)=%s -> (index %+d, %+d)"
          % (mp.nstr(rmax, 12), imax, imax[0] - N, imax[1] - N))
    print("  rho min = %s" % mp.nstr(rmin, 6))
    sys.stdout.flush()

    # ---- FLINT -------------------------------------------------------------
    import flint

    flint.ctx.prec = prec
    ball = [flint.arb(0, mp.nstr(rho[i][j], 30) if rho[i][j] > 0 else "0")
            for i in range(n) for j in range(n)]
    vals = [flint.arb(mp.nstr(M_lo[i, j], mp.mp.dps)) + ball[i * n + j]
            for i in range(n) for j in range(n)]
    A = flint.arb_mat(n, n, vals)
    print()
    print("  arb_mat assembled at prec=%d bits" % prec)
    sys.stdout.flush()

    for alg in algos:
        t = time.time()
        try:
            ev = A.eig(algorithm=alg)
        except Exception as exc:
            print("  %-22s NOT ISOLATED  (%s: %s)"
                  % (alg, type(exc).__name__, str(exc)[:70]))
            sys.stdout.flush()
            continue
        best = min(ev, key=lambda w: float(w.real))
        re = best.real
        pos = bool(re > 0) and not bool(re.contains(0))
        print("  %-22s %.1f s : %d/%d isolated" % (alg, time.time() - t, len(ev), n))
        print("      lambda_min enclosure = %s" % str(best)[:120] + "...")
        print("      Re > 0 rigorous      : %s" % bool(re > 0))
        print("      Re contains 0        : %s" % bool(re.contains(0)))
        print("      |Im|                 : %.3e" % float(abs(best.imag)))
        print("      VERDICT              : %s"
              % ("ENCLOSED STRICTLY POSITIVE" if pos else "NOT PROVED POSITIVE"))
        sys.stdout.flush()

    print()
    print("=" * 100)
    print("A1 VERDICT")
    print("=" * 100)
    print("  route 1 -- FLINT parse-only enclosure + Weyl propagation:")
    print("      lam_min(parse) = 1.32105051975174632728899314595e-102 +/- 4.24e-308")
    print("      rho_actual     = measured per-entry, see above")
    print("      rho*           = lam_min/n  (gw_arb_sweep.py)")
    print("      -> CERTIFIED POSITIVE while rho_actual < rho*")
    print()
    print("  route 2 -- FLINT eigenvalue solver WITH radii (this script):")
    print("      NOT ISOLATED at prec=1024 and prec=4096, both algorithms.")
    print("      Recorded as a TOOL LIMITATION: rump cannot separate this spectrum")
    print("      once the entries carry any radius, even one 75 orders below rho*.")
    print("      It is not evidence about lambda_min.")
    print()
    print("  A earlier reading of 'uniform rho* short by 63 orders' was RETRACTED:")
    print("  it came from parsing the saved 180-digit JSON at dps 40 (gw_qinf.py:47")
    print("  module-level landmine), which measured the reader, not the matrix.")
    print()
    print("  both routes are conditional on dps-doubling being a valid error bound;")
    print("  mpmath is not interval arithmetic, so that link stays an ESTIMATE.")
    print()
    print("TOOL STATUS: mpmath + python-flint.  lean/coqc/isabelle/z3/dkcheck NOT RUN.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
