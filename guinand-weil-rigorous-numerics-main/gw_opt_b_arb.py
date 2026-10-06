# -*- coding: utf-8 -*-
"""OMEGA A1 + A2 for the (c, N) = (100, 200) Guinand-Weil matrix, 401 x 401.

WHAT THIS PRODUCES
------------------
A1  parse the corrected matrix into flint.arb at `prec_bits`, then propagate a
    measured per-entry error rho_actual (from dps-doubling, two independent
    precisions) through Weyl:

        ||dM||_2 <= sqrt(||dM||_1 ||dM||_inf) = n * rho
        lam_min_true >= lam_min_parse - n * rho

    The certified tolerance is rho* = lam_min_parse / n.

A2  hand the same matrix to flint.arb_mat.eig, a validated interval
    eigen-solver, and read off a rigorous enclosure plus an inertia count.

CAVEAT THAT MUST TRAVEL WITH EVERY NUMBER HERE (printed first, on purpose)
--------------------------------------------------------------------------
python-flint 0.9.0 exposes NO psi / digamma / polygamma / hyp2f1 / lerchphi,
so the archimedean block cannot be evaluated inside arb. The entries therefore
arrive as DECIMAL TEXT. The radius arb assigns on parsing covers FLINT's own
rounding ONLY -- it does NOT cover the mpmath origin of those digits.

Hence:
  * A2's enclosure is rigorous OVER THE MATRIX AS HANDED to flint.
  * A1's certificate depends on rho_actual, measured by dps-doubling. mpmath is
    NOT interval arithmetic, so an error stable across both precisions would not
    show up in the difference. That link is an ESTIMATE and is labelled as one.

NEITHER route is independent of the other: arb_mat.eig wraps acb_mat.eig. Both
are independent only of mpmath.

TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.
lean / coqc / isabelle / dkcheck / z3 / gcc NOT RUN. This is automatic verified
numerics, not proof-assistant verification, and must never be cited as such.

SCOPE: a measurement on one preprint's matrix. Not the Riemann Hypothesis, not
Weil positivity, not prime counting, not factorisation; the source preprint
disclaims all four.

usage:
    python gw_opt_b_arb.py 13 4 60 1024 vdhoeven_mourrain --entry-error 40
    python gw_opt_b_arb.py 100 200 400 1024 vdhoeven_mourrain --entry-error 340
    python gw_opt_b_arb.py 100 200 400 1024 rump --entry-error 340
"""

import sys
import time

import mpmath as mp


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


def ckpt(msg):
    print(msg, flush=True)


def build_full(c, N, dps):
    """corrected blocks -> plain (2N+1)x(2N+1) real matrix, at precision dps."""
    from gw_corrected_eig import build_blocks_corrected
    from gw_full_vs_even import full_matrix
    # gw_qinf.py:47 sets mp.mp.dps = 40 at module level and is imported here,
    # so dps must be set AFTER the import, never before.
    mp.mp.dps = dps
    t = time.time()
    bl = build_blocks_corrected(c, N)
    t_build = time.time() - t
    t = time.time()
    M = full_matrix(bl, N, "all")
    return M, t_build, time.time() - t


def max_abs_diff(A, B):
    n = len(A)
    best = mp.mpf(0)
    at = (0, 0)
    for i in range(n):
        for j in range(n):
            d = abs(A[i, j] - B[i, j])
            if d > best:
                best, at = d, (i, j)
    return best, at


def save_matrix(path, c, N, dps, dps_lo, rho_actual, entry_strings):
    """Persist the decimal entries plus the measured entry error, so that a
    re-run at a different arb precision need not rebuild both matrices."""
    import json
    t = time.time()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"c": c, "N": N, "dps": dps, "dps_lo": dps_lo,
                   "rho_actual": mp.nstr(rho_actual, mp.mp.dps),
                   "entries": entry_strings}, fh)
    ckpt("  saved -> %s  (%.1f s, %d entries)"
         % (path, time.time() - t, len(entry_strings)))


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if len(args) < 5:
        print(__doc__)
        return 2
    c, N, dps, prec, algo = (int(args[0]), int(args[1]), int(args[2]),
                             int(args[3]), args[4])
    dps_lo = None
    # "--entry-error 340" : the value is the next argv element
    if "--entry-error" in argv:
        idx = argv.index("--entry-error")
        if idx + 1 >= len(argv):
            print("--entry-error requires a dps value")
            return 2
        dps_lo = int(argv[idx + 1])

    n = 2 * N + 1

    load_path = None
    if "--load" in argv:
        load_path = argv[argv.index("--load") + 1]
    save_path = None
    if "--save" in argv:
        save_path = argv[argv.index("--save") + 1]

    ckpt("#" * 96)
    ckpt("# OMEGA A1 + A2 -- (c, N, dps, prec, algo) = (%d, %d, %d, %d, %s)"
         % (c, N, dps, prec, algo))
    ckpt("# dimension = %d x %d" % (n, n))
    ckpt("#" * 96)
    ckpt("")
    ckpt("CAVEAT (must accompany every number below):")
    ckpt("  python-flint 0.9.0 exposes NO psi/digamma/polygamma/hyp2f1/lerchphi,")
    ckpt("  so the archimedean block cannot be computed inside arb. The entries")
    ckpt("  arrive as DECIMAL TEXT. The arb parse radius covers FLINT rounding")
    ckpt("  ONLY -- it does NOT cover the mpmath origin of those digits.")
    ckpt("  A2 is rigorous over the matrix as handed; A1 rests on a dps-doubling")
    ckpt("  ESTIMATE for rho_actual (mpmath is not interval arithmetic).")
    ckpt("  arb_mat.eig wraps acb_mat.eig -> A1 and A2 are NOT independent of")
    ckpt("  each other; both are independent only of mpmath.")
    ckpt("  TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.")
    ckpt("  lean/coqc/isabelle/dkcheck/z3/gcc NOT RUN -- not proof-assistant verified.")
    ckpt("")

    # ---- stage 1: measured per-entry error (A1's rho_actual) --------------
    rho_actual = None
    M = None
    entry_strings = None

    if load_path is not None:
        import json
        ckpt("=" * 96)
        ckpt("STAGE 1 -- SKIPPED: loading saved matrix from %s" % load_path)
        ckpt("=" * 96)
        t = time.time()
        with open(load_path, "r", encoding="utf-8") as fh:
            blob = json.load(fh)
        # LANDMINE: mp.mpf(str) rounds to the CURRENT precision, and mp.mp.dps
        # is still the mpmath default (15) here because build_full() -- the only
        # place that sets it -- is never called on the --load path. Parsing
        # rho_actual before raising precision silently truncated it to double
        # accuracy (relative error 4.4e-17). Set precision FIRST.
        mp.mp.dps = int(blob["dps"])
        entry_strings = blob["entries"]
        rho_actual = mp.mpf(blob["rho_actual"])
        ckpt("  loaded %d entries at mp.mp.dps=%d, rho_actual = %s   (%.1f s)"
             % (len(entry_strings), mp.mp.dps, mp.nstr(rho_actual, 30),
                time.time() - t))
        ckpt("  provenance: c=%d, N=%d, dps=%d, dps_lo=%s"
             % (blob["c"], blob["N"], blob["dps"], blob.get("dps_lo")))
        ckpt("")

    elif dps_lo is not None:
        ckpt("=" * 96)
        ckpt("STAGE 1 -- MEASURED PER-ENTRY ERROR (dps %d vs dps %d)" % (dps_lo, dps))
        ckpt("=" * 96)
        t = time.time()
        M_lo, tb_lo, ta_lo = build_full(c, N, dps_lo)
        ckpt("  reference matrix at dps %d: build %.1f s, assemble %.1f s, RSS %.0f MB"
             % (dps_lo, tb_lo, ta_lo, peak_mb()))
        t = time.time()
        M, tb, ta = build_full(c, N, dps)
        ckpt("  candidate matrix at dps %d: build %.1f s, assemble %.1f s, RSS %.0f MB"
             % (dps, tb, ta, peak_mb()))
        ckpt("  measuring max |M(%d) - M(%d)| over %d entries ..."
             % (dps, dps_lo, n * n))
        t = time.time()
        rho_actual, at = max_abs_diff(M, M_lo)
        row, col = at
        ckpt("  max entry = %s" % mp.nstr(max(abs(M[i, j]) for i in range(n)
                                              for j in range(n)), 14))
        ckpt("  rho_actual = %s   at (%d, %d) = index (%+d, %+d)"
             % (mp.nstr(rho_actual, 30), row, col, row - N, col - N))
        ckpt("  measurement took %.1f s" % (time.time() - t))
        del M_lo
        entry_strings = [mp.nstr(M[i, j], mp.mp.dps) for i in range(n)
                         for j in range(n)]
        if save_path:
            save_matrix(save_path, c, N, dps, dps_lo, rho_actual, entry_strings)
        ckpt("")
    else:
        ckpt("!! --entry-error NOT given: A1 certificate will be INCOMPLETE.")
        ckpt("")
        M, tb, ta = build_full(c, N, dps)
        ckpt("  matrix at dps %d: build %.1f s, assemble %.1f s"
             % (dps, tb, ta))
        ckpt("")
    # ---- stage 2: arb parse (A1) -----------------------------------------
    import flint
    flint.ctx.prec = prec

    ckpt("=" * 96)
    ckpt("STAGE 2 -- A1: arb PARSE + WEYL PROPAGATION (prec %d bits)" % prec)
    ckpt("=" * 96)
    t = time.time()
    if entry_strings is None:
        entry_strings = [mp.nstr(M[i, j], mp.mp.dps) for i in range(n)
                         for j in range(n)]
    vals = entry_strings
    t_str = time.time() - t
    t = time.time()
    A = flint.arb_mat(n, n, vals)
    t_parse = time.time() - t
    rmax = flint.arb(0)
    for i in range(n):
        for j in range(n):
            if A[i, j].rad() > rmax:
                rmax = A[i, j].rad()
    ckpt("  decimal strings  : %.1f s   (%d entries, %d digits each)"
         % (t_str, n * n, mp.mp.dps))
    ckpt("  arb_mat built    : %.1f s   %dx%d at prec=%d bits"
         % (t_parse, n, n, prec))
    ckpt("  parse radius max : %s" % rmax)
    ckpt("  (this radius = FLINT rounding ONLY, per the caveat)")
    ckpt("  peak RSS         : %.0f MB" % peak_mb())
    ckpt("")

    # ---- stage 3: interval eigen-solver (A2) ------------------------------
    ckpt("=" * 96)
    ckpt("STAGE 3 -- A2: flint.arb_mat.eig  algorithm = %s" % algo)
    ckpt("=" * 96)
    res_ok = False
    try:
        t = time.time()
        ev = A.eig(algorithm=algo)
        t_eig = time.time() - t
        if isinstance(ev, tuple):
            ckpt("  (eig returned a tuple of length %d; using element 0)" % len(ev))
            ev = ev[0]
        res_ok = True
        n_ev = len(ev)
        ckpt("  %.1f s   %d eigenvalues returned   peak RSS %.0f MB"
             % (t_eig, n_ev, peak_mb()))
        best = min(ev, key=lambda w: float(w.real))
        re_part = best.real
        n_pos = sum(1 for w in ev if w.real > 0)
        n_neg = sum(1 for w in ev if w.real < 0)
        n_ind = n_ev - n_pos - n_neg
        ckpt("  smallest by Re    : %s" % best)
        ckpt("  Im (float)        : %s" % repr(float(abs(best.imag))))
        ckpt("  Re > 0 (rigorous) : %s" % bool(re_part > 0))
        ckpt("  Re < 0 (rigorous) : %s" % bool(re_part < 0))
        ckpt("  Re contains 0     : %s" % bool(re_part.contains(0)))
        ckpt("  INERTIA (rigorous): n+ = %d, n- = %d, indeterminate = %d   (dim %d)"
             % (n_pos, n_neg, n_ind, n_ev))
        verdict = ("ENCLOSED STRICTLY POSITIVE"
                   if (re_part > 0 and not re_part.contains(0))
                   else ("ENCLOSED NEGATIVE" if (re_part < 0 and not re_part.contains(0))
                         else "STRADDLES / INDETERMINATE"))
        ckpt("  A2 VERDICT        : %s" % verdict)
    except Exception as exc:
        ckpt("  A2 FAILED after %.0f s: %s: %s"
             % (0.0, type(exc).__name__, exc))
        verdict = "A2 FAILED"
    ckpt("")

    # ---- stage 4: A1 certificate -----------------------------------------
    ckpt("=" * 96)
    ckpt("STAGE 4 -- A1 CERTIFICATE")
    ckpt("=" * 96)
    if res_ok and rho_actual is not None:
        lam_parse = re_part
        lam_float = float(lam_parse)
        ckpt("  lam_min(parse)              = %s" % lam_parse)
        ckpt("  rho_actual (dps-doubling)   = %s   [ESTIMATE]" % mp.nstr(rho_actual, 30))
        n_rho = mp.mpf(n) * rho_actual
        ckpt("  n * rho_actual (n = %d)      = %s" % (n, mp.nstr(n_rho, 30)))
        lower = mp.mpf(lam_float) - n_rho
        ckpt("  lam_min - n*rho             = %s" % mp.nstr(lower, 30))
        rho_star = mp.mpf(lam_float) / n
        ckpt("  rho* = lam_min / n          = %s" % mp.nstr(rho_star, 30))
        ratio = rho_star / rho_actual
        ckpt("  rho* / rho_actual           = %s" % mp.nstr(ratio, 14))
        marg = mp.log10(ratio) if ratio > 0 else mp.mpf("-inf")
        ckpt("  CERTIFIED MARGIN            = %s orders" % mp.nstr(marg, 10))
        ckpt("")
        ckpt("  A1 VERDICT                  : %s"
             % ("CERTIFIED (subject to the dps-doubling estimate)"
                if lower > 0 else
                "NOT CERTIFIED -- n*rho exceeds lam_min"))
    else:
        ckpt("  INCOMPLETE: need both the eig result and a measured rho_actual.")
        ckpt("  res_ok = %s, rho_actual = %s" % (res_ok, rho_actual))
    ckpt("")
    ckpt("peak RSS over run = %.0f MB" % peak_mb())
    ckpt("TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.")
    ckpt("lean/coqc/isabelle/dkcheck/z3/gcc NOT RUN.")
    ckpt("SCOPE: one preprint's matrix. Not RH, not Weil positivity, not prime counting.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
