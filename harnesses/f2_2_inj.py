# FILE: harnesses/f2_2_inj.py
# PURPOSE: re-produce the F2-2 fault-injection counts for znone_check.py.
#
# F2_REPORT 2.4 published 15/15 mutants and 3/3 controls but kept no harness
# (F2_REPORT 8.3: "recorded, not reproducible").  This is that harness.
#
# One document is mutated at a time, the gate is run, the published exit code
# is required, and the original bytes are restored before the next case.  The
# gate reads five documents; a mutation therefore has to name which one it
# touches, or a "mutant" could silently land on the wrong file.
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
GATE = os.path.join(ROOT, "znone_check.py")
PY = sys.executable

GLOSSARY = "DEFINISI_OPERASIONAL_MSAF.md"
SKILL = "Skill.md"
MANIFESTO = "CONSOLIDATED_MASTER_MANIFESTO.md"
DRAF = "DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md"
VISUAL = "msaf_visual.py"

TARGET_MUTANTS = 15
TARGET_CONTROLS = 3

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


ROW5 = ("0.50000... (+5 \\(\\Delta _{\\text{univ}}\\))\t5 "
        "\\(\\Delta _{\\text{univ}}\\)\t7,283804 \u00d7 "
        "10\u207b\u2076\u00b2\tOUTSIDE $\\mathcal{Z}_{\\text{none}}$ "
        "-- root destroyed")
ROW2 = ("0.50000... (+2 \\(\\Delta _{\\text{univ}}\\))\t2 "
        "\\(\\Delta _{\\text{univ}}\\)\t2,913522 \u00d7 "
        "10\u207b\u2076\u00b2\tOUTSIDE $\\mathcal{Z}_{\\text{none}}$ "
        "-- root destroyed")

# --------------------------------------------------------------------------
# MUTANTS   (id, target file, needle, replacement[, count])
# CONTROLS  (id, target file, needle, replacement[, count], expected exit)
# The needle must be present before the mutation is applied: a mutation that
# silently does nothing is a control dressed up as a mutant.
# --------------------------------------------------------------------------
MUTANTS = [
    # Z1 -- the canonical set must be strict, and must say it is the record
    ("Z1a", GLOSSARY, "0 < |x - x_0|", "0 \\le |x - x_0|", 1),
    ("Z1b", GLOSSARY, "| < \\Delta_{\\text{univ}}",
     "| \\le \\Delta_{\\text{univ}}", 1),
    ("Z1c", GLOSSARY, "**This is the canonical definition of record "
     "(F2-2).**", "**Definition.**", 1),

    # Z2 / Z3 -- every document that names the set must reproduce it
    ("Z2", SKILL, "0 < \\lvert x-x_0\\rvert < \\Delta_{\\text{univ}}",
     "|x - x_0| \\le 10^{-62}", 1),
    ("Z3", MANIFESTO, "0 < \\lvert x-x_0\\rvert < \\Delta_{\\text{univ}}",
     "|x - x_0| \\le 10^{-62}", 1),

    # Z4 -- the ambiguous label must stay gone
    ("Z4a", DRAF, "**Reading the table (F1-L, corrected 2026-10-04).**",
     "**NON-EXISTENCE ZONE. Reading the table (F1-L, corrected "
     "2026-10-04).**", 1),
    ("Z4b", VISUAL, "Zone of Non-Existence", "NON-EXISTENCE ZONE", 1),
    ("Z4c", SKILL, "- No evaluating functions/limits/eigenvalues inside",
     "- No evaluating functions/limits/eigenvalues inside the "
     "NON-EXISTENCE ZONE", 1),

    # Z5 -- the five sweep rows sit OUTSIDE, n = 1..5, and none claims entry
    ("Z5a", DRAF, ROW5 + "\n", "", 1),
    ("Z5b", DRAF, ROW2,
     ROW2.replace("OUTSIDE $\\mathcal{Z}_{\\text{none}}$",
                  "IN $\\mathcal{Z}_{\\text{none}}$"), 1),

    # Z6 -- the reading note that separates sweep from zone
    ("Z6", DRAF,
     "**Reading the table (F1-L, corrected 2026-10-04).** No row of the "
     "table above lies *inside* $\\mathcal{Z}_{\\text{none}}$. The zone is "
     "the open pixel $0 < \\lvert x-x_0\\rvert < \\Delta_{\\text{univ}}$ -- "
     "the definition of record is `DEFINISI_OPERASIONAL_MSAF.md` section 1 "
     "-- and it is **non-operational**: nothing is evaluated there at all, "
     "so it has no rows. The table sweeps the five integer *pixel shifts* "
     "$x = x_0 + n\\,\\Delta_{\\text{univ}}$, $n = 1\\ldots5$, every one of "
     "which sits at distance $\\ge \\Delta_{\\text{univ}}$ and is therefore "
     "**outside** the zone. Those rows demonstrate the linear law "
     "$\\lvert\\Delta\\zeta\\rvert \\propto \\Delta_{\\text{univ}}$ in the "
     "region where evaluation is allowed; they are not members of the zone "
     "and must not be read as its definition. The space between $0,5$ and "
     "$0,5 + \\Delta_{\\text{univ}}$ is ruled a **Non-Existence Zoning** "
     "because it falls below the Planck threshold of spatial "
     "information." + "\n", "", 1),

    # Z7 -- the plot must be titled as a sweep outside the zone
    ("Z7a", VISUAL, "plt.title('Pixel-shift sweep OUTSIDE",
     "plt.title('Zone of Non-Existence", 1),
    ("Z7b", VISUAL, "Pixel-shift sweep OUTSIDE ",
     "Pixel-shift sweep ", 1),

    # Z8 -- the zone stays non-operational
    ("Z8a", SKILL,
     "- No evaluating functions/limits/eigenvalues inside "
     "$\\mathcal{Z}_{\\text{none}}$.", "- (rule removed).", 1),
    ("Z8b", GLOSSARY, "strictly forbidden from evaluating functions",
     "may not compute", 1),
]

CONTROLS = [
    # must still pass -- the gate must not be reading this
    ("K1", SKILL, "\\lvert x-x_0\\rvert", "|x-x_0|", 1, 0),
    ("K2", VISUAL, "which is the same ambiguity",
     "which had been the same ambiguity", 1, 0),
    ("K3", MANIFESTO,
     "*Archived permanently for the civilization of open science across the "
     "coordinates DOI: 10.5281/zenodo.22791556.*",
     "*Archived permanently for the civilization of open science across the "
     "coordinates DOI: 10.5281/zenodo.22791556.*"
     "\n\nA trailing sentence added by the control.", 1, 0),
]


def apply_case(path, orig, needle, replacement, count, cid):
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
    for entry in MUTANTS + CONTROLS:
        fid = entry[1]
        path = os.path.join(ROOT, fid)
        if fid in docs:
            continue
        if not check(os.path.isfile(path), "missing document: %s" % fid):
            print("")
            print("HARNESS: FAIL -- document absent")
            return 1
        with io.open(path, "rb") as fh:
            docs[fid] = fh.read()

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
            if apply_case(path, orig, needle, repl, count, cid) is None:
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
            if apply_case(path, orig, needle, repl, count, cid) is None:
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

    rc = run_gate()
    check(rc == 0, "restored baseline: the gate must pass again, "
                   "got exit %d" % rc)
    for fid, orig in docs.items():
        now = io.open(os.path.join(ROOT, fid), "rb").read()
        check(sha(orig) == sha(now), "%s left modified" % fid)

    mutants = [r for r in results if not r[0].startswith("K")]
    controls = [r for r in results if r[0].startswith("K")]
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
