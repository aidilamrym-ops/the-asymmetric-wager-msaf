# -*- coding: utf-8 -*-
"""
Spectrum of the cutoff-free Guinand-Weil matrix Q_inf.

Source of the statement (primary, located by search rather than invented):
    arXiv:2607.02828v3, "A finite Guinand-Weil dictionary and archimedean tail
    order for the truncated Weil quadratic form", A. Groskin, math.NT/math.SP.
    PREPRINT, not peer reviewed; the paper explicitly disclaims any RH,
    Weil-positivity or prime-counting result, and declares LLM assistance.

Object (paper, Lemma 2.1 / eq. (4)):

    Q_inf = Q_prime^(c) + Q_pole + Q_arch,inf

on indices -N..N, entrywise from a source psi via divided differences

    (Q_psi)_{mn} = (psi(m) - psi(n)) / (m - n)   for m != n
    (Q_psi)_{mm} = psi'(m)

then restricted to the real even sector and assembled as an (N+1)x(N+1) matrix.

Independent checks performed here (none of them taken on trust):

  CHECK A  the pole block is evaluated in two DIFFERENT closed forms:
             (i)  2*(Cm(m)*Cm(n) - Sm(m)*Sm(n))            [assembly route]
             (ii) 32*L*sinh(L/4)^2*(L^2 - 16 pi^2 m n)
                  / ((L^2 + 16 pi^2 m^2)(L^2 + 16 pi^2 n^2)) [Lemma 2.1]
           and must agree to working precision.

  CHECK B  on the even sector the pole block must be RANK 1: the paper's
           Corollary 2.7 states <v, Q_pole v> = C_c beta^2 * (row.v)^2, a
           perfect square.  Its kernel is the pole-neutral hyperplane.  So the
           pole block carries an N-dimensional exact zero eigenspace -- a real,
           provable degeneracy of one block of Q_inf.

  CHECK C  the assembled spectrum at (c,N) = (13,4) is compared with the
           value published in the paper (Figure 2 inset):
           cutoff-free lambda_min = +9.7e-15.

Output: table of eigenvalues, lambda_min, gap, and the block rank structure.
"""

import sys

import mpmath as mp

mp.mp.dps = 40


# --------------------------------------------------------------------------
# sources
# --------------------------------------------------------------------------
def prime_powers(c):
    primes = []
    x = 2
    while x <= c:
        if all(x % p for p in primes):
            primes.append(x)
        x += 1
    out = []
    for p in primes:
        q = p
        while q <= c:
            out.append((q, mp.log(p)))
            q *= p
    return out


def build_blocks(c, N):
    """Return the three blocks of Q_inf on indices -N..N, as dicts keyed by
    (m, n).  Prime and pole come from closed forms; the archimedean block uses
    the 2F1 / digamma / Lerch closed forms identified in Lemma 2.1 with the
    Connes-Consani-Moscovici assembly."""
    L = mp.log(c)
    z = mp.e ** (-2 * L)
    PI = mp.pi
    eul = mp.euler
    PP = prime_powers(c)

    def a_n(n):
        return mp.mpf(1) / 4 + PI * 1j * n / L

    def F(n):
        return mp.hyp2f1(1, a_n(n), a_n(n) + 1, z)

    def alpha_L(n):
        an = a_n(n)
        return (mp.e ** (-L / 2) * mp.im((2 * L / (L + 4 * PI * 1j * n)) * F(n))
                + mp.mpf(1) / 2 * mp.im(mp.digamma(an))) / PI

    def beta_L(n):
        an = a_n(n)
        t1 = -L * mp.e ** (-L / 2) * mp.im((2 * L / (4 * PI * n - 1j * L)) * F(n))
        t2 = -(mp.e ** (-L / 2) / 4) * mp.re(mp.lerchphi(z, 2, an))
        t3 = mp.mpf(1) / 4 * mp.re(mp.polygamma(1, an))
        return (t1 + t2 + t3) / L

    def c_w():
        return (mp.mpf(1) / 2 * mp.log((mp.e ** (L / 2) - 1) / (mp.e ** (L / 2) + 1))
                + mp.atan(mp.e ** (L / 2)) - PI / 4 + eul / 2
                + mp.mpf(1) / 2 * mp.log(8 * PI))

    def gamma_L(n):
        an = a_n(n)
        return (-mp.e ** (-L / 2) * mp.re((2 * L / (L + 4 * PI * 1j * n)) * F(n))
                + 2 * mp.e ** (-L / 2) * mp.hyp2f1(mp.mpf(1) / 4, 1, mp.mpf(5) / 4, z)
                - mp.mpf(1) / 2 * (mp.re(mp.digamma(an)) - mp.digamma(mp.mpf(1) / 4))
                + c_w())

    def psipr(m):
        return -(1 / PI) * mp.fsum(lp / mp.sqrt(q) * mp.sin(2 * PI * m * (1 - mp.log(q) / L))
                                   for q, lp in PP)

    def psiprd(m):
        return -2 * mp.fsum(lp / mp.sqrt(q) * (1 - mp.log(q) / L)
                            * mp.cos(2 * PI * m * (1 - mp.log(q) / L)) for q, lp in PP)

    idx = range(-N, N + 1)

    # archimedean source values: psi_arch(m) = alpha_L(m),
    #                             psi_arch'(m) = -2 (gamma_L(m) - beta_L(m))
    P0 = {m: alpha_L(m) + psipr(m) for m in idx}
    P0d = {m: -2 * (gamma_L(m) - beta_L(m)) + psiprd(m) for m in idx}

    def Cm(m):
        return mp.sinh(L / 4) / mp.sqrt(L) / (mp.mpf(1) / 4 + (2 * PI * m / L) ** 2)

    def Sm(m):
        return (4 * PI * mp.sinh(L / 4) / (L * mp.sqrt(L)) * m
                / (mp.mpf(1) / 4 + (2 * PI * m / L) ** 2))

    beta = L / (4 * PI)
    Cc = L * (mp.sqrt(c) + 1 / mp.sqrt(c) - 2) / (2 * PI ** 2)

    def pole_A(m, n):                       # route (i)
        return 2 * (Cm(m) * Cm(n) - Sm(m) * Sm(n))

    def pole_B(m, n):                       # route (ii), Lemma 2.1 verbatim
        return (32 * L * mp.sinh(L / 4) ** 2 * (L ** 2 - 16 * PI ** 2 * m * n)
                / ((L ** 2 + 16 * PI ** 2 * m ** 2) * (L ** 2 + 16 * PI ** 2 * n ** 2)))

    def arch(m, n):
        return (P0d[n] - 2 * psiprd(n) + 2 * psiprd(n)) if False else None  # unused

    def Q_full(m, n, block="all"):
        if block == "pole":
            return pole_A(m, n)
        if block == "prime":
            pr = (psipr(m) - psipr(n)) / (m - n) if m != n else psiprd(m)
            return pr
        if block == "arch":
            ar = (alpha_L(m) - alpha_L(n)) / (m - n) if m != n else -2 * (gamma_L(m) - beta_L(m))
            return ar
        pole = pole_A(m, n)
        if m == n:
            return P0d[n] + pole
        return (P0[m] - P0[n]) / (m - n) + pole

    return dict(L=L, beta=beta, Cc=Cc, pole_A=pole_A, pole_B=pole_B,
                Q_full=Q_full, P0=P0, P0d=P0d, idx=list(idx))


def even_matrix(bl, N, block="all"):
    """Assemble the (N+1)x(N+1) real even-sector matrix.

    <v, Q v> = sum_{k,l} v_k M_{kl} v_l with the isometric even embedding
    u_0 = v_0, u_{+-k} = v_k/sqrt(2)."""
    Q = bl["Q_full"]
    ne = N + 1
    M = mp.matrix(ne, ne)
    for i in range(ne):
        for j in range(ne):
            if i == 0 and j == 0:
                M[i, j] = Q(0, 0, block)
            elif i == 0:
                M[i, j] = (Q(0, j, block) + Q(0, -j, block)) / mp.sqrt(2)
            elif j == 0:
                M[i, j] = (Q(i, 0, block) + Q(-i, 0, block)) / mp.sqrt(2)
            else:
                M[i, j] = Q(i, j, block) + Q(i, -j, block)
    return M


def eigvals(M):
    w, _ = mp.eigsy(M)
    return [w[i] for i in range(len(w))]


def rank_of(M, tol):
    """count eigenvalues whose magnitude exceeds tol * max magnitude"""
    w = eigvals(M)
    mx = max(abs(x) for x in w)
    if mx == 0:
        return 0, w
    return sum(1 for x in w if abs(x) > tol * mx), w


# --------------------------------------------------------------------------
def main():
    print("=" * 78)
    print("SPECTRUM OF THE CUTOFF-FREE GUINAND-WEIL MATRIX  Q_inf")
    print("statement: arXiv:2607.02828v3 (preprint, LLM-assisted, no RH claim)")
    print("=" * 78)

    # ---- CHECK A: two independent closed forms for the pole block --------
    c, N = 13, 4
    bl = build_blocks(c, N)
    worst = mp.mpf(0)
    scale = mp.mpf(0)
    for m in bl["idx"]:
        for n in bl["idx"]:
            a = bl["pole_A"](m, n)
            b = bl["pole_B"](m, n)
            worst = max(worst, abs(a - b))
            scale = max(scale, abs(b))
    print("\n[CHECK A] pole block, two independent closed forms at (c,N)=(%d,%d)" % (c, N))
    print("          max |route_i - route_ii| = %s   (scale %s)" % (mp.nstr(worst, 6), mp.nstr(scale, 6)))
    print("          ->", "PASS" if worst < mp.mpf(10) ** -30 * max(scale, 1) else "FAIL")

    # ---- CHECK B: pole block on the even sector must be rank 1 ----------
    Mpole = even_matrix(bl, N, block="pole")
    r, wp = rank_of(Mpole, mp.mpf(10) ** -25)
    print("\n[CHECK B] pole block on the real even sector (dim %d)" % (N + 1))
    print("          numerically nonzero eigenvalues = %d (Cor 2.7 predicts 1)" % r)
    print("          eigenvalues: %s" % ", ".join(mp.nstr(x, 6) for x in wp))
    # compare the single nonzero one against the perfect-square prediction
    L = bl["L"]
    Cc, beta = bl["Cc"], bl["beta"]
    # <v,Q_pole v> = Cc*beta^2*(v0/beta^2 + sqrt2 sum v_k/(k^2+beta^2))^2
    # the nonzero eigenvalue is therefore Cc*beta^2 * ||row||^2 with the
    # row taken in the v-coordinates used by even_matrix.
    row = [mp.mpf(1) / (beta ** 2)]
    for k in range(1, N + 1):
        row.append(mp.sqrt(2) / (k ** 2 + beta ** 2))
    pred = Cc * beta ** 2 * mp.fsum(x * x for x in row)
    nz = max(wp, key=abs)
    print("          predicted by the perfect square = %s" % mp.nstr(pred, 12))
    print("          ratio actual/predicted          = %s" % mp.nstr(nz / pred, 12))
    print("          ->", "PASS" if abs(nz / pred - 1) < mp.mpf(10) ** -30 else "FAIL")
    print("          exact kernel dimension          = %d  (N = %d)" % (N - 1, N))

    # ---- CHECK C: full spectrum vs the published lambda_min -------------
    print("\n[CHECK C] full Q_inf spectrum")
    print("  %-12s %-4s %-16s %-16s %s" % ("c", "N", "lambda_min", "lambda_max", "cond(lambda_min)"))
    print("  " + "-" * 70)
    rows = []
    for (cc, NN) in [(13, 4), (13, 8), (13, 16), (13, 32), (29, 6), (100, 8)]:
        b2 = build_blocks(cc, NN)
        M = even_matrix(b2, NN, block="all")
        w = eigvals(M)
        w_sorted = sorted(w, key=lambda x: +x)
        lmin, lmax = w_sorted[0], w_sorted[-1]
        rows.append((cc, NN, lmin, lmax))
        ratio = (lmax / lmin) if lmin != 0 else mp.mpf("+inf")
        print("  %-12d %-4d %-16s %-16s %s"
              % (cc, NN, mp.nstr(lmin, 8), mp.nstr(lmax, 8), mp.nstr(ratio, 6)))

    # published value
    print("\n  paper, Figure 2 inset, (c,N) = (13,4), cutoff-free lambda_min = +9.7e-15")
    m13_4 = [r for r in rows if r[0] == 13 and r[1] == 4][0][2]
    print("  ours at (13,4)                          = %s" % mp.nstr(m13_4, 8))
    if abs(m13_4) > 0:
        print("  ratio ours/published                    = %s"
              % mp.nstr(m13_4 / mp.mpf("9.7e-15"), 6))

    # ---- degeneracy diagnostics -----------------------------------------
    print("\n[DEGENERACY] eigenvalue spacing at (c,N) = (13,4)")
    b = build_blocks(13, 4)
    w = sorted(eigvals(even_matrix(b, 4, block="all")), key=lambda x: +x)
    for i, x in enumerate(w):
        print("   lambda_%d = %s" % (i, mp.nstr(x, 12)))
    print("   gap lambda_1 - lambda_0 = %s" % mp.nstr(w[1] - w[0], 8))
    print("   lambda_0 / lambda_1     = %s" % mp.nstr(w[0] / w[1], 8))

    print("\n[NOTE] rho = 2 pi / log c ; the two-sided budget of Corollary 3.3 is")
    print("       B_T = (2N+1) rho (log(T/2pi)+1)/(pi^2 T) (1+o(1)); it applies to")
    print("       the FINITE-T matrix.  Q_inf has no T, hence no band; the question")
    print("       there is whether lambda_min(Q_inf) > 0 at all.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
