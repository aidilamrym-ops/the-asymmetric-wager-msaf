# FILE: harnesses/a3_report_inj.py
# PURPOSE: prove report_claim_check.py can fail.
#
# The gate reads prose, and prose is the one part of this workspace that every
# other gate ignores.  A gate over sentences that has only ever printed "PASS"
# is a gate that has been run, not a gate that has been tested.  This harness
# applies ten defects, each aimed at a different condition, and requires the
# gate to reject every one of them:
#
#   SKILL_GATES  Skill.md's root-gate count        -> the canonical suite number
#   BRAIN_FOLDER Brain.MD's harness folder count   -> the canonical harness number
#   SKILL_ENTRY  Skill.md's --with-harness ordinal -> the appended-entry ordinal
#   P5           an unanchored stale tally in a report -> the dated-claim rule
#   P6           a citation of a harness that does not exist -> the reference rule
#   P4           a second Brain.MD version string  -> the version rule
#   SPOKEN_*     a stale cardinal word in the constitution -> the spelled-out
#                reading of the same rule (a number written as words is a
#                claim exactly as a digit is, and the sweep must not lap)
#   P5 spoken    an unanchored stale cardinal word in a report -> the dated-claim
#                rule applied to words instead of digits
#   P6 row       a file named on a line whose own column claims it lives in
#                harnesses\ -> the form of citation P6 originally missed
#   P8           a root file the knowledge map does not name -> the map rule
#
# The numbers are read from the live rig rather than written into this file,
# so the harness does not rot the moment a gate or a harness is added: each
# defect is always "one more than whatever is true today".
#
# Each case is applied, observed and reverted before the next begins, so one
# over-broad check cannot satisfy the whole harness.  The baseline is required
# to pass before the first case and again after the last one, byte-identical.
#
# EXIT:   0 = every case was caught, baseline green, bytes restored
#         1 = a case was not caught, or the baseline stopped passing
#         2 = a tool the harness needs is missing (never reported as success)

import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GATE = os.path.join(ROOT, "report_claim_check.py")
PY = sys.executable

sys.path.insert(0, ROOT)
import harness_check
import suite_check

SKILL = "Skill.md"
BRAIN = "Brain.MD"
F4 = "F4_REPORT.md"

GATES = len(suite_check.GATES)
HARNS = len(harness_check.HARNESSES)

ORDINALS = ["zeroth", "first", "second", "third", "fourth", "fifth", "sixth",
            "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth",
            "thirteenth", "fourteenth", "fifteenth", "sixteenth",
            "seventeenth", "eighteenth", "nineteenth", "twentieth"]

CARDINALS = ["zero", "one", "two", "three", "four", "five", "six", "seven",
             "eight", "nine", "ten", "eleven", "twelve", "thirteen",
             "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
             "nineteen", "twenty", "twenty-one", "twenty-two", "twenty-three",
             "twenty-four", "twenty-five", "twenty-six", "twenty-seven",
             "twenty-eight", "twenty-nine", "thirty"]

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL  %s" % msg)


def ordinal(n):
    return ORDINALS[n] if 0 <= n < len(ORDINALS) else str(n)


def spelled(n):
    return CARDINALS[n] if 0 <= n < len(CARDINALS) else str(n)


def read(name):
    with io.open(os.path.join(ROOT, name), "rb") as fh:
        return fh.read()


def write_raw(name, data):
    if b"\r" in data:
        raise SystemExit("BLOCKED %s: CR introduced" % name)
    with io.open(os.path.join(ROOT, name), "wb") as fh:
        fh.write(data)


def run_gate():
    """Returns (exit code, FAIL lines, last verdict line)."""
    p = subprocess.run([PY, GATE], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    out = p.stdout or ""
    verdict = [l for l in out.splitlines()
               if l.startswith("report_claim_check:")]
    return p.returncode, [l for l in out.splitlines() if l.startswith("FAIL")], \
        (verdict[-1] if verdict else "<no verdict>")


def sub_group(name, pattern, replacement):
    """Rewrite capture group 1 of the single match, returning old bytes."""
    data = read(name)
    text = data.decode("utf-8")
    rx = re.compile(pattern)
    hits = list(rx.finditer(text))
    if len(hits) != 1:
        raise SystemExit("BLOCKED %s: /%s/ matched %d times, wanted 1"
                         % (name, pattern, len(hits)))
    m = hits[0]
    if not m.group(1):
        raise SystemExit("BLOCKED %s: /%s/ has no capture group" % (name, pattern))
    new = text[:m.start(1)] + replacement(m) + text[m.end(1):]
    if new == text:
        raise SystemExit("BLOCKED %s: rewrite changed nothing" % name)
    write_raw(name, new.encode("utf-8"))
    return data


def append_line(name, line):
    """Append a blank line then `line`, returning the old bytes."""
    data = read(name)
    text = data.decode("utf-8")
    if not text.endswith("\n"):
        raise SystemExit("BLOCKED %s: no trailing newline" % name)
    if line in text:
        raise SystemExit("BLOCKED %s: injected line already present" % name)
    write_raw(name, (text + "\n" + line + "\n").encode("utf-8"))
    return data


# (label, needle the gate must print, apply, target file)
CASES = [
    ("SKILL_GATES  suite gate count",
     "SKILL_GATES",
     lambda: sub_group(SKILL, r"runs the (\d+) root gates",
                       lambda m: "runs the %d root gates" % (GATES + 1)),
     SKILL),
    ("BRAIN_FOLDER harness folder count",
     "BRAIN_FOLDER",
     lambda: sub_group(BRAIN, r"The (\d+) proof harnesses, checked into",
                       lambda m: "The %d proof harnesses, checked into"
                                 % (HARNS + 1)),
     BRAIN),
    ("SKILL_ENTRY  --with-harness ordinal",
     "SKILL_ENTRY",
     lambda: sub_group(SKILL, r"as a (\w+) entry",
                       lambda m: "as a %s entry" % ordinal(GATES + 2)),
     SKILL),
    ("P5           unanchored stale tally",
     "P5 %s" % F4,
     lambda: append_line(F4, "passed=99  failed=0  not_run=0  of 99"),
     F4),
    ("P6           ghost harness citation",
     "P6 reports name harnesses",
     lambda: append_line(F4, "`harnesses\\nosuch_harness.py` is cited here "
                             "but was never written"),
     F4),
    ("P4           second version string",
     "P4 Brain.MD declares",
     lambda: append_line(BRAIN, "Brain.MD v1.99"),
     BRAIN),
    ("SPOKEN_BRAIN_GATES stale cardinal word",
     "SPOKEN_BRAIN_GATES",
     lambda: sub_group(BRAIN,
                       r"the (" + spelled(GATES) + r") gates are a read-only contract",
                       lambda m: "the %s gates are a read-only contract"
                                 % spelled(GATES + 1)),
     BRAIN),
    ("P5 spoken    unanchored stale cardinal",
     "harness count=",
     lambda: append_line(F4, "All %s harnesses are enumerated in this "
                             "paragraph." % spelled(HARNS + 1)),
     F4),
    ("P6 row      ghost file behind a harnesses/ column",
     "P6 F4_REPORT.md",
     lambda: append_line(F4, "| `f4_ghost_survey.py` | corpus survey "
                             "(harnesses/) |"),
     F4),
    ("P8          a root file the map does not name",
     "P8 Brain.MD does not name",
     lambda: sub_group(BRAIN, r"`(AGENTS\.md)`",
                       lambda m: "`AGENTS_probed.md`"),
     BRAIN),
]


def main():
    print("report claim injection harness -- %d cases against %s"
          % (len(CASES), os.path.basename(GATE)))
    print("live values: suite=%d harnesses=%d" % (GATES, HARNS))
    if not os.path.isfile(GATE):
        print("SKIP  gate is missing: %s" % GATE)
        print("HARNESS: SKIP -- tool not run")
        return 2

    rc, fails, verdict = run_gate()
    if rc != 0:
        print("SKIP  baseline must pass before injection, got exit %d (%s)"
              % (rc, verdict))
        for line in fails:
            print("      " + line)
        print("HARNESS: FAIL -- baseline not green, nothing was injected")
        return 1
    print("ok  baseline exit 0, %s" % verdict)

    caught = 0
    for label, needle, apply, target in CASES:
        before = read(target)
        try:
            apply()
        except SystemExit as exc:
            fail("%s: could not be applied -- %s" % (label, exc))
            continue
        rc, fails, verdict = run_gate()
        write_raw(target, before)
        if rc == 0:
            fail("%s: gate returned 0 -- the defect was NOT caught" % label)
            continue
        if not any(needle in f for f in fails):
            fail("%s: gate returned %d but never named %r (verdict %s)"
                 % (label, rc, needle, verdict))
            continue
        if read(target) != before:
            fail("%s: target not byte-identical after revert" % label)
            continue
        caught += 1
        print("ok  %-36s caught, exit %d" % (label, rc))

    rc, fails, verdict = run_gate()
    if rc != 0:
        fail("restored baseline: exit %d (%s)" % (rc, verdict))
        for line in fails:
            print("      " + line)
    else:
        print("ok  restored baseline exit 0, %s" % verdict)

    total = len(CASES)
    if failures:
        print("HARNESS: FAIL -- %d/%d cases caught, %d defect(s)"
              % (caught, total, len(failures)))
        return 1
    print("HARNESS: PASS -- %d/%d cases caught, baseline and restored baseline "
          "exit 0, every target byte-identical" % (caught, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
