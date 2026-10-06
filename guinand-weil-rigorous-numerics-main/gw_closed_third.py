# -*- coding: utf-8 -*-
"""Third-route evaluation of closed_dpsi(n, L) in gw_deep_v2.

Motivation
----------
The assembled identity residual for psi' sits at 3.3911092e-102 while every
directly cross-checked component is far deeper:

    head  <= 1.5e-137   (GL224 vs GL400, vs mp.quad, and vs an algebraic
                         rearrangement that cancels nothing)
    E1    <= 8.9e-145   (dps sweep)
    E2    <= 5.2e-151   (last retained IBP term)
    closed <= 1.9e-182  (dps sweep)

A dps sweep only proves CONVERGENCE.  A component that converges to a wrong
limit is invisible to it.  head has three genuinely independent checks; the
other three have only self-convergence.  This script attacks `closed`.

closed_dpsi is built from pieces that are all evaluable a second way, from
their defining series, with no mpmath special-function code path involved:

    F  = hyp2f1(1, a, a+1, z)  = sum_k  a/(a+k) z^k
    L1 = lerchphi(z, 1, a)     = sum_k  z^k/(k+a)          (so F = a*L1)
    L2 = lerchphi(z, 2, a)     = sum_k  z^k/(k+a)^2
    H  = hyp2f1(1/4, 1, 5/4, z)= sum_k (1/4)/(1/4+k) z^k
    psi(a)                     = shift-up + Bernoulli asymptotic
    psi'(a)                    = shift-up + Bernoulli asymptotic
    psi(1/4)                   = -EulerGamma - pi/2 - 3 ln 2   (exact)

For c = 100, z = exp(-2L) = 1e-4 exactly, so every series above is truncated
at ~40 terms for 160 digits.

Read-only with respect to every other file; writes nothing but stdout.

usage: python gw_closed_third.py <c> <n> <dps> [M]
example: python gw_closed_third.py 100 40 160 400
"""
import sys

import mpmath as mp

# Imported at module load, BEFORE main() sets mp.mp.dps.  Importing it inside
# main() would let its own module-level precision setting override ours and
# silently compute everything at the wrong dps.
import gw_deep_v2 as D


TOL = None  # set in main from dps


def series_F(z, a):
    """hyp2f1(1, a, a+1, z) = sum_k a/(a+k) z^k."""
    s = mp.mpc(0)
    zk = mp.mpf(1)
    for k in range(100000):
        t = a / (a + k) * zk
        s += t
        if abs(t) < TOL:
            break
        zk *= z
    return s, k


def series_lerch(z, s, a):
    """lerchphi(z, s, a) = sum_k z^k / (k+a)^s."""
    out = mp.mpc(0)
    zk = mp.mpf(1)
    for k in range(100000):
        t = zk / (k + a) ** s
        out += t
        if abs(t) < TOL:
            break
        zk *= z
    return out, k


def psi_ind(z, M):
    """digamma via shift-up then Bernoulli asymptotic.  Independent path."""
    w = z + M
    val = mp.log(w) - 1 / (2 * w)
    n_used = 0
    for n in range(1, 400):
        term = -mp.bernoulli(2 * n) / (2 * n * w ** (2 * n))
        val += term
        n_used = n
        if abs(term) < TOL:
            break
    corr = mp.mpf(0)
    for k in range(M):
        corr += 1 / (z + k)
    return val - corr, n_used


def psi1_ind(z, M):
    """trigamma via shift-up then Bernoulli asymptotic.  Independent path."""
    w = z + M
    val = 1 / w + 1 / (2 * w ** 2)
    n_used = 0
    for n in range(1, 400):
        term = mp.bernoulli(2 * n) / w ** (2 * n + 1)
        val += term
        n_used = n
        if abs(term) < TOL:
            break
    corr = mp.mpc(0)
    for k in range(M):
        corr += 1 / (z + k) ** 2
    return val + corr, n_used


def closed_dpsi_ind(z, n, L, M):
    """Full closed_dpsi rebuilt from the independent pieces above."""
    an = mp.mpf(1) / 4 + mp.pi * 1j * n / L
    F, kF = series_F(z, an)
    L2, kL2 = series_lerch(z, 2, an)
    H, kH = series_F(z, mp.mpf(1) / 4)          # hyp2f1(1/4,1,5/4,z) same shape
    psi_an, nA = psi_ind(an, M)
    psi1_an, nB = psi1_ind(an, M)
    # psi(1/4) has an exact closed form: -EulerGamma - pi/2 - 3 ln 2
    psi_q = -mp.euler - mp.pi / 2 - 3 * mp.log(2)

    t1 = -L * mp.e ** (-L / 2) * mp.im((2 * L / (4 * mp.pi * n - 1j * L)) * F)
    t2 = -(mp.e ** (-L / 2) / 4) * mp.re(L2)
    t3 = mp.mpf(1) / 4 * mp.re(psi1_an)
    beta = (t1 + t2 + t3) / L

    gamma = (-mp.e ** (-L / 2) * mp.re((2 * L / (L + 4 * mp.pi * 1j * n)) * F)
             + 2 * mp.e ** (-L / 2) * H
             - mp.mpf(1) / 2 * (mp.re(psi_an) - psi_q)
             + (mp.mpf(1) / 2 * mp.log((mp.e ** (L / 2) - 1) / (mp.e ** (L / 2) + 1))
                + mp.atan(mp.e ** (L / 2)) - mp.pi / 4 + mp.euler / 2
                + mp.mpf(1) / 2 * mp.log(8 * mp.pi)))
    return -2 * (gamma - beta), dict(kF=kF, kL2=kL2, kH=kH, nA=nA, nB=nB)


def main(argv):
    global TOL
    c = int(argv[1])
    n = int(argv[2])
    dps = int(argv[3])
    M = int(argv[4]) if len(argv) > 4 else 400

    mp.mp.dps = dps
    TOL = mp.mpf(10) ** (-(dps + 10))
    L = mp.log(c)
    z = mp.e ** (-2 * L)
    an = mp.mpf(1) / 4 + mp.pi * 1j * n / L

    print("=" * 100)
    print("# THIRD-ROUTE EVALUATION OF closed_dpsi: is the residual inside it?")
    print("# c = %d, n = %d, dps = %d, M = %d" % (c, n, dps, M))
    print("# L = %s   z = exp(-2L) = %s   an = %s" % (mp.nstr(L, 20), mp.nstr(z, 20), mp.nstr(an, 20)))
    print("# |an| = %s" % mp.nstr(abs(an), 16))
    print("=" * 100, flush=True)

    # ---- individual pieces: mpmath vs defining series ----------------------
    print("")
    print("-" * 100)
    print("PIECEWISE: mpmath  vs  defining series (independent)")
    print("-" * 100)

    F_ref, kF = series_F(z, an)
    F_mp = mp.hyp2f1(1, an, an + 1, z)
    print("  F  = hyp2f1(1,an,an+1,z)   series(%d) = %s" % (kF, mp.nstr(F_ref, 34)))
    print("       mpmath                hyp2f1      = %s" % mp.nstr(F_mp, 34))
    print("       |mp - series|         = %s" % mp.nstr(abs(F_mp - F_ref), 16))

    L2_ref, kL2 = series_lerch(z, 2, an)
    L2_mp = mp.lerchphi(z, 2, an)
    print("  L2 = lerchphi(z,2,an)     series(%d) = %s" % (kL2, mp.nstr(L2_ref, 34)))
    print("       mpmath                lerchphi   = %s" % mp.nstr(L2_mp, 34))
    print("       |mp - series|         = %s" % mp.nstr(abs(L2_mp - L2_ref), 16))

    L1_ref, kL1 = series_lerch(z, 1, an)
    print("  L1 = lerchphi(z,1,an)     series(%d) = %s   (F should equal an*L1)" % (kL1, mp.nstr(L1_ref, 34)))
    print("       |an*L1 - F_series|    = %s" % mp.nstr(abs(an * L1_ref - F_ref), 16))
    print("       |an*L1 - F_mpmath|    = %s" % mp.nstr(abs(an * L1_ref - F_mp), 16))

    H_ref, kH = series_F(z, mp.mpf(1) / 4)
    H_mp = mp.hyp2f1(mp.mpf(1) / 4, 1, mp.mpf(5) / 4, z)
    print("  H  = hyp2f1(1/4,1,5/4,z)  series(%d) = %s" % (kH, mp.nstr(H_ref, 34)))
    print("       mpmath                hyp2f1      = %s" % mp.nstr(H_mp, 34))
    print("       |mp - series|         = %s" % mp.nstr(abs(H_mp - H_ref), 16))

    psi_an_ind, nA = psi_ind(an, M)
    psi_an_mp = mp.digamma(an)
    print("  psi(an)   shift+asymptotic(%d terms, M=%d) = %s" % (nA, M, mp.nstr(psi_an_ind, 34)))
    print("            mpmath digamma                 = %s" % mp.nstr(psi_an_mp, 34))
    print("            |mp - independent|             = %s" % mp.nstr(abs(psi_an_mp - psi_an_ind), 16))

    psi_q_series = -mp.euler - mp.pi / 2 - 3 * mp.log(2)
    psi_q_mp = mp.digamma(mp.mpf(1) / 4)
    print("  psi(1/4)  exact -Euler - pi/2 - 3ln2     = %s" % mp.nstr(psi_q_series, 34))
    print("            mpmath digamma                  = %s" % mp.nstr(psi_q_mp, 34))
    print("            |mp - exact|                    = %s" % mp.nstr(abs(psi_q_mp - psi_q_series), 16))

    psi1_ref, nB = psi1_ind(an, M)
    psi1_mp = mp.polygamma(1, an)
    print("  psi'(an)  shift+asymptotic(%d terms, M=%d) = %s" % (nB, M, mp.nstr(psi1_ref, 34)))
    print("            mpmath polygamma                = %s" % mp.nstr(psi1_mp, 34))
    print("            |mp - independent|              = %s" % mp.nstr(abs(psi1_mp - psi1_ref), 16))

    # ---- assembled closed_dpsi, both ways ---------------------------------
    print("")
    print("-" * 100)
    print("ASSEMBLED closed_dpsi")
    print("-" * 100)
    ref = D.closed_dpsi(n, L)
    ind, info = closed_dpsi_ind(z, n, L, M)
    print("  gw_deep_v2.closed_dpsi      = %s" % mp.nstr(ref, 40))
    print("  independent reconstruction  = %s" % mp.nstr(ind, 40))
    diff = abs(ref - ind)
    print("  |difference|                = %s" % mp.nstr(diff, 16))
    print("  (the psi' residual to explain is 3.391109217077509e-102)")
    if diff > mp.mpf(10) ** (-(dps - 15)):
        print("  --> INDEPENDENT ROUTE DISAGREES: the discrepancy is inside closed_dpsi")
    else:
        print("  --> independent route AGREES: closed_dpsi is exonerated at this depth")
    print("  piecewise iteration counts: %s" % info)
    print("=" * 100)


if __name__ == "__main__":
    main(sys.argv)
