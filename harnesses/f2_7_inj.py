# FILE: harnesses/f2_7_inj.py
# PURPOSE: re-produce the F2-7 fault-injection counts for gw_verify_production.py.
#
# F2_REPORT 7.4 published 24 mutants + 2 controls = 26/26, plus a separate
# 4/4 missing-document run (rename -> run -> restore -> hash).  No harness was
# kept for it (F2_REPORT 8.3).  This is that harness.
#
# Reconstructing the case set from 7.4: its "Mutants covered" list holds 25
# items, and the first of them -- "absent file" -- is the missing-document row
# printed immediately above it, not a 25th JSON mutant.  The 24 JSON mutants
# below are items 2..25 of that list, in the list's own order.  The two
# controls are not listed in 7.4 (controls were never "mutants covered").
#
# Every JSON mutant is written to a TEMP file and handed to the gate as
# argv[2]; argv[1] and the three documentary records are never written.
# argv[1] still points at the real N=800 artefact, so an injected N=400 row is
# judged against an untouched sibling on every run.
#
# Exit codes: 0 = every case behaved as required and bytes restored
#             1 = a case was not caught, or a control stopped passing
#             2 = a tool or document the harness needs is missing

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GW = os.path.join(ROOT, "guinand-weil-rigorous-numerics-main")
GATE = os.path.join(GW, "gw_verify_production.py")
PY = sys.executable

PROD_N800 = os.path.join(GW, "omega_core_v2_results.json")
PROD_N400 = os.path.join(GW, "omega_core_v2_results_N400.json")

MISSING_DOCS = (
    "PROVENANCE.txt",
    "OMEGA_CORE_CERTIFICATE.md",
    "omega_core_v2_run.log",
    "omega_core_v2_results_N400.json",
)

WORK = os.path.join(os.environ.get("TEMP", os.getcwd()), "opencode", "f2_7")
TMP = os.path.join(WORK, "row_N400.json")

TARGET_MUTANTS = 24
TARGET_CONTROLS = 2
TARGET_MISSING = 4

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL  %s" % msg)


def check(cond, msg):
    if not cond:
        fail(msg)
    return cond


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rd(p):
    with io.open(p, "rb") as fh:
        return fh.read()


def wr(p, data):
    with io.open(p, "wb") as fh:
        fh.write(data)


def run_gate(prod=PROD_N800, n400=None, cwd=None):
    args = [PY, "-u", GATE, prod, n400 or TMP]
    p = subprocess.run(args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       cwd=cwd or GW, timeout=300)
    return p.returncode


def walk(obj, path):
    cur = obj
    parts = path.split(".")
    for p in parts[:-1]:
        cur = cur[p]
    return cur, parts[-1]


def mutate(raw_text, op, needle, value):
    """Return the mutated file text, or None if the case cannot be applied."""
    if op == "raw":
        return value if value != raw_text else None
    obj = json.loads(raw_text)
    if op == "rows":
        row = obj[0] if isinstance(obj, list) and obj else None
        if row is None:
            return None
        out = json.dumps([row] * int(needle), indent=2,
                         ensure_ascii=False) + "\n"
        return None if out == raw_text else out
    if op == "reindent":
        return json.dumps(obj, indent=4, ensure_ascii=False) + "\n"
    # every remaining op addresses a key of row 0
    if not isinstance(obj, list) or len(obj) != 1 or not isinstance(obj[0], dict):
        return None
    row = obj[0]
    cur, key = walk(row, needle.split("|")[0])
    if op == "drop":
        if key not in cur:
            return None
        del cur[key]
    elif op == "set":
        cur[key] = value
    elif op == "set_pair":
        # both halves of one derived mutant: lb and the bound_detail input
        # that implies it have to move together, or deep_invariants() fires
        # first and the intended "internally consistent" case never happens
        cur[key] = value[0]
        cur2, key2 = walk(row, needle.split("|")[1])
        cur2[key2] = value[1]
    else:
        raise ValueError("unknown op %r" % op)
    out = json.dumps([row], indent=2, ensure_ascii=False) + "\n"
    return None if out == raw_text else out


def scaled(row, factor):
    """lb and bound_detail.min_abs_pivot both scaled, so implied == lb again."""
    import mpmath as mp
    mp.mp.dps = 60
    lb = mp.mpf(str(row["lambda_min_lower_bound"])) * factor
    mpv = mp.mpf(str(row["bound_detail"]["min_abs_pivot"])) * factor
    return (mp.nstr(lb, 30, strip_zeros=False),
            mp.nstr(mpv, 30, strip_zeros=False))


def past_log_precision(row):
    """Digit 26 of the bound changed: the 25 sf log still agrees, the two
    30 sf documents do not."""
    txt = str(row["lambda_min_lower_bound"])
    mant, _, expo = txt.partition("e")
    digits = mant.replace(".", "").replace("-", "").replace("+", "")
    if len(digits) < 30:
        return None
    digits = digits[:25] + ("7" if digits[25] != "7" else "8") + digits[26:]
    return "%s.%se%s" % (digits[0], digits[1:], expo)


def build_cases(row):
    """(id, op, needle, value, expected exit) -- value for op='set' may be a
    callable taking the pristine row, so the derived mutants are exact."""
    lb2, mp2 = scaled(row, 2)
    return [
        # --- the 24 JSON mutants, in the order F2_REPORT 7.4 lists them ----
        ("M01_non_list", "raw", "", '{"not": "a list"}', 1),
        ("M02_empty_list", "raw", "", "[]", 1),
        ("M03_two_rows", "rows", "2", None, 1),
        ("M04_missing_key", "drop", "n_pos", None, 1),
        ("M05_wrong_N", "set", "N", 401, 1),
        ("M06_wrong_dim", "set", "dim", 800, 1),
        ("M07_n_neg", "set", "n_neg", 1, 1),
        ("M08_nonhex_sha", "set", "sha256", "z" * 64, 1),
        ("M09_symmetry_dev", "set", "symmetry_dev", "0.0", 1),
        ("M10_caveats", "set", "caveats", ["injected"], 1),
        ("M11_anomaly", "set", "anomaly", True, 1),
        ("M12_non_result", "set", "non_result", True, 1),
        ("M13_undetermined", "set", "undetermined_pivot", 723, 1),
        ("M14_attempts", "set", "attempts", [], 1),
        ("M15_reason", "set", "non_result_reason",
         "UNDETERMINED (injected)", 1),
        ("M16_bound_one", "set", "lambda_min_lower_bound", "1", 1),
        ("M17_bound_negative", "set", "lambda_min_lower_bound",
         "-" + str(row["lambda_min_lower_bound"]), 1),
        ("M18_min_abs_pivot", "set", "bound_detail.min_abs_pivot",
         "1.000000000000000000000000e-112", 1),
        ("M19_pivot_sign", "set", "bound_detail.pivot_sign", "-", 1),
        ("M20_entry_radius", "set", "max_entry_radius",
         "1.000000000000000000000000e-40", 1),
        ("M21_bound_vs_docs",
         "set_pair",
         "lambda_min_lower_bound|bound_detail.min_abs_pivot",
         (lb2, mp2), 1),
        ("M22_past_log_precision", "set", "lambda_min_lower_bound",
         past_log_precision(row), 1),
        ("M23_null_doc", "raw", "", "null", 1),
        ("M24_unparsable", "raw", "", "{ this is not json", 1),

        # --- the two controls --------------------------------------------
        ("K1_unused_key", "set", "unused_control_key", 42, 0),
        ("K2_reindent", "reindent", "", None, 0),
    ]


def main():
    if not check(os.path.isfile(GATE), "missing gate: %s" % GATE):
        print("")
        print("HARNESS: FAIL -- gate absent")
        return 1
    live = {}
    for p in (PROD_N800, PROD_N400) + tuple(
            os.path.join(GW, f) for f in MISSING_DOCS):
        if not check(os.path.isfile(p), "missing live file: %s" % p):
            print("")
            print("HARNESS: FAIL -- live file absent")
            return 1
        live[p] = rd(p)

    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    pristine = live[PROD_N400]
    row = json.loads(pristine.decode("utf-8"))[0]
    cases = build_cases(row)

    rc = run_gate(n400=PROD_N400)
    check(rc == 0, "baseline: gate against the real artefacts must pass, "
                   "got exit %d" % rc)
    wr(TMP, pristine)
    rc = run_gate()
    check(rc == 0, "baseline: gate against an unmutated copy must pass, "
                   "got exit %d" % rc)

    results = []
    try:
        for cid, op, needle, value, want in cases:
            wr(TMP, pristine)
            text = pristine.decode("utf-8")
            if value is not None and callable(value):
                value = value(row)
            if op in ("set", "set_pair") and value is None:
                fail("%s: no value to inject" % cid)
                results.append((cid, False, "not applied"))
                continue
            out = mutate(text, op, needle, value)
            if out is None:
                fail("%s: case could not be applied (no-op mutation)" % cid)
                results.append((cid, False, "not applied"))
                continue
            wr(TMP, out.encode("utf-8"))
            rc = run_gate()
            good = check(rc == want,
                         "%s: gate must exit %d, got exit %d"
                         % (cid, want, rc))
            results.append((cid, good, "exit %d want %d" % (rc, want)))
        wr(TMP, pristine)
    finally:
        wr(TMP, pristine)
        for p, blob in live.items():
            if os.path.isfile(p) and rd(p) != blob:
                wr(p, blob)
            elif not os.path.isfile(p):
                fail("live file still missing: %s" % p)

    print("\n-- missing-document path: rename, run, restore, hash ----------")
    missing_results = []
    for name in MISSING_DOCS:
        path = os.path.join(GW, name)
        blob = live[path]
        # same directory: os.rename refuses to cross drives, and a harness that
        # cannot move the file cannot test its absence
        backup = path + ".harness_saved"
        if os.path.isfile(backup):
            # a stale backup from an interrupted run would be silently
            # restored over the live file below; refuse to touch it blindly
            if rd(backup) == blob:
                os.remove(backup)
            else:
                fail("%s: stale backup %s differs from the live file; "
                     "refusing to overwrite it" % (name, os.path.basename(backup)))
                missing_results.append((name, False, "stale backup"))
                continue
        try:
            os.rename(path, backup)
            rc = run_gate(n400=PROD_N400)
            good = check(rc != 0,
                         "%s: the gate must not pass without %s, got exit %d"
                         % (name, name, rc))
            restored = "renamed"
        except Exception as exc:
            good = False
            fail("%s: %s: %s" % (name, type(exc).__name__, exc))
            restored = "error"
        finally:
            if os.path.isfile(backup):
                os.replace(backup, path)
            elif not os.path.isfile(path):
                wr(path, blob)
            if not os.path.isfile(path):
                fail("%s: could not be restored" % name)
                good = False
            elif rd(path) != blob:
                fail("%s: restore is not byte-identical" % name)
                good = False
            else:
                restored = "restored byte-identical"
        missing_results.append((name, good, restored))

    for p, blob in live.items():
        if not os.path.isfile(p):
            fail("live file missing at the end: %s" % p)
        elif rd(p) != blob:
            fail("live file modified: %s" % p)

    rc = run_gate(n400=PROD_N400)
    check(rc == 0, "restored baseline: gate must pass again, got exit %d" % rc)

    mutants = [r for r in results if not r[0].startswith("K")]
    controls = [r for r in results if r[0].startswith("K")]
    m_ok = sum(1 for _, g, _ in mutants if g)
    c_ok = sum(1 for _, g, _ in controls if g)
    d_ok = sum(1 for _, g, _ in missing_results if g)
    cases_ok = m_ok + c_ok

    print("")
    for cid, good, note in results:
        print("  %s %s  %s" % ("ok  " if good else "FAIL  ", cid, note))
    for name, good, note in missing_results:
        print("  %s %s  %s" % ("ok  " if good else "FAIL  ", name, note))
    print("")
    print("fault-injection %d/%d (mutants %d/%d, controls %d/%d)   "
          "missing-document %d/%d"
          % (cases_ok, len(results), m_ok, len(mutants), c_ok, len(controls),
             d_ok, len(missing_results)))

    shutil.rmtree(WORK, ignore_errors=True)

    if failures:
        print("HARNESS: FAIL -- %d problem(s)" % len(failures))
        return 1
    if (len(mutants) != TARGET_MUTANTS or len(controls) != TARGET_CONTROLS
            or len(missing_results) != TARGET_MISSING):
        print("HARNESS: FAIL -- expected %d/%d/%d cases, table has %d/%d/%d"
              % (TARGET_MUTANTS, TARGET_CONTROLS, TARGET_MISSING,
                 len(mutants), len(controls), len(missing_results)))
        return 1
    print("HARNESS: PASS -- %d/%d fault-injection cases (%d mutants, "
          "%d controls), %d/%d missing-document"
          % (cases_ok, TARGET_MUTANTS + TARGET_CONTROLS, TARGET_MUTANTS,
             TARGET_CONTROLS, d_ok, TARGET_MISSING))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print("FAIL  unexpected error: %s: %s" % (type(exc).__name__, exc))
        sys.exit(1)
