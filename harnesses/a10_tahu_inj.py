# FILE: harnesses/a10_tahu_inj.py
# PURPOSE: prove tahap_uji_audit.py is a gate and not a reviewer's habit.
#
# A gate whose every condition has only ever returned "ok" has not been
# tested.  This harness applies independent defects to the two live
# `tahap uji` documents and requires the audit gate to reject each one,
# then requires the gate to pass again on the restored bytes.
#
# Defect classes (each aimed at a different condition):
#   C1  vacuum: claim "error = 0"            -> V3
#   C2  vacuum: drop the Planck density needle -> V2
#   C3  vacuum: delete "remains open"        -> V3
#   C4  vacuum: drop "dimensionless"         -> V4
#   C5  sieve: claim Navier-Stokes proven    -> V6
#   C6  sieve: delete the Gate 2 not-implemented sentence -> V8
#   C7  sieve: claim the Protocol 09 context proves all SAT -> V7
#   C8  vacuum: re-introduce "renormalisasi kotor" -> V3
#
# Both tracked documents are restored byte-for-byte; harness_check.py hashes
# the workspace before and after and fails if a single byte does not return.
#
# EXIT:   0 = every case behaved as required, bytes restored
#         1 = a case was not caught, or the baseline stopped passing
#         2 = a tool the harness needs is missing (never reported as success)

import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GATE = os.path.join(ROOT, "tahap_uji_audit.py")
VAC = os.path.join(ROOT, "Theory_of_Everything_Derivations", "tahap uji",
                   "THE_VACUUM_CATASTROPHE_SOLUTION.md")
SIEVE = os.path.join(ROOT, "Theory_of_Everything_Derivations", "tahap uji",
                     "THE_SOVEREIGN_SIEVE_PROTOCOL.md")
PY = sys.executable

TARGET = "HARNESS: PASS -- 8/8 cases"

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL  %s" % msg)


def check(cond, msg):
    if not cond:
        fail(msg)
    return cond


def run_gate():
    p = subprocess.run([PY, GATE], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    lines = [l for l in (p.stdout or "").splitlines() if l.startswith("FAIL")]
    return p.returncode, lines


def read(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def apply_edits(path, pairs):
    text = read(path)
    mutated = text
    for old, new in pairs:
        if old not in mutated:
            fail("mutation needle absent in %s: %r" % (os.path.basename(path), old[:60]))
            continue
        mutated = mutated.replace(old, new, 1)
    if mutated != text:
        write(path, mutated)
    return mutated != text


CASES = [
    ("C1 vacuum error=0", VAC,
     [("They are withdrawn.",
       "Absolute error equals zero and the computation is fully verified.")],
     "V3"),
    ("C2 vacuum drop density needle", VAC,
     [("`5{,}867696 \\times 10^{111}`", "`5{,}867696 \\times 10^{110}`")],
     "V2"),
    ("C3 vacuum drop remains-open", VAC,
     [("and **remains open** in this corpus",
       "and is fully resolved in this corpus")],
     "V3"),
    ("C4 vacuum drop dimensionless", VAC,
     [("Its reciprocal is\ndimensionless (a length ratio, **not** a frequency in s$^{-1}$).",
       "Its reciprocal is\na frequency in s$^{-1}$ (a length ratio).")],
     "V4"),
    ("C5 sieve NS proven", SIEVE,
     [("This corpus does **not** prove that solutions are\n  smooth.",
       "This corpus proves that solutions are\n  smooth.")],
     "V6"),
    ("C6 sieve Gate 2 not implemented", SIEVE,
     [("**Not implemented.** No gate script in this workspace checks for local quantum black-hole formation.",
       "Implemented and passing on every scale.")],
     "V8"),
    ("C7 sieve Gate 3 all-SAT", SIEVE,
     [("It does\n**not** mean \"every claim written in prose is true\".",
       "It does\n**mean** that every claim written in prose is true.")],
     "V7"),
    ("C8 vacuum dirty renormalisation", VAC,
     [("This\n  document does not call it a \"dirty trick\"",
       "This\n  document calls it renormalisasi kotor")],
     "V3"),
]


def main():
    baseline_rc, baseline_fails = run_gate()
    if baseline_rc != 0:
        fail("baseline gate did not exit 0 (rc=%d, fails=%d): %s"
             % (baseline_rc, len(baseline_fails), baseline_fails[:3]))
        print("%s" % TARGET.replace("PASS", "FAIL"))
        return 1

    raw_vac = read(VAC)
    raw_sieve = read(SIEVE)
    caught = 0
    total = len(CASES)

    for label, path, pairs, needle in CASES:
        # restore first so each case starts from the shipped bytes
        write(VAC, raw_vac)
        write(SIEVE, raw_sieve)
        if not apply_edits(path, pairs):
            fail("%s: mutation did not apply" % label)
            continue
        rc, fails = run_gate()
        if rc == 0:
            fail("%s: gate still exited 0 after mutation" % label)
            continue
        if not any(needle in f for f in fails):
            fail("%s: gate failed but without needle %r (got %r)"
                 % (label, needle, fails[:4]))
            continue
        print("ok    %s -> %s" % (label, needle))
        caught += 1

    # restore and require green baseline again
    write(VAC, raw_vac)
    write(SIEVE, raw_sieve)
    final_rc, final_fails = run_gate()
    if final_rc != 0:
        fail("restored baseline did not exit 0 (rc=%d)" % final_rc)

    if caught == total and final_rc == 0 and not failures:
        print("%s" % TARGET)
        print("HARNESS: PASS -- %d/%d cases behaved as expected, "
              "documents byte-identical, gate green at the end"
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
