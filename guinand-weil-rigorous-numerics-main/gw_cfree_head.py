# -*- coding: utf-8 -*-
"""Cancellation-free re-evaluation of the psi' (dpsi) archimedean head.

Why this script exists
----------------------
gw_panel_diag.py established that every component of the assembled residual
is verified far deeper than the residual itself:

    head (GL224)   <= 1.5e-137   (vs GL400 and vs mp.quad on panel 0)
    E1             <= 8.9e-145   (dps sweep)
    closed_dpsi    <= 1.9e-182   (dps sweep)
    E2             <= 5.2e-151   (last retained IBP term)

yet the assembled residual stands at 3.3911092e-102 -- 36 orders above the
best-verified component.  That is only possible if one "verification" does
not test what it appears to test.

All three head tests (GL96, GL224, mp.quad) evaluate the SAME integrand

    f_old(r) = h_+(r) * (1 - cos(L r)) * g(r)

so they cannot detect a common-mode error inside f_old.  That expression
cancels twice near r = d, where (1 - cos) has a double zero and g a double
pole, and again at every panel edge, where L*r = 2*k*pi and cos = 1.

With d = N*T so that L*d = 2*pi*N exactly, sin(L*r/2) = sin(L*(r-d)/2), hence

    (1 - cos L r) * g(r)
        = 2 (r^2 + d^2) / (r + d)^2 * ( sin(L (r-d)/2) / (r - d) )^2

which is regular at r = d (limit L^2/4) and loses no digits.  This script
evaluates both forms on identical nodes and reports the difference.

Read-only with respect to every other file; writes nothing but stdout.

usage: python gw_cfree_head.py <c> <N> <dps> <R_cut> <order> [n_report]
example: python gw_cfree_head.py 100 40 140 1000 224 15
"""
import sys
import time

import mpmath as mp

import gw_arch_check as GA
import gw_tail_deep as TD

JMAX = 46


def main(argv):
    c = int(argv[1])
    N = int(argv[2])
    dps = int(argv[3])
    R_cut = mp.mpf(argv[4])
    order = int(argv[5])
    n_report = int(argv[6]) if len(argv) > 6 else 15

    mp.mp.dps = dps
    L = mp.log(c)
    T = 2 * mp.pi / L
    rho = 2 * mp.pi / L
    K = int(mp.floor(R_cut / T))
    R_head = K * T
    d = rho * N
    g, gk = TD.make_g('dpsi', d)
    pref = rho / mp.pi ** 2

    # exactness gate for the substitution used below
    phase_ok = abs(mp.nint(L * d / (2 * mp.pi)) - L * d / (2 * mp.pi)) < mp.mpf(10) ** (-(dps - 5))

    print("=" * 100)
    print("# CANCELLATION-FREE HEAD: does the psi' residual live inside f_old?")
    print("# c = %d, N = %d, dps = %d, R = %s, K = %d, order = %d"
          % (c, N, dps, mp.nstr(R_cut, 6), K, order))
    print("# d = %s,  L*d/(2 pi) = %s   [exact-integer phase = %s]"
          % (mp.nstr(d, 17), mp.nstr(L * d / (2 * mp.pi), 17), phase_ok))
    print("=" * 100, flush=True)
    if not phase_ok:
        print("!! L*d/(2*pi) is NOT an integer to working precision:")
        print("   the substitution sin(L r/2) = sin(L (r-d)/2) does NOT hold")
        print("   and this script must not be trusted.  STOPPING.")
        return

    x, w = mp.gauss_quadrature(order, "legendre")

    def f_old(r):
        return GA.hplus(r) * (1 - mp.cos(L * r)) * g(r)

    def f_new(r):
        """Cancellation-free form of the same integrand."""
        delta = r - d
        if delta == 0:
            s = L / 2
        else:
            s = mp.sin(L * delta / 2) / delta
        return GA.hplus(r) * (2 * (r * r + d * d) / (r + d) ** 2) * s * s

    old_pan, new_pan = [], []
    t0 = time.time()
    worst = []
    for k in range(K):
        a, b = k * T, (k + 1) * T
        half, mid = (b - a) / 2, (b + a) / 2
        acc_o = mp.mpf(0)
        acc_n = mp.mpf(0)
        for xi, wi in zip(x, w):
            r = mid + half * xi
            prod = wi * half * GA.hplus(r)
            acc_o += prod * (1 - mp.cos(L * r)) * g(r)
            delta = r - d
            s = L / 2 if delta == 0 else mp.sin(L * delta / 2) / delta
            acc_n += prod * (2 * (r * r + d * d) / (r + d) ** 2) * s * s
        old_pan.append(acc_o)
        new_pan.append(acc_n)
        worst.append((abs(acc_n - acc_o), k))
    print("  evaluated %d panels at order %d in %.1f s"
          % (K, order, time.time() - t0), flush=True)

    old_sum = mp.fsum(old_pan)
    new_sum = mp.fsum(new_pan)
    delta_sum = new_sum - old_sum

    print("")
    print("-" * 100)
    print("HEAD TOTALS")
    print("-" * 100)
    print("  old form (1-cos * g)          = %s" % mp.nstr(old_sum, 40))
    print("  new form (cancellation-free)  = %s" % mp.nstr(new_sum, 40))
    print("  new - old                     = %s" % mp.nstr(delta_sum, 16))
    print("  residual would move by        = %s" % mp.nstr(abs(pref * delta_sum), 16))
    print("  (target residual being explained: 3.3911092170775e-102)")

    worst.sort(reverse=True)
    print("")
    print("-" * 100)
    print("PANELS WHERE THE TWO FORMS DISAGREE MOST")
    print("-" * 100)
    print("   k        panel range                 |new - old|        pref-weighted")
    for dv, k in worst[:n_report]:
        print("  %4d  [%10.5f, %10.5f]   %-18s %s"
              % (k, k * T, (k + 1) * T, mp.nstr(dv, 14), mp.nstr(abs(pref * dv), 14)))

    print("")
    print("-" * 100)
    print("FULL RESIDUAL WITH EACH FORM")
    print("-" * 100)
    E1 = GA.tail_E1(R_head, g, dps)
    E2, last, n_terms, turned = TD.E2_deep(g, gk, L, R_head, JMAX)
    closed = TD.closed_dpsi(N, L)
    print("  E1     = %s" % mp.nstr(E1, 34))
    print("  E2     = %s  (last %s, turned=%s)" % (mp.nstr(E2, 34), mp.nstr(last, 8), turned))
    print("  closed = %s" % mp.nstr(closed, 34))
    print("  lambda_min target = 1.32105051975e-102")
    print("")
    for label, hs in (("old form", old_sum), ("new form", new_sum)):
        print("  %-9s : residual = %s" % (label, mp.nstr(abs(pref * (hs + E1 - E2) - closed), 16)))
    print("=" * 100)


if __name__ == "__main__":
    main(sys.argv)
