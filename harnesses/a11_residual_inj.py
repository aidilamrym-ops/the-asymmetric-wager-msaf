# FILE: harnesses/a11_residual_inj.py
# PURPOSE: prove the A11 residual closures can fail.
#
# A11 closed two F8 residuals and neither may close on a green run alone.
# F8-R1 said report_claim_check never parsed the string form "N conditions"
# as a claim about provenance_check.CONDITIONS; F8-R2 said the liveness
# record's freshness was not gated at all.  Both are now answered by new
# machinery, and new machinery that has only ever printed PASS is a tool that
# has been run, not a tool that has been tested.
#
# Group 1 -- conditions claim (F8-R1).  A line whose scope names the constants
# gate and carries "N conditions" must equal len(CONDITIONS); anchored history
# is allowed; lines outside that scope are not compared against this gate:
#
#   C1 "nine conditions" on a provenance line, no anchor -> P9 FAIL
#   C2 "11 conditions" on a provenance line              -> control, PASS
#   C3 "ten conditions as of F5"                         -> history, PASS
#   C4 "19 conditions" on a znone line (out of scope)    -> control, PASS
#
# Group 2 -- liveness age (F8-R2).  P11 measures and prints record age; a
# future-dated generated_utc is impossible and fails; malformed stamps fail;
# a well-formed past stamp passes with age printed:
#
#   A1 generated_utc in the future                       -> P11 FAIL "future"
#   A2 generated_utc malformed                           -> P11 FAIL "malformed"
#   A3 baseline record                                   -> control, age printed
#
# Every mutation is applied, observed and reverted before the next begins,
# and the baseline must be green before the first case and again after the
# last, with every target byte-identical.
#
# EXIT:   0 = every case behaved, baseline green, bytes restored
#         1 = a case was not caught, or a baseline stopped passing
#         2 = a tool this harness needs is missing (never reported as success)

import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GATE = os.path.join(ROOT, "report_claim_check.py")
PROV = os.path.join(ROOT, "provenance_check.py")
RECORD = os.path.join(ROOT, "provenance", "url_liveness.json")
REPORT = "F8_REPORT.md"
PY = sys.executable

TARGET = "HARNESS: PASS -- 7/7 cases"

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL  %s" % msg)


def read_root(name):
    with io.open(os.path.join(ROOT, name), "rb") as fh:
        return fh.read()


def write_root(name, data):
    if b"\r" in data:
        raise SystemExit("BLOCKED %s: CR introduced" % name)
    with io.open(os.path.join(ROOT, name), "wb") as fh:
        fh.write(data)


def run_gate():
    p = subprocess.run([PY, GATE], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120,
                       cwd=ROOT)
    out = p.stdout or ""
    fails = [l for l in out.splitlines() if l.startswith("FAIL")]
    return p.returncode, fails, out


def run_prov():
    p = subprocess.run([PY, PROV], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120,
                       cwd=ROOT)
    out = p.stdout or ""
    fails = [l for l in out.splitlines() if l.startswith("FAIL")]
    return p.returncode, fails, out


def append_line(name, line):
    data = read_root(name)
    text = data.decode("utf-8")
    if not text.endswith("\n"):
        raise SystemExit("BLOCKED %s: no trailing newline" % name)
    if line in text:
        raise SystemExit("BLOCKED %s: injected line already present" % name)
    write_root(name, (text + "\n" + line + "\n").encode("utf-8"))


def rewrite_record(transform):
    with io.open(RECORD, encoding="utf-8") as fh:
        doc = json.load(fh)
    new = transform(json.loads(json.dumps(doc)))
    text = json.dumps(new, indent=2, ensure_ascii=False) + "\n"
    write_root("provenance/url_liveness.json", text.encode("utf-8"))


def set_future(doc):
    doc["generated_utc"] = "2099-01-01T00:00:00Z"
    return doc


def set_malformed(doc):
    doc["generated_utc"] = "not-a-timestamp"
    return doc


CASES = [
    ("C1 nine conditions no anchor", "gate",
     "provenance_check has nine conditions in total.",
     "P9"),
    ("C2 eleven conditions control", "gate",
     "provenance_check has 11 conditions in total.",
     None),
    ("C3 ten conditions as of F5", "gate",
     "provenance_check had ten conditions as of F5 (2026-10-05).",
     None),
    ("C4 znone nineteen conditions out of scope", "gate",
     "znone_check has nineteen conditions in total.",
     None),
    ("A1 generated_utc future", "prov_record", set_future, "future"),
    ("A2 generated_utc malformed", "prov_record", set_malformed, "malformed"),
    ("A3 baseline age printed", "prov_record", None, None),
]


def main():
    raw_report = read_root(REPORT)
    raw_record = read_root("provenance/url_liveness.json")

    baseline_rc, baseline_fails, _ = run_gate()
    if baseline_rc != 0:
        fail("baseline report_claim_check did not exit 0 (rc=%d, fails=%s)"
             % (baseline_rc, baseline_fails[:3]))
        print(TARGET.replace("PASS", "FAIL"))
        return 1
    prov_rc, prov_fails, _ = run_prov()
    if prov_rc != 0:
        fail("baseline provenance_check did not exit 0 (rc=%d, fails=%s)"
             % (prov_rc, prov_fails[:3]))
        print(TARGET.replace("PASS", "FAIL"))
        return 1

    caught = 0
    total = len(CASES)

    for label, kind, payload, needle in CASES:
        write_root(REPORT, raw_report)
        write_root("provenance/url_liveness.json", raw_record)
        if kind == "gate":
            append_line(REPORT, payload)
            rc, fails, out = run_gate()
        else:
            if payload is None:
                rc, fails, out = run_prov()
            else:
                rewrite_record(payload)
                rc, fails, out = run_prov()
        if needle is None:
            # control: gate must stay green; A3 must also print record age
            if rc != 0:
                fail("%s: control did not stay green (rc=%d, fails=%s)"
                     % (label, rc, fails[:3]))
                continue
            if label.startswith("A3") and "age:" not in out:
                fail("%s: control did not print record age" % label)
                continue
            print("ok    %s -> control green" % label)
            caught += 1
            continue
        if rc == 0:
            fail("%s: gate still exited 0 after mutation" % label)
            continue
        if not any(needle in f for f in fails):
            fail("%s: gate failed but without needle %r (got %r)"
                 % (label, needle, fails[:4]))
            continue
        print("ok    %s -> %s" % (label, needle))
        caught += 1

    write_root(REPORT, raw_report)
    write_root("provenance/url_liveness.json", raw_record)
    final_rc, final_fails, _ = run_gate()
    if final_rc != 0:
        fail("restored report_claim_check did not exit 0 (rc=%d)" % final_rc)
    final_prov, final_prov_fails, final_prov_out = run_prov()
    if final_prov != 0:
        fail("restored provenance_check did not exit 0 (rc=%d)" % final_prov)
    if "age:" not in final_prov_out:
        fail("restored provenance_check did not print record age")

    if caught == total and final_rc == 0 and final_prov == 0 and not failures:
        print(TARGET)
        print("HARNESS: PASS -- %d/%d cases behaved as expected, "
              "targets byte-identical, both gates green at the end"
              % (caught, total))
        return 0
    print("HARNESS: FAIL -- %d/%d cases behaved as expected, %d defect(s)"
          % (caught, total, len(failures)))
    return 1


if __name__ == "__main__":
    try:
        rc = main()
    except Exception as exc:
        print("FAIL  unexpected error: %s: %s" % (type(exc).__name__, exc))
        rc = 2
    sys.exit(rc)
