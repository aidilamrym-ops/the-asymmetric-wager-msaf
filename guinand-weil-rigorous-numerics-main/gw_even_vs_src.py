# -*- coding: utf-8 -*-
"""Entrywise diff of the EVEN sector against the SOURCE package's build_arb_tau().

WHY THIS RUN EXISTS
-------------------
Option (a) (gw_opt_a_diff.py) closed the full 401x401 matrix against the source
package to 398 digits. Section 7e closed the ODD block directly (gate G3, same
threshold). The EVEN block was never diffed on its own: its tie to the source was
two steps REMOVED -- via the full-matrix equivalence (i) and via the G2b
quadratic-form reconstruction (ii), which bounds it at ~ sqrt(2)*4.11e-398.
That is a DERIVED bound, not a measurement. This script measures it.

This is the last DERIVED link in the (100,200) matrix.

PRE-REGISTERED DECISION RULE (locked BEFORE the first run, identical V1..V4 to
Option (a) so no threshold is tuned after seeing results)
------------------------------------------------------------------------
  V1  delta_rel < 1e-300         -> EQUIVALENT TO >=300 DIGITS
  V2  1e-300 <= delta_rel < 1e-6 -> DIFFERENT BEYOND ROUNDING
  V3  delta_rel >= 1e-6          -> STRUCTURALLY DIFFERENT
  V4  source code fails to run   -> NOT COMPARABLE (never report as IDENTICAL)

Secondary diagnostics (delta_flip, median ratio, distance to the dps floor)
classify the failure mode but do NOT change the verdict.

A SEPARATE, ALSO PRE-REGISTERED PREDICTION, stated before the run:
  delta_predicted <= sqrt(2) * 4.1137e-398 ~ 5.82e-398
derived in GW_STATUS_2026-09-26.md section 7f.7. It is reported next to the
measurement as an ORDERED PREDICTION, not as a pass/fail threshold -- the
verdict is decided by V1..V4 alone.

WHAT THIS IS NOT
----------------
Not the Riemann Hypothesis, not Weil positivity, not prime counting, not
factorisation; the source preprint disclaims all four.

TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.
lean / coqc / isabelle / dkcheck / z3 / gcc NOT RUN -- not proof-assistant
verified, and nothing here claims to be.

usage:
    python gw_even_vs_src.py 100 200 400 2000
    python gw_even_vs_src.py 100 200 400 2000 > gw_even_vs_src_100_200.log
"""

import hashlib
import importlib.util
import sys
import time

import mpmath as mp

SRC_PATH = "source_arb_ldlt_certify.py"
# Two pinned copies of that file exist in this repository's history; see
# THIRD_PARTY_SOURCES.md section 1 and OMEGA_CORE_CERTIFICATE.md section 1.
# The provenance check below accepts EITHER, reports which one it found, and
# fails anything else.  Neither value is interchangeable with the other.
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

# The prediction made in GW_STATUS section 7f.7, BEFORE this run.
# LANDMINE (defect 8a): 4.11e-398 as a PYTHON FLOAT LITERAL underflows to 0.0.
# Build the constant from a STRING, exactly as mp.mp.dps must be set before any
# string->number conversion. A float here silently produced DELTA_PRED = 0.
DELTA_PRED = mp.mpf("4.1137004583661995868e-398") * mp.sqrt(2)


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
    return mp.mpf(ball.mid().str(digits, radius=False))


def even_extract(A, N, digits):
    """Even-sector block out of a full (2N+1) source matrix.

    Mirrors gw_qinf.even_matrix exactly:
        (0,0)      -> Q(0,0)
        (0,j)      -> (Q(0,j)  + Q(0,-j)) / sqrt(2)
        (i,0)      -> (Q(i,0)  + Q(-i,0)) / sqrt(2)
        (i,j)      ->  Q(i,j)  + Q(i,-j)          (no sqrt(2): the 1/2 from the
                                                   isometric embedding cancels)
    Indices in the full matrix are offset by N, so value m sits at index N+m.
    """
    ne = N + 1
    s2 = mp.sqrt(2)
    M = mp.matrix(ne, ne)
    for i in range(ne):
        for j in range(ne):
            if i == 0 and j == 0:
                M[i, j] = arb_to_mpf(A[N, N], digits)
            elif i == 0:
                M[i, j] = ((arb_to_mpf(A[N, N + j], digits)
                            + arb_to_mpf(A[N, N - j], digits)) / s2)
            elif j == 0:
                M[i, j] = ((arb_to_mpf(A[N + i, N], digits)
                            + arb_to_mpf(A[N - i, N], digits)) / s2)
            else:
                M[i, j] = (arb_to_mpf(A[N + i, N + j], digits)
                           + arb_to_mpf(A[N + i, N - j], digits))
    return M


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) < 4:
        print(__doc__)
        return 2
    c, N, dps, prec = int(args[0]), int(args[1]), int(args[2]), int(args[3])
    ne = N + 1

    ckpt("#" * 96)
    ckpt("# OMEGA -- EVEN SECTOR vs SOURCE PACKAGE (option 1, closes the last derived link)")
    ckpt("# (c, N, dps, prec) = (%d, %d, %d, %d)   even block %dx%d"
         % (c, N, dps, prec, ne, ne))
    ckpt("#" * 96)
    ckpt("")
    ckpt("PRE-REGISTERED DECISION RULE (identical to option (a)):")
    ckpt("  V1  delta_rel < 1e-300          -> EQUIVALENT TO >=300 DIGITS")
    ckpt("  V2  1e-300 <= delta_rel < 1e-6  -> DIFFERENT BEYOND ROUNDING")
    ckpt("  V3  delta_rel >= 1e-6           -> STRUCTURALLY DIFFERENT")
    ckpt("  V4  source code fails           -> NOT COMPARABLE")
    ckpt("PRE-REGISTERED PREDICTION (reported, NOT a threshold):")
    ckpt("  delta_pred = sqrt(2) * 4.1137004583661995868e-398 = %s"
         % mp.nstr(DELTA_PRED, 12))
    ckpt("  (GW_STATUS 7f.7, written before this run)")
    ckpt("")

    # ---- provenance of the vendored source file -------------------------
    ckpt("=" * 96)
    ckpt("PROVENANCE")
    ckpt("=" * 96)
    digest = hashlib.sha256(open(SRC_PATH, "rb").read()).hexdigest()
    ckpt("  sha256(%s)" % SRC_PATH)
    ckpt("    computed = %s" % digest)
    if digest == SRC_SHA256_VERBATIM[0]:
        ckpt("    pinned   = %s  (%s)" % SRC_SHA256_VERBATIM)
        ckpt("    MATCH -- byte-identical to script_sha256 in their provenance")
    elif digest == SRC_SHA256_SHIPPED[0]:
        ckpt("    pinned   = %s  (%s)" % SRC_SHA256_SHIPPED)
        ckpt("    MATCH -- documented local extension: three default-preserving")
        ckpt("             resume kwargs added 2026-09-30, no arithmetic changed.")
        ckpt("             The verbatim upstream copy is at git b76be0d and is")
        ckpt("             what this check printed when it ran on 2026-09-27.")
    else:
        ckpt("    pinned   = %s  (%s)" % SRC_SHA256_VERBATIM)
        ckpt("             %s  (%s)" % SRC_SHA256_SHIPPED)
        ckpt("    *** MISMATCH -- do NOT trust this run ***")
    ckpt("")

    # ---- our side --------------------------------------------------------
    ckpt("=" * 96)
    ckpt("OUR SIDE -- even block rebuilt at dps %d" % dps)
    ckpt("=" * 96)
    from gw_corrected_eig import build_blocks_corrected
    from gw_qinf import even_matrix

    # LANDMINE: gw_qinf sets mp.mp.dps = 40 at its module level and this import
    # pulls it in. Re-raise AFTER the import, never before.
    mp.mp.dps = dps
    ckpt("  mp.mp.dps = %d (set AFTER importing gw_qinf)" % mp.mp.dps)

    t = time.time()
    bl = build_blocks_corrected(c, N)
    ckpt("  blocks built in %.1f s" % (time.time() - t))
    t = time.time()
    Me = even_matrix(bl, N, "all")
    ckpt("  even block %dx%d built in %.1f s" % (ne, ne, time.time() - t))
    mp.mp.dps = dps
    our = [mp.nstr(Me[a, b], mp.mp.dps) for a in range(ne) for b in range(ne)]
    our = [mp.mpf(s) for s in our]
    ckpt("")

    # ---- source side -----------------------------------------------------
    ckpt("=" * 96)
    ckpt("SOURCE SIDE -- build_arb_tau(prec %d bits)" % prec)
    ckpt("=" * 96)
    # verdict is decided AFTER the try (defect 8b fix); None means "the diff ran".
    verdict = None
    delta_rel = None
    delta = mp.mpf(0)
    try:
        mod = load_source_module()
        ckpt("  imported %s" % SRC_PATH)
        t = time.time()
        A, DIM = mod.build_arb_tau(c, N, prec)
        ckpt("  build_arb_tau done in %.1f s, dimension %d" % (time.time() - t, DIM))
        if DIM != 2 * N + 1:
            raise SystemExit("dimension mismatch: source %d vs expected %d"
                             % (DIM, 2 * N + 1))

        digits = max(20, int(prec * 0.30103) - 10)
        ckpt("  extracting midpoints at %d significant decimals ..." % digits)
        mp.mp.dps = max(dps, digits + 20)
        ckpt("  (mp.mp.dps raised to %d for the source-side parse)" % mp.mp.dps)
        t = time.time()
        src = even_extract(A, N, digits)
        rad_max = max(A[a, b].rad() for a in range(DIM) for b in range(DIM))
        ckpt("  done in %.1f s" % (time.time() - t))
        ckpt("  max arb radius on source side (full matrix): %s" % rad_max)
        ckpt("")

        # ---- the diff ----------------------------------------------------
        ckpt("=" * 96)
        ckpt("ENTRYWISE DIFF (%d x %d = %d entries)" % (ne, ne, ne * ne))
        ckpt("=" * 96)
        t = time.time()
        delta = mp.mpf(0)
        delta_flip = mp.mpf(0)
        at = (0, 0)
        where = ""
        max_src = mp.mpf(0)
        max_our = mp.mpf(0)
        n_flip = 0
        ratios = []
        for i in range(ne):
            for j in range(ne):
                o = our[i * ne + j]
                s = src[i, j]
                d = abs(o - s)
                if d > delta:
                    delta = d
                    at = (i, j)
                    if i == 0 and j == 0:
                        where = "(0,0) corner"
                    elif i == 0 or j == 0:
                        where = "sqrt(2) row/column"
                    else:
                        where = "interior (no sqrt2)"
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
        ckpt("  delta = max|ours-src| = %s   at (%d, %d), %s"
             % (mp.nstr(delta, 20), at[0], at[1], where))
        ckpt("  delta_rel             = %s" % mp.nstr(delta_rel, 12))
        # DEFECT 9 (2026-09-27): max|ours+src| is ~2*max even when SOME entries
        # flip sign, so it cannot detect a flip. Count disagreeing signs
        # directly instead. Verdict unaffected: V1..V4 use delta_rel only.
        ckpt("  delta_flip = max|ours+src| = %s   (= 2*max => same sign at peak)"
             % mp.nstr(delta_flip, 20))
        ckpt("  entries with OPPOSITE sign  = %d / %d   -> %s"
             % (n_flip, ne * ne,
                "NO SIGN FLIP" if n_flip == 0 else "*** SIGN FLIP ***"))
        if ratios:
            ratios.sort()
            med = ratios[len(ratios) // 2]
            ckpt("  median per-entry ratio ours/source = %s   (large => global scale)"
                 % mp.nstr(med, 14))
        ckpt("")

        # DIAGNOSTIC ONLY -- V1..V4 above are untouched by this block.
        floor = mp.mpf(10) ** -dps
        ckpt("  our working-precision floor = 10^-%d = %s" % (dps, mp.nstr(floor, 8)))
        if delta < floor:
            ckpt("  delta is AT (or below) the floor -> UNRESOLVABLY EQUAL at dps %d" % dps)
        else:
            ckpt("  delta is %s orders ABOVE the working-precision floor"
                 % mp.nstr(mp.log10(delta / floor), 6))
        ckpt("")

    except SystemExit:
        raise
    except Exception as exc:
        ckpt("  SOURCE SIDE FAILED: %s: %s" % (type(exc).__name__, exc))
        ckpt("")
        # V4 applies only if the DIFF never completed. If delta_rel was already
        # produced, the numbers stand and the verdict must still come from V1..V4.
        if delta_rel is None:
            verdict = "V4 NOT COMPARABLE"

    # ---- verdict ----------------------------------------------------------
    # OUTSIDE the try (defect 8b): the verdict is decided ONLY by delta_rel,
    # which is produced by the diff above. A failure in any diagnostic printed
    # afterwards must never be able to overwrite it -- in the first run a
    # ZeroDivisionError inside the prediction block was caught by this same
    # except and printed V4 NOT COMPARABLE over a perfectly good diff.
    if verdict is None:
        if delta_rel < V1_REL:
            verdict = "V1 EQUIVALENT TO >=300 DIGITS"
        elif delta_rel < V2_REL:
            verdict = "V2 DIFFERENT BEYOND ROUNDING"
        else:
            verdict = "V3 STRUCTURALLY DIFFERENT"

    # ---- the pre-registered prediction (NON-FATAL, outside the try) -------
    if delta_rel is not None:
        try:
            ckpt("-" * 96)
            ckpt("PREDICTION CHECK (reported; does NOT decide the verdict)")
            ckpt("  predicted (7f.7, pre-run) = %s" % mp.nstr(DELTA_PRED, 12))
            ckpt("  measured (this run)       = %s" % mp.nstr(delta, 20))
            if DELTA_PRED != 0 and delta > 0:
                ckpt("  measured / predicted      = %s" % mp.nstr(delta / DELTA_PRED, 12))
                ckpt("  %s orders %s the pre-registered prediction"
                     % (mp.nstr(abs(mp.log10(delta / DELTA_PRED)), 6),
                        "ABOVE" if delta > DELTA_PRED else "BELOW"))
            ckpt("-" * 96)
            ckpt("")
        except Exception as exc:
            ckpt("  PREDICTION CHECK FAILED (verdict UNAFFECTED): %s: %s"
                 % (type(exc).__name__, exc))
            ckpt("")

    ckpt("#" * 96)
    ckpt("# VERDICT -- EVEN SECTOR vs SOURCE PACKAGE")
    ckpt("#" * 96)
    ckpt("  %s" % verdict)
    if verdict.startswith("V1"):
        ckpt("  every even-sector entry agrees with the source package to >=300 digits.")
        ckpt("  The section 7f.7 DERIVED bound (~5.82e-398) is now MEASURED.")
    elif verdict.startswith("V4"):
        ckpt("  NOT COMPARABLE -- never to be reported as identical.")
    else:
        ckpt("  investigate before using this block further.")
    ckpt("")
    ckpt("TOOL STATUS: python 3.14 + mpmath + python-flint 0.9.0.")
    ckpt("lean/coqc/isabelle/dkcheck/z3/gcc NOT RUN.")
    ckpt("SCOPE: one preprint's even sector. Not RH, not Weil positivity.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
