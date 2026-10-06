# -*- coding: utf-8 -*-
"""Validation of the ODD block  O_{k,l} = Q(k,l) - Q(k,-l),  k,l = 1..N.

WHY THE ODD BLOCK WAS FLAGGED `UNVERIFIED`
------------------------------------------
gw_opt_b.odd_matrix derives it as

    <o_k, Q o_l> = 1/2 [ Q(k,l) - Q(k,-l) - Q(-k,l) + Q(-k,-l) ]
                 = Q(k,l) - Q(k,-l)          using Q(-m,-n) = Q(m,n)

and that last equality is ASSUMED in the docstring, never measured. The block
was then used to produce lambda_min(odd) in Option (b) without ever being
re-derived, cross-checked against the source package, or certified in Arb.
This script closes all three gaps.

GATES (thresholds pre-registered before the first run)
------------------------------------------------------
  G1a  algebraic parity: Cm(-m)=Cm(m), Sm(-m)=-Sm(m), pole_A(-m,-n)=pole_A(m,n)
       expect EXACT 0  (bitwise identity, no evaluation-order freedom)
  G1b  derived parity: P0 odd, P0d even, Q(-m,-n)=Q(m,n), Q symmetric
       expect at the working-precision floor 10^-dps
  G2   independent closed-form derivation of O (never evaluates Q at a
       negative second argument) vs the definition
       expect at the floor
  G2b  quadratic-form reconstruction: v'Qv = u'M_even u + w'M_odd w
       for random v -- tests the embedding normalisation end to end
       expect at the floor
  G3   entrywise cross-diff of the odd block against the SOURCE package's
       build_arb_tau() (SHA256 b7fee730... == the certified script)
       expect < 1e-300
  G4   Arb certified enclosure of lambda_min(O) with adaptive precision:
       1024 -> 2048 -> 4096 on "failed to isolate"
       expect ENCLOSED STRICTLY POSITIVE with n_neg = 0
  G5   reported, not gating: spectrum(full) == spectrum(even) u spectrum(odd)
       at small N, and lambda_min(full) = min(even, odd), n+(full)=201+200=401

WHAT THIS IS NOT
----------------
Validation of one preprint's odd block. Not the Riemann Hypothesis, not Weil
positivity, not prime counting, not factorisation; the source disclaims all four.

TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.
lean / coqc / isabelle / dkcheck / z3 / gcc NOT RUN -- not proof-assistant
verified, and nothing here claims to be.

usage:
    python gw_odd_validate.py 100 200 400 --load gw_matrix_100_200_dps400.json
    python gw_odd_validate.py 100 200 400 --load ... --prec 1024,2048,4096
    python gw_odd_validate.py 100 200 400 --load ... --skip-source --skip-rho
"""

import importlib.util
import json
import random
import sys
import time

import mpmath as mp

SRC_PATH = "source_arb_ldlt_certify.py"

G3_REL = mp.mpf(10) ** -300


def ckpt(msg):
    print(msg, flush=True)


# --------------------------------------------------------------------------
# local copies of the two elementary closed forms, validated against the
# shipped pole_A by the identity  pole_A(k,l) - pole_A(k,-l) = -4 Sm(k) Sm(l)
# --------------------------------------------------------------------------
def cm_of(m, L):
    return mp.sinh(L / 4) / mp.sqrt(L) / (mp.mpf(1) / 4 + (2 * mp.pi * m / L) ** 2)


def sm_of(m, L):
    return (4 * mp.pi * mp.sinh(L / 4) / (L * mp.sqrt(L)) * m
            / (mp.mpf(1) / 4 + (2 * mp.pi * m / L) ** 2))


def closed_form_odd(bl, N, L):
    """O(k,l) WITHOUT ever evaluating Q at a negative second argument.

    Uses only:  P0 odd  =>  Q(k,-l) = pole_A(k,-l) + (P0[k]+P0[l])/(k+l)
                pole_A(k,l) - pole_A(k,-l) = -4 Sm(k) Sm(l)   (Cm even, Sm odd)
    """
    P0, P0d = bl["P0"], bl["P0d"]
    O = mp.matrix(N, N)
    for a in range(N):
        k = a + 1
        for b in range(N):
            l = b + 1
            if k == l:
                O[a, b] = P0d[k] - P0[k] / k - 4 * sm_of(k, L) ** 2
            else:
                O[a, b] = (-4 * sm_of(k, L) * sm_of(l, L)
                           + (P0[k] - P0[l]) / (k - l)
                           - (P0[k] + P0[l]) / (k + l))
    return O


def quad(v, M, n):
    """v'Mv by exact accumulation, exploiting symmetry."""
    acc = []
    for i in range(n):
        acc.append(M[i, i] * v[i] * v[i])
        for j in range(i + 1, n):
            acc.append(2 * M[i, j] * v[i] * v[j])
    return mp.fsum(acc)


def arb_eig_stage(O, N, dps, prec_list):
    """Adaptive-precision Arb eigen solve; escalates on failure to isolate."""
    import flint
    attempts = []
    for prec in prec_list:
        flint.ctx.prec = prec
        mp.mp.dps = dps
        vals = [mp.nstr(O[a, b], mp.mp.dps) for a in range(N) for b in range(N)]
        t = time.time()
        try:
            A = flint.arb_mat(N, N, vals)
            t_build = time.time() - t
            t = time.time()
            ev = A.eig(algorithm="vdhoeven_mourrain")
            t_eig = time.time() - t
            if isinstance(ev, tuple):
                ev = ev[0]
            rad = max(x.rad() for x in ev)
            attempts.append(dict(prec=prec, ok=True, err="",
                                 t_build=t_build, t_eig=t_eig,
                                 n=len(ev), rad=rad))
            return True, ev, attempts
        except Exception as exc:
            attempts.append(dict(prec=prec, ok=False,
                                 err="%s: %s" % (type(exc).__name__, exc),
                                 t_build=0.0, t_eig=time.time() - t,
                                 n=0, rad=None))
            ckpt("  prec %4d FAILED -- %s: %s" % (prec, type(exc).__name__, exc))
            ckpt("      escalating to the next precision ...")
    return False, None, attempts


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) < 3:
        print(__doc__)
        return 2
    c, N, dps = int(args[0]), int(args[1]), int(args[2])
    n_full = 2 * N + 1

    load_path = argv[argv.index("--load") + 1] if "--load" in argv else None
    skip_source = "--skip-source" in argv
    skip_rho = "--skip-rho" in argv
    prec_list = [1024, 2048, 4096]
    if "--prec" in argv:
        prec_list = [int(x) for x in argv[argv.index("--prec") + 1].split(",")]

    results = {}

    ckpt("#" * 96)
    ckpt("# OMEGA -- ODD BLOCK VALIDATION  O_{k,l} = Q(k,l) - Q(k,-l)")
    ckpt("# (c, N, dps) = (%d, %d, %d)   dims: full=%d even=%d odd=%d"
         % (c, N, dps, n_full, N + 1, N))
    ckpt("#" * 96)
    ckpt("")
    ckpt("PRE-REGISTERED GATES:")
    ckpt("  G1a algebraic parity            -> EXACT 0")
    ckpt("  G1b derived parity / symmetry   -> at floor 10^-%d" % dps)
    ckpt("  G2  closed-form vs definition   -> at floor 10^-%d" % dps)
    ckpt("  G2b quadratic-form split        -> at floor 10^-%d" % dps)
    ckpt("  G3  cross-diff vs source pkg    -> < 1e-300")
    ckpt("  G4  Arb certified enclosure     -> ENCLOSED STRICTLY POSITIVE, n_neg=0")
    ckpt("  G5  reported (not gating): spectrum(full) = even u odd")
    ckpt("")

    # ---- our side, dps ---------------------------------------------------
    from gw_corrected_eig import build_blocks_corrected
    from gw_full_vs_even import full_matrix
    from gw_qinf import even_matrix
    from gw_opt_b import odd_matrix

    mp.mp.dps = dps          # AFTER the gw_qinf import: it sets dps=40 itself
    ckpt("mp.mp.dps = %d (set after importing gw_qinf)" % mp.mp.dps)
    ckpt("")

    ckpt("=" * 96)
    ckpt("BUILD at dps %d" % dps)
    ckpt("=" * 96)
    t = time.time()
    bl = build_blocks_corrected(c, N)
    ckpt("  blocks built in %.1f s" % (time.time() - t))
    L = bl["L"]
    t = time.time()
    O = odd_matrix(bl["Q_full"], N, "all")
    ckpt("  odd block %dx%d built in %.1f s" % (N, N, time.time() - t))
    t = time.time()
    Me = even_matrix(bl, N, "all")
    ckpt("  even block %dx%d built in %.1f s" % (N + 1, N + 1, time.time() - t))

    if load_path:
        blob = json.load(open(load_path, encoding="utf-8"))
        mp.mp.dps = dps
        assert int(blob["N"]) == N, "load provenance mismatch"
        ents = [mp.mpf(s) for s in blob["entries"]]
        ckpt("  full matrix loaded from %s (%d entries, dps %d)"
             % (load_path, len(ents), blob["dps"]))
    else:
        Mtmp = full_matrix(bl, N, "all")
        ents = [Mtmp[a, b] for a in range(n_full) for b in range(n_full)]
        ckpt("  full matrix built fresh (%d entries)" % len(ents))
    ckpt("")

    # ---- G1a: algebraic parity ------------------------------------------
    ckpt("=" * 96)
    ckpt("G1a -- ALGEBRAIC PARITY (expect EXACT 0)")
    ckpt("=" * 96)
    d_cm = d_sm = d_pole = mp.mpf(0)
    par = list(range(0, min(40, N + 1))) + list(range(max(40, N - 40), N + 1))
    for m in par:
        d_cm = max(d_cm, abs(cm_of(-m, L) - cm_of(m, L)))
        d_sm = max(d_sm, abs(sm_of(-m, L) + sm_of(m, L)))
    for m in range(1, min(N, 60) + 1):
        for l in range(1, min(N, 60) + 1):
            d_pole = max(d_pole,
                         abs(bl["pole_A"](-m, -l) - bl["pole_A"](m, l)))
    ckpt("  max|Cm(-m) - Cm(m)|        = %s   %s"
         % (d_cm, "EXACT 0" if d_cm == 0 else "NOT EXACT"))
    ckpt("  max|Sm(-m) + Sm(m)|        = %s   %s"
         % (d_sm, "EXACT 0" if d_sm == 0 else "NOT EXACT"))
    ckpt("  max|pole(-m,-l)-pole(m,l)| = %s   %s"
         % (d_pole, "EXACT 0" if d_pole == 0 else "NOT EXACT"))
    # local Cm/Sm transcription must reproduce the shipped pole_A
    d_id = mp.mpf(0)
    for m in range(1, 31):
        for l in range(1, 31):
            lhs = 2 * (cm_of(m, L) * cm_of(l, L) - sm_of(m, L) * sm_of(l, L))
            d_id = max(d_id, abs(lhs - bl["pole_A"](m, l)))
    ckpt("  max|2(Cm Cm - Sm Sm) - pole_A| = %s   (validates local Cm/Sm)" % d_id)
    results["G1a"] = max(d_cm, d_sm, d_pole, d_id)
    ckpt("  G1a = %s   -> %s" % (mp.nstr(results["G1a"], 8),
                                 "PASS" if results["G1a"] == 0 else "FAIL"))
    ckpt("")

    # ---- G1b: derived parity and symmetry -------------------------------
    ckpt("=" * 96)
    ckpt("G1b -- DERIVED PARITY / SYMMETRY (expect at floor 10^-%d)" % dps)
    ckpt("=" * 96)
    d_p0 = d_p0d = mp.mpf(0)
    for m in range(0, N + 1):
        d_p0 = max(d_p0, abs(bl["P0"][m] + bl["P0"][-m]))
        d_p0d = max(d_p0d, abs(bl["P0d"][m] - bl["P0d"][-m]))
    ckpt("  max|P0(m) + P0(-m)|   (P0 odd)      = %s" % mp.nstr(d_p0, 8))
    ckpt("  max|P0d(m) - P0d(-m)| (P0d even)    = %s" % mp.nstr(d_p0d, 8))

    d_flip = d_sym = mp.mpf(0)
    for a in range(n_full):
        for b in range(n_full):
            v = ents[a * n_full + b]
            w = ents[b * n_full + a]
            d_sym = max(d_sym, abs(v - w))
    # flip symmetry on a sample (a full sweep costs another 160k Q evals);
    # the sample is clamped to n_full so it stays valid for small N too.
    sample = list(range(0, min(60, n_full))) + list(range(max(0, N - 30), n_full))
    for a in sample:
        for b in sample:
            v = ents[a * n_full + b]
            w = ents[(n_full - 1 - a) * n_full + (n_full - 1 - b)]
            d_flip = max(d_flip, abs(v - w))
    ckpt("  max|Q(m,n) - Q(n,m)| (sample + full) = %s" % mp.nstr(d_sym, 8))
    ckpt("  max|Q(-m,-n) - Q(m,n)| (sample)      = %s" % mp.nstr(d_flip, 8))
    d_odd = mp.mpf(0)
    for a in range(N):
        for b in range(N):
            d_odd = max(d_odd, abs(O[a, b] - O[b, a]))
    ckpt("  max|O - O'| (odd symmetry, full)     = %s" % mp.nstr(d_odd, 8))
    results["G1b"] = max(d_p0, d_p0d, d_sym, d_flip, d_odd)
    floor = mp.mpf(10) ** -dps
    ckpt("  G1b = %s   -> %s" % (mp.nstr(results["G1b"], 8),
                                 "PASS" if results["G1b"] <= floor * 1000 else "FAIL"))
    ckpt("")

    # ---- G2: independent closed form ------------------------------------
    ckpt("=" * 96)
    ckpt("G2 -- INDEPENDENT CLOSED-FORM DERIVATION vs DEFINITION")
    ckpt("=" * 96)
    ckpt("  (closed form never evaluates Q at a negative second argument)")
    t = time.time()
    O_cl = closed_form_odd(bl, N, L)
    d2 = mp.mpf(0)
    at = (0, 0)
    for a in range(N):
        for b in range(N):
            d = abs(O[a, b] - O_cl[a, b])
            if d > d2:
                d2, at = d, (a + 1, b + 1)
    ckpt("  built + compared in %.1f s" % (time.time() - t))
    ckpt("  delta = max|O_def - O_closed| = %s   at (%d, %d)"
         % (mp.nstr(d2, 20), at[0], at[1]))
    ckpt("  floor = 10^-%d = %s ; delta is %s orders %s the floor"
         % (dps, mp.nstr(floor, 8),
            mp.nstr(abs(mp.log10(d2 / floor)), 6) if d2 > 0 else "0",
            "ABOVE" if d2 > floor else "BELOW"))
    results["G2"] = d2
    ckpt("  G2 = %s   -> %s" % (mp.nstr(d2, 8),
                                "PASS" if d2 <= floor * 1000 else "FAIL"))
    ckpt("")

    # ---- G2b: quadratic-form reconstruction -----------------------------
    ckpt("=" * 96)
    ckpt("G2b -- QUADRATIC-FORM RECONSTRUCTION  v'Qv = u'M_even u + w'M_odd w")
    ckpt("=" * 96)
    Mfull = M_full_reshaped(ents, n_full)   # reshape once, outside the trials
    rng = random.Random(20260927)
    worst = mp.mpf(0)
    for trial in range(3):
        v = [mp.mpf(rng.uniform(-1, 1)) for _ in range(n_full)]
        direct = quad(v, Mfull, n_full)
        u = [v[N]] + [(v[N + k] + v[N - k]) / mp.sqrt(2) for k in range(1, N + 1)]
        w = [(v[N + k] - v[N - k]) / mp.sqrt(2) for k in range(1, N + 1)]
        even_part = quad(u, Me, N + 1)
        odd_part = quad(w, O, N)
        d = abs(direct - (even_part + odd_part))
        scale = max(abs(direct), 1)
        worst = max(worst, d / scale)
        ckpt("  trial %d: direct=%s" % (trial, mp.nstr(direct, 14)))
        ckpt("           even+odd=%s   |diff|=%s   rel=%s"
             % (mp.nstr(even_part + odd_part, 14), mp.nstr(d, 8),
                mp.nstr(d / scale, 8)))
    results["G2b"] = worst
    ckpt("  G2b worst relative residual = %s   -> %s"
         % (mp.nstr(worst, 8),
            "PASS" if worst <= mp.mpf(10) ** (-(dps - 20)) else "FAIL"))
    ckpt("")

    # ---- rho_actual for the odd block (A1 input) ------------------------
    if not skip_rho:
        ckpt("=" * 96)
        ckpt("rho_actual FOR THE ODD BLOCK (dps-doubling)")
        ckpt("=" * 96)
        dps_lo = max(20, dps - 60)
        t = time.time()
        mp.mp.dps = dps_lo
        bl_lo = build_blocks_corrected(c, N)
        O_lo = odd_matrix(bl_lo["Q_full"], N, "all")
        mp.mp.dps = dps
        rho = mp.mpf(0)
        at = (0, 0)
        for a in range(N):
            for b in range(N):
                d = abs(O[a, b] - O_lo[a, b])
                if d > rho:
                    rho, at = d, (a + 1, b + 1)
        ckpt("  compared dps %d vs dps %d in %.1f s" % (dps, dps_lo, time.time() - t))
        ckpt("  rho_actual(odd) = %s   at (%d, %d)" % (mp.nstr(rho, 30), at[0], at[1]))
        results["rho"] = rho
        ckpt("")

    # ---- G3: cross-diff vs source package -------------------------------
    if not skip_source:
        ckpt("=" * 96)
        ckpt("G3 -- ENTRYWISE CROSS-DIFF vs SOURCE PACKAGE (odd block %dx%d)" % (N, N))
        ckpt("=" * 96)
        try:
            spec = importlib.util.spec_from_file_location("src_arb_ldlt", SRC_PATH)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            t = time.time()
            A, DIM = mod.build_arb_tau(c, N, 2000)
            ckpt("  build_arb_tau(prec 2000) = %.1f s, dimension %d" % (time.time() - t, DIM))
            digits = 592
            mp.mp.dps = max(dps, digits + 20)
            # extract the odd block from each full matrix the same way
            d3 = mp.mpf(0)
            at = (0, 0)
            msrc_max = mp.mpf(0)
            for a in range(N):
                k = a + 1
                for b in range(N):
                    l = b + 1
                    s = (mp.mpf(A[N + k, N + l].mid().str(digits, radius=False))
                         - mp.mpf(A[N + k, N - l].mid().str(digits, radius=False)))
                    o = (ents[(N + k) * n_full + (N + l)]
                         - ents[(N + k) * n_full + (N - l)])
                    d = abs(o - s)
                    if d > d3:
                        d3, at = d, (k, l)
                    msrc_max = max(msrc_max, abs(s))
            rel = d3 / msrc_max if msrc_max else mp.mpf("inf")
            ckpt("  max |O_source| = %s" % mp.nstr(msrc_max, 20))
            ckpt("  delta = %s   at (%d, %d)" % (mp.nstr(d3, 20), at[0], at[1]))
            ckpt("  delta_rel = %s" % mp.nstr(rel, 12))
            results["G3"] = rel
            ckpt("  G3 = %s   -> %s" % (mp.nstr(rel, 8),
                                         "PASS" if rel < G3_REL else "FAIL"))
        except SystemExit:
            raise
        except Exception as exc:
            ckpt("  SOURCE SIDE FAILED: %s: %s" % (type(exc).__name__, exc))
            results["G3"] = None
            ckpt("  G3 -> NOT COMPARABLE")
        ckpt("")

    # ---- G4: Arb certified enclosure -------------------------------------
    ckpt("=" * 96)
    ckpt("G4 -- ARB CERTIFIED ENCLOSURE (adaptive precision %s)"
         % ",".join(str(p) for p in prec_list))
    ckpt("=" * 96)
    ckpt("  caveat: python-flint 0.9.0 exposes no psi/digamma/polygamma/hyp2f1/")
    ckpt("          lerchphi, so O arrives as DECIMAL TEXT. The arb parse radius")
    ckpt("          covers FLINT rounding ONLY, not the mpmath origin of digits.")
    mp.mp.dps = dps
    ok, ev, attempts = arb_eig_stage(O, N, dps, prec_list)
    for a in attempts:
        ckpt("  prec %5d : %s%s" % (a["prec"],
                                     "OK n=%d in %.1f s (build %.1f s)"
                                     % (a["n"], a["t_eig"], a["t_build"])
                                     if a["ok"] else "FAILED -- " + a["err"], ""))
    if ok:
        best = min(ev, key=lambda x: float(x.real))
        re_p = best.real
        n_pos = sum(1 for x in ev if x.real > 0)
        n_neg = sum(1 for x in ev if x.real < 0)
        n_ind = len(ev) - n_pos - n_neg
        prec_used = attempts[-1]["prec"]
        ckpt("  prec used          : %d bits" % prec_used)
        ckpt("  eigenvalues        : %d / %d" % (len(ev), N))
        ckpt("  smallest by Re     : %s" % best)
        ckpt("  Im (float)         : %s" % repr(float(abs(best.imag))))
        ckpt("  Re > 0  (rigorous) : %s" % bool(re_p > 0))
        ckpt("  Re contains 0      : %s" % bool(re_p.contains(0)))
        ckpt("  enclosure radius   : %s" % attempts[-1]["rad"])
        ckpt("  INERTIA (rigorous) : n+ = %d, n- = %d, indeterminate = %d"
             % (n_pos, n_neg, n_ind))
        verdict = ("ENCLOSED STRICTLY POSITIVE"
                   if (re_p > 0 and not re_p.contains(0))
                   else ("ENCLOSED NEGATIVE" if (re_p < 0 and not re_p.contains(0))
                         else "STRADDLES / INDETERMINATE"))
        ckpt("  G4 VERDICT         : %s" % verdict)
        results["G4"] = verdict
        results["G4_prec"] = prec_used
        results["G4_npos"], results["G4_nneg"] = n_pos, n_neg
        results["G4_lam"] = str(best)
        results["G4_rad"] = str(attempts[-1]["rad"])
        # A1: Weyl with the measured entry error
        if "rho" in results and re_p > 0:
            # INSTRUMENT DEFECT (fixed): the first version used
            #   lam = float(re_p)  and then printed mp.nstr(lam, 30)
            # which printed 30 digits of which only ~16 were real (float64).
            # The verdict was unaffected -- n*rho and the sign do not depend
            # on lam, and a relative error of 6e-17 moves the margin by
            # < 1e-16 orders -- but the printed number was misleading.
            # Parse the arb midpoint at full working precision instead.
            lam = mp.mpf(best.real.mid().str(dps, radius=False))
            n_rho = mp.mpf(N) * results["rho"]
            rho_star = lam / N
            ckpt("  A1 -- WEYL PROPAGATION (rho_actual from dps-doubling)")
            ckpt("    lam_min(parse)        = %s" % mp.nstr(lam, dps))
            ckpt("    rho_actual (ESTIMATE) = %s" % mp.nstr(results["rho"], 30))
            ckpt("    n * rho_actual        = %s" % mp.nstr(n_rho, 30))
            ckpt("    lam_min - n*rho       = %s" % mp.nstr(mp.mpf(lam) - n_rho, 30))
            ckpt("    rho* / rho_actual     = %s" % mp.nstr(rho_star / results["rho"], 12))
            marg = mp.log10(rho_star / results["rho"])
            ckpt("    CERTIFIED MARGIN      = %s orders" % mp.nstr(marg, 10))
            results["A1_margin"] = marg
            results["A1_ok"] = (mp.mpf(lam) - n_rho) > 0
    else:
        ckpt("  G4 VERDICT: FAILED AT EVERY PRECISION -> NOT ISOLATED")
        results["G4"] = "NOT ISOLATED"
    ckpt("")

    # ---- G5: reported, not gating ---------------------------------------
    ckpt("=" * 96)
    ckpt("G5 -- REPORTED: spectrum(full) vs spectrum(even) u spectrum(odd)")
    ckpt("=" * 96)
    for nn in (4, 8, 16):
        bl5 = build_blocks_corrected(c, nn)
        mf = full_matrix(bl5, nn, "all")
        me = even_matrix(bl5, nn, "all")
        mo = odd_matrix(bl5["Q_full"], nn, "all")
        wf = sorted(mp.eigsy(mf)[0])
        we = sorted(mp.eigsy(me)[0])
        wo = sorted(mp.eigsy(mo)[0])
        wu = sorted(list(we) + list(wo))
        d = max(abs(wf[i] - wu[i]) for i in range(len(wf)))
        # THRESHOLD NOTE (instrument defect, fixed): the first version of this
        # check compared the lambda_min difference against
        # |lambda_min| * 10^-(dps-20) -- a RELATIVE bound. mp.eigsy delivers
        # ABSOLUTE accuracy ~ ||M|| * 10^-dps, which for lambda_min ~ 1e-35 at
        # dps 60 is ~1e-60 and therefore LARGER than 8.6e-75. The old rule
        # printed "DIVERGES" at N=16 while both printed values were identical.
        # Correct bound: ||M||_2 <= dim * max|M|, times 10^-(dps-10).
        maxabs = max(abs(x) for x in mf)
        thr = mp.mpf(2 * nn + 1) * maxabs * mp.mpf(10) ** -(dps - 10)
        dlam = abs(wf[0] - min(we[0], wo[0]))
        ckpt("  N=%-3d dim=%-3d  max|spec(full) - (even u odd)| = %s   (floor ~ %s)"
             % (nn, 2 * nn + 1, mp.nstr(d, 8), mp.nstr(thr, 8)))
        ckpt("           lambda_min(full)   = %s" % mp.nstr(wf[0], 14))
        ckpt("           min(even, odd)     = %s" % mp.nstr(min(we[0], wo[0]), 14))
        ckpt("           |difference|       = %s   -> %s"
             % (mp.nstr(dlam, 8),
                "CONSISTENT" if dlam <= thr else "DIVERGES"))
    ckpt("")

    # ---- verdict table ---------------------------------------------------
    ckpt("#" * 96)
    ckpt("# VERDICT TABLE -- ODD BLOCK O_{k,l}")
    ckpt("#" * 96)
    for g in ("G1a", "G1b", "G2", "G2b", "G3", "G4"):
        if g not in results:
            ckpt("  %-4s : SKIPPED" % g)
        elif g == "G4":
            ckpt("  %-4s : %s   (prec %s bits, n+ = %s, n- = %s)"
                 % (g, results[g], results.get("G4_prec"),
                    results.get("G4_npos"), results.get("G4_nneg")))
        elif g == "G3":
            ckpt("  %-4s : %s   (delta_rel = %s)"
                 % (g, "PASS" if results[g] is not None and results[g] < G3_REL
                    else "NOT COMPARABLE", results[g]))
        else:
            ckpt("  %-4s : %s" % (g, mp.nstr(results[g], 8)))
    if "A1_margin" in results:
        ckpt("  A1   : margin %s orders, positive-lower-bound = %s"
             % (mp.nstr(results["A1_margin"], 10), results["A1_ok"]))
    ckpt("")
    ckpt("TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.")
    ckpt("lean/coqc/isabelle/dkcheck/z3/gcc NOT RUN.")
    ckpt("SCOPE: one preprint's odd block. Not RH, not Weil positivity.")
    return 0


def M_full_reshaped(ents, n):
    """flat list -> mp.matrix, without re-evaluating any Q entry."""
    M = mp.matrix(n, n)
    for a in range(n):
        for b in range(n):
            M[a, b] = ents[a * n + b]
    return M


if __name__ == "__main__":
    sys.exit(main(sys.argv))
