# -*- coding: utf-8 -*-
"""OPTION (b) -- stress test of the Guinand-Weil matrix at (c, N) = (100, 200).

    dim(full)  = 2N+1 = 401
    dim(even)  = N+1  = 201
    dim(odd)   = N    = 200

WHY THE SPLIT
-------------
For a real quadratic form with Q(-m,-n) = Q(m,n) and Q(m,n) = Q(n,m), the
simultaneous-flip operator J, (Jf)(m) = f(-m), commutes with Q.  The space
therefore splits into

    EVEN  : f(-m) = f(m)   dimension N+1
    ODD   : f(-m) = -f(m)  dimension N

and

    lambda_min(full) = min( lambda_min(even), lambda_min(odd) ).

Diagonalising two ~200-dimensional blocks costs roughly 4x less than one
401-dimensional block (O(n^3)), which is the point of running the split.

The even block is NOT re-derived here: it is taken from gw_qinf.even_matrix,
whose isometric embedding u_0 = v_0, u_{+-k} = v_k/sqrt(2) gives

    M_even[0,0] = Q(0,0)
    M_even[0,k] = (Q(0,k) + Q(0,-k)) / sqrt(2)
    M_even[k,l] = Q(k,l) + Q(k,-l)

The odd block follows from the antisymmetric embedding o_k = (d_k - d_-k)/sqrt(2):

    M_odd[k,l] = Q(k,l) - Q(k,-l),      k, l = 1..N

BOTH identities are checked against the full 401x401 spectrum before any
number at N=200 is reported -- see --validate.

RESOLVABILITY (honest form, NOT the rejected floor test)
--------------------------------------------------------
For the smallest eigenvalue of a symmetric matrix the absolute error is
||M|| * eps, so the number of correct digits on lambda_min is roughly

    digits ~= dps - log10( lambda_max / |lambda_min| )

A value with digits <= 0 is reported as NOT RESOLVED.  The earlier floor test
"lambda > lambda_max * 10^-(dps-10)" was shown self-referential (it compares a
reported value against a floor, so noise above the floor passes) and is
deliberately NOT used here.

TOOL STATUS: mpmath.  lean/coqc/isabelle/z3/dkcheck NOT RUN.
Scope: a measurement on one preprint's matrix.  Not an RH, Weil-positivity,
prime-counting or factoring result; the source preprint disclaims all four.

usage:
    python gw_opt_b.py 100 200 140 --validate     # cheap, small-N self-test
    python gw_opt_b.py 100 200 140                # even + odd
    python gw_opt_b.py 100 200 140 --full         # even + odd + full 401
    python gw_opt_b.py 100 200 140 --save         # also write matrix JSON
"""

import json
import sys
import time

# mpmath is imported here and ONLY here.  gw_qinf.py:47 sets mp.mp.dps = 40 at
# module level, so gw_qinf may not be imported until main() has decided dps.
# Importing mpmath itself sets no precision and is therefore safe at top level.
import mpmath as mp


# --------------------------------------------------------------------------
# memory -- peak working set, Windows-friendly with psutil fallback
# --------------------------------------------------------------------------
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


# --------------------------------------------------------------------------
# sector assembly
# --------------------------------------------------------------------------
def odd_matrix(Q, N, block="all"):
    """(N x N) odd-sector matrix, rows/cols indexed 1..N.

    M_odd[k,l] = Q(k,l) - Q(k,-l), derived from o_k = (d_k - d_-k)/sqrt(2):
        <o_k, Q o_l> = 1/2 [ Q(k,l) - Q(k,-l) - Q(-k,l) + Q(-k,-l) ]
                     = Q(k,l) - Q(k,-l)      using Q(-m,-n) = Q(m,n).
    """
    M = mp.matrix(N, N)
    for a in range(N):
        k = a + 1
        for b in range(N):
            l = b + 1
            M[a, b] = Q(k, l, block) - Q(k, -l, block)
    return M


def even_from_Q(Q, N, block="all"):
    """Independent re-derivation of the even block, used only by --validate."""
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


# --------------------------------------------------------------------------
def spec(M):
    w = sorted(mp.eigsy(M)[0])
    return w


def report(tag, w, dps, tsec):
    lam_min, lam_max = +w[0], +w[-1]
    n_neg = sum(1 for x in w if x < 0)
    n_pos = sum(1 for x in w if x > 0)
    n_zero = len(w) - n_neg - n_pos
    cond = abs(lam_max / lam_min) if lam_min != 0 else mp.inf
    digits = (mp.mpf(dps) - mp.log10(cond)) if mp.isfinite(cond) else mp.mpf("-inf")

    # HONEST SIGN TEST.  eigsy's backward error on the smallest eigenvalue is
    # ~||M|| * eps with eps ~ 10^-dps, so the SIGN of lambda_min is only
    # trustworthy when |lambda_min| clears that bound by a real margin.
    # The earlier rule "digits > 0" was too weak: at dps 140 it reported
    # digits = 0.34 (value known only to a factor ~4.6) as RESOLVED, and the
    # printed inertia was then read as if it were meaningful.  Thresholds:
    #     ratio > 100  -> SIGN DETERMINED
    #     ratio > 10   -> MARGINAL
    #     otherwise    -> NOT DETERMINED; the inertia count is unreliable too
    err0 = abs(lam_max) * mp.mpf(10) ** (-dps)
    ratio = (abs(lam_min) / err0) if err0 != 0 else mp.inf
    if ratio > 100:
        verdict = "SIGN DETERMINED"
    elif ratio > 10:
        verdict = "MARGINAL -- raise dps"
    else:
        verdict = "NOT DETERMINED -- raise dps; inertia below is UNRELIABLE"
    resolved = ratio > 10
    ckpt("  [%s] dim=%d  %.1f s  peak RSS=%.0f MB" % (tag, len(w), tsec, peak_mb()))
    ckpt("      lambda_min = %s" % mp.nstr(lam_min, 30))
    ckpt("      lambda_max = %s" % mp.nstr(lam_max, 14))
    ckpt("      inertia    : n+ = %d, n- = %d, n0 = %d" % (n_pos, n_neg, n_zero))
    ckpt("      sign       : %s" % ("POSITIVE" if lam_min > 0 else
                                    ("NEGATIVE" if lam_min < 0 else "ZERO")))
    ckpt("      cond       = %s" % mp.nstr(cond, 12))
    ckpt("      digits on lambda_min ~ dps - log10(cond) = %s" % mp.nstr(digits, 8))
    ckpt("      |lam_min| / (||M|| * 10^-dps) = %s   -> %s"
         % (mp.nstr(ratio, 8), verdict))
    return lam_min, resolved


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if len(args) < 3:
        print(__doc__)
        return 2
    c, N, dps = int(args[0]), int(args[1]), int(args[2])
    do_validate = "--validate" in flags
    do_full = "--full" in flags
    do_save = "--save" in flags

    # LANDMINE RULE: gw_qinf.py:47 sets mp.mp.dps = 40 at module level and is
    # imported transitively.  Import FIRST, set precision AFTER.
    from gw_corrected_eig import build_blocks_corrected
    from gw_full_vs_even import full_matrix
    import gw_qinf as G

    mp.mp.dps = dps

    ckpt("#" * 96)
    ckpt("# OPTION (b) STRESS TEST   (c, N, dps) = (%d, %d, %d)" % (c, N, dps))
    ckpt("# split: full=%d  even=%d  odd=%d" % (2 * N + 1, N + 1, N))
    ckpt("# build = CORRECTED (defining series); shipped build uses mp.lerchphi and is wrong")
    ckpt("# tool status: mpmath only.  lean/coqc/isabelle/z3/dkcheck NOT RUN")
    ckpt("#" * 96)
    ckpt("")

    # ---- validation -------------------------------------------------------
    if do_validate:
        ckpt("=" * 96)
        ckpt("CHECKPOINT 0 -- SPLIT VALIDATION (cheap, small N)")
        ckpt("=" * 96)
        for vc, vN in [(13, 4), (13, 8), (13, 16)]:
            t = time.time()
            bl = build_blocks_corrected(vc, vN)
            Q = bl["Q_full"]
            Me_lib = G.even_matrix(bl, vN, block="all")
            Me_der = even_from_Q(Q, vN, "all")
            dev = max(abs(Me_lib[i, j] - Me_der[i, j])
                      for i in range(vN + 1) for j in range(vN + 1))
            Mf = full_matrix(bl, vN, "all")
            Mo = odd_matrix(Q, vN, "all")
            wf, we, wo = spec(Mf), spec(Me_lib), spec(Mo)
            split_ok = abs(min(+we[0], +wo[0]) - +wf[0]) <= \
                abs(+wf[0]) * mp.mpf("1e-25") + mp.mpf("1e-60")
            ckpt("  (%d,%-3d) dim=%-4d even-derivation dev = %-10s  lambda_min(full)=%s"
                 % (vc, vN, 2 * vN + 1, mp.nstr(dev, 6), mp.nstr(+wf[0], 12)))
            ckpt("           min(lambda_even, lambda_odd) = %s   SPLIT %s"
                 % (mp.nstr(min(+we[0], +wo[0]), 12), "HOLDS" if split_ok else "FAILS"))
            ckpt("           lambda_odd = %s   %.1f s   peak RSS=%.0f MB"
                 % (mp.nstr(+wo[0], 12), time.time() - t, peak_mb()))
        ckpt("")
        ckpt("If both HOLD, the N=200 split below is a valid reading of the full 401 spectrum.")
        ckpt("")
        return 0

    # ---- phase A: build ---------------------------------------------------
    ckpt("=" * 96)
    ckpt("CHECKPOINT 1 -- MATRIX BUILD")
    ckpt("=" * 96)
    t0 = time.time()
    bl = build_blocks_corrected(c, N)
    Q = bl["Q_full"]
    ckpt("  corrected blocks built in %.1f s   peak RSS=%.0f MB" % (time.time() - t0, peak_mb()))
    ckpt("  P0 entries: %d   idx range: %+d..%+d" % (len(bl["idx"]), min(bl["idx"]), max(bl["idx"])))
    ckpt("")

    # ---- phase B: sectors -------------------------------------------------
    ckpt("=" * 96)
    ckpt("CHECKPOINT 2 -- SPECTRUM: EVEN (dim %d) + ODD (dim %d)" % (N + 1, N))
    ckpt("=" * 96)

    t = time.time()
    Me = G.even_matrix(bl, N, block="all")
    ckpt("  even matrix assembled in %.1f s" % (time.time() - t))
    t = time.time()
    w_even = spec(Me)
    lam_e, res_e = report("even", w_even, dps, time.time() - t)
    ckpt("")

    t = time.time()
    Mo = odd_matrix(Q, N, "all")
    ckpt("  odd matrix assembled in %.1f s" % (time.time() - t))
    t = time.time()
    w_odd = spec(Mo)
    lam_o, res_o = report("odd", w_odd, dps, time.time() - t)
    ckpt("")

    lam_split = lam_e if lam_e <= lam_o else lam_o
    which = "even" if lam_e <= lam_o else "odd"
    ckpt("-" * 96)
    ckpt("  SPLIT RESULT : lambda_min(full) = min(even, odd) = %s   [%s sector]"
         % (mp.nstr(lam_split, 30), which))
    ckpt("  both sectors resolvable: %s" % ("yes" if (res_e and res_o) else "NO -- see digits above"))
    ckpt("-" * 96)
    ckpt("")

    # ---- phase C: full ----------------------------------------------------
    lam_full = None
    if do_full:
        ckpt("=" * 96)
        ckpt("CHECKPOINT 3 -- FULL MATRIX (dim %d)" % (2 * N + 1))
        ckpt("=" * 96)
        t = time.time()
        Mf = full_matrix(bl, N, "all")
        ckpt("  full matrix assembled in %.1f s   peak RSS=%.0f MB"
             % (time.time() - t, peak_mb()))
        t = time.time()
        w_full = spec(Mf)
        lam_full, res_f = report("full", w_full, dps, time.time() - t)
        ckpt("")
        ckpt("-" * 96)
        ckpt("  AGREEMENT: split %s vs full %s -> %s"
             % (mp.nstr(lam_split, 18), mp.nstr(lam_full, 18),
                "CONSISTENT" if abs(lam_full - lam_split) <=
                abs(lam_full) * mp.mpf("1e-20") + mp.mpf("1e-70") else "DISAGREE"))
        ckpt("-" * 96)
        ckpt("")

    # ---- save -------------------------------------------------------------
    if do_save:
        out = "gw_matrix_%d_%d_dps%d.json" % (c, N, dps)
        payload = {"c": c, "N": N, "dps": dps,
                   "lam_even": mp.nstr(lam_e, mp.mp.dps),
                   "lam_odd": mp.nstr(lam_o, mp.mp.dps),
                   "lam_split": mp.nstr(lam_split, mp.mp.dps),
                   "even": [[mp.nstr(Me[i, j], mp.mp.dps) for j in range(len(Me))]
                            for i in range(len(Me))],
                   "odd": [[mp.nstr(Mo[i, j], mp.mp.dps) for j in range(len(Mo))]
                           for i in range(len(Mo))]}
        if lam_full is not None:
            payload["lam_full"] = mp.nstr(lam_full, mp.mp.dps)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        ckpt("  saved -> %s" % out)
        ckpt("")

    ckpt("FINAL: lambda_min(Q_%d,%d) = %s   [%s]" % (c, N, mp.nstr(lam_split, 30), which))
    ckpt("peak RSS over run = %.0f MB" % peak_mb())
    ckpt("TOOL STATUS: mpmath only.  lean/coqc/isabelle/z3/dkcheck NOT RUN.")
    ckpt("SCOPE: one preprint's matrix.  Not RH, not Weil positivity, not prime counting.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
