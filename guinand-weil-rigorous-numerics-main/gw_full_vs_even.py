# -*- coding: utf-8 -*-
"""
Does the FULL (2N+1)-dimensional matrix have the same lambda_min as the real
EVEN-sector reduction?

Why this matters: arXiv:2607.02828v3 states Q_inf acts on C^{I_N} of dimension
2N+1, but every anchor we have reproduced (lambda_min(13,4) = 9.7e-15, and the
three finite-T values) was reproduced on the EVEN sector of dimension N+1,
using the assembly in gw_qinf.even_matrix.

For a real quadratic form with Q(-m,-n) = Q(m,n) and Q(m,n) = Q(n,m), the
simultaneous-flip operator J (Jf)(m) = f(-m) commutes with Q, so the space
splits as EVEN (dimension N+1) + ODD (dimension N).  Hence

    lambda_min(full) = min( lambda_min(even), lambda_min(odd) )

This file assembles the PLAIN (2N+1)x(2N+1) matrix directly from the divided
differences -- no sector assembly, no sqrt(2) conventions to get wrong -- and
compares its spectrum with the even-sector one.  Consequences:

  * if they agree, the full space and the even sector give the same
    lambda_min, and the published anchors are consistent with the full-space
    reading; it also means the whole-space count n_+ = 2N+1 can be attacked
    directly (relevant for the published n_+ = 401, n_- = 0 at (100,200))

  * if they differ, the published numbers belong to the even reduction, and
    the odd sector is a separate object that this project has NOT validated

Either way the answer is a measurement on one preprint's matrix, not an RH
statement.
"""

import mpmath as mp

import gw_qinf as G


def full_matrix(bl, N, block="all"):
    """plain (2N+1)x(2N+1) real matrix, rows/cols indexed -N..N in order."""
    Q = bl["Q_full"]
    n = 2 * N + 1
    M = mp.matrix(n, n)
    for a in range(n):
        m = a - N
        for b in range(n):
            nn = b - N
            M[a, b] = Q(m, nn, block)
    return M


def spec(M):
    w = sorted(mp.eigsy(M)[0])
    return w


def main():
    print("#" * 96)
    print("# FULL (2N+1) SPACE vs EVEN SECTOR (N+1): same lambda_min?")
    print("# source: arXiv:2607.02828v3 (PREPRINT, LLM-assisted, no RH claim)")
    print("#" * 96)
    print()
    print("   (c,N)   dim(full)  dim(even)   lambda_min(full)     lambda_min(even)"
          "     equal?     lambda_max(full)")
    print("   " + "-" * 100)
    ok_all = True
    for c, N in [(13, 4), (13, 8), (13, 16), (29, 6)]:
        # the eigenvalue comparison is RELATIVE and demands 25 agreeing digits.
        # lambda_min is ~1e-(2.1N+6) while lambda_max is O(1), so the working
        # precision must clear both the exponent and the condition number:
        #   digits needed on lambda_min  ~  dps - log10(lambda_max/lambda_min)
        # a fixed dps=50 gave a spurious "NO" at (13,16) for exactly this reason.
        mp.mp.dps = 70 + 2 * N
        bl = G.build_blocks(c, N)
        Mf = full_matrix(bl, N, "all")
        Me = G.even_matrix(bl, N, block="all")
        wf, we = spec(Mf), spec(Me)
        lf, le = +wf[0], +we[0]
        # the even-sector spectrum must be a SUBSET of the full spectrum
        max_dev = mp.mpf(0)
        for x in we:
            d = min(abs(x - y) for y in wf)
            max_dev = max(max_dev, d)
        same = abs(lf - le) / max(abs(le), mp.mpf("10") ** -300) < mp.mpf("10") ** -25
        sub = max_dev < mp.mpf("10") ** -25 * max(abs(wf[-1]), 1)
        print("   (%d,%-3d) %-10d %-11d %-20s %-19s %-10s %-16s"
              % (c, N, 2 * N + 1, N + 1, mp.nstr(lf, 12), mp.nstr(le, 12),
                 "yes" if same else "NO", mp.nstr(+wf[-1], 10)))
        print("        even-sector spectrum is a subset of the full spectrum: %s"
              % ("yes" if sub else "NO"))
        if not same:
            print("        -> the two readings DIFFER; the published anchor must be")
            print("           attributed to one of them explicitly")
            print("        odd-sector lambda_min (inferred) = %s" % mp.nstr(lf, 12))
            ok_all = False

    print()
    print("   check against the published anchor, full-space reading:")
    mp.mp.dps = 50
    bl = G.build_blocks(13, 4)
    lf = +spec(full_matrix(bl, 4, "all"))[0]
    print("      lambda_min(full 9x9) at (13,4) = %s" % mp.nstr(lf, 12))
    print("      published                       = +9.7e-15")
    print("      ratio                           = %s" % mp.nstr(lf / mp.mpf("9.7e-15"), 8))
    print()
    print("SCOPE: this compares two readings of one preprint's matrix.  It is not")
    print("an RH result, and it does not by itself reproduce n_+ = 401, n_- = 0")
    print("at (100,200), which is a much larger computation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
