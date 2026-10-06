# -*- coding: utf-8 -*-
"""Option (a): entrywise diff of our (c, N) matrix against the SOURCE PACKAGE's matrix.

PROVENANCE OF THE SOURCE SIDE
-----------------------------
  papers/2_guinand_weil_dictionary_tail_order/scripts/arb_ldlt_certify.py
  repo  : github.com/akivag613/connes-cvs-
  local : source_arb_ldlt_certify.py
  SHA256: b7fee730a83baedc860ca456547d2799ec10894a79edecc6d5612931b41509e3
          == script_sha256 recorded in
          artifacts/c100_N200_arb_ldlt_prec9000_provenance.json
  => byte-identical to the code that produced the published certificate
     n_pos = 401, n_neg = 0 at (c, N) = (100, 200), prec 9000 bits.

WHAT IS COMPARED
----------------
  source : tau = W02 - WR - Wp, built by THEIR build_arb_tau(), Arb balls at
           --prec bits (closed forms: digamma/trigamma at 1/4 + i*pi*n/L plus
           rigorously truncated geometric sums).
  ours   : Q = pole_A + divided difference of (alpha_L + psipr), built by
           gw_corrected_eig.build_blocks_corrected + gw_full_vs_even.full_matrix
           at dps --dps, handed over as decimal entries.

Both use row/col index a -> a - N, so entry (a, b) is the same matrix position.

PRE-REGISTERED DECISION RULE (written before the first diff run)
----------------------------------------------------------------
Let delta_rel = max|ours - source| / max|source|.
  V1  delta_rel < 1e-300        -> EQUIVALENT TO >=300 DIGITS  (hypothesis (c) dies)
  V2  1e-300 <= delta_rel < 1e-6-> DIFFERENT BEYOND ROUNDING
  V3  delta_rel >= 1e-6         -> STRUCTURALLY DIFFERENT
  V4  source code fails to run  -> NOT COMPARABLE (never report as IDENTICAL)
Secondary diagnostics, to CLASSIFY a nonzero delta rather than to change the
verdict: delta_flip = max|ours + source| (sign flip) and the median per-entry
ratio ours/source (global scale).

WHAT THIS IS NOT
----------------
A matrix-agreement measurement on one preprint's implementation. It is not the
Riemann Hypothesis, not Weil positivity, not prime counting, not factorisation;
the source preprint disclaims all four.

TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.
lean / coqc / isabelle / dkcheck / z3 / gcc NOT RUN. Not proof-assistant
verified, and this script does not claim to be.

usage:
    python gw_opt_a_diff.py 13 4 60 300
    python gw_opt_a_diff.py 100 200 400 2000 --load gw_matrix_100_200_dps400.json
"""

import hashlib
import importlib.util
import sys
import time

import mpmath as mp

SRC_PATH = "source_arb_ldlt_certify.py"
# Two pinned copies of that file exist in this repository's history; see
# THIRD_PARTY_SOURCES.md section 1 and OMEGA_CORE_CERTIFICATE.md section 1.
# This script prints which one it is actually running against; the hard gate
# (anything that is neither value fails) lives in gw_even_vs_src.py.
SRC_SHA256_VERBATIM = (
    "b7fee730a83baedc860ca456547d2799ec10894a79edecc6d5612931b41509e3",
    "12256 bytes, git b76be0d, byte-identical to script_sha256 upstream",
)
SRC_SHA256_SHIPPED = (
    "33617ce64b0e052c07873b196a3744f2f5142a4aaf7b4cfbe9e3de43d17c27bb",
    "12863 bytes, git bfa40dc, the 2026-09-30 resume copy that ran N=800",
)

V1_REL = mp.mpf(10) ** -300
V2_REL = mp.mpf(10) ** -6


def ckpt(msg):
    print(msg, flush=True)


def load_source_module():
    """Import the downloaded source script by path, without executing main()."""
    spec = importlib.util.spec_from_file_location("src_arb_ldlt", SRC_PATH)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load %s" % SRC_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def arb_to_mpf(ball, digits):
    """Midpoint of an arb ball as an mpf, at `digits` significant decimals."""
    s = ball.mid().str(digits, radius=False)
    return mp.mpf(s)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) < 4:
        print(__doc__)
        return 2
    c = int(args[0])
    N = int(args[1])
    dps = int(args[2])
    prec = int(args[3])
    n = 2 * N + 1

    load_path = None
    if "--load" in argv:
        load_path = argv[argv.index("--load") + 1]

    ckpt("#" * 96)
    ckpt("# OMEGA OPTION (a) -- ENTRYWISE DIFF vs SOURCE PACKAGE")
    ckpt("# (c, N, dps, prec) = (%d, %d, %d, %d)  dimension %d x %d"
         % (c, N, dps, prec, n, n))
    ckpt("# source: %s" % SRC_PATH)
    digest = hashlib.sha256(open(SRC_PATH, "rb").read()).hexdigest()
    if digest == SRC_SHA256_VERBATIM[0]:
        note = "verbatim upstream copy (%s)" % SRC_SHA256_VERBATIM[1]
    elif digest == SRC_SHA256_SHIPPED[0]:
        note = "documented local extension: %s" % SRC_SHA256_SHIPPED[1]
    else:
        note = "*** NOT A PINNED COPY -- do NOT trust this run ***"
    ckpt("# source sha256 = %s" % digest)
    ckpt("#                 %s" % note)
    ckpt("# byte-identity gate (fails on any third value): gw_even_vs_src.py")
    ckpt("#" * 96)
    ckpt("")
    ckpt("PRE-REGISTERED RULE:")
    ckpt("  V1 delta_rel < 1e-300          -> EQUIVALENT TO >=300 DIGITS")
    ckpt("  V2 1e-300 <= delta_rel < 1e-6  -> DIFFERENT BEYOND ROUNDING")
    ckpt("  V3 delta_rel >= 1e-6           -> STRUCTURALLY DIFFERENT")
    ckpt("  V4 source code fails           -> NOT COMPARABLE")
    ckpt("  diagnostics: delta_flip (sign), median ratio (scale)")
    ckpt("")

    # LANDMINE: every string->mpf conversion below must happen at the target
    # precision. Set mp.mp.dps BEFORE any of them, and before importing a
    # module that might reset it (gw_qinf sets 40 at its own module level).
    mp.mp.dps = dps
    ckpt("mp.mp.dps set to %d BEFORE any string->mpf conversion" % mp.mp.dps)
    ckpt("")

    # ---- our side --------------------------------------------------------
    ckpt("=" * 96)
    ckpt("OUR SIDE")
    ckpt("=" * 96)
    t = time.time()
    if load_path is not None:
        import json
        with open(load_path, "r", encoding="utf-8") as fh:
            blob = json.load(fh)
        if int(blob["c"]) != c or int(blob["N"]) != N:
            raise SystemExit("load provenance mismatch: saved c,N = %d,%d"
                             % (blob["c"], blob["N"]))
        our_str = blob["entries"]
        ckpt("  loaded %d entries from %s" % (len(our_str), load_path))
        ckpt("  provenance: c=%d, N=%d, dps=%d" % (blob["c"], blob["N"], blob["dps"]))
    else:
        from gw_corrected_eig import build_blocks_corrected
        from gw_full_vs_even import full_matrix
        # LANDMINE: gw_qinf sets mp.mp.dps = 40 at ITS module level, and this
        # import pulls it in. Re-raise precision AFTER the import, never before.
        mp.mp.dps = dps
        ckpt("  (mp.mp.dps re-raised to %d after importing gw_qinf)" % mp.mp.dps)
        bl = build_blocks_corrected(c, N)
        M = full_matrix(bl, N, "all")
        our_str = [mp.nstr(M[a, b], mp.mp.dps) for a in range(n) for b in range(n)]
        ckpt("  built fresh at dps %d" % dps)
    # Re-assert before any string->mpf parse: the load path never imported
    # gw_qinf, the build path did. Both must convert at the target precision.
    mp.mp.dps = dps
    ckpt("  conversion of %d entries to mpf at mp.mp.dps=%d ..." % (n * n, mp.mp.dps))
    our = [mp.mpf(s) for s in our_str]
    ckpt("  done in %.1f s" % (time.time() - t))
    ckpt("")

    # ---- source side -----------------------------------------------------
    ckpt("=" * 96)
    ckpt("SOURCE SIDE -- their build_arb_tau() at prec %d bits" % prec)
    ckpt("=" * 96)
    verdict = None
    try:
        mod = load_source_module()
        ckpt("  imported %s" % SRC_PATH)
        t = time.time()
        A, DIM = mod.build_arb_tau(c, N, prec)
        t_build = time.time() - t
        ckpt("  build_arb_tau done in %.1f s, dimension %d" % (t_build, DIM))
        if DIM != n:
            raise SystemExit("dimension mismatch: source %d vs ours %d" % (DIM, n))

        digits = max(20, int(prec * 0.30103) - 10)
        ckpt("  extracting midpoints at %d significant decimals ..." % digits)
        mp.mp.dps = max(dps, digits + 20)   # must hold the source digits too
        ckpt("  (mp.mp.dps raised to %d for the source-side parse)" % mp.mp.dps)
        t = time.time()
        src = [arb_to_mpf(A[a, b], digits) for a in range(n) for b in range(n)]
        rad_max = max(A[a, b].rad() for a in range(n) for b in range(n))
        ckpt("  done in %.1f s" % (time.time() - t))
        ckpt("  max arb radius on source side: %s" % rad_max)
        ckpt("")

        # ---- the diff ----------------------------------------------------
        ckpt("=" * 96)
        ckpt("ENTRYWISE DIFF (%d x %d = %d entries)" % (n, n, n * n))
        ckpt("=" * 96)
        t = time.time()
        delta = mp.mpf(0)
        delta_flip = mp.mpf(0)
        at = (0, 0)
        max_src = mp.mpf(0)
        max_our = mp.mpf(0)
        n_flip = 0
        ratios = []
        for a in range(n):
            for b in range(n):
                o = our[a * n + b]
                s = src[a * n + b]
                d = abs(o - s)
                if d > delta:
                    delta = d
                    at = (a, b)
                df = abs(o + s)
                if df > delta_flip:
                    delta_flip = df
                if abs(s) > max_src:
                    max_src = abs(s)
                if abs(o) > max_our:
                    max_our = abs(o)
                if s != 0:
                    ratios.append(o / s)
                    if o != 0 and mp.sign(o) != mp.sign(s):
                        n_flip += 1
        ckpt("  diff completed in %.1f s" % (time.time() - t))

        delta_rel = delta / max_src if max_src != 0 else mp.mpf("inf")
        ckpt("")
        ckpt("  max |source|          = %s" % mp.nstr(max_src, 20))
        ckpt("  max |ours|            = %s" % mp.nstr(max_our, 20))
        ckpt("  delta = max|ours-src| = %s   at (%d, %d) = index (%+d, %+d)"
             % (mp.nstr(delta, 20), at[0], at[1], at[0] - N, at[1] - N))
        ckpt("  delta_rel             = %s" % mp.nstr(delta_rel, 12))
        # DIAGNOSTIC REWRITTEN (defect 9, 2026-09-27): max|ours+src| is ~2*max
        # even when SOME entries flip sign, so it cannot detect a flip. Count
        # the disagreeing signs directly instead. Verdicts unaffected (V1..V4
        # depend on delta_rel only).
        n_flip = sum(1 for a in range(ne) for b in range(ne)
                     if src_val(a, b) != 0 and our_val(a, b) != 0
                     and mp.sign(src_val(a, b)) != mp.sign(our_val(a, b)))
        ckpt("  delta_flip = max|ours+src| = %s   (=2*max => same sign at the peak)"
             % mp.nstr(delta_flip, 20))
        ckpt("  entries with OPPOSITE sign  = %d / %d   -> %s"
             % (n_flip, n * n,
                "NO SIGN FLIP" if n_flip == 0 else "*** SIGN FLIP ***"))
        if ratios:
            ratios.sort()
            med = ratios[len(ratios) // 2]
            ckpt("  median per-entry ratio ours/source = %s   (large => global scale)"
                 % mp.nstr(med, 14))
        ckpt("")
        # DIAGNOSTIC ONLY -- the pre-registered V1..V4 thresholds above are
        # untouched. This says whether the measured delta is even resolvable
        # at the precision the entries were computed.
        floor = mp.mpf(10) ** -dps
        ckpt("  our working-precision floor = 10^-%d = %s" % (dps, mp.nstr(floor, 8)))
        if delta < floor:
            ckpt("  delta is AT (or below) the working-precision floor")
            ckpt("      -> the two sides are UNRESOLVABLY EQUAL at dps %d" % dps)
        else:
            ckpt("  delta is %s orders ABOVE the working-precision floor"
                 % mp.nstr(mp.log10(delta / floor), 6))
        ckpt("")

        # ---- verdict ------------------------------------------------------
        if delta_rel < V1_REL:
            verdict = "V1 EQUIVALENT TO >=300 DIGITS"
        elif delta_rel < V2_REL:
            verdict = "V2 DIFFERENT BEYOND ROUNDING"
        else:
            verdict = "V3 STRUCTURALLY DIFFERENT"
    except SystemExit:
        raise
    except Exception as exc:
        ckpt("  SOURCE SIDE FAILED: %s: %s" % (type(exc).__name__, exc))
        verdict = "V4 NOT COMPARABLE"

    ckpt("=" * 96)
    ckpt("VERDICT: %s" % verdict)
    ckpt("=" * 96)
    if verdict.startswith("V1"):
        ckpt("Hypothesis (c) of the §7a retraction -- 'our matrix differs from the")
        ckpt("source matrix' -- is NOT SUPPORTED at >=300 decimal digits.")
    elif verdict.startswith("V4"):
        ckpt("No claim of agreement can be made: the source side did not run.")
    ckpt("")
    ckpt("TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.")
    ckpt("lean/coqc/isabelle/dkcheck/z3/gcc NOT RUN.")
    ckpt("SCOPE: agreement of one preprint's matrix. Not RH, not Weil positivity.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
