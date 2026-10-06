# FILE: harnesses/p09_inj.py
# PURPOSE: prove protocol_09_check.py can fail.
#
# A gate whose every condition has only ever returned "ok" has not been
# tested; it has merely been run.  This harness applies four independent
# defects to the shipped encoding and requires the gate to reject each one,
# then requires the gate to pass again on the restored bytes.
#
# The four defects target four different conditions, so that a single
# over-broad check cannot satisfy the whole harness:
#   C1  the context is made inconsistent without changing the assertion
#       count or the claim's position  -> P5 must call it VACUOUS
#   C2  the log's sha256 is clobbered   -> P2 must call the log stale
#   C3  a core axiom is deleted         -> P4 must see the script go sat
#   C4  the MACHINE RESULT marker goes  -> P3 must find nothing to bind
#
# Both tracked artefacts are restored byte-for-byte; harness_check.py hashes
# the workspace before and after and fails if a single byte does not return.
#
# EXIT:   0 = every case behaved as required, bytes restored
#         1 = a case was not caught, or the baseline stopped passing
#         2 = a tool the harness needs is missing (never reported as success)

import hashlib
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GATE = os.path.join(ROOT, "protocol_09_check.py")
SMT = os.path.join(ROOT, "protocol_09.smt2")
LOG = os.path.join(ROOT, "protocol_09.log")
PY = sys.executable

TARGET = "HARNESS: PASS -- 6/6 cases"

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL  %s" % msg)


def check(cond, msg):
    if not cond:
        fail(msg)
    return cond


def run_gate():
    """Run the gate.  Returns (exit code, list of FAIL lines)."""
    p = subprocess.run([PY, GATE], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600)
    lines = [l for l in (p.stdout or "").splitlines() if l.startswith("FAIL")]
    return p.returncode, lines


def rebind_log(new_raw):
    """Point the log at a script it has not seen, so P2 cannot mask P4/P5."""
    digest = hashlib.sha256(new_raw.encode("utf-8")).hexdigest()
    with io.open(LOG, encoding="utf-8", newline="") as fh:
        log = fh.read()
    log, n = re.subn(r"^sha256\s*:\s*[0-9a-f]{64}$", "sha256   : %s" % digest,
                     log, count=1, flags=re.M)
    if n != 1:
        fail("could not re-bind the log sha256 line (%d replacements)" % n)
        return
    with io.open(LOG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(log)


def apply_raw(text):
    with io.open(SMT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def main():
    for path in (GATE, SMT, LOG):
        if not check(os.path.isfile(path), "missing prerequisite: %s" % path):
            print("")
            print("%s" % ("HARNESS: FAIL -- %s" % ", ".join(failures)))
            return 1

    with io.open(SMT, "rb") as fh:
        orig_smt = fh.read()
    with io.open(LOG, "rb") as fh:
        orig_log = fh.read()

    raw = orig_smt.decode("utf-8")
    cases = []

    try:
        # ------------------------------------------------ case 1: baseline --
        rc, fails = run_gate()
        ok = check(rc == 0 and not fails,
                   "C1 baseline: gate must pass on the shipped bytes, "
                   "got exit %d with %d FAIL line(s)" % (rc, len(fails)))
        for line in fails:
            print("      %s" % line[:170])
        cases.append(("baseline", ok))

        # ------------------------------ case 2: context made inconsistent --
        # Replace N > 0 by (and N > 0  N < 0): the context collapses, the
        # assertion count is unchanged, and the claim stays at index 15, so
        # nothing structural can trip the gate before P5 gets to look.
        mutated = raw.replace("(assert (> N 0))",
                              "(assert (and (> N 0) (< N 0)))", 1)
        if check(mutated != raw, "C2 mutation did not apply (needle absent)"):
            apply_raw(mutated)
            rebind_log(mutated)
            rc, fails = run_gate()
            hit = any("P5" in f and "VACUOUS" in f for f in fails)
            auditor = any("P8" in f and "VACUOUS" in f for f in fails)
            ok = check(rc == 1 and hit,
                       "C2 vacuous context: gate must exit 1 with a P5 "
                       "VACUOUS failure, got exit %d and %r"
                       % (rc, [f[:60] for f in fails[:3]]))
            if not check(auditor,
                         "C2 vacuous context: the auditor condition P8 should "
                         "independently report VACUOUS"):
                pass
            cases.append(("vacuous context", ok))
            with io.open(SMT, "wb") as fh:
                fh.write(orig_smt)
            with io.open(LOG, "wb") as fh:
                fh.write(orig_log)

        # ------------------------------------------------ case 3: stale log --
        clobbered = re.sub(r"^sha256\s*:\s*[0-9a-f]{64}$",
                           "sha256   : " + "0" * 64,
                           orig_log.decode("utf-8"), count=1, flags=re.M)
        if check(clobbered != orig_log.decode("utf-8"),
                 "C3 mutation did not apply (sha256 line absent)"):
            with io.open(LOG, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(clobbered)
            rc, fails = run_gate()
            hit = any("P2" in f and "stale" in f for f in fails)
            ok = check(rc == 1 and hit,
                       "C3 stale log: gate must exit 1 with a P2 stale-log "
                       "failure, got exit %d" % rc)
            cases.append(("stale log hash", ok))
            with io.open(LOG, "wb") as fh:
                fh.write(orig_log)

        # ------------------------------------------- case 4: axiom removed --
        mutated = raw.replace("(assert (> M N))\n", "", 1)
        if check(mutated != raw, "C4 mutation did not apply (needle absent)"):
            apply_raw(mutated)
            rebind_log(mutated)
            rc, fails = run_gate()
            hit = any(f.startswith("FAIL  P4") for f in fails)
            ok = check(rc == 1 and hit,
                       "C4 removed axiom: gate must exit 1 with a P4 "
                       "failure (the script is no longer unsat or no longer "
                       "carries the claim), got exit %d" % rc)
            cases.append(("core axiom removed", ok))
            with io.open(SMT, "wb") as fh:
                fh.write(orig_smt)
            with io.open(LOG, "wb") as fh:
                fh.write(orig_log)

        # ------------------------------------------------ case 5: no marker --
        mutated = raw.replace("; MACHINE RESULT: unsat",
                              "; machine verdict", 1)
        if check(mutated != raw, "C5 mutation did not apply (needle absent)"):
            apply_raw(mutated)
            rebind_log(mutated)
            rc, fails = run_gate()
            hit = any(f.startswith("FAIL  P3") for f in fails)
            ok = check(rc == 1 and hit,
                       "C5 missing marker: gate must exit 1 with a P3 "
                       "failure, got exit %d" % rc)
            cases.append(("MACHINE RESULT removed", ok))
            with io.open(SMT, "wb") as fh:
                fh.write(orig_smt)
            with io.open(LOG, "wb") as fh:
                fh.write(orig_log)

    finally:
        # Bytes come back no matter what happened above; harness_check.py
        # hashes the workspace before and after and fails if they differ.
        with io.open(SMT, "wb") as fh:
            fh.write(orig_smt)
        with io.open(LOG, "wb") as fh:
            fh.write(orig_log)

    # ------------------------------------------------- restored baseline ----
    rc, fails = run_gate()
    ok = check(rc == 0 and not fails,
               "restored baseline: gate must pass again after every "
               "mutation, got exit %d" % rc)
    for line in fails:
        print("      %s" % line[:170])
    cases.append(("restored baseline", ok))

    caught = sum(1 for _, good in cases if good)
    total = len(cases)
    print("")
    for label, good in cases:
        print("  %s %-24s %s" % ("ok  " if good else "FAIL  ", label,
                                 "caught" if good else "NOT caught"))
    print("")
    if failures:
        print("HARNESS: FAIL -- %d/%d cases" % (caught, total))
        return 1
    print("%s (%d injected defects + baseline + restored)" % (TARGET, total - 2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print("FAIL  unexpected error: %s: %s" % (type(exc).__name__, exc))
        sys.exit(1)
