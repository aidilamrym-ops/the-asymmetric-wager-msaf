# -*- coding: utf-8 -*-
"""
DEEP VALIDATION OF THE ARCHIMEDAN CLOSED FORMS.

WHY THIS SCRIPT EXISTS
----------------------
Everything computed for Q_infty uses the paper's closed forms

    psi_arch(n)      = alpha_L(n)                      [hyp2f1 + digamma]
    psi_arch'(n)     = -2 (gamma_L(n) - beta_L(n))     [hyp2f1 + digamma + lerchphi]

rather than the DEFINING integral (eq. 3)

    psi_arch(n) = (1/pi^2) * int_0^inf h_+(r) S(r, n, L) dr.

gw_arch_check.py [V2]/[V2b] compares the two, but does so at dps = 30 with an
acceptance threshold of 1e-12.  The observed agreement there is only about
1e-19 .. 1e-20 RELATIVE.  Every eigenvalue reported for Q_infty below that
level -- which includes essentially the whole lambda_min ladder
(1e-35 .. 1e-59) and the c = 100 probe (-4.2e-71) -- is therefore only as good
as the assumption that the closed form is an EXACT IDENTITY for the integral.

A relative discrepancy of 1e-19 can have three very different sources:

  (A) ARITHMETIC-LIMITED : the reference quadrature / tail integration is not
      computed deep enough.  Then the discrepancy shrinks as dps increases
      and the closed form is exact.
  (T) TAIL-LIMITED       : the head stops at R and the dropped oscillatory
      remainder is only bounded.  Then the discrepancy shrinks as R increases
      (like a power of 1/R) and the closed form is exact.
  (D) DEFINITE ERROR     : the closed form is not the integral.  The
      discrepancy plateaus under BOTH sweeps.

Only case (D) would invalidate the ladder.  This script separates them with
two independent sweeps and prints the raw columns so the reader can see which
of (A), (T), (D) the data exhibit.  It does not decide the question in
advance.

USAGE
    python gw_deep_v2.py dps     # sweep the working precision at fixed R
    python gw_deep_v2.py r       # sweep the head cutoff R at fixed dps
    python gw_deep_v2.py both     # (default) both

VERDICT printed at the end is purely mechanical: it reports which sweep moved
the discrepancy and by how many orders of magnitude.  Nothing here bears on
RH, Weil positivity, prime counting or factoring.
"""

import sys
import time

import mpmath as mp

import gw_arch_check as GA


C = 13
R_REF = mp.mpf(10) ** 4


# ---------------------------------------------------------------------------
# the closed forms, transcribed from gw_qinf.build_blocks (the assembly itself)
# ---------------------------------------------------------------------------
def closed_psi(n, L):
    if n == 0:
        return mp.mpf(0)
    z = mp.e ** (-2 * L)
    an = mp.mpf(1) / 4 + mp.pi * 1j * n / L
    F = mp.hyp2f1(1, an, an + 1, z)
    return (mp.e ** (-L / 2) * mp.im((2 * L / (L + 4 * mp.pi * 1j * n)) * F)
            + mp.mpf(1) / 2 * mp.im(mp.digamma(an))) / mp.pi


def closed_dpsi(n, L):
    z = mp.e ** (-2 * L)
    an = mp.mpf(1) / 4 + mp.pi * 1j * n / L
    F = mp.hyp2f1(1, an, an + 1, z)
    t1 = -L * mp.e ** (-L / 2) * mp.im((2 * L / (4 * mp.pi * n - 1j * L)) * F)
    t2 = -(mp.e ** (-L / 2) / 4) * mp.re(mp.lerchphi(z, 2, an))
    t3 = mp.mpf(1) / 4 * mp.re(mp.polygamma(1, an))
    beta = (t1 + t2 + t3) / L
    gamma = (-mp.e ** (-L / 2) * mp.re((2 * L / (L + 4 * mp.pi * 1j * n)) * F)
             + 2 * mp.e ** (-L / 2) * mp.hyp2f1(mp.mpf(1) / 4, 1,
                                                mp.mpf(5) / 4, z)
             - mp.mpf(1) / 2 * (mp.re(mp.digamma(an)) - mp.digamma(mp.mpf(1) / 4))
             + (mp.mpf(1) / 2 * mp.log((mp.e ** (L / 2) - 1) / (mp.e ** (L / 2) + 1))
                + mp.atan(mp.e ** (L / 2)) - mp.pi / 4 + mp.euler / 2
                + mp.mpf(1) / 2 * mp.log(8 * mp.pi)))
    return -2 * (gamma - beta)


def measure(n, R, dps, which):
    """return (closed, direct, abs.diff, rel.diff, explicit bound, seconds)"""
    L = mp.log(C)
    t0 = time.time()
    val, bnd = GA.arch_source(n, C, R, dps, which)
    dt = time.time() - t0
    closed = closed_psi(n, L) if which == "psi" else closed_dpsi(n, L)
    diff = abs(val - closed)
    rel = diff / abs(closed) if closed != 0 else diff
    return closed, val, diff, rel, bnd, dt


# ---------------------------------------------------------------------------
def sweep_dps():
    print("=" * 100)
    print("SWEEP 1 -- ARITHMETIC-LIMITED?  fixed head cutoff R = %s, varying dps"
          % mp.nstr(R_REF, 6))
    print("  if case (A): rel falls by orders of magnitude as dps rises")
    print("  if case (T) or (D): rel stays roughly put")
    print("=" * 100)
    print("  which   n    dps      direct value                  "
          "abs diff        rel diff        bound          seconds")
    print("  " + "-" * 96)
    rows = []
    for dps in (30, 60, 100):
        for which, n in (("psi", 1), ("psi", 3), ("dpsi", 1)):
            closed, val, diff, rel, bnd, dt = measure(n, R_REF, dps, which)
            rows.append((dps, which, n, rel))
            print("  %-6s %-4d %-8d %-30s %-15s %-15s %-14s %.1f"
                  % (which, n, dps, mp.nstr(val, 14), mp.nstr(diff, 6),
                     mp.nstr(rel, 6), mp.nstr(bnd, 6), dt))
            sys.stdout.flush()
    print()
    return rows


def sweep_R():
    print("=" * 100)
    print("SWEEP 2 -- TAIL-LIMITED?  fixed dps = 100, varying head cutoff R")
    print("  if case (T): rel falls like a power of 1/R as R rises")
    print("  if case (A) or (D): rel stays roughly put")
    print("=" * 100)
    print("  which   n    R          dps      abs diff        rel diff"
          "        bound          seconds")
    print("  " + "-" * 96)
    rows = []
    for R in (mp.mpf(10) ** 3, mp.mpf(10) ** 4, mp.mpf(10) ** 5):
        for which, n in (("psi", 1), ("dpsi", 1)):
            closed, val, diff, rel, bnd, dt = measure(n, R, 100, which)
            rows.append((R, which, n, rel))
            print("  %-6s %-4d %-11s %-8d %-15s %-15s %-14s %.1f"
                  % (which, n, mp.nstr(R, 4), 100, mp.nstr(diff, 6),
                     mp.nstr(rel, 6), mp.nstr(bnd, 6), dt))
            sys.stdout.flush()
    print()
    return rows


def main(argv):
    mode = argv[1] if len(argv) > 1 else "both"
    print("#" * 100)
    print("# DEEP VALIDATION OF THE ARCHIMEDAN CLOSED FORMS vs THE DEFINING INTEGRAL")
    print("# c = %d,  L = %s" % (C, mp.nstr(mp.log(C), 12)))
    print("# closed form is EXACT iff the discrepancy vanishes under BOTH sweeps")
    print("#" * 100)
    print()

    d_rows = sweep_dps() if mode in ("dps", "both") else []
    r_rows = sweep_R() if mode in ("r", "both") else []

    print("=" * 100)
    print("MECHANICAL VERDICT")
    print("=" * 100)

    if d_rows:
        first = [rel for dps, _, _, rel in d_rows if dps == 30]
        last = [rel for dps, _, _, rel in d_rows if dps == 100]
        if first and last:
            drop_dps = max(mp.log10(a / b) for a, b in zip(first, last)
                           if a > 0 and b > 0)
            print("  dps sweep 30 -> 100 : discrepancy dropped by %.1f decades"
                  % drop_dps)
    if r_rows:
        first = [rel for R, _, _, rel in r_rows if R == 10 ** 3]
        last = [rel for R, _, _, rel in r_rows if R == 10 ** 5]
        if first and last:
            drop_R = max(mp.log10(a / b) for a, b in zip(first, last)
                         if a > 0 and b > 0)
            print("  R sweep 1e3 -> 1e5  : discrepancy dropped by %.1f decades"
                  % drop_R)

    print()
    print("  reading: a drop under the dps sweep => case (A), arithmetic-limited;")
    print("           a drop under the R sweep    => case (T), tail-limited;")
    print("           a plateau under BOTH        => case (D), the closed form")
    print("           does not reproduce the defining integral.")
    print()
    print("  CASE (D) IS THE ONLY ONE THAT WOULD INVALIDATE THE lambda_min LADDER.")
    print("  until this is settled, every eigenvalue below the observed")
    print("  agreement floor must be reported as resting on the identity")
    print("  assumption, not on an independent check of it.")
    print()
    print("  no RH, Weil-positivity, prime-counting or factoring claim is involved;")
    print("  the source preprint disclaims all of those.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
