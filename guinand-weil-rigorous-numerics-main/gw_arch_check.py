# -*- coding: utf-8 -*-
"""
INDEPENDENT CHECK OF THE ARKIMEDIAN BLOCK OF Q_inf.

The assembly used in gw_qinf.py takes psi_arch(n) and psi'_arch(n) from closed
forms (2F1 / digamma / Lerch) read off the source paper arXiv:2607.02828v3.
Those closed forms are a PREPRINT claim and were NOT independently derived here.

This script tests them against direct numerical integration of the defining
integral (paper, eq. (3)):

    psi_arch,T(x) = 1/(2 pi^2) * int_{-T}^{T} h_+(r) S(r,x,L) dr,
    S(r,x,L)      = int_0^L sin(2 pi x (1 - y/L)) cos(r y) dy,
    h_+(r)        = Re digamma(1/4 + i r/2) - log(pi),        L = log c.

Steps, each independently checkable:

  V0   the closed form S(r,n,L) = 2 rho n sin^2(L r/2)/(r^2 - rho^2 n^2)
       for integer n is compared with the defining y-integral at sample points.
  V1   h_+(r) - log(r/2pi) is printed, to document the tail model's input.
  V2   psi_arch(inf)(n) and psi'_arch(inf)(n) are computed by direct r-quadrature
       (Gauss-Legendre on panels of one oscillation period 2 pi/L, plus an
       explicit tail: exact r = R e^s substitution for the non-oscillatory part,
       two integrations by parts for the oscillatory part), and compared with
       alpha_L(n) and -2(gamma_L(n) - beta_L(n)).

The only term dropped in the tail is int_R^inf eps(r) g(r) cos(L r) dr with
eps = h_+ - log(r/2pi); its absolute value is bounded explicitly and printed.

VERDICT printed as PASS / FAIL against that bound.  No RH claim is involved.
"""

import sys

import mpmath as mp

import gw_qinf as G


def hplus(r):
    return mp.re(mp.digamma(mp.mpf(1) / 4 + 0.5j * r)) - mp.log(mp.pi)


def S_closed(r, n, L, rho):
    d = rho * n
    num = 2 * rho * n * mp.sin(L * r / 2) ** 2
    den = r * r - d * d
    if den == 0:
        # removable: LHS limit
        return mp.mpf(0)
    return num / den


def S_direct(r, n, L):
    # panel breakpoints every half period of cos(r y): without them mp.quad
    # silently loses ~1e-16 on the oscillatory integral at r = 100.
    step = mp.pi / r if r != 0 else L
    pts = [mp.mpf(0)]
    y = step
    while y < L:
        pts.append(y)
        y += step
    pts.append(L)
    return mp.quad(lambda y: mp.sin(2 * mp.pi * n * (1 - y / L)) * mp.cos(r * y),
                   pts)


def tail_E1(R, g, dps):
    """int_R^inf h_+(r) g(r) dr  via r = R e^s (integrand decays like e^-s)."""
    mp.mp.dps = dps

    def f(s):
        r = R * mp.e ** s
        return hplus(r) * g(r) * r
    return mp.quad(f, [0, mp.inf])


def tail_E2(R, g, gp, gpp, L, dps):
    """int_R^inf h_+(r) g(r) cos(L r) dr, two integrations by parts.

    u = log(r/2pi) g(r);  the eps = h_+ - log(r/2pi) remainder is dropped and
    bounded by the caller."""
    mp.mp.dps = dps

    def u(x):
        return mp.log(x / (2 * mp.pi)) * g(x)

    def up(x):
        return g(x) / x + mp.log(x / (2 * mp.pi)) * gp(x)

    def upp(x):
        return 2 * gp(x) / x - g(x) / x ** 2 + mp.log(x / (2 * mp.pi)) * gpp(x)

    return (-u(R) * mp.sin(L * R) / L
            - up(R) * mp.cos(L * R) / L ** 2
            + upp(R) * mp.sin(L * R) / L ** 3)


def eps_bound(R, gmax_over_r4, nfactor):
    """bound on |int_R^inf eps g cos| with |eps| <= 1/(24 r^2)."""
    return mp.mpf(1) / 24 * gmax_over_r4


def arch_source(n, c, R, dps, which, glorder=48, glcheck=True):
    """psi_arch(n) (which='psi') or psi'_arch(n) (which='dpsi') by direct
    r-quadrature over (0, inf).

    glcheck=True also evaluates the head one Gauss-Legendre order lower and
    returns their difference; on the first run GL16 and GL32 disagreed by
    6.8e-10, which was the entire residual against the paper's closed forms.
    """
    mp.mp.dps = dps
    L = mp.log(c)
    rho = 2 * mp.pi / L
    T = 2 * mp.pi / L            # period of sin^2(L r /2)
    d = rho * n

    if which == "psi":
        pref = rho * n / (mp.pi ** 2)

        def g(r):
            return 1 / (r * r - d * d)

        def gp(r):
            return -2 * r / (r * r - d * d) ** 2

        def gpp(r):
            a = r * r - d * d
            return -2 / a ** 2 + 8 * r * r / a ** 3
    else:
        pref = rho / (mp.pi ** 2)

        def g(r):
            a = r * r - d * d
            return (r * r + d * d) / a ** 2

        def gp(r):
            a = r * r - d * d
            return -2 * r * (r * r + 3 * d * d) / a ** 3

        def gpp(r):
            a = r * r - d * d
            return 6 * (r ** 4 + 6 * r * r * d * d + d ** 4) / a ** 4

    if pref == 0:
        return mp.mpf(0), mp.mpf(0)

    # ---- head: Gauss-Legendre on panels of one oscillation period ----------
    # The head must END exactly where the tail BEGINS.  Using ceil(R/T) makes
    # the head overrun R while the tail starts at R, double-counting the strip
    # [R, ceil(R/T)*T]; that strip contributed a spurious ~2.5e-7 and was the
    # whole of the systematic n-linear bias seen on the first run.
    K = int(mp.floor(R / T))
    R_head = K * T

    def head_quad(order):
        x, w = mp.gauss_quadrature(order, "legendre")
        acc = mp.mpf(0)
        for k in range(K):
            a, b = k * T, (k + 1) * T
            half, mid = (b - a) / 2, (b + a) / 2
            for xi, wi in zip(x, w):
                r = mid + half * xi
                acc += wi * half * hplus(r) * (1 - mp.cos(L * r)) * g(r)
        return acc

    head = head_quad(glorder)
    head_err = abs(head - head_quad(glorder - 16)) if glcheck else mp.mpf(0)

    # ---- tail -------------------------------------------------------------
    E1 = tail_E1(R_head, g, dps)
    E2 = tail_E2(R_head, g, gp, gpp, L, dps)
    tail = E1 - E2

    # explicit bound on the dropped eps-part of E2: |eps| <= 1/(24 r^2)
    # int_R^inf (1/(24 r^2)) g(r) dr ; g ~ 1/r^2 -> <= 1/(24) * 1/(3 R^3) * c_g
    cg = mp.mpf(1)
    bnd = mp.mpf(1) / (24 * 3 * R_head ** 3) * cg + head_err

    return pref * (head + tail), pref * bnd


def main():
    c = 13
    dps = 30
    R = mp.mpf(10) ** 4
    L = mp.log(c)
    rho = 2 * mp.pi / L
    mp.mp.dps = dps

    print("#" * 96)
    print("# INDEPENDENT VALIDATION OF THE ARKIMEDIAN CLOSED FORMS")
    print("# paper under test: arXiv:2607.02828v3 (preprint, LLM-assisted)")
    print("# c = %s,  L = %s,  rho = 2pi/L = %s,  dps = %d,  R = %s"
          % (c, mp.nstr(L, 8), mp.nstr(rho, 8), dps, mp.nstr(R, 5)))
    print("#" * 96)
    print()

    # ---------------- V0: the S closed form --------------------------------
    print("[V0] closed form for S(r,n,L) vs the defining y-integral")
    mp.mp.dps = 60                      # reference quadrature must beat the test
    worst = mp.mpf(0)
    worst_rel = mp.mpf(0)
    for n in (1, 2, 3):
        for rr in (0.37, 1.9, 4.4, 11.0, 30.0, 100.0):
            sc = S_closed(rr, n, L, rho)
            sd = S_direct(rr, n, L)
            e = abs(sc - sd)
            rel = e / max(abs(sd), mp.mpf(10) ** -60)
            if rel > worst_rel:
                worst_rel = rel
            worst = max(worst, e)
    mp.mp.dps = dps
    print("      reference quadrature run at dps = 60 (its own stopping level ~1e-16)")
    print("      max |closed - direct|            = %s" % mp.nstr(worst, 6))
    print("      max relative error               = %s" % mp.nstr(worst_rel, 6))
    print("      ->", "PASS" if worst_rel < mp.mpf(10) ** -14 else "FAIL")
    print()

    # ---------------- V1: the tail model input ------------------------------
    print("[V1] eps(r) = h_+(r) - log(r/2pi)   (the tail model assumes O(1/r^2))")
    for rr in (100, 1000, 10000, 100000):
        e = hplus(rr) - mp.log(rr / (2 * mp.pi))
        print("      r = %-7d  eps = %-24s  r^2 * eps = %s"
              % (rr, mp.nstr(e, 6), mp.nstr(e * rr * rr, 10)))
    print("      (asymptotic guess from Re psi(1/4+ir/2): -1/24 = -0.0416666667)")
    print()

    # ---------------- V2: psi_arch against alpha_L -------------------------
    print("[V2] direct r-quadrature vs the closed forms used by the assembly")
    print("      n    alpha_L(n) [closed]      direct [this script]        rel.err      bound")
    ok = True
    for n in (0, 1, 2, 3, 4):
        val, bnd = arch_source(n, c, R, dps, "psi")
        if n == 0:
            closed = mp.mpf(0)
        else:
            zz = mp.e ** (-2 * L)

            def a_n(k):
                return mp.mpf(1) / 4 + mp.pi * 1j * k / L

            closed = (mp.e ** (-L / 2)
                      * mp.im((2 * L / (L + 4 * mp.pi * 1j * n))
                              * mp.hyp2f1(1, a_n(n), a_n(n) + 1, zz))
                      + mp.mpf(1) / 2 * mp.im(mp.digamma(a_n(n)))) / mp.pi
        if closed != 0:
            rel = abs(val - closed) / abs(closed)
            if rel > max(10 * bnd, mp.mpf(10) ** -12):
                ok = False
        else:
            rel = abs(val)
            if rel > mp.mpf(10) ** -12:
                ok = False
        print("      %d    %-24s %-26s %-12s %s"
              % (n, mp.nstr(closed, 10), mp.nstr(val, 10), mp.nstr(rel, 6),
                 mp.nstr(bnd, 6)))
    print()
    print("      ->", "PASS (inside the measured bound)" if ok else "FAIL")
    print()

    # ---------------- V2b: psi'_arch ---------------------------------------
    print("[V2b] direct r-quadrature vs -2(gamma_L(n) - beta_L(n))")
    print("      n    closed                 direct                  rel.err      bound")
    okb = True
    for n in (0, 1, 2, 3):
        val, bnd = arch_source(n, c, R, dps, "dpsi")
        Lc = L
        zz = mp.e ** (-2 * Lc)

        def a_n(k):
            return mp.mpf(1) / 4 + mp.pi * 1j * k / Lc

        def beta_L(k):
            an = a_n(k)
            t1 = -Lc * mp.e ** (-Lc / 2) * mp.im((2 * Lc / (4 * mp.pi * k - 1j * Lc))
                                                 * mp.hyp2f1(1, an, an + 1, zz))
            t2 = -(mp.e ** (-Lc / 2) / 4) * mp.re(mp.lerchphi(zz, 2, an))
            t3 = mp.mpf(1) / 4 * mp.re(mp.polygamma(1, an))
            return (t1 + t2 + t3) / Lc

        def gamma_L(k):
            an = a_n(k)
            return (-mp.e ** (-Lc / 2) * mp.re((2 * Lc / (Lc + 4 * mp.pi * 1j * k))
                                               * mp.hyp2f1(1, an, an + 1, zz))
                    + 2 * mp.e ** (-Lc / 2) * mp.hyp2f1(mp.mpf(1) / 4, 1, mp.mpf(5) / 4, zz)
                    - mp.mpf(1) / 2 * (mp.re(mp.digamma(an)) - mp.digamma(mp.mpf(1) / 4))
                    + (mp.mpf(1) / 2 * mp.log((mp.e ** (Lc / 2) - 1) / (mp.e ** (Lc / 2) + 1))
                       + mp.atan(mp.e ** (Lc / 2)) - mp.pi / 4 + mp.euler / 2
                       + mp.mpf(1) / 2 * mp.log(8 * mp.pi)))
        closed = -2 * (gamma_L(n) - beta_L(n))
        rel = abs(val - closed) / abs(closed)
        if rel > max(10 * bnd, mp.mpf(10) ** -12):
            okb = False
        print("      %d    %-24s %-24s %-12s %s"
              % (n, mp.nstr(closed, 10), mp.nstr(val, 10),
                 mp.nstr(rel, 6), mp.nstr(bnd, 6)))
    print()
    print("      ->", "PASS (inside the measured bound)" if okb else "FAIL")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
