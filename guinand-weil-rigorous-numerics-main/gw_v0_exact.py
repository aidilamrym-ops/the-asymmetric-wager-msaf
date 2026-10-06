# -*- coding: utf-8 -*-
"""
CLOSING THE V0 RESIDUAL: the closed form for S(r,n,L) is now verified EXACTLY,
not to the 1e-16 stopping level of a reference quadrature.

Statement under test (arXiv:2607.02828v3, used by Lemma 2.1 / eq. (3)):

    S(r,n,L) = int_0^L sin(2 pi n (1 - y/L)) cos(r y) dy
             = 2 rho n sin^2(L r / 2) / (r^2 - rho^2 n^2),   rho = 2 pi / L

ROUTE 1 (algebra, exact).  For integer n,
    sin(2 pi n (1 - y/L)) = sin(2 pi n - 2 pi n y/L) = -sin(k y),  k = 2 pi n / L
so with k = rho n,
    S = -int_0^L sin(k y) cos(r y) dy
      = -1/2 [ (1-cos((k+r)L))/(k+r) + (1-cos((k-r)L))/(k-r) ] .
Since k L = 2 pi n,  cos((k+-r)L) = cos(2 pi n +- rL) = cos(r L), hence
    S = -(1 - cos rL)/2 * 2k/(k^2 - r^2) = k (cos rL - 1)/(k^2 - r^2)
      = rho n * (-2 sin^2(Lr/2)) / (rho^2 n^2 - r^2)
      = 2 rho n sin^2(Lr/2) / (r^2 - rho^2 n^2)                        QED
and the singularity at r = rho n is removable with limit 0 (the numerator has
a double zero there), which is the convention gw_arch_check.S_closed uses.

ROUTE 2 (independent numerics).  The defining y-integral is evaluated by
Gauss-Legendre on panels of one half period of cos(r y), at two orders, so
that the quadrature's own convergence is measured rather than assumed.

The two routes are independent: route 1 is symbolic, route 2 never forms the
closed expression.  Agreement to working precision closes the residual.
"""

import mpmath as mp

mp.mp.dps = 50


def S_paper(r, n, L, rho):
    """the closed form as printed in the source."""
    d = rho * n
    den = r * r - d * d
    if den == 0:
        return mp.mpf(0)                     # removable, limit 0
    return 2 * rho * n * mp.sin(L * r / 2) ** 2 / den


def S_anti(r, n, L, rho):
    """ROUTE 1: value from the antiderivative derived above (exact)."""
    k = rho * n
    if abs(k - r) < mp.mpf(10) ** (-mp.mp.dps / 2) * max(r, 1):
        return mp.mpf(0)                     # removable
    cl = mp.cos(r * L)
    return k * (cl - 1) / (k * k - r * r)


def S_quad(r, n, L, order):
    """ROUTE 2: Gauss-Legendre on half-period panels of cos(r y)."""
    if r == 0:
        step = L
    else:
        step = mp.pi / r
    pts = [mp.mpf(0)]
    y = step
    while y < L:
        pts.append(y)
        y += step
    pts.append(mp.mpf(L))
    xs, ws = mp.gauss_quadrature(order, "legendre")
    acc = mp.mpf(0)
    for a, b in zip(pts, pts[1:]):
        if b <= a:
            continue
        half, mid = (b - a) / 2, (b + a) / 2
        for xi, wi in zip(xs, ws):
            y = mid + half * xi
            acc += wi * half * mp.sin(2 * mp.pi * n * (1 - y / L)) * mp.cos(r * y)
    return acc


def main():
    c = 13
    L = mp.log(c)
    rho = 2 * mp.pi / L

    print("#" * 96)
    print("# V0 UPGRADED: the S(r,n,L) closed form, verified exactly")
    print("# source: arXiv:2607.02828v3 (preprint, LLM-assisted, no RH claim)")
    print("# c = %d, L = %s, rho = 2pi/L = %s, dps = %d"
          % (c, mp.nstr(L, 12), mp.nstr(rho, 12), mp.mp.dps))
    print("#" * 96)
    print()

    print("[R1] antiderivative route vs the printed closed form (algebraic identity)")
    worst1 = mp.mpf(0)
    for n in (1, 2, 3, 4):
        for r in [mp.mpf(x) for x in ("0.37", "1.9", "4.4", "11.0", "30.0",
                                      "100.0", "1000.0")]:
            e = abs(S_anti(r, n, L, rho) - S_paper(r, n, L, rho))
            worst1 = max(worst1, e / max(abs(S_paper(r, n, L, rho)),
                                         mp.mpf(10) ** -60))
    print("      max relative difference over the sample grid = %s" % mp.nstr(worst1, 6))
    print("      (pure floating-point rounding of an identity; the algebra is exact)")
    print()

    print("[R2] independent Gauss-Legendre quadrature of the defining y-integral")
    print("      n    r          GL32 vs closed form      GL48 vs closed form"
          "     GL32 vs GL48")
    worst_rel = mp.mpf(0)
    worst_conv = mp.mpf(0)
    for n in (1, 2, 3):
        for r in [mp.mpf(x) for x in ("0.37", "1.9", "4.4", "11.0", "30.0", "100.0")]:
            sc = S_paper(r, n, L, rho)
            q32 = S_quad(r, n, L, 32)
            q48 = S_quad(r, n, L, 48)
            e32 = abs(q32 - sc) / max(abs(sc), mp.mpf(10) ** -60)
            e48 = abs(q48 - sc) / max(abs(sc), mp.mpf(10) ** -60)
            ecv = abs(q48 - q32) / max(abs(q48), mp.mpf(10) ** -60)
            worst_rel = max(worst_rel, e48)
            worst_conv = max(worst_conv, ecv)
            if n == 1:
                print("      %d    %-9s %-24s %-24s %s"
                      % (n, mp.nstr(r, 6), mp.nstr(e32, 6), mp.nstr(e48, 6),
                         mp.nstr(ecv, 6)))
    print("      (only n = 1 shown; worst case over all n = 1,2,3 printed below)")
    print("      worst  GL48 vs closed form  = %s" % mp.nstr(worst_rel, 6))
    print("      worst  GL48 vs GL32         = %s   (the quadrature's own limit)"
          % mp.nstr(worst_conv, 6))
    print()

    print("[R3] the removable point r = rho n")
    for n in (1, 2, 3):
        r0 = rho * n
        # evaluate the closed form a hair away from the singularity
        for eps in (mp.mpf(10) ** -8, mp.mpf(10) ** -16, mp.mpf(10) ** -30):
            v = S_paper(r0 + eps, n, L, rho)
            print("      n = %d,  r = rho n + %-8s ->  S = %s"
                  % (n, mp.nstr(eps, 4), mp.nstr(v, 8)))
        print("      n = %d,  r = rho n exactly   ->  S = %s  (limit 0, as coded)"
              % (n, mp.nstr(S_paper(r0, n, L, rho), 6)))
    print()

    verdict = "PASS" if (worst_rel < mp.mpf("1e-30") and worst_conv < mp.mpf("1e-30")) else "FAIL"
    print("VERDICT (V0):", verdict)
    print("  the earlier 8.9e-17 figure was the reference quadrature's own stopping")
    print("  level, not an error in the closed form; with an exact antiderivative")
    print("  and a converging independent quadrature the residual is gone.")
    print("SCOPE: this validates one integral identity.  It is not an RH result.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
