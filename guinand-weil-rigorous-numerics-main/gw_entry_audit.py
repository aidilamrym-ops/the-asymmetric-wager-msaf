# -*- coding: utf-8 -*-
"""Entry-level audit: does the lerchphi defect reach the matrix diagonal?

WHY THIS EXISTS
---------------
gw_qinf.build_blocks assembles Q_inf with

    P0d[n] = -2 * (gamma_L(n) - beta_L(n)) + psiprd(n)      (diagonal)
    P0[n]  = alpha_L(n) + psipr(n)                          (row differences)
    Q(m,n) = (P0[m] - P0[n]) / (m - n) + pole(m,n)          (m != n)
    Q(m,m) = P0d[m] + pole(m,m)

and beta_L(n) evaluates t2 with mp.lerchphi(z, 2, an).  That exact call was
shown in section 7b of GW_STATUS to be wrong by 8.42831291456e-100 at
dps 140..252 while being perfectly dps-stable -- i.e. converged to the wrong
value.  The propagation factor into -2*(gamma - beta) is

    d(closed)/d(Re L2) = -2 * (1/L) * (-e^{-L/2}/4),

which at c = 100 equals 0.0108573620475813, giving exactly the identity
residual 3.391109217077509e-102 measured at n = 40.

Only beta_L carries lerchphi, and beta_L enters ONLY through the diagonal.
Therefore the matrix error is purely diagonal:

    M_buggy = M_corrected + diag(delta[n])

and Weyl's inequality brackets the corrected eigenvalue without needing a
second diagonalisation:

    lam_min(M_corr) in [ lam_min(M_buggy) - max delta,
                         lam_min(M_buggy) - min delta ]

This script measures delta[n] for every index in -N..N and prints that
bracket.  Nothing is assumed about the sign or the variation of delta: both
are measured.

usage:
    python gw_entry_audit.py <c> <N> <dps> [n1 n2 ...]

With no n-list, every index -N..N is audited.  With an n-list, only those
indices are audited (fast timing probe).

SCOPE: a measurement on one preprint's matrix.  Not an RH, Weil-positivity,
prime-counting or factoring result; the source preprint disclaims all four.
"""
import sys
import time

import mpmath as mp

# Import order matters.  gw_qinf.py sets mp.mp.dps = 40 at MODULE LEVEL and is
# pulled in transitively; every import here must run BEFORE mp.mp.dps is
# assigned in main().  See GW_STATUS section 7b (landmine gw_qinf.py:47).
import gw_deep_v3 as V3


def closed_pair(c, n):
    """Return (closed_buggy, closed_corrected) = -2*(gamma_L - beta_L).

    gamma_L is computed once: it contains no lerchphi.  Only the t2 term
    differs between the two routes, so the difference delta = buggy - corrected
    equals t2_new - t2_old scaled by the same chain-rule factor that produced
    the identity residual.
    """
    L = mp.log(c)
    z = mp.e ** (-2 * L)
    an = mp.mpf(1) / 4 + mp.pi * 1j * n / L
    PI = mp.pi
    eL = mp.e ** (-L / 2)
    F = mp.hyp2f1(1, an, an + 1, z)

    # gamma_L -- identical in gw_qinf.build_blocks and gw_deep_v2.closed_dpsi
    gamma_L = (
        -eL * mp.re((2 * L / (L + 4 * PI * 1j * n)) * F)
        + 2 * eL * mp.hyp2f1(mp.mpf(1) / 4, 1, mp.mpf(5) / 4, z)
        - mp.mpf(1) / 2 * (mp.re(mp.digamma(an)) - mp.digamma(mp.mpf(1) / 4))
        + (mp.mpf(1) / 2 * mp.log((mp.e ** (L / 2) - 1) / (mp.e ** (L / 2) + 1))
           + mp.atan(mp.e ** (L / 2)) - PI / 4 + mp.euler / 2
           + mp.mpf(1) / 2 * mp.log(8 * PI))
    )

    t1 = -L * eL * mp.im((2 * L / (4 * PI * n - 1j * L)) * F)
    t3 = mp.mpf(1) / 4 * mp.re(mp.polygamma(1, an))

    t2_bug = -(eL / 4) * mp.re(mp.lerchphi(z, 2, an))       # gw_qinf, as shipped
    t2_fix = -(eL / 4) * mp.re(V3.lerchphi_series(z, 2, an))  # defining series

    beta_bug = (t1 + t2_bug + t3) / L
    beta_fix = (t1 + t2_fix + t3) / L

    return -2 * (gamma_L - beta_bug), -2 * (gamma_L - beta_fix)


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    c, N, dps = int(argv[1]), int(argv[2]), int(argv[3])
    ns = [int(x) for x in argv[4:]] or list(range(-N, N + 1))

    mp.mp.dps = dps          # AFTER every import -- see module docstring

    print("#" * 100)
    print("# ENTRY AUDIT (c, N, dps) = (%d, %d, %d) -- lerchphi defect vs matrix diagonal"
          % (c, N, dps))
    print("# delta[n] = P0d_buggy[n] - P0d_corrected[n]  (only beta_L differs)")
    print("# lambda_min(Q_%d,%d) under test = 1.32105051975e-102" % (c, N))
    print("#" * 100)
    print()

    rows = []
    t0 = time.time()
    for n in ns:
        t1 = time.time()
        bug, fix = closed_pair(c, n)
        d = bug - fix
        rows.append((n, d, time.time() - t1))
        print("  n=%4d   delta = %s   (signed)   |delta| = %s   %.1f s"
              % (n, mp.nstr(d, 8), mp.nstr(abs(d), 8), time.time() - t1))
        sys.stdout.flush()

    dt = time.time() - t0
    print()
    print("  %d indices in %.1f s" % (len(ns), dt))
    print()

    if not rows:
        return 0

    absd = [abs(r[1]) for r in rows]
    imax = max(range(len(rows)), key=lambda i: absd[i])
    imin = min(range(len(rows)), key=lambda i: absd[i])
    mx, mn = absd[imax], absd[imin]
    ds = [r[1] for r in rows]
    dmax, dmin = max(ds), min(ds)

    # lambda_min reference values come from PRIOR runs and are printed for
    # context only.  They are not recomputed here, and when the pair (c, N) is
    # unknown every ratio against them is suppressed rather than guessed.
    lam_ref = {"(100, 40)": mp.mpf("1.32105051975e-102"),
               "(13, 64)": mp.mpf("6.32135140948e-59"),
               "(13, 4)": mp.mpf("9.67926186051e-15"),
               "(100, 20)": mp.mpf("3.0256658e-62")}
    lam = lam_ref.get("(%d, %d)" % (c, N))

    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print("  indices audited        : %s" % (("%d..%d" % (min(r[0] for r in rows),
                                                          max(r[0] for r in rows)))
                                             if len(rows) > 1 else str(rows[0][0])))
    print("  max |delta|            : %s   at n = %+d" % (mp.nstr(mx, 18), rows[imax][0]))
    print("  min |delta|            : %s   at n = %+d" % (mp.nstr(mn, 18), rows[imin][0]))
    print("  delta (signed) range   : %s .. %s" % (mp.nstr(dmin, 12), mp.nstr(dmax, 12)))
    if lam is None:
        print("  lambda_min reference   : none known for this (c, N) -- ratio suppressed")
    else:
        print("  lambda_min reference   : %s   [prior run, context only]" % mp.nstr(lam, 18))
        print("  max|delta| / lambda_min: %s" % mp.nstr(mx / lam, 12))
    print()
    print("  delta == 0 exactly?    : %s" % ("yes (no defect reached the matrix)"
                                             if mx == 0 else "NO -- defect reaches the matrix"))
    print()

    if len(rows) == len(range(-N, N + 1)) and lam is not None:
        # full scan: Weyl bracket for the corrected eigenvalue
        lo = lam - dmax
        hi = lam - dmin
        print("WEYL BRACKET (valid because the perturbation is purely diagonal):")
        print("  lam_min(M_corr) in [ %s , %s ]" % (mp.nstr(lo, 18), mp.nstr(hi, 18)))
        print("  bracket straddles zero ? %s"
              % ("YES -- SIGN NOT DETERMINED by the shipped build"
                 if (lo < 0 < hi) else "no -- sign determined"))
    else:
        print("(Weyl bracket suppressed: needs BOTH a full -N..N scan AND a known)"
              "\n (lambda_min reference for this (c, N))")

    print()
    print("TOOL STATUS: mpmath only.  lean/coqc/isabelle/z3/dkcheck NOT RUN.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
