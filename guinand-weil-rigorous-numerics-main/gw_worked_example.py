# -*- coding: utf-8 -*-
"""
Second external anchor (independent of the (13,4) eigenvalue anchor).

Statement under test: arXiv:2607.02828v3, Section 2.3, "A worked example over
the first 512 zeros".

    take c = 13, N = 4, and the pole- and moment-neutral vector
    v in H_0(4) cap P_4(13) with (v2, v3, v4) = (1, 0, -3)/sqrt(2), and
    (v0, v1) determined by the two linear conditions; numerically
        v = (-0.0859452, 1.4749860, 0.7071068, 0, -2.1213203)
    the cutoff-free contraction, computed from the closed-form
    Connes-Consani-Moscovici assembly at 40 digits, is
        <v, Q_inf v> = 0.049968414571096979730 ...

Corollary 2.7 of the same source gives the two linear conditions explicitly:

    M_0(v) = v_0 + sqrt(2) * sum_{k=1..N} v_k          (moment-neutral, H_0)
    P_N(c):  v_0/beta^2 + sqrt(2) * sum_{k=1..N} v_k/(k^2 + beta^2) = 0
    beta = L / (4 pi),  L = log c                        (pole-neutral)

So (v0, v1) is determined EXACTLY, not to 7 digits.  We solve the 2x2 system in
arbitrary precision and then evaluate <v, Q_inf v> with our own assembly
(gw_qinf.build_blocks -> even_matrix), which already passed CHECK A, CHECK B,
CHECK C (lambda_min(13,4) = 9.6792619e-15 vs published 9.7e-15).

Two coordinate conventions are tested, because the source writes v with N+1 = 5
entries while Q_inf is stated to act on C^{I_N} of dimension 2N+1 = 9:

    A) raw      : quad = v^T M v
    B) isometric: quad = u^T M u with u = (v0, v1/sqrt2, ..., vN/sqrt2)

Whichever reproduces 0.049968414571096979730 is the convention used.

NO RH CLAIM IS MADE OR IMPLIED.  This checks one quadratic form of one
preprint, nothing more.
"""

import mpmath as mp

import gw_qinf as G

mp.mp.dps = 50

TARGET = mp.mpf("0.049968414571096979730")
PRINTED_V = [mp.mpf("-0.0859452"), mp.mpf("1.4749860"),
             mp.mpf("0.7071068"), mp.mpf(0), mp.mpf("-2.1213203")]


def solve_vector(c, N):
    """Solve M_0(v) = 0 and P_N(c)(v) = 0 for (v0, v1) given (v2..vN)."""
    L = mp.log(c)
    beta = L / (4 * mp.pi)
    b2 = beta * beta
    tail = [mp.mpf(0), mp.mpf(0), 1 / mp.sqrt(2), mp.mpf(0), -3 / mp.sqrt(2)]
    tail = tail[:N + 1]

    # unknowns v0, v1 ;  v2..vN fixed
    fixed_m0 = mp.sqrt(2) * sum(tail[2:])
    fixed_p = mp.sqrt(2) * sum(tail[k] / (k * k + b2) for k in range(2, N + 1))

    #   v0            + sqrt2 * v1              = -fixed_m0
    #   v0 / b2       + sqrt2 * v1/(1+b2)       = -fixed_p
    A = [[mp.mpf(1), mp.sqrt(2)],
         [1 / b2, mp.sqrt(2) / (1 + b2)]]
    rhs = [-fixed_m0, -fixed_p]
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    v0 = (rhs[0] * A[1][1] - A[0][1] * rhs[1]) / det
    v1 = (A[0][0] * rhs[1] - rhs[0] * A[1][0]) / det
    v = [v0, v1] + tail[2:]
    return v, b2


def main():
    print("#" * 96)
    print("# SECOND EXTERNAL ANCHOR: the Section 2.3 worked example of arXiv:2607.02828v3")
    print("# (PREPRINT, LLM-assisted; the source disclaims RH / Weil positivity results)")
    print("#" * 96)
    print()

    c, N = 13, 4
    v, b2 = solve_vector(c, N)
    print("c = %d, N = %d,  L = log c = %s,  beta = L/(4 pi) = %s" %
          (c, N, mp.nstr(mp.log(c), 15), mp.nstr(mp.sqrt(b2), 15)))
    print("beta^2 = %s" % mp.nstr(b2, 15))
    print()

    print("EXACT v solved from the two linear conditions of Corollary 2.7:")
    for k in range(N + 1):
        print("   v_%d = %s        (source prints %s, diff %s)" %
              (k, mp.nstr(v[k], 20), PRINTED_V[k],
               mp.nstr(v[k] - PRINTED_V[k], 6)))
    print()

    # residual checks on the printed vector, to see whether the printed
    # 7-digit v actually satisfies the two conditions
    M0 = lambda w: w[0] + mp.sqrt(2) * sum(w[1:])
    PP = lambda w: w[0] / b2 + mp.sqrt(2) * sum(w[k] / (k * k + b2)
                                                for k in range(1, N + 1))
    print("condition residuals")
    print("   exact v :  M_0 = %s ,  P = %s"
          % (mp.nstr(M0(v), 6), mp.nstr(PP(v), 6)))
    print("   printed v:  M_0 = %s ,  P = %s"
          % (mp.nstr(M0(PRINTED_V), 6), mp.nstr(PP(PRINTED_V), 6)))
    print("   printed v deviates from exact by max %s" %
          mp.nstr(max(abs(v[k] - PRINTED_V[k]) for k in range(N + 1)), 6))
    print()

    # ---- the quadratic form, our own assembly -------------------------------
    mp.mp.dps = 50
    bl = G.build_blocks(c, N)
    M = G.even_matrix(bl, N, block="all")

    u = [v[0]] + [v[k] / mp.sqrt(2) for k in range(1, N + 1)]
    quadA = mp.fdot(v, M * mp.matrix(v))
    quadB = mp.fdot(u, M * mp.matrix(u))

    print("<v, Q_inf v>  from our own assembly (50 dps):")
    print("   convention A (raw v, N+1 entries)      = %s" % mp.nstr(quadA, 30))
    print("   convention B (isometric v/sqrt2)       = %s" % mp.nstr(quadB, 30))
    print()
    print("source value                              = %s" % mp.nstr(TARGET, 30))
    print()
    for name, q in (("A", quadA), ("B", quadB)):
        rel = abs(q - TARGET) / abs(TARGET)
        print("   convention %s: |diff| = %-14s relative = %-14s  digits matched = %s"
              % (name, mp.nstr(abs(q - TARGET), 6), mp.nstr(rel, 6),
                 mp.nstr(-mp.log10(rel), 5) if rel > 0 else "inf"))
    print()

    # ---- which convention is right?  also test the printed vector ------------
    print("cross-check: convention A evaluated on the source's PRINTED vector:")
    qA_p = mp.fdot(PRINTED_V, M * mp.matrix(PRINTED_V))
    print("   = %s   (relative diff to source = %s)"
          % (mp.nstr(qA_p, 20), mp.nstr(abs(qA_p - TARGET) / abs(TARGET), 6)))
    print()

    # ---- Table 1 reproduction: partial sums over the first zeros ------------
    print("-" * 96)
    print("NOTE ON SCOPE: this checks one quadratic form of one preprint.")
    print("It does not verify RH, Weil positivity, prime counting, or factoring.")
    print("-" * 96)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
