# -*- coding: utf-8 -*-
"""lambda_min(Q_inf, corrected) at an arbitrary dps -- the precision ladder for
the eigenvalue itself.

WHY THIS EXISTS
---------------
gw_entry_error.py measured the entry error of the corrected matrix at
dps 180 as

    max |M(180) - M(260)| = 4.19986259663e-41   (max relative 1.1209866e-41)

which is ~139 orders coarser than dps 180 would suggest.  Under the worst-case
Weyl bound that is 81 * rho = 3.4e-39, far larger than
lambda_min = 1.32e-102, so Weyl refuses to certify the sign by ~63 orders.

Weyl is known to be pessimistic on this matrix: it once predicted the lerchphi
correction could flip the sign, while the measured shift was 7.36e-118,
because lambda_min's eigenvector is concentrated where the perturbation is
zero.  Whether the dps-rounding error behaves the same way is an EMPIRICAL
question, and this script answers it by evaluating the eigenvalue directly at
several precisions.

If lambda_min is stable across dps while the ENTRIES move by 1e-41, the
eigenvector-localisation argument is confirmed by measurement rather than
asserted.  If it is not stable, the value is not resolved and must be
retracted.

usage:  python gw_lam_dps.py <c> <N> <dps> [<dps> ...]

SCOPE: a measurement on one preprint's matrix.  Not an RH, Weil-positivity,
prime-counting or factoring result; the source preprint disclaims all four.
"""
import sys
import time

import mpmath as mp

# imports before mp.mp.dps is assigned -- gw_qinf sets 40 at module level
from gw_corrected_eig import build_blocks_corrected
from gw_full_vs_even import full_matrix

# previously measured, printed here only so every run can be read in context
KNOWN = {
    140: "1.32105051975174632728899314595e-102",
    180: "1.32105051975174632728899314595e-102",
}


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    c, N = int(argv[1]), int(argv[2])
    dpss = [int(x) for x in argv[3:]]

    print("#" * 100)
    print("# LAMBDA_MIN vs dps   (c, N) = (%d, %d)   corrected build" % (c, N))
    print("# entries are known to move by ~4e-41 between dps 180 and 260,")
    print("# so this asks whether the eigenvalue moves too.")
    print("#" * 100)
    print()
    print("  %-6s %-18s %-46s %s" % ("dps", "build+eigsy s", "lambda_min", "vs prior"))
    print("  " + "-" * 100)

    vals = {}
    for d in dpss:
        mp.mp.dps = d
        t = time.time()
        bl = build_blocks_corrected(c, N)
        M = full_matrix(bl, N, "all")
        t1 = time.time()
        w = sorted(mp.eigsy(M)[0])
        lam = +w[0]
        dt = time.time() - t1
        vals[d] = lam
        known = KNOWN.get(d)
        note = ""
        if known is not None:
            note = " (prior run: %s)" % known
        print("  %-6d %-18.1f %-46s%s"
              % (d, dt, mp.nstr(lam, 30), note))
        sys.stdout.flush()

    print()
    print("=" * 100)
    print("STABILITY")
    print("=" * 100)
    keys = sorted(vals)
    if len(keys) >= 2:
        for a, b in zip(keys, keys[1:]):
            va, vb = vals[a], vals[b]
            diff = abs(vb - va)
            y_a = -mp.log10(abs(va))
            y_b = -mp.log10(abs(vb))
            dy = abs(y_b - y_a)
            rel = diff / abs(va) if va != 0 else mp.nan
            print("  dps %d -> %d" % (a, b))
            print("      |diff| = %s      relative = %s" % (mp.nstr(diff, 12), mp.nstr(rel, 8)))
            print("      y = -log10|lam| : %s -> %s      dy = %s   (rule: < 1e-4)"
                  % (mp.nstr(y_a, 15), mp.nstr(y_b, 15), mp.nstr(dy, 6)))
            print("      -> %s" % ("RESOLVED" if dy < mp.mpf("1e-4") else "NOT RESOLVED"))
            print()
    print("  context: entry error over this range is ~4.2e-41 absolute.")
    print("           if lambda_min does NOT move while entries do, the")
    print("           eigenvector localisation is measured, not assumed.")
    print()
    print("TOOL STATUS: mpmath.  lean/coqc/isabelle/z3/dkcheck NOT RUN.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
