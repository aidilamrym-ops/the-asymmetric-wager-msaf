# -*- coding: utf-8 -*-
"""Capture the FULL certified spectrum of the Guinand-Weil matrix at (c, N).

WHY THIS RUN EXISTS
-------------------
Every prior A2 run (gw_opt_b_arb.py, gw_odd_validate.py, gw_even_arb.py) read
ONLY lambda_min and the inertia out of flint.arb_mat.eig. Opsi (d) -- Montgomery
pair correlation -- needs all 2N+1 eigenvalues, each with a rigorous radius.

PRE-REGISTERED GATE G-M0 (brain #1001630, written BEFORE this script ran)
-------------------------------------------------------------------------
  G-M0a  all eigenvalues finite
  G-M0b  all eigenvalues rigorously POSITIVE -> must reproduce the certified
         inertia 401/0. Any eigenvalue whose ball contains 0 counts as
         indeterminate and FAILS the gate.
  G-M0c  eigenvalues strictly increasing after sorting
  G-M0d  |sum(lam) - trace(M)| / |trace(M)| < 1e-300
  G-M0e  |sum(lam^2) - ||M||_F^2| / ||M||_F^2 < 1e-300
  Failure -> ABNO: no statistics are computed at all.

HONEST LIMIT OF G-M0d/G-M0e: both moments are dominated by the LARGEST
eigenvalues, so they are insensitive to the smallest ones. The per-eigenvalue
positivity test (G-M0b) is what actually certifies the tiny levels; G-M0d/e
check the COUNT and the bulk. These are consistency checks of ONE solver
(arb_mat.eig wraps acb_mat.eig) -- NOT independent evidence.

WHAT THIS IS NOT
----------------
Not RH, not Weil positivity, not prime counting, not factorisation; the source
preprint disclaims all four. "Certified" here means an arb ball enclosure at
the stated precision, never an absolute truth.

TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.
lean / coqc / isabelle / dkcheck / z3 / gcc NOT RUN -- no proof assistant was
involved and nothing here claims to be one.

usage:
    python gw_spectrum_arb.py 100 200 400 2048 vdhoeven_mourrain \
        --load gw_matrix_100_200_dps400.json --save-out gw_spectrum_100_200.json
"""

import json
import sys
import time

import mpmath as mp


def ckpt(msg):
    print(msg, flush=True)


def peak_mb():
    try:
        import psutil
        return psutil.Process().memory_info().peak_wset / 1e6
    except Exception:
        pass
    try:
        import ctypes

        class PMC(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_uint32),
                ("PageFaultCount", ctypes.c_uint32),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        ctypes.windll.psapi.GetProcessMemoryInfo(
            ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
        return pmc.PeakWorkingSetSize / 1e6
    except Exception:
        return float("nan")


def arb_mid_str(ball, digits):
    """Midpoint of an arb/acb component as a decimal string."""
    return ball.mid().str(digits, radius=False)


def arb_rad_str(ball):
    """Radius of an arb as a decimal string (0 when exact)."""
    try:
        return ball.rad().mid().str(40, radius=False)
    except Exception:
        return "0"


def main(argv):
    flags = [a for a in argv[1:] if a.startswith("--")]
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) < 5:
        print(__doc__)
        return 2
    c, N, dps, prec = int(args[0]), int(args[1]), int(args[2]), int(args[3])
    algo = args[4]
    n = 2 * N + 1

    if "--load" not in argv:
        raise SystemExit("--load <matrix.json> is required (rebuild is slow)")
    load_path = argv[argv.index("--load") + 1]
    out_path = None
    if "--save-out" in argv:
        out_path = argv[argv.index("--save-out") + 1]

    ckpt("#" * 96)
    ckpt("# OMEGA OPSI (d) PREREQ -- FULL SPECTRUM CAPTURE, (c, N, dps, prec) = (%d, %d, %d, %d)"
         % (c, N, dps, prec))
    ckpt("# algo = %s   dimension = %d   -- GATE G-M0 pre-registered (brain #1001630)" % (algo, n))
    ckpt("#" * 96)
    ckpt("")
    ckpt("GATE G-M0 (pre-registered, decided before any eigenvalue existed):")
    ckpt("  G-M0a  all eigenvalues finite")
    ckpt("  G-M0b  all rigorously POSITIVE (must reproduce certified inertia %d/0)" % n)
    ckpt("  G-M0c  strictly increasing after sort")
    ckpt("  G-M0d  |sum(lam) - trace| / |trace| < 1e-300")
    ckpt("  G-M0e  |sum(lam^2) - ||M||_F^2| / ||M||_F^2 < 1e-300")
    ckpt("  NOTE   G-M0d/G-M0e are dominated by the LARGEST eigenvalues; the")
    ckpt("         per-level positivity test G-M0b is what certifies the small")
    ckpt("         levels. All three are ONE solver's self-consistency, not")
    ckpt("         independent evidence.")
    ckpt("  Failure -> ABORT: no Opsi (d) statistics are computed.")
    ckpt("")

    # ---- stage 1: load the saved matrix -----------------------------------
    ckpt("=" * 96)
    ckpt("STAGE 1 -- load saved matrix")
    ckpt("=" * 96)
    t = time.time()
    with open(load_path, "r", encoding="utf-8") as fh:
        blob = json.load(fh)
    if int(blob["c"]) != c or int(blob["N"]) != N:
        raise SystemExit("load provenance mismatch: saved c,N = %d,%d"
                         % (blob["c"], blob["N"]))
    entry_strings = blob["entries"]
    if len(entry_strings) != n * n:
        raise SystemExit("entry count %d != %d" % (len(entry_strings), n * n))
    ckpt("  loaded %d entries from %s in %.1f s" % (len(entry_strings), load_path,
                                                    time.time() - t))
    ckpt("  provenance: c=%d, N=%d, dps=%d" % (blob["c"], blob["N"], blob["dps"]))

    # LANDMINE: string -> number conversion honours the CURRENT precision.
    # Set dps before parsing any entry into mpf (same class of bug as
    # gw_qinf.py:47 and the rho_actual truncation in gw_opt_b_arb.py).
    mp.mp.dps = dps
    ckpt("  mp.mp.dps set to %d BEFORE parsing entries -> mpf" % mp.mp.dps)

    # ---- stage 2: build arb_mat at prec bits -------------------------------
    ckpt("")
    ckpt("=" * 96)
    ckpt("STAGE 2 -- flint.arb_mat parse at prec %d bits" % prec)
    ckpt("=" * 96)
    from flint import arb_mat, arb, ctx
    # LANDMINE (same class): ctx.prec governs EVERY arb built from a string.
    ctx.prec = prec
    ckpt("  flint.ctx.prec set to %d BEFORE building any arb from a string" % ctx.prec)

    t = time.time()
    M = arb_mat(n, n)
    for i in range(n):
        row = i * n
        for j in range(n):
            M[i, j] = arb(entry_strings[row + j])
    t_parse = time.time() - t
    ckpt("  arb_mat built: %.1f s   %dx%d at prec=%d bits" % (t_parse, n, n, prec))

    # moments of the MATRIX itself, in arb (same precision as the solve)
    t = time.time()
    tr = arb(0)
    frob = arb(0)
    for i in range(n):
        tr += M[i, i]
        for j in range(n):
            frob += M[i, j] * M[i, j]
    ckpt("  matrix moments (arb): %.1f s" % (time.time() - t))
    ckpt("    trace(M)      = %s" % arb_mid_str(tr, 30))
    ckpt("    ||M||_F^2     = %s" % arb_mid_str(frob, 30))
    ckpt("")

    # ---- stage 3: full eig -------------------------------------------------
    ckpt("=" * 96)
    ckpt("STAGE 3 -- flint.arb_mat.eig  algorithm = %s" % algo)
    ckpt("=" * 96)
    t = time.time()
    ev = M.eig(algorithm=algo)
    t_eig = time.time() - t
    if isinstance(ev, tuple):
        ckpt("  (eig returned a tuple of length %d; using element 0)" % len(ev))
        ev = ev[0]
    n_ev = len(ev)
    ckpt("  %.1f s   %d eigenvalues returned   peak RSS %.0f MB" % (t_eig, n_ev, peak_mb()))
    ckpt("")

    # ---- gate G-M0 ---------------------------------------------------------
    ckpt("=" * 96)
    ckpt("GATE G-M0 -- EVALUATION")
    ckpt("=" * 96)
    results = {}
    ok = True

    # G-M0a: finite
    bad = 0
    for w in ev:
        try:
            if not (w.real.mid().is_finite() and w.imag.mid().is_finite()):
                bad += 1
        except Exception:
            bad += 1
    results["G-M0a_finite"] = (bad == 0)
    ckpt("  G-M0a  finite eigenvalues            : %s   (non-finite = %d)"
         % ("PASS" if bad == 0 else "FAIL", bad))
    ok = ok and bad == 0

    # G-M0b: rigorous positivity / inertia
    n_pos = sum(1 for w in ev if w.real > 0)
    n_neg = sum(1 for w in ev if w.real < 0)
    n_ind = n_ev - n_pos - n_neg
    im_max = max(abs(w.imag) for w in ev)
    results["G-M0b_inertia"] = (n_pos == n and n_neg == 0 and n_ind == 0)
    ckpt("  G-M0b  inertia (rigorous)            : n+ = %d, n- = %d, indeterminate = %d"
         % (n_pos, n_neg, n_ind))
    ckpt("           expected from certified runs: n+ = %d, n- = 0" % n)
    ckpt("           -> %s" % ("PASS" if results["G-M0b_inertia"] else "FAIL"))
    ckpt("           max |Im| (float)            : %s" % repr(float(im_max)))
    ok = ok and results["G-M0b_inertia"]

    # G-M0c: strictly increasing after sort
    re_mid = [w.real.mid().str(60, radius=False) for w in ev]
    vals = sorted(mp.mpf(s) for s in re_mid)
    n_dup = sum(1 for k in range(len(vals) - 1) if vals[k + 1] <= vals[k])
    results["G-M0c_strict"] = (n_dup == 0 and len(vals) == n)
    ckpt("  G-M0c  strictly increasing           : %s   (violations = %d, count = %d)"
         % ("PASS" if results["G-M0c_strict"] else "FAIL", n_dup, len(vals)))
    ok = ok and results["G-M0c_strict"]

    # G-M0d / G-M0e: moments
    lam_sum = arb(0)
    lam_sq = arb(0)
    for w in ev:
        r = w.real
        lam_sum += r
        lam_sq += r * r
    d_tr = abs(lam_sum - tr) / abs(tr)
    d_fr = abs(lam_sq - frob) / abs(frob)
    log_d_tr = mp.log10(mp.mpf(d_tr.mid().str(30, radius=False))) if d_tr != 0 else mp.mpf("-inf")
    log_d_fr = mp.log10(mp.mpf(d_fr.mid().str(30, radius=False))) if d_fr != 0 else mp.mpf("-inf")
    results["G-M0d_trace"] = (log_d_tr < -300)
    results["G-M0e_frob"] = (log_d_fr < -300)
    ckpt("  G-M0d  |sum(lam)-trace|/|trace|      : 1e%s   -> %s"
         % (mp.nstr(log_d_tr, 8), "PASS" if results["G-M0d_trace"] else "FAIL"))
    ckpt("  G-M0e  |sum(lam^2)-||M||F^2|/...     : 1e%s   -> %s"
         % (mp.nstr(log_d_fr, 8), "PASS" if results["G-M0e_frob"] else "FAIL"))
    ckpt("           (both moments dominated by the LARGEST levels -- they check")
    ckpt("            the count and the bulk, not the small levels)")
    ok = ok and results["G-M0d_trace"] and results["G-M0e_frob"]

    # radius quality per level
    worst_rel = mp.mpf(0)
    worst_idx = -1
    for k, w in enumerate(ev):
        r = w.real
        rad = mp.mpf(r.rad().mid().str(30, radius=False))
        mid = mp.mpf(r.mid().str(60, radius=False))
        if mid != 0:
            rel = rad / abs(mid)
            if rel > worst_rel:
                worst_rel = rel
                worst_idx = k
    ckpt("  radius worst |rad|/|mid|             : 1e%s   (level index %d)"
         % (mp.nstr(mp.log10(worst_rel), 8) if worst_rel > 0 else "-inf", worst_idx))

    verdict_g0 = "G-M0 PASS" if ok else "G-M0 FAIL -- ABORT, NO STATISTICS"
    ckpt("")
    ckpt("  >>> %s <<<" % verdict_g0)
    ckpt("")

    # ---- spectrum summary (diagnostic, printed regardless) -----------------
    ckpt("=" * 96)
    ckpt("SPECTRUM SUMMARY (diagnostic)")
    ckpt("=" * 96)
    if len(vals) == n:
        lo, hi = vals[0], vals[-1]
        ckpt("  lambda_min = %s" % mp.nstr(lo, 30))
        ckpt("  lambda_max = %s" % mp.nstr(hi, 30))
        ckpt("  spread     = %s orders   (pre-registered expectation: ~295)"
             % mp.nstr(mp.log10(hi / lo), 12))
        # decade histogram in log10
        import math
        buckets = {}
        for v in vals:
            e = int(math.floor(mp.log10(v))) if v > 0 else None
            buckets[e] = buckets.get(e, 0) + 1
        ckpt("  levels per decade (log10 bin, count):")
        for e in sorted(k for k in buckets if k is not None):
            ckpt("     10^%+4d : %3d" % (e, buckets[e]))
        if None in buckets:
            ckpt("     (non-positive levels: %d)" % buckets[None])
    ckpt("")

    # ---- save --------------------------------------------------------------
    if out_path:
        digits = 60
        payload = {
            "c": c, "N": N, "dps": dps, "prec": prec, "algo": algo,
            "n": n, "eig_seconds": round(t_eig, 3),
            "gate_GM0": {k: bool(v) for k, v in results.items()},
            "gate_verdict": verdict_g0,
            "inertia": {"n_pos": n_pos, "n_neg": n_neg, "indeterminate": n_ind},
            "im_max_float": float(im_max),
            "trace_mid": arb_mid_str(tr, 60),
            "frob2_mid": arb_mid_str(frob, 60),
            "eig": [{"re": arb_mid_str(w.real, digits),
                     "re_rad": arb_rad_str(w.real),
                     "im_abs": abs(w.imag).mid().str(20, radius=False)}
                    for w in ev],
        }
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        import os
        ckpt("saved -> %s  (%.1f MB, %d eigenvalues)"
             % (out_path, os.path.getsize(out_path) / 1048576.0, len(ev)))
    ckpt("")
    ckpt("peak RSS over run = %.0f MB" % peak_mb())
    ckpt("TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.")
    ckpt("lean/coqc/isabelle/dkcheck/z3/gcc NOT RUN.")
    ckpt("SCOPE: one preprint's matrix. Not RH, not Weil positivity, not prime counting.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
