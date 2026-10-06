# -*- coding: utf-8 -*-
"""
WHERE DOES THE HEAD QUADRATURE ERROR LIVE?

After the tail is treated exactly (gw_tail_deep.py), the agreement between the
paper's closed form and the defining integral is limited solely by

      |GL64 - GL48|  =  2.8e-30 (dps 30)  /  2.3e-30 (dps 70)

for the head integral  int_0^R h_+(r) (1 - cos Lr) g(r) dr.
It does NOT shrink when the working precision is raised, so it is a property
of the quadrature, not of the arithmetic.

This script localises it:
  * accumulates the GL48 and GL64 contribution OF EVERY PANEL separately
  * ranks panels by |GL64 - GL48|
  * re-evaluates ONLY the worst panels at GL96 and GL128

Three outcomes, and they mean different things:

  CONVERGING : GL96 and GL128 keep moving towards one another and away from
               GL48/GL64  =>  raise the order and the identity verifies
               deeper; nothing is wrong, we were simply using too few nodes.
  SATURATED  : GL96 - GL64 stays at ~1e-30 regardless  =>  some feature of
               the integrand caps the accuracy and must be identified
               (the integrand has a zero/pole cancellation at r = rho*n
               inside the first panels).
  NOISY      : the panel differences scatter at the dps floor  =>  the number
               is arithmetic-limited after all.

Output is diagnostic only; no RH / Weil / prime-counting claim is involved.
"""

import sys
import time

import mpmath as mp

import gw_arch_check as GA


C = 13
N_IDX = 1
R = mp.mpf(10) ** 4


def head_panels(K, T, L, g, order):
    """per-panel contributions of the head integral at Gauss-Legendre `order`"""
    x, w = mp.gauss_quadrature(order, "legendre")
    out = []
    for k in range(K):
        a, b = k * T, (k + 1) * T
        half, mid = (b - a) / 2, (b + a) / 2
        acc = mp.mpf(0)
        for xi, wi in zip(x, w):
            r = mid + half * xi
            acc += wi * half * GA.hplus(r) * (1 - mp.cos(L * r)) * g(r)
        out.append(acc)
    return out


def main(argv):
    dps = int(argv[1]) if len(argv) > 1 else 30
    mp.mp.dps = dps
    L = mp.log(C)
    rho = 2 * mp.pi / L
    d = rho * N_IDX
    T = 2 * mp.pi / L
    K = int(mp.floor(R / T))
    pref = rho * N_IDX / (mp.pi ** 2)

    def g(r):
        return 1 / (r * r - d * d)

    print("#" * 100)
    print("# LOCALISING THE HEAD QUADRATURE ERROR   c = %d, n = %d, dps = %d"
          % (C, N_IDX, dps))
    print("# panels K = %d,  period T = %s,  pole of g at r = rho*n = %s"
          % (K, mp.nstr(T, 8), mp.nstr(d, 8)))
    print("#" * 100)
    print()

    t0 = time.time()
    p48 = head_panels(K, T, L, g, 48)
    print("  GL48  done  (%.1f s)" % (time.time() - t0))
    sys.stdout.flush()
    t0 = time.time()
    p64 = head_panels(K, T, L, g, 64)
    print("  GL64  done  (%.1f s)" % (time.time() - t0))
    sys.stdout.flush()

    s48 = mp.fsum(p48)
    s64 = mp.fsum(p64)
    diffs = [(abs(b - a), k) for k, (a, b) in enumerate(zip(p48, p64))]
    diffs.sort(reverse=True)

    print()
    print("  head(GL48) = %s" % mp.nstr(s48, 22))
    print("  head(GL64) = %s" % mp.nstr(s64, 22))
    print("  |GL64 - GL48| = %s      (this is the current verification floor)"
          % mp.nstr(abs(s64 - s48), 8))
    print()
    print("  worst panels by |GL64 - GL48|:")
    print("    rank   panel k     r-range                        "
          "|GL64-GL48|      share")
    print("    " + "-" * 88)
    cum = mp.mpf(0)
    for i, (dv, k) in enumerate(diffs[:8]):
        cum += dv
        print("    %-5d %-11d [%-13s, %-13s]  %-16s %s"
              % (i + 1, k, mp.nstr(k * T, 6), mp.nstr((k + 1) * T, 6),
                 mp.nstr(dv, 8),
                 mp.nstr(100 * dv / abs(s64 - s48), 4) + "%"
                 if s64 != s48 else "n/a"))
    print("    " + "-" * 88)
    print("    top 8 together account for %s of the total difference"
          % mp.nstr(100 * cum / abs(s64 - s48), 6) + "%")
    print()

    # ---- re-evaluate the worst panels at higher order ----------------------
    print("  re-evaluating the worst panels at higher order:")
    print("    panel k     GL48              GL64              GL96             "
          "GL128")
    print("    " + "-" * 92)
    for _, k in diffs[:6]:
        # recompute only this panel at higher order
        def panel(order, k=k):
            x, w = mp.gauss_quadrature(order, "legendre")
            a, b = k * T, (k + 1) * T
            half, mid = (b - a) / 2, (b + a) / 2
            acc = mp.mpf(0)
            for xi, wi in zip(x, w):
                r = mid + half * xi
                acc += wi * half * GA.hplus(r) * (1 - mp.cos(L * r)) * g(r)
            return acc
        v48, v64 = p48[k], p64[k]
        v96 = panel(96)
        v128 = panel(128)
        print("    %-11d %-17s %-17s %-17s %s"
              % (k, mp.nstr(v48, 8), mp.nstr(v64, 8), mp.nstr(v96, 8),
                 mp.nstr(v128, 8)))
        sys.stdout.flush()
    print()

    print("=" * 100)
    print("READING")
    print("=" * 100)
    print("  if GL96/GL128 keep converging, the identity verifies deeper simply")
    print("  by raising the order -- then gw_tail_deep.py should be re-run with")
    print("  that order as its head, and the achievable floor is set by dps.")
    print("  if they saturate near 1e-30, a feature of the integrand caps it and")
    print("  that feature must be named before ANY eigenvalue below that level")
    print("  can be called independently verified.")
    print()
    print("  no RH, Weil-positivity, prime-counting or factoring claim is")
    print("  involved; the source preprint disclaims all of those.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
