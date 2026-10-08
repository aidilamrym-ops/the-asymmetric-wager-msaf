# FILE: harnesses/p5_files_inj.py
# PURPOSE: A16-R1 closed by A20 -- prove report_claim_check's P5 now reads the
#          claim form it used to skip, and only that form.  The residual said
#          it plainly: "cannot read a bare N files / N-gate claim outside a
#          rows/gates= pattern, so stale figures reached a reader unchallenged."
#          Nine mutations against five tracked documents, each restored
#          byte-for-byte before the next:
#            M1  Brain.MD's canonical manifest tally moved by one (C1, no
#                escape hatch -- must FAIL as BRAIN_ROWS)
#            M2  README's contract-bullet files count moved by one (the new
#                digit form -- must FAIL as P5 manifest rows)
#            M3  the same bullet replaced by a spelled count (the new spoken
#                form -- must FAIL)
#            M4  README's reversed form "Proof harnesses: **N**" moved by
#                one -- no pattern read unit-then-number before A20
#            M5  an out-of-scope encoding scan (F6: "216 files report CR/BOM")
#                moved by one -- must stay GREEN: scope is what stops the new
#                pattern condemning true sentences about other objects
#            M6  an anchored history line (A16: "97 files (at A16)") moved by
#                one -- must stay GREEN: dated history is allowed
#            M7  the same line with its anchor stripped -- must FAIL
#            M8  F0's A18 summary moved by one, date kept (neighbour-line
#                anchor reach) -- must stay GREEN
#            M9  the same with the neighbour date stripped -- must FAIL
#          Every live number (manifest rows, harness count) is READ from the
#          rig at run time, the way a9_drift_inj.py does, so adding a gate or
#          a harness cannot rot this file.  Baseline and restored baseline must
#          both be green, and all five targets must come back byte-identical.
# EXIT:    0 = every case behaved as expected and the workspace was restored
#          1 = a case did not, or a byte did not come back
# MUTATION: mutates tracked root documents; restores before every assertion
#           and again at the end.  Nothing else is written.

import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
PY = sys.executable
GATE = os.path.join(ROOT, "report_claim_check.py")

import report_claim_check as RCC  # noqa: E402  (live values, not its main)

TARGETS = {
    "brain": os.path.join(ROOT, "Brain.MD"),
    "readme": os.path.join(ROOT, "README.md"),
    "a16": os.path.join(ROOT, "A16_REPORT.md"),
    "f6": os.path.join(ROOT, "F6_REPORT.md"),
    "f0": os.path.join(ROOT, "F0_REPORT.md"),
}

originals = {}    # raw bytes, for restore
baseline = {}     # sha256 of those bytes, for the byte-identity check
results = []


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def run_gate():
    p = subprocess.run([PY, GATE], cwd=ROOT, capture_output=True, timeout=300)
    out = ((p.stdout or b"") + (p.stderr or b"")).decode("utf-8", "replace")
    return p.returncode, out


def mutate(key, edits):
    text = originals[key].decode("utf-8")
    for old, new in edits:
        c = text.count(old)
        if c != 1:
            raise RuntimeError("needle %r occurs %d times in %s (want 1)"
                               % (old, c, key))
        text = text.replace(old, new, 1)
    with open(TARGETS[key], "wb") as fh:
        fh.write(text.encode("utf-8"))


def restore_all():
    for key, path in sorted(TARGETS.items()):
        with open(path, "wb") as fh:
            fh.write(originals[key])


def restored():
    return all(sha(TARGETS[k]) == v for k, v in baseline.items())


def record(label, passed, detail):
    results.append(passed)
    print("  %s   %s%s" % ("ok  " if passed else "FAIL",
                           label, ("  " + detail) if detail else ""))


def case(label, key, edits, want_rc, needles):
    mutate(key, edits)
    try:
        rc, out = run_gate()
    finally:
        restore_all()
    got = [n for n in needles if n not in out]
    passed = rc == want_rc and not got and restored()
    detail = "exit=%d want=%d" % (rc, want_rc)
    if got:
        detail += ", missing %s" % got
    if not restored():
        detail += ", TARGET NOT RESTORED"
    record(label, passed, detail)


def main():
    for key, path in sorted(TARGETS.items()):
        with open(path, "rb") as fh:
            originals[key] = fh.read()
        baseline[key] = sha(path)

    # Live rig values, read now so a future count change cannot rot the cases.
    L, err = RCC.live_values()
    if L is None:
        print("HARNESS: FAIL -- live values unavailable: %s" % err)
        return 1
    rows, harnesses = L["rows"], L["harnesses"]
    brain_text = originals["brain"].decode("utf-8")
    m = re.search(r"\*\*(\d+) files\*\*", brain_text)
    if m is None:
        print("HARNESS: FAIL -- Brain.MD declares no **N files** tally")
        return 1
    brain_old = m.group(0)
    brain_new = "**%d files**" % (rows - 1)
    bullet_old = "- Manifest scope: **%d** files" % rows
    bullet_new = "- Manifest scope: **%d** files" % (rows - 1)
    spelled_word = "ninety-nine" if str(rows) != "99" else "ninety-eight"
    bullet_spoken = "- Manifest scope: %s files" % spelled_word
    rev_old = "- Proof harnesses: **%d**" % harnesses
    rev_new = "- Proof harnesses: **%d**" % (harnesses - 1)

    print("P5 FILES INJECTION -- 9 mutations of report_claim_check's newest "
          "claim form (live rows=%d, harnesses=%d)" % (rows, harnesses))
    rc, out = run_gate()
    record("baseline green", rc == 0 and "report_claim_check: PASS" in out,
           "exit=%d" % rc)

    case("M1 Brain canonical tally moved by one (want BRAIN_ROWS)",
         "brain", [(brain_old, brain_new)], 1, ["BRAIN_ROWS"])
    case("M2 README files bullet moved by one (want P5 manifest rows)",
         "readme", [(bullet_old, bullet_new)], 1,
         ["manifest rows=%d" % (rows - 1)])
    case("M3 README files bullet spelled in words (want P5 spoken rows)",
         "readme", [(bullet_old, bullet_spoken)], 1,
         ["manifest rows=%s" % spelled_word])
    case("M4 README reversed form moved by one (want P5 harness count)",
         "readme", [(rev_old, rev_new)], 1,
         ["harness count=%d" % (harnesses - 1)])
    case("M5 out-of-scope encoding count 216 -> 217 stays GREEN",
         "f6", [("216 files report CR/BOM", "217 files report CR/BOM")], 0,
         ["report_claim_check: PASS"])
    case("M6 anchored history 97 -> 96 files (at A16) stays GREEN",
         "a16", [("manifest written, 97 files (at A16)",
                  "manifest written, 96 files (at A16)")], 0,
         ["report_claim_check: PASS"])
    case("M7 same line with anchor stripped (want P5 manifest rows)",
         "a16", [("manifest written, 97 files (at A16)",
                  "manifest written, 96 files")], 1, ["manifest rows=96"])
    case("M8 F0 summary moved by one, neighbour date kept, stays GREEN",
         "f0", [("manifest **101** files", "manifest **100** files")], 0,
         ["report_claim_check: PASS"])
    case("M9 same with the neighbour date stripped (want P5 manifest rows)",
         "f0", [("manifest **101** files", "manifest **100** files"),
                ("Rig after A18 (2026-10-07): suite",
                 "Rig after A18: suite")], 1, ["manifest rows=100"])

    rc, out = run_gate()
    record("restored baseline green",
           rc == 0 and "report_claim_check: PASS" in out, "exit=%d" % rc)
    record("all five targets byte-identical", restored(), "")

    passed = sum(1 for r in results if r)
    total = len(results)
    if passed == total and restored():
        print("HARNESS: PASS -- %d/%d cases behaved as expected, five targets "
              "byte-identical" % (passed, total))
        return 0
    print("HARNESS: FAIL -- %d/%d cases behaved as expected" % (passed, total))
    return 1


if __name__ == "__main__":
    sys.exit(main())
