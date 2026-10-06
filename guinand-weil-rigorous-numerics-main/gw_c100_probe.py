# -*- coding: utf-8 -*-
"""
lambda_min of Q_infty at a large (c, N), at one or more working precisions.

WHY THIS EXISTS
---------------
At (c, N) = (100, 40) two earlier probes disagree in *sign* with the published
certificate:

    dps =  70 :  lambda_min = -1.063556e-70   floor = 5.98e-60  -> below floor
    dps = 100 :  lambda_min = -4.183251e-71   floor = 5.98e-90  -> above floor

A negative lambda_min at (100,40) would, by Cauchy interlacing (Q_40 is a
principal submatrix of Q_200 -- every entry is independent of N), force
lambda_min(Q_200) < 0 and hence n_- >= 1, contradicting the published
n_+ = 401, n_- = 0 at (100,200).

That inference is VOID until two things are settled:
  (1) the value must be resolved across two successive precisions, both of
      which put lambda_min ABOVE the floor  lambda_max * 10^-(dps-10);
  (2) the archimedean closed forms must have been validated against the
      defining integral to a depth well below |lambda_min| -- see
      gw_tail_deep.py, which currently reaches ~1e-74 at (13,1).

This script supplies (1): it builds the blocks once per precision and prints
lambda_min for BOTH the even sector (N+1) and the full (2N+1) matrix, together
with the floor and the successive-precision exponent difference dy.  The
RESOLUTION RULE is applied mechanically:

    RESOLVED iff two successive dps give dy = |y_hi - y_lo| < 1e-4 on
    y = -log10|lambda_min|, with lambda_min above the floor at BOTH.

usage:  python gw_c100_probe.py <c> <N> <dps> [dps ...]

Nothing here bears on RH, Weil positivity, prime counting or factoring; the
source preprint disclaims those claims.
"""

import sys
import time

import mpmath as mp

import gw_qinf as G
from gw_full_vs_even import full_matrix


def probe(c, N, dps):
    mp.mp.dps = dps
    t0 = time.time()
    bl = G.build_blocks(c, N)
    t_build = time.time() - t0

    Me = G.even_matrix(bl, N, block="all")
    Mf = full_matrix(bl, N, "all")

    we = sorted(mp.eigsy(Me)[0])
    wf = sorted(mp.eigsy(Mf)[0])
    le, lf = +we[0], +wf[0]
    lmax = max(abs(+wf[0]), abs(+wf[-1]))
    floor = lmax * mp.mpf(10) ** (-(dps - 10))

    out = dict(dps=dps, le=le, lf=lf, lmax=lmax, floor=floor,
               t_build=t_build, t=time.time() - t0)
    return out


def report(r, prev):
    c_line = "  dps = %-4d  even(N+1) lambda_min = %-24s  full(2N+1) = %-24s"
    print(c_line % (r["dps"], mp.nstr(r["le"], 12), mp.nstr(r["lf"], 12)))
    for name, v in (("even", r["le"]), ("full", r["lf"])):
        if v > 0:
            y = -mp.log10(v)
            tag = "POSITIVE"
        else:
            y = -mp.log10(-v)
            tag = "NEGATIVE"
        above = abs(v) > r["floor"]
        print("      %-5s y = -log10|lambda_min| = %-16s %s   |floor = %s -> %s"
              % (name, mp.nstr(y, 12), tag, mp.nstr(r["floor"], 6),
                 "above" if above else "BELOW FLOOR"))
    print("      lambda_max = %s   build %.1f s   total %.1f s"
          % (mp.nstr(r["lmax"], 10), r["t_build"], r["t"]))

    if prev is None:
        return None
    # resolution on the FULL matrix (the object the certificate refers to)
    ok = abs(r["lf"]) > r["floor"] and abs(prev["lf"]) > prev["floor"]
    dy = abs(-mp.log10(abs(r["lf"])) - (-mp.log10(abs(prev["lf"]))))
    verdict = "RESOLVED" if (ok and dy < mp.mpf("1e-4")) else "NOT RESOLVED"
    print("      successive precisions: dy = %s   both above floor: %s   -> %s"
          % (mp.nstr(dy, 6), ok, verdict))
    if ok and r["lf"] < 0:
        print("      NOTE: if this is genuine, interlacing forces")
        print("      lambda_min(Q_%d) < 0 as well, i.e. n_- >= 1." % (N,))
    return dy


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    c, N = int(argv[1]), int(argv[2])
    dpss = [int(x) for x in argv[3:]]

    print("#" * 100)
    print("# lambda_min probe at (c, N) = (%d, %d)" % (c, N))
    print("# dps sequence: %s" % dpss)
    print("# resolution rule: dy < 1e-4 on y = -log10|lambda_min|, both above")
    print("#                  floor = lambda_max * 10^-(dps-10)")
    print("#" * 100)
    print()

    prev = None
    for dps in dpss:
        r = probe(c, N, dps)
        report(r, prev)
        print()
        sys.stdout.flush()
        prev = r

    print("SCOPE: this is a measurement on one preprint's matrix.  It is not an")
    print("RH, Weil-positivity, prime-counting or factoring result.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
