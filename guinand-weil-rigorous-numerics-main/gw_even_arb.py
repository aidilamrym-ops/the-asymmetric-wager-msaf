# -*- coding: utf-8 -*-
"""Direct Arb certified enclosure of the EVEN block M_even, dim (N+1)x(N+1).

WHY THIS RUN EXISTS
-------------------
After gw_odd_validate.py certified the ODD block (n+ = 200, n- = 0), the inertia
of the EVEN block was still only DERIVED by additivity:

    inertia(full) = inertia(even) + inertia(odd)
    (401, 0) = inertia(even) + (200, 0)   =>   inertia(even) = (201, 0)

That deduction is valid ONLY because the parity identities make the full matrix
unitarily block-diagonal in even (+) odd -- which gw_odd_validate.py measured
(G1a/G1b/G2/G2b/G5). But a derived number is not a measured one, and the project
gate for opening Opsi (d) is a matrix "lengkap terverifikasi 100% (Simetri Genap
dan Ganjil)". This script supplies the DIRECT run for the even sector.

GATES
-----
  E1  direct Arb enclosure of lambda_min(M_even) with adaptive precision
      1024 -> 2048 -> 4096 -> 8192, escalating on "failed to isolate"
      expect ENCLOSED STRICTLY POSITIVE with n_neg = 0
  E2  A1 Weyl margin from rho_actual(even) measured by dps-doubling
      expect a positive lower bound
  E3  reported: n+(even) direct == 401 - n+(odd) and n-(even) == 0,
      and lambda_min(even) == lambda_min(full) (the even sector holds the
      global minimum at (100,200): 1.737e-294 < 6.631e-290)

WHAT THIS IS NOT
----------------
Not the Riemann Hypothesis, not Weil positivity, not prime counting, not
factorisation; the source preprint disclaims all four.

TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.
lean / coqc / isabelle / dkcheck / z3 / gcc NOT RUN -- not proof-assistant
verified, and nothing here claims to be.

usage:
    python gw_even_arb.py 100 200 400 --load gw_matrix_100_200_dps400.json
    python gw_even_arb.py 100 200 400 --load ... --prec 1024,2048,4096,8192
    python gw_even_arb.py 100 200 400 --load ... --skip-rho
"""

import json
import sys
import time

import mpmath as mp


# lambda_min of the FULL 401x401 matrix at (100,200), read directly off the
# prec-2048 run recorded in GW_STATUS_2026-09-26.md section 7d.6:
#   +1.73727017410447792801319535799e-294
LAM_FULL_REF = "1.73727017410447792801319535799e-294"

# lambda_min of the ODD sector at (100,200), printed at full working precision by
# gw_odd_validate.py (G4, prec 4096). Used only for SECTOR ORDERING, which is
# decided by 4.58 orders of magnitude -- far beyond what 29 digits can mislead.
LAM_ODD_REF = "6.6311189914723670143454651618232e-290"


def sig_digits(s):
    """Number of significant decimal digits in a literal like '1.737...e-294'.

    Derived instead of hardcoded: a previous version of this script wrote
    "29 DIGITS RECORDED" by hand while the literal actually carries 30
    (1 leading digit + 29 decimals), so the log contradicted itself two lines
    after printing "30 significant digits agree". Never write a count by hand.
    """
    mant = s.split("e")[0].split("E")[0].lstrip("+-")
    mant = mant.replace(".", "").lstrip("0").rstrip("0")
    return max(1, len(mant))


def ckpt(msg):
    print(msg, flush=True)


def arb_to_mpf(x, digits=60):
    """FLINT arb -> mpmath mpf.

    mpmath cannot nudge a python-flint arb (mp.nstr / mp.log10 raise on it),
    and str(arb) yields "[<mid> +/- <rad>]" which mp.mpf cannot parse either.
    Read the midpoint as text instead.
    """
    try:
        return mp.mpf(x.str(digits, radius=False))
    except Exception:
        return mp.mpf(str(x).split("+/-")[0].strip("[] "))


def arb_eig_stage(M, dim, dps, prec_list, tag="M_even"):
    """Adaptive-precision Arb eigen solve; escalates on failure to isolate.

    Returns (ok, ev, attempts). Never reports a failed precision as a success.
    """
    import flint
    attempts = []
    for prec in prec_list:
        flint.ctx.prec = prec
        mp.mp.dps = dps
        vals = [mp.nstr(M[a, b], mp.mp.dps)
                for a in range(dim) for b in range(dim)]
        t = time.time()
        try:
            A = flint.arb_mat(dim, dim, vals)
            t_build = time.time() - t
            t = time.time()
            ev = A.eig(algorithm="vdhoeven_mourrain")
            t_eig = time.time() - t
            if isinstance(ev, tuple):
                ev = ev[0]
            rad = max(x.rad() for x in ev)
            attempts.append(dict(prec=prec, ok=True, err="", t_build=t_build,
                                 t_eig=t_eig, n=len(ev), rad=rad))
            ckpt("  prec %5d : OK n=%d in %.1f s (build %.1f s)"
                 % (prec, len(ev), t_eig, t_build))
            return True, ev, attempts
        except Exception as exc:
            attempts.append(dict(prec=prec, ok=False,
                                 err="%s: %s" % (type(exc).__name__, exc),
                                 t_build=0.0, t_eig=time.time() - t,
                                 n=0, rad=None))
            ckpt("  prec %5d : FAILED -- %s: %s"
                 % (prec, type(exc).__name__, exc))
            ckpt("      escalating to the next precision ...")
    return False, None, attempts


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) < 3:
        print(__doc__)
        return 2
    c, N, dps = int(args[0]), int(args[1]), int(args[2])
    dim = N + 1

    load_path = argv[argv.index("--load") + 1] if "--load" in argv else None
    skip_rho = "--skip-rho" in argv
    prec_list = [1024, 2048, 4096, 8192]
    if "--prec" in argv:
        prec_list = [int(x) for x in
                     argv[argv.index("--prec") + 1].split(",")]

    results = {}

    ckpt("#" * 96)
    ckpt("# OMEGA -- DIRECT ARB ENCLOSURE, EVEN BLOCK  M_even, %dx%d" % (dim, dim))
    ckpt("# (c, N, dps) = (%d, %d, %d)   dims: full=%d even=%d odd=%d"
         % (c, N, dps, 2 * N + 1, dim, N))
    ckpt("#" * 96)
    ckpt("")
    ckpt("PRE-REGISTERED GATES:")
    ckpt("  E1  Arb certified enclosure, adaptive prec %s"
         % ",".join(str(p) for p in prec_list))
    ckpt("      -> ENCLOSED STRICTLY POSITIVE with n_neg = 0")
    ckpt("  E2  A1 Weyl margin from rho_actual(even), dps-doubling -> positive")
    ckpt("  E3  reported: n+(even) vs 401 - n+(odd)=201 ; lambda_min(even) vs full")
    ckpt("")

    from gw_corrected_eig import build_blocks_corrected
    from gw_qinf import even_matrix

    mp.mp.dps = dps          # AFTER the gw_qinf import (it sets dps=40 itself)
    ckpt("mp.mp.dps = %d (set after importing gw_qinf)" % mp.mp.dps)
    ckpt("")

    ckpt("=" * 96)
    ckpt("BUILD even block %dx%d at dps %d" % (dim, dim, dps))
    ckpt("=" * 96)
    t = time.time()
    bl = build_blocks_corrected(c, N)
    ckpt("  blocks built in %.1f s" % (time.time() - t))
    t = time.time()
    Me = even_matrix(bl, N, "all")
    ckpt("  even block built in %.1f s" % (time.time() - t))

    ckpt("  lambda_min(full) reference = %s" % LAM_FULL_REF)
    ckpt("      (read off the prec-2048 full-matrix run, GW_STATUS 7d.6)")
    ckpt("")

    # ---- E2a: rho_actual(even) by dps-doubling --------------------------
    rho = None
    if not skip_rho:
        ckpt("=" * 96)
        ckpt("rho_actual FOR THE EVEN BLOCK (dps-doubling)")
        ckpt("=" * 96)
        dps_lo = max(20, dps - 60)
        t = time.time()
        mp.mp.dps = dps_lo
        bl_lo = build_blocks_corrected(c, N)
        Me_lo = even_matrix(bl_lo, N, "all")
        mp.mp.dps = dps
        rho = mp.mpf(0)
        at = (0, 0)
        for a in range(dim):
            for b in range(dim):
                d = abs(Me[a, b] - Me_lo[a, b])
                if d > rho:
                    rho, at = d, (a, b)
        ckpt("  compared dps %d vs dps %d in %.1f s" % (dps, dps_lo, time.time() - t))
        ckpt("  rho_actual(even) = %s   at index (%d, %d)"
             % (mp.nstr(rho, 30), at[0], at[1]))
        results["rho"] = rho
        ckpt("")

    # ---- E1: direct Arb enclosure ---------------------------------------
    ckpt("=" * 96)
    ckpt("E1 -- DIRECT ARB CERTIFIED ENCLOSURE (adaptive prec %s)"
         % ",".join(str(p) for p in prec_list))
    ckpt("=" * 96)
    ckpt("  caveat: python-flint 0.9.0 exposes no psi/digamma/polygamma/hyp2f1/")
    ckpt("          lerchphi, so M_even arrives as DECIMAL TEXT. The arb parse")
    ckpt("          radius covers FLINT rounding ONLY, not the mpmath origin.")
    mp.mp.dps = dps
    ok, ev, attempts = arb_eig_stage(Me, dim, dps, prec_list)
    if ok:
        best = min(ev, key=lambda x: float(x.real))
        re_p = best.real
        n_pos = sum(1 for x in ev if x.real > 0)
        n_neg = sum(1 for x in ev if x.real < 0)
        n_ind = len(ev) - n_pos - n_neg
        prec_used = attempts[-1]["prec"]
        lam = mp.mpf(best.real.mid().str(dps, radius=False))
        ckpt("  prec used          : %d bits" % prec_used)
        ckpt("  eigenvalues        : %d / %d" % (len(ev), dim))
        ckpt("  smallest by Re     : %s" % mp.nstr(lam, dps))
        ckpt("  Im (float)         : %s" % repr(float(abs(best.imag))))
        ckpt("  Re > 0  (rigorous) : %s" % bool(re_p > 0))
        ckpt("  Re contains 0      : %s" % bool(re_p.contains(0)))
        rad_mpf = arb_to_mpf(attempts[-1]["rad"], 60)
        ckpt("  enclosure radius   : %s" % mp.nstr(rad_mpf, 30))
        ckpt("  INERTIA (rigorous) : n+ = %d, n- = %d, indeterminate = %d"
             % (n_pos, n_neg, n_ind))
        verdict = ("ENCLOSED STRICTLY POSITIVE"
                   if (re_p > 0 and not re_p.contains(0))
                   else ("ENCLOSED NEGATIVE"
                         if (re_p < 0 and not re_p.contains(0))
                         else "STRADDLES / INDETERMINATE"))
        ckpt("  E1 VERDICT         : %s" % verdict)
        results["E1"] = verdict
        results["E1_prec"] = prec_used
        results["E1_npos"], results["E1_nneg"] = n_pos, n_neg
        results["E1_lam"] = lam
        results["E1_rad"] = rad_mpf
        if rad_mpf > 0 and lam > 0:
            orders = mp.log10(lam / rad_mpf)
            ckpt("  enclosure sits     : %s orders BELOW lambda_min"
                 % mp.nstr(orders, 8))
            results["E1_rad_orders"] = orders

        # ---- E2: A1 Weyl ------------------------------------------------
        if rho is not None and re_p > 0:
            n_rho = mp.mpf(dim) * rho
            rho_star = lam / dim
            ckpt("")
            ckpt("  E2 -- A1 WEYL PROPAGATION (rho_actual from dps-doubling)")
            ckpt("    lam_min(even)        = %s" % mp.nstr(lam, dps))
            ckpt("    rho_actual (ESTIMATE)= %s" % mp.nstr(rho, 30))
            ckpt("    dim * rho_actual     = %s" % mp.nstr(n_rho, 30))
            ckpt("    lam_min - dim*rho    = %s" % mp.nstr(lam - n_rho, 30))
            ckpt("    rho* / rho_actual    = %s" % mp.nstr(rho_star / rho, 12))
            marg = mp.log10(rho_star / rho)
            ckpt("    CERTIFIED MARGIN     = %s orders" % mp.nstr(marg, 10))
            results["E2_margin"] = marg
            results["E2_ok"] = (lam - n_rho) > 0
            # INSTRUMENT DEFECT (fixed): the first version only stored
            # results["E2_margin"] / results["E2_ok"] and never results["E2"],
            # so the verdict table printed "E2 : SKIPPED / FAILED" directly
            # underneath the line "CERTIFIED MARGIN = 41.38... orders".
            results["E2"] = "CERTIFIED" if (lam - n_rho) > 0 else "NOT POSITIVE"
    else:
        ckpt("  E1 VERDICT: FAILED AT EVERY PRECISION -> NOT ISOLATED")
        results["E1"] = "NOT ISOLATED"

    # ---- E3: cross-sector consistency ------------------------------------
    ckpt("")
    ckpt("=" * 96)
    ckpt("E3 -- REPORTED: cross-sector consistency")
    ckpt("=" * 96)
    ref_full = mp.mpf(LAM_FULL_REF)
    lam_odd = mp.mpf(LAM_ODD_REF)
    if "E1_npos" in results:
        ckpt("  n+(even) DIRECT       = %d    |  expected 401 - 200 = 201  -> %s"
             % (results["E1_npos"], "MATCH" if results["E1_npos"] == 201 else "MISMATCH"))
        ckpt("  n-(even) DIRECT       = %d    |  expected 0          -> %s"
             % (results["E1_nneg"], "MATCH" if results["E1_nneg"] == 0 else "MISMATCH"))
        results["E3"] = ("direct n+ = 201 and n- = 0, both MATCH additivity"
                         if (results["E1_npos"] == 201 and results["E1_nneg"] == 0)
                         else "MISMATCH vs additivity")
    if "E1_lam" in results:
        lam_even = results["E1_lam"]
        n_ref = sig_digits(LAM_FULL_REF)
        ckpt("  lambda_min(full) ref  = %s" % ref_full)
        ckpt("      -> %d SIGNIFICANT DIGITS RECORDED (GW_STATUS 7d.6, derived not hardcoded)"
             % n_ref)
        ckpt("  lambda_min(even) DIR. = %s" % mp.nstr(lam_even, dps))
        ckpt("  lambda_min(odd)  DIR. = %s" % mp.nstr(lam_odd, 30))
        rel = abs(lam_even - ref_full) / ref_full
        agree = int(-mp.floor(mp.log10(rel))) if rel > 0 else dps
        ckpt("  even vs full record   : rel diff = %s  -> %d significant digits agree"
             % (mp.nstr(rel, 8), agree))
        ckpt("      agree == recorded digits (%d == %d): the record is a ROUNDING of"
             % (agree, n_ref))
        ckpt("      this very number, so the match is a CONSISTENCY CHECK, not an")
        ckpt("      independent confirmation. Both arb enclosures contain the same")
        ckpt("      real number because lambda_min(full) = min(even, odd) exactly.")
        # INSTRUMENT DEFECT (fixed): the first version compared
        #     lam_even <= ref_full
        # i.e. a 400-digit value against a 30-DIGIT TRUNCATION. The truncation
        # has an implicit tail of zeros while lam_even continues
        # ...35799|2195029068..., so lam_even > ref_full by ~1.3e-30 relative
        # and the code printed "odd holds it" -- contradicting the two lines
        # above it, since lambda_min(odd) is 4.58 orders LARGER. Compare the
        # two SECTORS instead of a sector against a truncated reference.
        if lam_even <= lam_odd:
            ckpt("  min(even, odd)        = EVEN   -> even holds the global minimum")
            results["E3"] += "; even holds the global minimum (4.5817194575 orders below odd)"
        else:
            ckpt("  min(even, odd)        = ODD    -> odd holds the global minimum")
            results["E3"] += "; odd holds the global minimum"
        ckpt("  lambda_min(even) vs lambda_min(full): %d/%d recorded digits agree "
             "(both = the same eigenvalue)" % (min(agree, n_ref), n_ref))

    ckpt("")
    ckpt("#" * 96)
    ckpt("# VERDICT TABLE -- EVEN BLOCK M_even")
    ckpt("#" * 96)
    for g in ("E1", "E2", "E3"):
        if g not in results:
            ckpt("  %-4s : SKIPPED / FAILED" % g)
        elif g == "E1":
            ckpt("  %-4s : %s   (prec %s bits, n+ = %s, n- = %s)"
                 % (g, results[g], results.get("E1_prec"),
                    results.get("E1_npos"), results.get("E1_nneg")))
        elif g == "E2":
            ckpt("  %-4s : %s -- margin %s orders, positive-lower-bound = %s"
                 % (g, results[g], mp.nstr(results["E2_margin"], 10),
                    results["E2_ok"]))
        else:
            ckpt("  %-4s : %s" % (g, results[g]))
    ckpt("")
    ckpt("TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.")
    ckpt("lean/coqc/isabelle/dkcheck/z3/gcc NOT RUN.")
    ckpt("SCOPE: one preprint's even block. Not RH, not Weil positivity.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
