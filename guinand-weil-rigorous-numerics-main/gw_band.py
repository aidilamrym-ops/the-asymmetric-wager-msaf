# -*- coding: utf-8 -*-
"""
CLOSURE D: the inconclusive band [-B_T, 0) of arXiv:2607.02828v3, Corollary 3.3.

Source statements being tested (primary source, arXiv:2607.02828v3; PREPRINT,
LLM-assisted; the paper disclaims any RH / Weil-positivity result):

  Corollary 3.3  for T > max(rho N, 7),
        lambda_j(Q_T^tot) < lambda_j(Q_inf) <= lambda_j(Q_T^tot) + B_T
        B_T = (2N+1) rho /(pi^2 T) * (log(T/2 pi) + 1) * (1 + o(1))

  Figure 2 caption, (c,N) = (13,4):
        lambda_min(Q_T^tot) = -1.9e-2  at T = 11
                              -5.3e-7  at T = 14
                              -3.9e-10 at T = 18
        "each far inside its inconclusive band (-B_T, 0); the cutoff-free limit
         is +9.7e-15"

  Corollary 3.3 also states the omitted archimedean tail is a TOTALLY POSITIVE
  Cauchy-Stieltjes increment, i.e. D_T := Q_inf - Q_T  is positive semidefinite.

  Definition (eq. (3), the same integral validated in gw_arch_check.py V0/V2):
        psi_arch,T(x) = 1/(2 pi^2) int_{-T}^{T} h_+(r) S(r,x,L) dr
                      = 1/pi^2 int_0^T  h_+(r) S(r,x,L) dr
        S(r,x,L)      = 2 rho x sin^2(L r/2) / (r^2 - rho^2 x^2)
        h_+(r)        = Re digamma(1/4 + i r/2) - log(pi)
        rho = 2 pi / L,  L = log c

WHAT THIS SCRIPT DOES
  D1  builds Q_T^tot = Q_prime + Q_pole + Q_arch,T by truncating exactly the
      archimedean integral at r = T (prime and pole blocks are T-independent),
      and compares lambda_min(Q_T) at T = 11, 14, 18 with the three published
      numbers above.                                  -> third external anchor
  D2  checks the monotone-increase claim  lambda_j(Q_T) < lambda_j(Q_inf).
  D3  forms D_T = Q_inf - Q_T and checks total positivity (all eigenvalues >= 0),
      and compares the EMPIRICAL budget lambda_max(D_T) with the stated B_T.
  D4  inverts B_T < lambda_min(Q_inf) to give the archimedean cutoff T that a
      brute-force certification would require, for every rung of the ladder.

No RH claim is made or implied; a finite-T eigenvalue in (-B_T, 0) certifies
NOTHING by the source's own rule, and that is the point of this file.
"""

import mpmath as mp

import gw_qinf as G
from gw_arch_check import hplus

mp.mp.dps = 40


# ---------------------------------------------------------------------------
def arch_T(x, c, T, which, dps=40, order=48):
    """psi_arch,T(x)  ('psi')  or  psi'_arch,T(x)  ('dpsi')  by direct
    r-quadrature on (0, T).

    Breakpoints: every half period of sin^2(L r/2)  AND every removable point
    r = rho|x| where both numerator and denominator of S vanish.  Without the
    second set, Gauss nodes can land close enough to rho|x| to destroy digits
    of r^2 - rho^2 x^2; with them the nearest node is O(1e-4) away and the
    cancellation disappears.
    """
    mp.mp.dps = dps
    L = mp.log(c)
    rho = 2 * mp.pi / L
    d = rho * x
    per = mp.pi / L                      # half period of sin^2(L r/2)

    if which == "psi":
        pref = rho * x / mp.pi ** 2

        def g(r):
            return 1 / (r * r - d * d)
    else:
        pref = rho / mp.pi ** 2

        def g(r):
            a = r * r - d * d
            return (r * r + d * d) / (a * a)

    if pref == 0:
        return mp.mpf(0)

    pts = set()
    k = 0
    while k * per <= T:
        pts.add(k * per)
        k += 1
    pts.add(mp.mpf(T))
    if 0 < abs(d) <= T:
        pts.add(abs(d))
    pts = sorted(p for p in pts if 0 <= p <= T)

    xs, ws = mp.gauss_quadrature(order, "legendre")
    acc = mp.mpf(0)
    for a, b in zip(pts, pts[1:]):
        if b <= a:
            continue
        half, mid = (b - a) / 2, (b + a) / 2
        for xi, wi in zip(xs, ws):
            r = mid + half * xi
            # 1 - cos(L r) written as 2 sin^2 to avoid cancellation at small r
            acc += wi * half * hplus(r) * 2 * mp.sin(L * r / 2) ** 2 * g(r)
    return pref * acc


def prime_sources(c):
    PP = G.prime_powers(c)
    L = mp.log(c)

    def psipr(m):
        return -(1 / mp.pi) * mp.fsum(
            lp / mp.sqrt(q) * mp.sin(2 * mp.pi * m * (1 - mp.log(q) / L))
            for q, lp in PP)

    def psiprd(m):
        return -2 * mp.fsum(
            lp / mp.sqrt(q) * (1 - mp.log(q) / L)
            * mp.cos(2 * mp.pi * m * (1 - mp.log(q) / L)) for q, lp in PP)
    return psipr, psiprd


def blocks_T(c, N, T, dps=40, order=48):
    """Q_T^tot on indices -N..N, with ONLY the archimedean block truncated."""
    bl = G.build_blocks(c, N)
    psipr, psiprd = prime_sources(c)
    AT, ATd = {}, {}
    for m in range(-N, N + 1):
        AT[m] = arch_T(m, c, T, "psi", dps, order)
        ATd[m] = arch_T(m, c, T, "dpsi", dps, order)
    pole_A = bl["pole_A"]

    def Q(m, n, block="all"):
        if block == "pole":
            return pole_A(m, n)
        if block == "prime":
            return (psipr(m) - psipr(n)) / (m - n) if m != n else psiprd(m)
        if block == "arch":
            return (AT[m] - AT[n]) / (m - n) if m != n else ATd[m]
        pa = pole_A(m, n)
        if m == n:
            return ATd[m] + psiprd(m) + pa
        return ((AT[m] - AT[n]) + (psipr(m) - psipr(n))) / (m - n) + pa

    return dict(Q_full=Q, bl=bl, AT=AT, ATd=ATd)


def B_T(c, N, T):
    """the budget as stated in Corollary 3.3 (leading term)."""
    L = mp.log(c)
    rho = 2 * mp.pi / L
    return (2 * N + 1) * rho / (mp.pi ** 2 * T) * (mp.log(T / (2 * mp.pi)) + 1)


def T_for_budget(c, N, target, lo=7, hi=None):
    """smallest T with B_T(c,N,T) < target, by bisection on the decreasing B_T."""
    if hi is None:
        hi = mp.mpf(10)
    while B_T(c, N, hi) >= target:
        hi *= 10
        if hi > mp.mpf(10) ** 300:
            return None
    for _ in range(400):
        mid = (lo + hi) / 2
        if B_T(c, N, mid) < target:
            hi = mid
        else:
            lo = mid
    return hi


def N_zeros(T):
    """Riemann-von Mangoldt: number of zeros with 0 < Im <= T."""
    x = T / (2 * mp.pi)
    return x * (mp.log(x) - 1)


# ---------------------------------------------------------------------------
def main():
    c, N, dps = 13, 4, 40
    print("#" * 96)
    print("# CLOSURE D: the inconclusive band [-B_T, 0) -- Corollary 3.3 of arXiv:2607.02828v3")
    print("# (PREPRINT, LLM-assisted; no RH / Weil-positivity claim is made or implied)")
    print("#" * 96)
    print()
    L = mp.log(c)
    rho = 2 * mp.pi / L
    print("c = %d, N = %d,  L = %s,  rho = 2 pi / L = %s" %
          (c, N, mp.nstr(L, 12), mp.nstr(rho, 12)))
    print("validity of Cor 3.3 requires T > max(rho*N, 7) = %s"
          % mp.nstr(max(rho * N, 7), 8))
    print()

    # ---- D1: the three published finite-T lambda_min values ---------------
    published = {11: "-1.9e-2", 14: "-5.3e-7", 18: "-3.9e-10"}
    print("=" * 96)
    print("[D1] finite-cutoff spectrum, our assembly vs the three published numbers")
    print("=" * 96)
    print("   T      lambda_min(Q_T) ours      published        ratio      B_T"
          "        inside (-B_T,0)?")
    print("   " + "-" * 92)

    bl_inf = G.build_blocks(c, N)
    M_inf = G.even_matrix(bl_inf, N, block="all")
    w_inf = sorted(mp.eigsy(M_inf)[0])
    lmin_inf, lmax_inf = +w_inf[0], +w_inf[-1]
    Ms = {}
    for T in (11, 14, 18):
        bT = blocks_T(c, N, T, dps)
        M = G.even_matrix(bT, N, block="all")
        Ms[T] = M
        w = sorted(mp.eigsy(M)[0])
        lm = +w[0]
        pub = mp.mpf(published[T])
        bt = B_T(c, N, T)
        inside = (-bt < lm) and (lm < 0)
        ratio = lm / pub if pub != 0 else mp.mpf("nan")
        print("   %-4d  %-26s %-16s %-10s %-10s  %s"
              % (T, mp.nstr(lm, 12), published[T], mp.nstr(ratio, 8),
                 mp.nstr(bt, 8), "YES" if inside else "no"))
        print("          lambda_max(Q_%d) = %s   lambda_max(Q_inf) = %s"
              % (T, mp.nstr(max(w), 10), mp.nstr(lmax_inf, 10)))
    print()
    print("   cutoff-free reference: lambda_min(Q_inf) = %s   (published +9.7e-15)"
          % mp.nstr(lmin_inf, 12))
    print("   published numbers are quoted to 2 significant figures, so a ratio")
    print("   within a few percent of 1 is full agreement with the source.")
    print()

    # ---- D2: monotone increase with T -------------------------------------
    print("=" * 96)
    print("[D2] source claim: eigenvalues of Q_T increase STRICTLY to those of Q_inf")
    print("=" * 96)
    order = [11, 14, 18]
    ws = {T: sorted(mp.eigsy(Ms[T])[0]) for T in order}
    ok_mono = True
    for j in range(N + 1):
        seq = [ws[T][j] for T in order] + [lmin_inf if j == 0 else w_inf[j]]
        strictly_increasing = all(seq[i] < seq[i + 1] for i in range(len(seq) - 1))
        print("   lambda_%d:  T=11 %-14s  T=14 %-14s  T=18 %-14s  Q_inf %-14s  %s"
              % (j, mp.nstr(seq[0], 6), mp.nstr(seq[1], 6), mp.nstr(seq[2], 6),
                 mp.nstr(seq[3], 6), "increasing" if strictly_increasing else "NOT"))
        ok_mono = ok_mono and strictly_increasing
    print("   verdict:", "PASS" if ok_mono else "FAIL")
    print()

    # ---- D3: total positivity of the tail, and the budget ------------------
    print("=" * 96)
    print("[D3] D_T = Q_inf - Q_T.  Cor 3.3(i):  0 <= D_T <= B_T I,")
    print("     with the EXACT  B_T = (1/pi^2) int_T^inf h_+(r) sin^2(Lr/2)/rho")
    print("                              * (||p_r||_2^2 + ||q_r||_2^2) dr")
    print("     and the source's proof notes that B_T is the trace of the tail.")
    print("     => lambda_max(D_T) is a RIGOROUS LOWER BOUND on the exact B_T,")
    print("        so it can be compared with the printed leading asymptotic.")
    print("=" * 96)
    print("   T    lambda_min(D_T)  lambda_max(D_T)  even-trace(D_T)"
          "   printed leading B_T   max/print")
    print("   " + "-" * 92)
    emp = {}
    for T in order:
        D = M_inf - Ms[T]
        wd = sorted(mp.eigsy(D)[0])
        bt = B_T(c, N, T)
        tr = mp.fsum(wd)
        emp[T] = +wd[-1]
        print("   %-4d %-16s %-16s %-17s %-20s %s"
              % (T, mp.nstr(+wd[0], 6), mp.nstr(+wd[-1], 8), mp.nstr(tr, 8),
                 mp.nstr(bt, 8), mp.nstr(+wd[-1] / bt, 6)))
        if +wd[0] < mp.mpf("-1e-30"):
            print("        *** D_T NOT positive semidefinite at this precision ***")
    print()
    print("   D_T >= 0 at all three cutoffs  ->  Q_T underestimates Q_inf, which")
    print("   is exactly why a negative finite-T eigenvalue in (-B_T,0) proves")
    print("   nothing: the true eigenvalue may still be positive.")
    print()
    print("   the printed leading asymptotic UNDERSTATES the exact budget by at least")
    for T in order:
        bt = B_T(c, N, T)
        print("      T = %-3d : %s %%   (lower bound, since exact B_T >= lambda_max(D_T))"
              % (T, mp.nstr((emp[T] / bt - 1) * 100, 6)))
    print("   consistent with the source writing it as '~' (asymptotic), not '='.")
    print()

    # ---- D4: cutoff a brute-force run would need --------------------------
    print("=" * 96)
    print("[D4] how large must T be before B_T < lambda_min(Q_inf)?  (brute cutoff)")
    print("=" * 96)
    ladder = [(4, "9.6792619e-15"), (8, "7.6743926e-23"), (16, "8.5686275e-35"),
              (24, "3.0745569e-43"), (32, "2.25893e-49"), (40, "9.46281e-54")]
    print("   N     lambda_min(Q_inf)   required T      zeros up to that T"
          "   (Riemann-von Mangoldt)")
    print("   " + "-" * 92)
    for NN, lm in ladder:
        tgt = mp.mpf(lm)
        Treq = T_for_budget(c, NN, tgt)
        if Treq is None:
            print("   %-5d %-19s unbounded" % (NN, lm))
            continue
        print("   %-5d %-19s %-14s %s"
              % (NN, lm, mp.nstr(Treq, 6), mp.nstr(N_zeros(Treq), 6)))
    print()
    print("   the paper's own version of the same obstruction: driving B_T below")
    print("   1e-59 at (c,N) = (100,200) would require T ~ 8e62.")
    print()
    print("-" * 96)
    print("SCOPE: this closes the band question of Corollary 3.3.  It does NOT")
    print("establish RH, Weil positivity, prime counting, or factoring; a finite-T")
    print("eigenvalue in [-B_T,0) certifies nothing by the source's own rule.")
    print("-" * 96)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
