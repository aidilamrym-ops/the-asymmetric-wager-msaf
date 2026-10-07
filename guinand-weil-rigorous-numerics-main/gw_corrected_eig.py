# -*- coding: utf-8 -*-
"""Recompute lambda_min(Q_inf) with the lerchphi defect REMOVED, then check it
with FLINT's interval eigenvalue solver (OMEGA A2).

WHAT CHANGED AND WHY
--------------------
gw_qinf.build_blocks evaluates beta_L's t2 term with mp.lerchphi(z, 2, an).
Section 7b of GW_STATUS established that this call is wrong by
8.42831291456e-100 at dps 140..252 while being dps-stable -- converged to the
wrong value.  beta_L enters Q_inf only through the diagonal entry

    P0d[n] = -2 * (gamma_L(n) - beta_L(n)) + psiprd(n),

so the shipped matrix satisfies  M_buggy = M_corr + diag(delta[n])  with
measured delta(+-40) = +3.391109217077509e-102 = 2.567 * lambda_min.
gw_entry_audit.py measures delta across the index range.

This script:
  phase 1  rebuild every block with beta_L corrected (defining series)
  phase 2  assemble the full (2N+1) matrix
  phase 3  mp.eigsy            -> lambda_min, the mpmath route
  phase 4  mp.det / prod rest  -> determinant cross-check of the same value
  phase 5  save the matrix (decimal, exact round-trip) for reuse
  phase 6  FLINT arb/acb interval route (OMEGA A1/A2)

Phase 6 notes on certification, stated up front so no claim later can exceed
it: python-flint 0.9.0 exposes NO psi/digamma/polygamma/hyp2f1/lerchphi, so
the archimedean block CANNOT be computed inside arb -- it arrives as decimal
strings parsed by arb, whose radius then covers only FLINT's own parse
rounding and NOT the mpmath origin of the digits.  The eigenvalue enclosures
returned by acb_mat.eig are rigorous over the matrix they are handed.  Whether
that matrix encloses the exact one is decided by phase 1-2, not by phase 6.

usage:  python gw_corrected_eig.py <c> <N> <dps>

SCOPE: a measurement on one preprint's matrix.  Not an RH, Weil-positivity,
prime-counting or factoring result; the source preprint disclaims all four.
"""
import json
import os
import sys
import time

import mpmath as mp

# Import order: gw_qinf sets mp.mp.dps = 40 at MODULE LEVEL.  Every import
# must run before main() assigns mp.mp.dps.  See GW_STATUS section 7b.
import gw_qinf as G
import gw_deep_v3 as V3
from gw_full_vs_even import full_matrix

BUGGY_LAM = mp.mpf("1.32105051975e-102")   # shipped build, dps 140 and 180


def build_blocks_corrected(c, N):
    """Byte-for-byte gw_qinf.build_blocks with ONE change:

        t2 = -(e^{-L/2}/4) * Re(mp.lerchphi(z, 2, an))          (shipped)
        t2 = -(e^{-L/2}/4) * Re(V3.lerchphi_series(z, 2, an))    (defining series)

    Everything else -- alpha_L, gamma_L, psipr, psiprd, pole_A, Cm, Sm, the
    assembly -- is copied unchanged so the two builds differ in exactly one
    call site.
    """
    L = mp.log(c)
    z = mp.e ** (-2 * L)
    PI = mp.pi
    eul = mp.euler
    PP = G.prime_powers(c)

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
        t2 = -(mp.e ** (-L / 2) / 4) * mp.re(V3.lerchphi_series(z, 2, an))  # <-- ONLY change
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
    P0, P0d = {}, {}
    for m in idx:
        P0[m] = alpha_L(m) + psipr(m)
        P0d[m] = -2 * (gamma_L(m) - beta_L(m)) + psiprd(m)

    def Cm(m):
        return mp.sinh(L / 4) / mp.sqrt(L) / (mp.mpf(1) / 4 + (2 * PI * m / L) ** 2)

    def Sm(m):
        return (4 * PI * mp.sinh(L / 4) / (L * mp.sqrt(L)) * m
                / (mp.mpf(1) / 4 + (2 * PI * m / L) ** 2))

    beta = L / (4 * PI)
    Cc = L * (mp.sqrt(c) + 1 / mp.sqrt(c) - 2) / (2 * PI ** 2)

    def pole_A(m, n):
        return 2 * (Cm(m) * Cm(n) - Sm(m) * Sm(n))

    def Q_full(m, n, block="all"):
        if block == "pole":
            return pole_A(m, n)
        if block == "prime":
            return (psipr(m) - psipr(n)) / (m - n) if m != n else psiprd(m)
        if block == "arch":
            return (alpha_L(m) - alpha_L(n)) / (m - n) if m != n else -2 * (gamma_L(m) - beta_L(m))
        pole = pole_A(m, n)
        if m == n:
            return P0d[n] + pole
        return (P0[m] - P0[n]) / (m - n) + pole

    return dict(L=L, beta=beta, Cc=Cc, pole_A=pole_A, Q_full=Q_full,
                P0=P0, P0d=P0d, idx=list(idx))


def phase_arb(M, prec_bits, algorithm):
    """A1/A2: hand the matrix to FLINT's interval eigenvalue solver."""
    import flint

    flint.ctx.prec = prec_bits
    n = len(M)
    vals = []
    for i in range(n):
        for j in range(n):
            vals.append(mp.nstr(M[i, j], mp.mp.dps))
    t0 = time.time()
    A = flint.arb_mat(n, n, vals)

    # entry radius provenance: radius as parsed (FLINT parse rounding only)
    rmax = flint.arb(0)
    for i in range(n):
        for j in range(n):
            if A[i, j].rad() > rmax:
                rmax = A[i, j].rad()
    print("  arb_mat built  %dx%d at prec=%d bits, parse radius max = %s"
          % (n, n, prec_bits, rmax))

    res = dict(prec_bits=prec_bits, algorithm=algorithm, t_build=time.time() - t0)
    try:
        t1 = time.time()
        ev = A.eig(algorithm=algorithm)
        res["t_eig"] = time.time() - t1
        res["n_eig"] = len(ev)
        # numerically smallest by real part (float key: arb comparison is a ball
        # comparison and must not be used for ordering)
        best = min(ev, key=lambda w: float(w.real))
        re_part = best.real                 # arb
        res["lam"] = str(best)
        res["lam_re_float"] = repr(float(re_part))
        res["imag_float"] = repr(float(abs(best.imag)))
        res["contains_zero"] = bool(best.contains(0))
        res["re_gt_0"] = bool(re_part > 0)
        res["re_lt_0"] = bool(re_part < 0)
        res["re_contains_0"] = bool(re_part.contains(0))
        res["ok"] = True
        print("  A2 %s (%.1f s): %d eigenvalues isolated" % (algorithm, res["t_eig"], len(ev)))
        print("      smallest by Re     : %s" % best)
        print("      Re (float)         : %s" % res["lam_re_float"])
        print("      Im (float)         : %s" % res["imag_float"])
        print("      best.contains(0)   : %s" % res["contains_zero"])
        print("      Re > 0  (rigorous) : %s" % res["re_gt_0"])
        print("      Re < 0  (rigorous) : %s" % res["re_lt_0"])
        print("      Re contains 0      : %s" % res["re_contains_0"])
        print("      VERDICT            : %s"
              % ("ENCLOSED STRICTLY POSITIVE"
                 if (res["re_gt_0"] and not res["re_contains_0"])
                 else ("ENCLOSED NEGATIVE" if res["re_lt_0"] and not res["re_contains_0"]
                       else "STRADDLES / INDETERMINATE")))
    except Exception as exc:
        res["ok"] = False
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
        print("  A2 %s FAILED: %s" % (algorithm, res["error"]))
    return res


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    c, N, dps = int(argv[1]), int(argv[2]), int(argv[3])
    mp.mp.dps = dps        # AFTER all imports

    print("#" * 100)
    print("# CORRECTED BUILD (lerchphi -> defining series) at (c, N, dps) = (%d, %d, %d)"
          % (c, N, dps))
    print("# shipped build lambda_min = %s" % mp.nstr(BUGGY_LAM, 25))
    print("#" * 100)
    sys.stdout.flush()

    # ---- phase 1 -----------------------------------------------------------
    t0 = time.time()
    bl = build_blocks_corrected(c, N)
    print("\n[phase 1] corrected blocks built in %.1f s" % (time.time() - t0))
    sys.stdout.flush()

    # Entry-level delta against the shipped values.  The shipped build is NOT
    # rebuilt here (it costs another ~11 min and gw_entry_audit.py already
    # measured delta at n = 0, +-40:  0, +3.391109217077509e-102, that value).
    # beta_L enters only through the diagonal, so max |delta P0d| is exactly
    # the Weyl scale reported below.
    dmax = mp.mpf("3.391109217077509e-102")
    n_at = 40
    print("[phase 1] shipped-vs-corrected max |delta P0d| = %s at n=%+d (measured by "
          "gw_entry_audit.py; not recomputed here)" % (mp.nstr(dmax, 18), n_at))
    sys.stdout.flush()

    # ---- phase 2 -----------------------------------------------------------
    t1 = time.time()
    M = full_matrix(bl, N, "all")
    n = len(M)
    print("[phase 2] full matrix %dx%d in %.1f s" % (n, n, time.time() - t1))
    sys.stdout.flush()

    # ---- phase 3 -----------------------------------------------------------
    t1 = time.time()
    w = sorted(mp.eigsy(M)[0])
    lam_corr = +w[0]
    print("[phase 3] mp.eigsy in %.1f s" % (time.time() - t1))
    print()
    print("=" * 100)
    print("LAMBDA_MIN, CORRECTED BUILD")
    print("=" * 100)
    print("  corrected (defining series)   = %s" % mp.nstr(lam_corr, 30))
    print("  sign                           : %s"
          % ("POSITIVE" if lam_corr > 0 else ("NEGATIVE" if lam_corr < 0 else "ZERO")))
    print()
    print("  NOTE -- the shipped value is NOT compared against a constant here.")
    print("  gw_corrected_eig.py once used BUGGY_LAM = mp.mpf('1.32105051975e-102'),")
    print("  a 12-digit literal whose own uncertainty is ~1e-114, which made any")
    print("  'shift' indistinguishable from that rounding.  The shipped build must be")
    print("  re-run to be compared; that is gw_compare_builds.py, which produced")
    print("    shipped   1.32105051975174706367212377355e-102  (dps 140, 602.3 s build)")
    print("    corrected 1.32105051975174632728899314595e-102  (dps 140,   2.6 s build)")
    print("    difference 7.363831306276056e-118, sign unchanged.")
    sys.stdout.flush()

    # ---- phase 4 -----------------------------------------------------------
    t1 = time.time()
    det = mp.det(M)
    prod_rest = mp.mpf(1)
    for x in w[1:]:
        prod_rest *= x
    lam_det = det / prod_rest
    print()
    print("[phase 4] mp.det route in %.1f s" % (time.time() - t1))
    print("  det / prod_{i>=2} lam_i       = %s" % mp.nstr(lam_det, 25))
    print("  ratio route(B)/route(A)       = %s"
          % mp.nstr(lam_det / lam_corr, 18) if lam_corr != 0 else "  n/a")
    sys.stdout.flush()

    # ---- phase 5 -----------------------------------------------------------
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "gw_matrix_%d_%d_dps%d.json" % (c, N, dps))
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"c": c, "N": N, "dps": dps,
                   "lam_corrected": mp.nstr(lam_corr, mp.mp.dps),
                   "lam_shipped": mp.nstr(BUGGY_LAM, mp.mp.dps),
                   "max_delta_p0d": mp.nstr(dmax, mp.mp.dps),
                   "M": [[mp.nstr(M[i, j], mp.mp.dps) for j in range(n)]
                         for i in range(n)]}, fh)
    print("[phase 5] matrix saved -> %s" % out)
    sys.stdout.flush()

    # ---- phase 6 -----------------------------------------------------------
    print()
    print("=" * 100)
    print("PHASE 6 -- FLINT INTERVAL ROUTE (OMEGA A1/A2)")
    print("=" * 100)
    print("  certification caveat, stated before any number: python-flint 0.9.0 has NO")
    print("  psi/digamma/polygamma/hyp2f1/lerchphi, so the archimedean block entered as")
    print("  decimal text.  arb's radius over those entries covers FLINT parse rounding")
    print("  ONLY, not the mpmath origin of the digits.  acb_mat.eig's enclosures are")
    print("  rigorous over the matrix handed to them.")
    print("  CAPABILITY CORRECTION (2026-10-07, A15): the three lines above are only")
    print("  half right.  On 0.9.0, arb.digamma, acb.polygamma and acb.hypgeom_2f1 ARE")
    print("  ball primitives; only lerchphi is missing.  gw_rho_formal.py therefore")
    print("  encloses the archimedean block directly and supplies rho_actual as an")
    print("  upper bound.  Phase 6 below is unchanged: it still reports over the")
    print("  decimal text handed to it.")
    print()
    results = []
    for prec, alg in ((1024, "rump"), (1024, "vdhoeven_mourrain")):
        results.append(phase_arb(M, prec, alg))
        sys.stdout.flush()

    print()
    print("PHASE 6 SUMMARY:", json.dumps(results, indent=2))
    print()
    print("TOOL STATUS: mpmath + python-flint.  lean/coqc/isabelle/z3/dkcheck NOT RUN.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
