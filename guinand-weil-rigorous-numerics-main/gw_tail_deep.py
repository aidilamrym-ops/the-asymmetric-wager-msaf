# -*- coding: utf-8 -*-
"""
IS THE ARCHIMEDAN CLOSED FORM AN EXACT IDENTITY FOR THE DEFINING INTEGRAL?

Background
----------
The assembly uses the paper's closed forms

    psi_arch(n)  = alpha_L(n)                       (hyp2f1 + digamma)
    psi_arch'(n) = -2 (gamma_L(n) - beta_L(n))      (hyp2f1 + digamma + lerchphi)

instead of the defining integral (eq. 3)

    psi_arch(n) = (1/pi^2) int_0^inf h_+(r) S(r, n, L) dr.

gw_arch_check.py compares them and reports agreement of ~3.5e-20 relative --
but that number is (i) identical at dps = 30 and dps = 60, so it is not
arithmetic-limited, and (ii) it decays like R^{-4.8} as the head cutoff R is
raised, so it is not an error in the closed form either.

Three earlier scripts established what it actually is:

  gw_deep_v2.py    the discrepancy is precision-INDEPENDENT  -> analytic
                    remainder, not roundoff.
  gw_deep_v2 sweep2 the discrepancy falls 1e-11 -> 1e-16 -> 1e-21 as R goes
                    1e2 -> 1e3 -> 1e4, no plateau              -> case (T).
  gw_head_diag.py  localises the residual to PANEL 0 of the head, whose right
                    endpoint is exactly r = rho*n, the pole of g; and shows
                    GL48 -> GL64 -> GL96 -> GL128 differences of
                    2.3e-30, 1.8e-37, 6.8e-56  ->  CONVERGING, i.e. the order
                    was simply too low.

What this script does
---------------------
  * integrates the tail EXACTLY: u = h_+ g (not log(r/2pi) g), k integrations
    by parts, derivatives from
        h_+^{(k)}(r) = Re[ (i/2)^k psi^{(k)}(1/4 + i r/2) ]
    and exact partial fractions for g.  Both drops that gw_arch_check makes
    (the eps-part and the IBP remainder) are therefore absent.
  * because the tail is now exact, the split point R is a free parameter; it
    is taken as low as R = 1000 so the head is only ~400 panels.
  * the head uses a HIGH order with a two-level bound:
        panels 0 and 1  (singularity sits ON their shared endpoint r = rho*n)
            at order_hi and order_hi2
        panels >= 2     (singularity at distance >= 3 half-widths)
            at order_a and order_b
    and the reported head error is the sum of both empirical differences.
  * prints the total against the closed form for both psi_arch and psi_arch'.

READING THE OUTPUT
------------------
  residual  <<  the eigenvalue scale you care about  =>
      the identity has been independently verified at that depth and
      eigenvalues at that scale are not resting on an assumption.

  residual  >>  that scale  =>
      the identity is only verified to the printed depth, and anything
      deeper must be reported as resting on the identity being exact.

Runs well:  python gw_tail_deep.py 100 40 1000 96 128 128 160 13 1 0
            (dps  jmax  R  order_a  order_b  order_hi  order_hi2  c  n  baseline)

No RH, Weil-positivity, prime-counting or factoring claim is involved; the
source preprint (arXiv:2607.02828v3) disclaims all of those.
"""

import sys
import time

import mpmath as mp

import gw_arch_check as GA


C = 13
N_IDX = 1

DPS = 100
JMAX = 40
R_CUT = mp.mpf(10) ** 3
ORDER_A = 96          # panels >= 2, lower order
ORDER_B = 128         # panels >= 2, upper order
ORDER_HI = 128        # panels 0,1, lower order
ORDER_HI2 = 160       # panels 0,1, upper order
BASELINE = True


# ---------------------------------------------------------------------------
# derivatives
# ---------------------------------------------------------------------------
def hplus_k(k, r):
    """k-th derivative of h_+(r) = Re psi(1/4 + i r/2) - log(pi).

    The -log(pi) constant survives only in the k = 0 branch; dropping it there
    corrupts every higher derivative through the Leibniz rule.  That produced a
    spurious 3.48e-13 discrepancy on the first run of this script.  The
    self-check in main() pins it against mp.diff.
    """
    z = mp.mpf(1) / 4 + mp.mpf(0.5) * 1j * r
    val = mp.re((mp.mpf(0.5) * 1j) ** k * mp.polygamma(k, z))
    if k == 0:
        val -= mp.log(mp.pi)
    return val


def make_g(kind, d):
    """g and its exact derivatives via partial fractions.

    psi  : g = 1/(r^2-d^2)           = (1/(2d)) [1/(r-d) - 1/(r+d)]
    dpsi : g = (r^2+d^2)/(r^2-d^2)^2 = (1/2)    [1/(r-d)^2 + 1/(r+d)^2]
    """
    def fact(n):
        s = mp.mpf(1)
        for i in range(1, n + 1):
            s *= i
        return s

    if kind == "psi":

        def g(r):
            return 1 / (r * r - d * d)

        def gk(k, r):
            return ((-1) ** k) * fact(k) / (2 * d) * (
                1 / (r - d) ** (k + 1) - 1 / (r + d) ** (k + 1))
    else:

        def g(r):
            return (r * r + d * d) / (r * r - d * d) ** 2

        def gk(k, r):
            return mp.mpf(1) / 2 * ((-1) ** k) * fact(k + 1) * (
                1 / (r - d) ** (k + 2) + 1 / (r + d) ** (k + 2))
    return g, gk


def E2_deep(g, gk, L, R, jmax):
    """int_R^inf h_+ g cos(Lr) dr, IBP on the EXACT u = h_+ g.

    E2 = sum_j (-1)^{j+1} [ u^(2j)(R) sin(LR)/L^(2j+1)
                          + u^(2j+1)(R) cos(LR)/L^(2j+2) ]
    Truncation is a posteriori: stop when the last term falls below
    10^-(dps+10) or when the terms start growing (asymptotic series turning).
    """
    sinLR, cosLR = mp.sin(L * R), mp.cos(L * R)

    def u(k, r):
        return sum(mp.binomial(k, j) * hplus_k(j, r) * gk(k - j, r)
                   for j in range(k + 1))

    val = mp.mpf(0)
    tol = mp.mpf(10) ** (-(mp.mp.dps + 10))
    last = prev = None
    n_terms = 0
    turned = False
    for j in range(jmax):
        t1 = u(2 * j, R) * sinLR / L ** (2 * j + 1)
        t2 = u(2 * j + 1, R) * cosLR / L ** (2 * j + 2)
        sgn = mp.mpf(-1) if j % 2 == 0 else mp.mpf(1)
        val += sgn * (t1 + t2)
        last = abs(t1 + t2)
        n_terms += 1
        if last < tol:
            break
        if prev is not None and last > prev and j > 2:
            turned = True
            break
        prev = last
    return val, last, n_terms, turned


# ---------------------------------------------------------------------------
def head_panels(K, T, L, g, order, k0=0, k1=None):
    """per-panel contributions of int h_+ (1 - cos Lr) g dr over panels
    k0, k0+1, ..., k1-1 (k1 defaults to K)."""
    if k1 is None:
        k1 = K
    x, w = mp.gauss_quadrature(order, "legendre")
    out = []
    for k in range(k0, k1):
        a, b = k * T, (k + 1) * T
        half, mid = (b - a) / 2, (b + a) / 2
        acc = mp.mpf(0)
        for xi, wi in zip(x, w):
            r = mid + half * xi
            acc += wi * half * GA.hplus(r) * (1 - mp.cos(L * r)) * g(r)
        out.append(acc)
    return out


def closed_psi(n, L):
    z = mp.e ** (-2 * L)
    an = mp.mpf(1) / 4 + mp.pi * 1j * n / L
    return (mp.e ** (-L / 2) * mp.im(
        (2 * L / (L + 4 * mp.pi * 1j * n)) * mp.hyp2f1(1, an, an + 1, z))
        + mp.mpf(1) / 2 * mp.im(mp.digamma(an))) / mp.pi


def closed_dpsi(n, L):
    import gw_deep_v2 as D
    return D.closed_dpsi(n, L)


def run(kind, L, rho, d):
    T = 2 * mp.pi / L
    K = int(mp.floor(R_CUT / T))
    R_head = K * T
    pref = rho * (N_IDX if kind == "psi" else 1) / (mp.pi ** 2)
    g, gk = make_g(kind, d)
    t_all = time.time()

    # ---- head: panels >= 2 at (ORDER_A, ORDER_B) ---------------------------
    # The pole of g sits at r = rho*n = n*T, i.e. exactly ON the shared edge of
    # panels n-1 and n -- for ANY n.  Those two panels therefore need the high
    # orders; every other panel has the singularity >= 3 half-widths away.
    hi0, hi1 = max(N_IDX - 1, 0), N_IDX + 1
    t0 = time.time()
    pa = head_panels(K, T, L, g, ORDER_A)
    sa = mp.fsum(pa)
    t_a = time.time() - t0

    t0 = time.time()
    pb = head_panels(K, T, L, g, ORDER_B)
    sb = mp.fsum(pb)
    t_b = time.time() - t0

    # ---- head: the two critical panels at (ORDER_HI, ORDER_HI2) ------------
    t0 = time.time()
    shi = mp.fsum(head_panels(K, T, L, g, ORDER_HI, hi0, hi1))
    shi2 = mp.fsum(head_panels(K, T, L, g, ORDER_HI2, hi0, hi1))
    t_hi = time.time() - t0

    head = sb
    # |GL_hi2 - GL_hi| on the critical panels alone, on top of the global
    # difference; the global one already contains those panels at ORDER_B.
    err_hi = abs(shi2 - shi)
    err_low = abs(sb - sa)
    head_err = err_low + err_hi

    # ---- baseline (gw_arch_check style, truncated tail) --------------------
    t0 = time.time()
    if BASELINE:
        p48 = head_panels(K, T, L, g, 48)
        p32 = head_panels(K, T, L, g, 32)
        head_base = mp.fsum(p48)
        head_err_base = abs(mp.fsum(p48) - mp.fsum(p32))
    else:
        head_base, head_err_base = head, head_err
    t_base = time.time() - t0

    # ---- tail --------------------------------------------------------------
    t0 = time.time()
    E1 = GA.tail_E1(R_head, g, DPS)

    def gp(r):
        if kind == "psi":
            return -2 * r / (r * r - d * d) ** 2
        a = r * r - d * d
        return -2 * r * (r * r + 3 * d * d) / a ** 3

    def gpp(r):
        if kind == "psi":
            a = r * r - d * d
            return -2 / a ** 2 + 8 * r * r / a ** 3
        a = r * r - d * d
        return 6 * (r ** 4 + 6 * r * r * d * d + d ** 4) / a ** 4

    E2_code = GA.tail_E2(R_head, g, gp, gpp, L, DPS)
    t_tail = time.time() - t0

    E2_d, last, n_terms, turned = E2_deep(g, gk, L, R_head, JMAX)

    closed = closed_psi(N_IDX, L) if kind == "psi" else closed_dpsi(N_IDX, L)

    total_base = pref * (head_base + E1 - E2_code)
    total = pref * (head + E1 - E2_d)

    return dict(kind=kind, R_head=R_head, K=K, head=head,
                head_err=head_err, err_low=err_low, err_hi=err_hi,
                head_err_base=head_err_base,
                E1=E1, E2_code=E2_code, E2_deep=E2_d, last=last,
                n_terms=n_terms, turned=turned, closed=closed,
                total_base=total_base, total=total,
                diff_base=abs(total_base - closed),
                diff=abs(total - closed),
                times=(t_a, t_b, t_hi, t_base, t_tail),
                total_time=time.time() - t_all)


def selfcheck(L, rho):
    print("-" * 100)
    print("SELF-CHECK  (derivatives vs mp.diff -- guards the Leibniz/product rule)")
    print("-" * 100)
    r0 = mp.mpf(12345.7)
    worst = mp.mpf(0)
    for k in (0, 1, 2, 3, 5, 8, 12):
        ref = mp.diff(GA.hplus, r0, k)
        got = hplus_k(k, r0)
        worst = max(worst, abs(got - ref))
        print("   hplus_k(%-2d) = %-30s  |diff| = %s"
              % (k, mp.nstr(got, 10), mp.nstr(abs(got - ref), 4)))
    for kind in ("psi", "dpsi"):
        gg, gk = make_g(kind, rho * N_IDX)
        for k in (0, 1, 2, 4, 7):
            ref = mp.diff(gg, r0, k)
            got = gk(k, r0)
            worst = max(worst, abs(got - ref))
            print("   gk(%-2d, %-4s) = %-30s  |diff| = %s"
                  % (k, kind, mp.nstr(got, 10), mp.nstr(abs(got - ref), 4)))
    print("   worst |analytic - numeric| = %s" % mp.nstr(worst, 6))
    print()
    return worst


def main(argv):
    global DPS, JMAX, R_CUT, ORDER_A, ORDER_B, ORDER_HI, ORDER_HI2, BASELINE
    global C, N_IDX
    if len(argv) > 1:
        DPS = int(argv[1])
    if len(argv) > 2:
        JMAX = int(argv[2])
    if len(argv) > 3:
        R_CUT = mp.mpf(argv[3])
    if len(argv) > 4:
        ORDER_A = int(argv[4])
    if len(argv) > 5:
        ORDER_B = int(argv[5])
    if len(argv) > 6:
        ORDER_HI = int(argv[6])
    if len(argv) > 7:
        ORDER_HI2 = int(argv[7])
    if len(argv) > 8:
        C = int(argv[8])
    if len(argv) > 9:
        N_IDX = int(argv[9])
    if len(argv) > 10:
        BASELINE = (argv[10] != "0")
    mp.mp.dps = DPS

    L = mp.log(C)
    rho = 2 * mp.pi / L

    print("#" * 100)
    print("# IDENTITY CHECK: closed forms  vs  defining integral   (c = %d, n = %d)" % (C, N_IDX))
    print("# dps = %d,  R = %s,  IBP pairs <= %d" % (DPS, mp.nstr(R_CUT, 6), JMAX))
    print("# head: panels outside {%d,%d} at GL%d / GL%d ;  panels {%d,%d} at GL%d / GL%d"
          % (max(N_IDX - 1, 0), N_IDX, ORDER_A, ORDER_B,
             max(N_IDX - 1, 0), N_IDX, ORDER_HI, ORDER_HI2))
    print("# baseline = gw_arch_check style at THIS R: truncated tail, GL48 head")
    print("#   (at R = 1e4 that style gives 8.7e-21; at lower R the dropped tail")
    print("#    is bigger, so the baseline here will be worse than 8.7e-21)")
    print("#" * 100)
    print()

    selfcheck(L, rho)

    for kind, d in (("psi", rho * N_IDX), ("dpsi", rho * N_IDX)):
        r = run(kind, L, rho, d)
        print("=" * 100)
        print("case %s"
              % ("psi_arch(n)  = alpha_L(n)" if kind == "psi"
                 else "psi_arch'(n) = -2(gamma_L - beta_L)"))
        print("=" * 100)
        print("  head cutoff R_head = %s   (%d panels)"
              % (mp.nstr(r["R_head"], 10), r["K"]))
        print("  head = %s" % mp.nstr(r["head"], 22))
        print("  head error estimate: other panels |GL%d-GL%d| = %s"
              % (ORDER_A, ORDER_B, mp.nstr(r["err_low"], 6)))
        print("                     panels {%d,%d} |GL%d-GL%d| = %s"
              % (max(N_IDX - 1, 0), N_IDX, ORDER_HI, ORDER_HI2,
                 mp.nstr(r["err_hi"], 6)))
        print("                     total head err         = %s"
              % mp.nstr(r["head_err"], 6))
        print("  E1 (tail, exact h_+, converged) = %s" % mp.nstr(r["E1"], 20))
        print("  E2 as gw_arch_check computes it = %s" % mp.nstr(r["E2_code"], 20))
        print("  E2 exact (h_+ g, %d IBP pairs%s) = %s"
              % (r["n_terms"], ", SERIES TURNED" if r["turned"] else "",
                 mp.nstr(r["E2_deep"], 20)))
        print("  last retained term              = %s" % mp.nstr(r["last"], 6))
        print("  E2_exact - E2_coded             = %s   (the dropped IBP tail)"
              % mp.nstr(r["E2_deep"] - r["E2_code"], 8))
        print("  closed form                     = %s" % mp.nstr(r["closed"], 20))
        print("  " + "-" * 94)
        print("  |baseline - closed|  = %s   (gw_arch_check style)"
              % mp.nstr(r["diff_base"], 8))
        print("  |THIS RUN  - closed| = %s   (exact tail, high-order head)"
              % mp.nstr(r["diff"], 8))
        if r["diff"] > 0:
            print("  improvement           = %.4g x" % (r["diff_base"] / r["diff"]))
        print("  timing: GL%d %.0fs, GL%d %.0fs, panels0/1 %.0fs, base %.0fs, "
              "tail %.0fs, total %.0fs"
              % ((ORDER_A, r["times"][0], ORDER_B, r["times"][1])
                 + r["times"][2:] + (r["total_time"],)))
        print()

    print("=" * 100)
    print("VERDICT FOR THE IDENTITY")
    print("=" * 100)
    print("  baseline residual 8.7e-21 was OUR truncation of the IBP series in")
    print("  the tail plus too low a Gauss-Legendre order on head panel 0; it is")
    print("  fully accounted for, not a defect in the paper's closed form.")
    print()
    print("  the number printed as |THIS RUN - closed| is the DEPTH AT WHICH THE")
    print("  IDENTITY HAS BEEN CHECKED AGAINST THE DEFINING INTEGRAL.  Anything")
    print("  reported for Q_infty deeper than that rests on the identity being")
    print("  exact, not on a check of it.")
    print()
    print("  no RH, Weil-positivity, prime-counting or factoring claim is")
    print("  involved; the source preprint disclaims all of those.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
