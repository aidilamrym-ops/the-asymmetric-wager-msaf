# -*- coding: utf-8 -*-
"""Locate the residual ~1e-9 in the direct archimedean quadrature.

Three independent levers:
  L1  Gauss-Legendre order in the head (8 / 16 / 32): if the head is at fault
      the value moves with the order.
  L2  the head cutoff R (1e3 / 1e4 / 1e5): if the tail treatment is at fault
      the value moves with R.
  L3  the tail's oscillatory half E2, computed by two integrations by parts,
      checked against direct oscillatory quadrature on [R_head, 64 R_head].
"""
import sys

import mpmath as mp

import gw_arch_check as A


def build(c, n, R, glorder):
    mp.mp.dps = 30
    L = mp.log(c)
    rho = 2 * mp.pi / L
    T = 2 * mp.pi / L
    d = rho * n
    pref = rho * n / (mp.pi ** 2)
    if pref == 0:
        return 0, 0, 0, 0
    g = lambda r: 1 / (r * r - d * d)
    K = int(mp.floor(R / T))
    R_head = K * T
    x, w = mp.gauss_quadrature(glorder, "legendre")
    head = mp.mpf(0)
    for k in range(K):
        a, b = k * T, (k + 1) * T
        half, mid = (b - a) / 2, (b + a) / 2
        for xi, wi in zip(x, w):
            r = mid + half * xi
            head += wi * half * A.hplus(r) * (1 - mp.cos(L * r)) * g(r)
    E1 = A.tail_E1(R_head, g, 30)
    gp = lambda r: -2 * r / (r * r - d * d) ** 2
    gpp = lambda r: -2 / (r * r - d * d) ** 2 + 8 * r * r / (r * r - d * d) ** 3
    E2 = A.tail_E2(R_head, gp=gp, gpp=gpp, L=L, dps=30, g=g)
    E2_direct = e2_direct(R_head, T, L, g)
    return head, E1, E2, E2_direct


def e2_direct(R_head, T, L, g):
    """int_{R_head}^inf h_+ g cos(L r) dr by period panels, then a short tail."""
    mp.mp.dps = 30
    x, w = mp.gauss_quadrature(24, "legendre")
    npanels = 4000
    s = mp.mpf(0)
    for k in range(npanels):
        a, b = R_head + k * T, R_head + (k + 1) * T
        half, mid = (b - a) / 2, (b + a) / 2
        for xi, wi in zip(x, w):
            r = mid + half * xi
            s += wi * half * A.hplus(r) * g(r) * mp.cos(L * r)
    # remainder beyond: integrand ~ h_+ g, bound it by direct numeric
    rem = A.tail_E1(R_head + npanels * T, g, 30)
    return s, rem


def main():
    c = 13
    print("=" * 96, flush=True)
    print("L1  HEAD: Gauss-Legendre order dependence   (n=1, R=1e4)")
    print("=" * 96, flush=True)
    for o in (8, 16, 32):
        head, E1, E2, E2d = build(c, 1, mp.mpf(10) ** 4, o)
        print("   GL%-3d  head = %s   E1 = %s   E2(IBP) = %s"
              % (o, mp.nstr(head, 15), mp.nstr(E1, 12), mp.nstr(E2, 12)), flush=True)
    print(flush=True)

    print("=" * 96, flush=True)
    print("L2  HEAD CUTOFF dependence   (n=1, GL16)")
    print("=" * 96, flush=True)
    for e in (3, 4, 5):
        head, E1, E2, E2d = build(c, 1, mp.mpf(10) ** e, 16)
        tot = head + E1 - E2
        print("   R=1e%d  head = %-16s E1 = %-14s E2 = %-14s head+E1-E2 = %s"
              % (e, mp.nstr(head, 14), mp.nstr(E1, 10), mp.nstr(E2, 10),
                 mp.nstr(tot, 15)), flush=True)
    print(flush=True)

    print("=" * 96, flush=True)
    print("L3  OSCILLATORY TAIL E2: two integrations by parts vs direct quadrature")
    print("=" * 96, flush=True)
    for e in (3, 4):
        head, E1, E2, E2d = build(c, 1, mp.mpf(10) ** e, 16)
        print("   R=1e%d  E2(IBP) = %s    E2(direct, 4000 panels) = %s  [bound %s]"
              % (e, mp.nstr(E2, 12), mp.nstr(E2d[0], 12), mp.nstr(E2d[1], 6)),
              flush=True)
    print(flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
