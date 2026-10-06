# -*- coding: utf-8 -*-
"""Map the dps regime of the mp.lerchphi defect.

Section 7b of GW_STATUS showed the defect at (c, n) = (100, 40):
8.42831291456e-100 at dps 140..252, jumping to 1.69901166253e-127 at dps >= 288.
That was measured at FOUR working precisions only, all of them high.

This script answers two questions the identity gate never asked:

  1. What does mp.lerchphi do at the LOW precisions actually used to produce
     published numbers here -- dps 60/70/100, the precisions behind
     (100,20) = 3.0256658e-62 and the c=13 ladder?
  2. Does the defect depend on the point (c, n), or only on dps?

Method: compare mp.lerchphi(z, 2, a_n) against its defining series

    Phi(z, s, a) = sum_{k>=0} z^k / (k + a)^s,   |z| < 1

evaluated at the SAME dps.  The series terminates (z = 1e-4 or 5.9e-3), so it
is limited only by the working precision.  A defect is present when

    |mp - series|  >>  10^(-dps)

i.e. when the disagreement is orders of magnitude larger than what the
precision can support.  When |mp - series| is at the dps floor, no conclusion
is drawn -- that is UNRESOLVED, not "correct".

usage:  python gw_lerchphi_regime.py [c n ...]   (pairs; default 100 40, 13 64)

SCOPE: a library measurement.  Not an RH, Weil-positivity, prime-counting or
factoring result; the source preprint disclaims all four.
"""
import sys
import time

import mpmath as mp

# import before mp.mp.dps is set (gw_qinf sets 40 at module level)
import gw_deep_v3 as V3

DPS_LIST = [40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 220,
            240, 260, 280, 300, 340, 384]


def run_pair(c, n, dps):
    mp.mp.dps = dps
    L = mp.log(c)
    z = mp.e ** (-2 * L)
    an = mp.mpf(1) / 4 + mp.pi * 1j * n / L

    ser = V3.lerchphi_series(z, 2, an)          # defining series, this dps
    t0 = time.time()
    try:
        raw = mp.lerchphi(z, 2, an)
        err = time.time() - t0
    except Exception as exc:
        return dict(c=c, n=n, dps=dps, err=abs(mp.nan), exc="%s: %s" % (type(exc).__name__, exc))

    gap = abs(raw - ser)
    floor = mp.mpf(10) ** (-dps)
    # how many orders the gap sits ABOVE the working-precision floor
    orders = mp.log10(gap / floor) if gap > 0 else mp.mpf("-inf")

    return dict(c=c, n=n, dps=dps, gap=gap, floor=floor, orders=orders, sec=err,
                z=z, an_abs=abs(an))


def main(argv):
    pairs = []
    args = argv[1:]
    if len(args) >= 2 and len(args) % 2 == 0:
        pairs = [(int(args[i]), int(args[i + 1])) for i in range(0, len(args), 2)]
    else:
        pairs = [(100, 40), (13, 64)]

    print("#" * 100)
    print("# mp.lerchphi(z, 2, a_n) DEFECT REGIME MAP  --  vs defining series, same dps")
    print("# defect declared only when |mp - series| exceeds 10^(-dps)")
    print("# pairs: %s" % "  ".join("(c=%d, n=%d)" % p for p in pairs))
    print("#" * 100)
    print()
    print("  %-6s %-5s %-6s %-16s %-16s %-9s %s"
          % ("c", "n", "dps", "|mp-series|", "dps floor", "orders>", "z, |a_n|"))
    print("  " + "-" * 96)

    verdict = {}
    for (c, n) in pairs:
        for dps in DPS_LIST:
            r = run_pair(c, n, dps)
            if "exc" in r:
                print("  %-6d %-5d %-6d EXCEPTION %s" % (c, n, dps, r["exc"]))
                continue
            flag = ""
            if r["orders"] > 3:
                flag = "  <== DEFECT (%.1f orders above floor)" % r["orders"]
            elif r["orders"] < -1:
                flag = "  (at floor -- inconclusive)"
            verdict[(c, n, dps)] = r["orders"]
            print("  %-6d %-5d %-6d %-16s %-16s %-9.2f %s%s"
                  % (c, n, dps, mp.nstr(r["gap"], 8), "1e-%d" % dps,
                     r["orders"], "z=%.3g |a_n|=%.4g" % (r["z"], r["an_abs"]), flag))
            sys.stdout.flush()
        print()

    print("=" * 100)
    print("SUMMARY -- defect above floor at which dps")
    print("=" * 100)
    for (c, n) in pairs:
        bad = [d for d in DPS_LIST if verdict.get((c, n, d), mp.mpf(-999)) > 3]
        good = [d for d in DPS_LIST if verdict.get((c, n, d), mp.mpf(999)) <= 0]
        print("  (c=%d, n=%d): defect at dps %s" % (c, n, bad if bad else "none"))
        print("                 at floor   at dps %s" % (good if good else "none"))
    print()
    print("NOTE: a defect present at the dps used to BUILD a matrix contaminates that")
    print("      matrix's diagonal (beta_L -> P0d).  See gw_entry_audit.py.")
    print("TOOL STATUS: mpmath only.  lean/coqc/isabelle/z3/dkcheck NOT RUN.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
