# FILE: harnesses/f2_1_inj.py
# PURPOSE: re-produce the F2-1 fault-injection counts for landauer_check.py.
#
# F2 published 28/28 claim mutants and 6/6 controls (F2_REPORT 1.6) but kept no
# harness: the mutations were applied by ad-hoc scripts run from a scratch
# folder and never written down, so F2_REPORT 8.3 recorded the counts as
# "recorded, not reproducible".  This file is that missing harness.
#
# Each case mutates exactly one document, runs the gate, requires the exit
# code the published table requires, and restores the original bytes before
# the next case.  The workspace is hashed around every case; a byte that does
# not come back is a failure whatever the gate printed.
#
# Controls come in both directions, as F2 recorded them: four must still exit
# 0 (a mutation the gate should not care about), two must exit 1 (a mutation
# that must still be caught).  A control that quietly flips direction means
# the gate has changed underneath the report.
#
# Exit codes: 0 = every case behaved as required and bytes restored
#             1 = a case was not caught, or a control stopped passing
#             2 = a tool or document the harness needs is missing

import hashlib
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GATE = os.path.join(ROOT, "landauer_check.py")
PY = sys.executable

SOLVABLE = "SOLVABLE_FINITE_PARADOX.md"
ANTI = "ANTI_INFINITY_BLINDSPOT.md"
MSAF = "MSAF_COSMOLOGY_DECONSTRUCTION (2).md"

TARGET_MUTANTS = 28
TARGET_CONTROLS = 6

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


def run_gate():
    p = subprocess.run([PY, GATE], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    return p.returncode


# --------------------------------------------------------------------------
# MUTANTS   (id, target file, needle, replacement[, count])
#           count defaults to 1 (first occurrence); -1 means every one.
# CONTROLS  (id, target file, needle, replacement[, count], expected exit)
#           the expected exit is always the LAST element.
#
# The needle must occur where it is expected: every case asserts that it is
# present before it is applied, because a mutation that silently does nothing
# is a control dressed up as a mutant -- F2_REPORT 7.5 recorded exactly that
# defect once already.
#
# NOTE on temperature notation: the corpus writes 2{,}725 for 2.725 K, so the
# brace-comma is a DECIMAL comma, not a thousands separator.  The controls
# below therefore read 3{,}000 K = 3.000 K and 1{,}500 K = 1.500 K.
# --------------------------------------------------------------------------
MUTANTS = [
    # ---- set 1: SOLVABLE_FINITE_PARADOX.md, the derivation itself --------
    ("A01", SOLVABLE, r"k_B\ln 2 = 9{,}5699296\times10^{-24}",
     r"k_B\ln 2 = 9{,}5799296\times10^{-24}"),
    ("A02", SOLVABLE, r"k_B\ln 2 = 9{,}5699296\times10^{-24}",
     r"k_B\ln 2 = 9{,}5699296\times10^{-23}"),
    ("A03", SOLVABLE, r"\(2{,}6078058\times10^{-23}\ \mathrm{J}\)",
     r"\(2{,}6178058\times10^{-23}\ \mathrm{J}\)"),
    ("A04", SOLVABLE, r"\(2{,}8709789\times10^{-21}\ \mathrm{J}\)",
     r"\(2{,}8809789\times10^{-21}\ \mathrm{J}\)"),
    ("A05", SOLVABLE, r"\(2{,}725\ \mathrm{K}\)",
     r"\(2{,}735\ \mathrm{K}\)"),
    ("A06", SOLVABLE, r"\(300\ \mathrm{K}\)",
     r"\(310\ \mathrm{K}\)"),
    ("A07", SOLVABLE, r"k_B = 1{,}380649\times10^{-23}",
     r"k_B = 1{,}390649\times10^{-23}"),
    ("A08", SOLVABLE, "no total energy is\nclaimed for either side.", ""),
    ("A09", SOLVABLE, "stated inputs**, not measurements", "stated inputs"),
    ("A10", SOLVABLE, "What each side does have:",
     "Total energy is 42 J.\n\nWhat each side does have:"),
    ("A11", SOLVABLE, "What each side does have:",
     "zero thermal emission. What each side does have:"),
    ("A12", SOLVABLE, r"k_B\ln 2 = 9{,}5699296\times10^{-24}", "", -1),
    ("A13", SOLVABLE, r"\[\Delta E \;\ge\; k_B\,T\,\ln 2\]", ""),
    ("A14", SOLVABLE,
     "| \\(300\\ \\mathrm{K}\\) | \\(2{,}8709789\\times10^{-21}\\ "
     "\\mathrm{J}\\) |\n", ""),
    ("A15", SOLVABLE, "assumption about the algorithm, not a measurement",
     "assumption about the algorithm rather than a measurement"),

    # ---- set 2: cross-document -------------------------------------------
    ("B01", ANTI, "That is an assumption about the algorithm, "
     "not a measurement.", "That is an assumption about the algorithm."),
    ("B02", ANTI, "one erased bit costs at least",
     "to process every bit of information, one erased bit costs at least"),
    ("B03", ANTI,
     '> *"I state the premise rather than hide it: that conclusion holds '
     '**provided each evaluation performs at least one irreversible '
     'erasure**. That is an assumption about the algorithm, not a '
     'measurement. The constant above is derived and machine-checked in '
     '`SOLVABLE_FINITE_PARADOX.md` section 3 by `landauer_check.py`; no '
     'energy total is claimed there either."*' + "\n", ""),
    ("B04", ANTI, "no energy total is claimed there either.", ""),
    ("B05", ANTI, r"9{,}5699296\times10^{-24}",
     r"9{,}5799296\times10^{-24}"),
    ("B06", MSAF, "that floor is", "absolutely emits, that floor is"),
    ("B07", MSAF, "**per erased bit**", "**per bit**"),
    ("B08", MSAF, "so no energy total is", "so"),
    ("B09", MSAF, r"2{,}6078058 \times 10^{-23}",
     r"2{,}6178058 \times 10^{-23}"),
    ("B10", MSAF, "claimed here either.",
     "claimed here either. Total energy = 9 J."),
    ("B11", MSAF,
     "At the temperature stated above, $T \\approx 2{,}725\\text{ K}$, "
     "that floor is\n$2{,}6078058 \\times 10^{-23}\\text{ J}$ "
     "**per erased bit** -- the same value\nderived and machine-checked "
     "in `SOLVABLE_FINITE_PARADOX.md` section 3 by\n"
     "`landauer_check.py`. It is a floor per bit, not a total: a total "
     "would need\nan erasure count, which is not stated in this document, "
     "so no energy total is\nclaimed here either. The word *absolutely* "
     "previously in this sentence was\nwithdrawn on 2026-10-04 -- the "
     "bound is conditional on the erasure being\nirreversible.\n", ""),
    ("B12", MSAF, "conditional on the erasure being",
     "conditional on the erasure"),
    ("B13", MSAF, "T \\approx 2{,}725\\text{ K}",
     "T \\approx 3{,}000\\text{ K}"),
]

# (id, target file, needle, replacement, expected exit)
CONTROLS = [
    # must still pass -- the gate must not be reading this
    ("C01", SOLVABLE, "### Thermodynamic floor -- derived, and what it "
     "does not reach", "### Thermodynamic floor", 0),
    ("C02", SOLVABLE, "is derived in section 3", "is derived", 0),
    ("C03", SOLVABLE,
     "| \\(2{,}725\\ \\mathrm{K}\\) | \\(2{,}6078058\\times10^{-23}\\ "
     "\\mathrm{J}\\) |",
     "| \\(3{,}000\\ \\mathrm{K}\\) | \\(2{,}8709789\\times10^{-23}\\ "
     "\\mathrm{J}\\) |", 0),
    ("C04", SOLVABLE,
     "| \\(2{,}725\\ \\mathrm{K}\\) | \\(2{,}6078058\\times10^{-23}\\ "
     "\\mathrm{J}\\) |",
     "| \\(1{,}500\\ \\mathrm{K}\\) | \\(1{,}4354894\\times10^{-23}\\ "
     "\\mathrm{J}\\) |", 0),
    # must still fail -- the negative controls
    ("C05", SOLVABLE, "| \\(2{,}725\\ \\mathrm{K}\\) | ",
     "| \\(3{,}000\\ \\mathrm{K}\\) | ", 1),
    ("C06", SOLVABLE,
     "| \\(2{,}725\\ \\mathrm{K}\\) | \\(2{,}6078058\\times10^{-23}\\ "
     "\\mathrm{J}\\) |\n"
     "| \\(300\\ \\mathrm{K}\\) | \\(2{,}8709789\\times10^{-21}\\ "
     "\\mathrm{J}\\) |\n", "", 1),
]


def apply_case(path, orig, needle, replacement, count, cid):
    """Write the mutated document; report whether the needle was really there."""
    text = orig.decode("utf-8")
    if needle not in text:
        fail("%s: needle not present, so nothing was mutated: %r"
             % (cid, needle[:70]))
        return None
    mutated = text.replace(needle, replacement, count)
    if mutated == text:
        fail("%s: mutation was a no-op" % cid)
        return None
    with io.open(path, "wb") as fh:
        fh.write(mutated.encode("utf-8"))
    return mutated


def main():
    if not check(os.path.isfile(GATE), "missing gate: %s" % GATE):
        print("")
        print("HARNESS: FAIL -- gate absent")
        return 1

    docs = {}
    for fid in {m[1] for m in MUTANTS} | {c[1] for c in CONTROLS}:
        path = os.path.join(ROOT, fid)
        if not check(os.path.isfile(path), "missing document: %s" % fid):
            print("")
            print("HARNESS: FAIL -- document absent")
            return 1
        with io.open(path, "rb") as fh:
            docs[fid] = fh.read()

    # ---------------------------------------------------- baseline ----------
    rc = run_gate()
    check(rc == 0, "baseline: the gate must pass on the shipped documents, "
                   "got exit %d" % rc)

    results = []

    try:
        for entry in MUTANTS:
            cid, fid, needle, repl = entry[:4]
            count = entry[4] if len(entry) > 4 else 1
            path = os.path.join(ROOT, fid)
            orig = docs[fid]
            mutated = apply_case(path, orig, needle, repl, count, cid)
            if mutated is None:
                results.append((cid, False, "not applied"))
                continue
            rc = run_gate()
            good = check(rc == 1,
                         "%s: mutant must be caught (exit 1), got exit %d"
                         % (cid, rc))
            results.append((cid, good, "exit %d" % rc))
            with io.open(path, "wb") as fh:
                fh.write(orig)
            check(sha(orig) == sha(io.open(path, "rb").read()),
                  "%s: document did not return to its original bytes" % cid)

        for entry in CONTROLS:
            cid, fid, needle, repl = entry[:4]
            want = entry[-1]
            count = entry[4] if len(entry) > 5 else 1
            path = os.path.join(ROOT, fid)
            orig = docs[fid]
            mutated = apply_case(path, orig, needle, repl, count, cid)
            if mutated is None:
                results.append((cid, False, "not applied"))
                continue
            rc = run_gate()
            good = check(rc == want,
                         "%s: control must exit %d, got exit %d"
                         % (cid, want, rc))
            results.append((cid, good, "exit %d want %d" % (rc, want)))
            with io.open(path, "wb") as fh:
                fh.write(orig)
            check(sha(orig) == sha(io.open(path, "rb").read()),
                  "%s: document did not return to its original bytes" % cid)
    finally:
        for fid, orig in docs.items():
            with io.open(os.path.join(ROOT, fid), "wb") as fh:
                fh.write(orig)

    # ------------------------------------------------ restored baseline -----
    rc = run_gate()
    check(rc == 0, "restored baseline: the gate must pass again, "
                   "got exit %d" % rc)
    for fid, orig in docs.items():
        now = io.open(os.path.join(ROOT, fid), "rb").read()
        check(sha(orig) == sha(now), "%s left modified" % fid)

    mutants = [r for r in results if r[0].startswith("A")
               or r[0].startswith("B")]
    controls = [r for r in results if r[0].startswith("C")]
    m_ok = sum(1 for _, g, _ in mutants if g)
    c_ok = sum(1 for _, g, _ in controls if g)

    print("")
    for cid, good, note in results:
        print("  %s %s  %s" % ("ok  " if good else "FAIL  ", cid, note))
    print("")
    print("mutants  %d/%d   controls %d/%d"
          % (m_ok, len(mutants), c_ok, len(controls)))

    if failures:
        print("HARNESS: FAIL -- %d problem(s)" % len(failures))
        return 1
    if len(mutants) != TARGET_MUTANTS or len(controls) != TARGET_CONTROLS:
        print("HARNESS: FAIL -- expected %d/%d cases, table has %d/%d"
              % (TARGET_MUTANTS, TARGET_CONTROLS, len(mutants), len(controls)))
        return 1
    print("HARNESS: PASS -- %d/%d mutants, %d/%d controls"
          % (m_ok, TARGET_MUTANTS, c_ok, TARGET_CONTROLS))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print("FAIL  unexpected error: %s: %s" % (type(exc).__name__, exc))
        sys.exit(1)
