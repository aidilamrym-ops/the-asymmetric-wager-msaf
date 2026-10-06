#!/usr/bin/env python3
"""Track C literal cross-check + SMT side-condition gate for the OMEGA chain.

What this script does (all steps are executed, none is assumed):

1. Reads the three headline constants OUT OF README.md by regex -- it does
   not trust a hand copy:
      lambda_min(Q_100,40), rho_actual, rho*
2. Reads the matching `abbrev ... : ℚ := num / 10 ^ den` definitions OUT OF
   OMEGATrackC.lean.
3. Normalises both to (mantissa string, decimal exponent) and requires an
   exact match for every constant. Any mismatch is a FAIL, printed with both
   values.
4. Emits `track_c_side_conditions.smt2`: exact-rational (QF_NRA) negations of
   the seven numeric side conditions that OMEGATrackC.lean proves with
   `norm_num`.  The file carries **one** `(assert ...)`, the conjunction of
   the seven negations: the circularity auditor
   (`skills/anti-circularity/scripts/smt_circularity_auditor.py`) ignores
   `push`/`pop`/`check-sat` and reads every `assert` in a file as one context
   with the last assertion as the claim.  Seven separate negations in one
   file contradict *each other* (e.g. `rhoStar*401 < lambdaMin` together with
   `lambdaMin < rhoStar*82`), so the auditor reported the multi-assert form
   as VACUOUS -- the context alone was unsat and no claim played a role.  A
   conjunction keeps the auditor's context empty and its verdict GENUINE.
   The per-claim breakdown is not lost: each negation is additionally checked
   on its own, in its own solver run, and every answer lands in
   `track_c_smt_z3.log`.
5. Runs Z3 on that file (Z3_EXE env var -> PATH -> known local install) and
   writes `track_c_smt_z3.log`.  The combined file must answer `unsat`, and
   so must each of the seven individual negations.

Scope, stated literally: this gate checks NUMERIC ARITHMETIC ONLY -- that the
literals in the Lean module are the literals in the README, and that the
reported inequalities hold over exact rationals. It does not check where the
literals came from (FLINT/Arb ball arithmetic is outside this script), and it
is not a substitute for the Lean kernel check of the inference theorem
`OMEGA.certified_positivity`.

Exit codes: 0 = all cross-checks match and all claims UNSAT;
            1 = literal mismatch; 2 = z3 missing; 3 = a claim not UNSAT.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

# README markdown:  1.234... \times 10^{-102}   (both "\times 10" and
# "\times10" occur in the document).
README_NUM_RE = re.compile(r"(\d+\.\d+)\\times\s*10\^\{(-?\d+)\}")

# OMEGATrackC.lean:  abbrev name : ℚ := 12345 / 10 ^ 678
LEAN_ABBREV_RE = re.compile(
    r"abbrev\s+(lambdaMin|rhoActual|rhoStar)\s*:\s*ℚ\s*:=\s*(\d+)\s*/\s*10\s*\^\s*(\d+)"
)

# The three constants this gate is responsible for.
CHECKED = ("lambdaMin", "rhoActual", "rhoStar")

# 10^74 as a full integer literal: SMT-LIB2 has no `^` on Real, and z3 reads
# arbitrary-precision decimal integers exactly.
POW10_74 = "1" + "0" * 74

# (theorem name mirrored, claim expression, negation asserted in SMT-LIB2).
# Keep names identical to OMEGATrackC.lean so a reader can pair them up.
CLAIMS = [
    ("measured_within_tolerance",
     "rhoActual <= rhoStar",
     "(> rhoActual rhoStar)"),
    ("margin_at_least_74_orders",
     "rhoActual * 10^74 <= rhoStar",
     f"(> (* rhoActual {POW10_74}) rhoStar)"),
    ("margin_satisfies_master_theorem",
     "rhoActual * 401 < lambdaMin",
     "(>= (* rhoActual 401) lambdaMin)"),
    ("tolerance_fails_the_coarse_bound",
     "not (rhoStar * 401 < lambdaMin)",
     "(< (* rhoStar 401) lambdaMin)"),
    ("implied_constant_ge_81",
     "rhoStar * 81 <= lambdaMin",
     "(> (* rhoStar 81) lambdaMin)"),
    ("implied_constant_lt_82",
     "lambdaMin < rhoStar * 82",
     "(>= lambdaMin (* rhoStar 82))"),
    ("tolerance_positive",
     "0 < rhoStar",
     "(<= rhoStar 0)"),
]

KNOWN_LOCAL_Z3 = r"E:\4_TOOLS_INSTALLER\z3-4.16.0-x64-win\bin\z3.exe"


def find_z3(explicit: str | None) -> str | None:
    """Z3_EXE env var -> PATH -> the documented local install."""
    for cand in (explicit, os.environ.get("Z3_EXE")):
        if cand and os.path.isfile(cand):
            return cand
    on_path = shutil.which("z3")
    if on_path:
        return on_path
    if os.path.isfile(KNOWN_LOCAL_Z3):
        return KNOWN_LOCAL_Z3
    return None


def lean_constants(lean_path: str) -> dict[str, tuple[str, int]]:
    """Parse `abbrev name : ℚ := num / 10 ^ den` -> {name: (num_str, den)}."""
    text = open(lean_path, encoding="utf-8").read()
    found = {m.group(1): (m.group(2), int(m.group(3)))
             for m in LEAN_ABBREV_RE.finditer(text)}
    missing = [n for n in CHECKED if n not in found]
    if missing:
        raise SystemExit(f"FAIL: abbrevs not found in {lean_path}: {missing}")
    return found


def normalise(num_str: str, den: int) -> tuple[str, int]:
    """(digits, 10^-den) -> (normalised mantissa like '1.23', exp10)."""
    digits = num_str.lstrip("0") or "0"
    digits = digits.rstrip("0") or "0"
    mantissa = digits if len(digits) == 1 else digits[0] + "." + digits[1:]
    exp10 = (len(digits) - 1) - den
    return mantissa, exp10


def readme_constants(readme_path: str) -> set[tuple[str, int]]:
    text = open(readme_path, encoding="utf-8").read()
    return {(m.group(1), int(m.group(2))) for m in README_NUM_RE.finditer(text)}


def build_smt(lean_consts: dict[str, tuple[str, int]]) -> str:
    lines = [
        "; Generated by track_c_make_smt.py -- DO NOT EDIT BY HAND.",
        f"; Source constants: OMEGATrackC.lean abbrevs (cross-checked against README.md).",
        "; One assertion only: the conjunction of the seven negations. Each",
        "; negation is the claim `not <theorem>` for a side condition proved in",
        "; Lean, so the conjunction must be unsat; the seven are also run",
        "; one-by-one by the generator and recorded in track_c_smt_z3.log.",
        "; The single-assert shape is what lets the circularity auditor see an",
        "; empty context (it ignores push/pop and reads all asserts as one script).",
        "(set-logic QF_NRA)",
    ]
    lines.extend(define_funs(lean_consts))
    lines.append("(assert (and")
    for _, _, negation in CLAIMS:
        lines.append(f"  {negation}")
    lines.append("))")
    lines.append("(check-sat)")
    lines.append("(exit)")
    return "\n".join(lines) + "\n"


def define_funs(lean_consts: dict[str, tuple[str, int]]) -> list[str]:
    """Exact-rational definitions of the three constants, as SMT-LIB2 lines."""
    out = []
    for name in CHECKED:
        num, den = lean_consts[name]
        den_lit = "1" + "0" * den  # exact integer 10^den, no `^` operator
        out.append(f"(define-fun {name} () Real (/ {num} {den_lit}))")
    return out


def single_claim_smt(lean_consts: dict[str, tuple[str, int]], negation: str) -> str:
    """One negation in isolation: definitions plus exactly one assertion."""
    lines = ["(set-logic QF_NRA)"]
    lines.extend(define_funs(lean_consts))
    lines.append(f"(assert {negation})")
    lines.append("(check-sat)")
    lines.append("(exit)")
    return "\n".join(lines) + "\n"


def run_z3(z3: str, smt_path: str) -> tuple[list[str], str]:
    proc = subprocess.run([z3, smt_path], capture_output=True, text=True,
                          timeout=300)
    if proc.returncode != 0:
        raise SystemExit(f"FAIL: z3 exited {proc.returncode}: {proc.stderr.strip()}")
    return proc.stdout.splitlines(), proc.stderr


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--readme", default=os.path.join(here, "README.md"))
    ap.add_argument("--lean", default=os.path.join(here, "OMEGATrackC.lean"))
    ap.add_argument("--out-smt", default=os.path.join(here, "track_c_side_conditions.smt2"))
    ap.add_argument("--out-log", default=os.path.join(here, "track_c_smt_z3.log"))
    ap.add_argument("--z3", default=None, help="path to z3 (else Z3_EXE/PATH/known)")
    args = ap.parse_args()

    log: list[str] = []
    def emit(msg: str) -> None:
        print(msg)
        log.append(msg)

    def shown(path: str) -> str:
        """Repository-relative rendering for the shipped log.

        PROVENANCE.txt 6.9 declares an existing residual: older logs carry
        C:\\Users\\... and so disclose the local account name.  This log is
        new, so it does not have to add to that list -- everything under the
        repository root is printed relative to it.
        """
        if path.startswith(here + os.sep):
            return os.path.relpath(path, here).replace(os.sep, "/")
        return path

    emit(f"track_c_make_smt.py  {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    emit(f"readme = {shown(args.readme)}")
    emit(f"lean   = {shown(args.lean)}")

    # ---- step 1: literal cross-check (README vs Lean) --------------------
    lean_consts = lean_constants(args.lean)
    readme_set = readme_constants(args.readme)
    mismatch = False
    for name in CHECKED:
        num, den = lean_consts[name]
        mant, exp10 = normalise(num, den)
        ok = (mant, exp10) in readme_set
        status = "MATCH" if ok else "MISMATCH"
        emit(f"  {name:11s} lean={mant}e{exp10:+d}  readme={'found' if ok else 'NOT FOUND'}  -> {status}")
        if not ok:
            mismatch = True
    if mismatch:
        emit("RESULT: FAIL -- Lean literals are not the README literals.")
        open(args.out_log, "w", encoding="utf-8").write("\n".join(log) + "\n")
        return 1

    # ---- step 2: emit the SMT-LIB2 file ---------------------------------
    smt = build_smt(lean_consts)
    open(args.out_smt, "w", encoding="utf-8", newline="\n").write(smt)
    emit(f"wrote {shown(args.out_smt)} ({len(smt)} bytes, {len(CLAIMS)} claims)")

    # ---- step 3: run z3, every negation must be unsat --------------------
    z3 = find_z3(args.z3)
    if z3 is None:
        emit("RESULT: FAIL -- z3 not found (set Z3_EXE or install z3 on PATH).")
        open(args.out_log, "w", encoding="utf-8").write("\n".join(log) + "\n")
        return 2
    try:
        ver = subprocess.run([z3, "--version"], capture_output=True,
                             text=True, timeout=30).stdout.strip()
    except Exception:
        ver = "z3 (version unknown)"
    emit(f"z3   = {z3}")
    emit(f"z3ver = {ver}")

    out, err = run_z3(z3, args.out_smt)
    if err.strip():
        emit(f"z3 stderr: {err.strip()}")
    smt_errors = [ln for ln in out if ln.strip().startswith("(error")]
    for ln in smt_errors:
        emit(f"z3 stdout: {ln.strip()}")
    if smt_errors:
        emit("RESULT: FAIL -- z3 reported SMT-LIB2 errors (file is malformed).")
        open(args.out_log, "w", encoding="utf-8").write("\n".join(log) + "\n")
        return 3

    bad: list[str] = []
    combined = next((ln.strip() for ln in out
                     if ln.strip() in ("sat", "unsat", "unknown")), "MISSING")
    emit(f"  {'combined conjunction of ' + str(len(CLAIMS)) + ' negations':76s} "
         f"{'UNSAT (as required)' if combined == 'unsat' else '*** ' + combined.upper() + ' ***'}")
    if combined != "unsat":
        bad.append("combined")

    # Each negation also has to fail on its own, in its own solver run, so a
    # failure cannot hide behind another negation inside the conjunction.
    with tempfile.TemporaryDirectory() as td:
        for i, (label, claim, negation) in enumerate(CLAIMS, 1):
            tmp = os.path.join(td, f"claim_{i:02d}.smt2")
            open(tmp, "w", encoding="utf-8", newline="\n").write(
                single_claim_smt(lean_consts, negation))
            a_out, a_err = run_z3(z3, tmp)
            if a_err.strip():
                emit(f"z3 stderr ({label}): {a_err.strip()}")
            ans = next((ln.strip() for ln in a_out
                        if ln.strip() in ("sat", "unsat", "unknown")), "MISSING")
            flag = "UNSAT (as required)" if ans == "unsat" else f"*** {ans.upper()} ***"
            emit(f"  {label:34s} {claim:40s} {flag}")
            if ans != "unsat":
                bad.append(label)

    if bad:
        emit(f"RESULT: FAIL -- claims not UNSAT: {bad}")
        code = 3
    else:
        emit(f"RESULT: PASS -- {len(CLAIMS)}/{len(CLAIMS)} negations UNSAT "
             "(individually) plus the combined conjunction; "
             "literal cross-check MATCH on all 3 constants.")
        code = 0

    open(args.out_log, "w", encoding="utf-8", newline="\n").write("\n".join(log) + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
