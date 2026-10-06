# -*- coding: utf-8 -*-
"""Per-panel diagnostic for the psi' (dpsi) archimedean head.

Motivation
----------
The dpsi identity residual at (c, N) has been observed to be INVARIANT
under Gauss-Legendre order: raising the order from 160 to 224 left the
residual at 3.3911092e-102 to eight significant digits, while over the
same change the psi residual moved 5.26e-127 -> 9.38e-140.  A quantity
that does not move when the quadrature order moves is not limited by the
quadrature order, so the error class must be found by localisation.

What this script does
---------------------
  (a) computes every head panel independently at each requested order;
  (b) ranks panels by |panel(hi) - panel(lo)|;
  (c) re-integrates the largest movers at an even higher GL order, but
      ONLY on those panels, so the cost stays bounded;
  (d) re-integrates the largest movers with an INDEPENDENT rule
      (mp.quad, tanh-sinh) so the comparison is not GL-versus-GL;
  (e) assembles the full residual pref*(head + E1 - E2) - closed for
      every order actually computed.

Read-only with respect to every other file; writes nothing but stdout.

usage: python gw_panel_diag.py <c> <N> <dps> <R_cut> <order_lo,order_hi> [n_top] [n_quad] [order_top]
example: python gw_panel_diag.py 100 40 140 1000 96,224 25 12 360
"""
import sys
import time

import mpmath as mp

import gw_arch_check as GA
import gw_tail_deep as TD

JMAX = 46          # IBP pairs, matched to the identity run under diagnosis


def head_order(K, T, L, g, order, k0=0, k1=None):
    """Per-panel contributions at one order, k0 <= k < k1."""
    return TD.head_panels(K, T, L, g, order, k0, k1)


def main(argv):
    c = int(argv[1])
    N = int(argv[2])
    dps = int(argv[3])
    R_cut = mp.mpf(argv[4])
    order_lo, order_hi = [int(v) for v in argv[5].split(',')]
    n_top = int(argv[6]) if len(argv) > 6 else 25
    n_quad = int(argv[7]) if len(argv) > 7 else 12
    order_top = int(argv[8]) if len(argv) > 8 else 0

    mp.mp.dps = dps
    L = mp.log(c)
    rho = 2 * mp.pi / L
    T = 2 * mp.pi / L
    K = int(mp.floor(R_cut / T))
    R_head = K * T
    d = rho * N
    g, gk = TD.make_g('dpsi', d)
    pref = rho / mp.pi ** 2

    print("=" * 100)
    print("# PER-PANEL DIAGNOSTIC: which head panel carries the psi' residual?")
    print("# c = %d, N = %d, dps = %d, R = %s, K = %d panels, IBP pairs <= %d"
          % (c, N, dps, mp.nstr(R_cut, 6), K, JMAX))
    print("# orders lo = %d, hi = %d, top = %d, quad top = %d"
          % (order_lo, order_hi, order_top, n_quad))
    print("# pole of g at r = d = %s  (= %s * T), panel edge %d*T"
          % (mp.nstr(d, 15), mp.nstr(d / T, 12), int(mp.nint(d / T))))
    print("=" * 100, flush=True)

    # ---- (a) full head at both requested orders ----------------------------
    sums, panels = {}, {}
    for o in (order_lo, order_hi):
        t0 = time.time()
        p = head_order(K, T, L, g, o)
        panels[o] = p
        sums[o] = mp.fsum(p)
        print("  head at order %4d : %7.1f s   sum = %s"
              % (o, time.time() - t0, mp.nstr(sums[o], 40)), flush=True)
    print("  |sum(hi) - sum(lo)| = %s" % mp.nstr(abs(sums[order_hi] - sums[order_lo]), 14))
    print("", flush=True)

    # ---- (b) rank the movers ----------------------------------------------
    diffs = sorted(
        ((abs(panels[order_hi][k] - panels[order_lo][k]), k) for k in range(K)),
        reverse=True)
    print("-" * 100)
    print("TOP %d PANELS BY |panel(%d) - panel(%d)|" % (min(n_top, K), order_hi, order_lo))
    print("-" * 100)
    print("   k        panel range                 |diff|            share of |sum diff|")
    tot_move = mp.fsum(x[0] for x in diffs) or mp.mpf(1)
    cum = mp.mpf(0)
    for dk, (mv, k) in enumerate(diffs[:n_top]):
        cum += mv
        print("  %4d  [%10.5f, %10.5f]   %-16s cum %s%%"
              % (k, k * T, (k + 1) * T, mp.nstr(mv, 12),
                 mp.nstr(100 * cum / tot_move, 6)))
    print("  (total movement over all %d panels = %s)"
          % (K, mp.nstr(tot_move, 14)))
    print("", flush=True)

    # ---- (c) highest order, but only on the movers -------------------------
    pt = None
    idx = []
    if order_top:
        idx = [k for _, k in diffs[:max(n_top, 50)]]
        lo_i, hi_i = min(idx), max(idx) + 1
        t0 = time.time()
        pt = head_order(K, T, L, g, order_top, lo_i, hi_i)
        print("-" * 100)
        print("HIGHER ORDER %d restricted to panels %d..%d (%.1f s)"
              % (order_top, lo_i, hi_i - 1, time.time() - t0))
        print("-" * 100)
        moved = sorted(((abs(pt[k - lo_i] - panels[order_hi][k]), k)
                        for k in idx), reverse=True)
        print("  max |panel(%d) - panel(%d)| over those panels = %s"
              % (order_top, order_hi, mp.nstr(moved[0][0], 14)))
        print("  top movers:")
        for mv, k in moved[:8]:
            print("    k=%4d  %s" % (k, mp.nstr(mv, 14)))
        print("", flush=True)

    # ---- (d) independent rule on the biggest movers ------------------------
    print("-" * 100)
    print("INDEPENDENT RE-INTEGRATION (mp.quad) ON THE %d BIGGEST MOVERS" % n_quad)
    print("-" * 100)
    f = lambda r: GA.hplus(r) * (1 - mp.cos(L * r)) * g(r)
    quad_shift = mp.mpf(0)
    for _, k in diffs[:n_quad]:
        a, b = k * T, (k + 1) * T
        t0 = time.time()
        q = mp.quad(f, [a, (a + b) / 2, b])
        gl_hi = panels[order_hi][k]
        gl_lo = panels[order_lo][k]
        quad_shift += (q - gl_hi)
        print("  k=%4d  quad = %s\n          GL%-4d = %s   d=%s   |quad-GL%d| = %s   (%.1fs)"
              % (k, mp.nstr(q, 22), order_hi, mp.nstr(gl_hi, 22),
                 mp.nstr(q - gl_hi, 6), order_hi, mp.nstr(abs(q - gl_hi), 10),
                 time.time() - t0), flush=True)
    print("  --> sum over movers of (quad - GL%d) = %s" % (order_hi, mp.nstr(quad_shift, 14)))
    print("      that would move the TOTAL head by that amount.", flush=True)
    print("", flush=True)

    # ---- (e) full residual at every order computed -------------------------
    print("-" * 100)
    print("FULL RESIDUAL  |pref*(head + E1 - E2) - closed|")
    print("-" * 100)
    E1 = GA.tail_E1(R_head, g, dps)
    E2, last, n_terms, turned = TD.E2_deep(g, gk, L, R_head, JMAX)
    closed = TD.closed_dpsi(N, L)
    print("  E1        = %s" % mp.nstr(E1, 34))
    print("  E2 (%d pairs, last %s, turned=%s) = %s"
          % (n_terms, mp.nstr(last, 8), turned, mp.nstr(E2, 34)))
    print("  closed    = %s" % mp.nstr(closed, 34))
    print("  lambda_min target = 1.32105051975e-102")
    print("")
    for o in sorted(sums):
        tot = pref * (sums[o] + E1 - E2)
        print("  order %4d : head = %s\n             residual = %s"
              % (o, mp.nstr(sums[o], 34), mp.nstr(abs(tot - closed), 14)))
    if pt is not None and idx:
        shift = mp.fsum(pt) - mp.fsum(panels[order_hi][k] for k in idx)
        tot = pref * (sums[order_hi] + shift + E1 - E2)
        print("  order %4d (restricted top set replaced) : residual = %s"
              % (order_top, mp.nstr(abs(tot - closed), 14)))
    print("=" * 100)


if __name__ == "__main__":
    main(sys.argv)
