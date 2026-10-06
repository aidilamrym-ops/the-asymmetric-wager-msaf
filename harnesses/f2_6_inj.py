# FILE: harnesses/f2_6_inj.py
# PURPOSE: re-produce the F2-6 fault-injection counts for visual_check.py.
#
# F2_REPORT 6.4 published 11/11 mutants and 3/3 controls but kept no harness
# (F2_REPORT 8.3).  This is that harness.
#
# Every mutant is applied to msaf_visual.py, the gate is run (which re-renders
# the figure from scratch in a fresh interpreter), the published exit code is
# required, and the original bytes are restored before the next case.
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
GATE = os.path.join(ROOT, "visual_check.py")
PY = sys.executable

VISUAL = "msaf_visual.py"

TARGET_MUTANTS = 11
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
    env = dict(os.environ)
    env["MPLBACKEND"] = "Agg"
    env["PYTHONIOENCODING"] = "utf-8"
    p = subprocess.run([PY, GATE], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env,
                       timeout=300)
    return p.returncode


# --------------------------------------------------------------------------
# MUTANTS   (id, needle, replacement[, count])
# CONTROLS  (id, needle, replacement[, count], expected exit)
# The needle must be present before the mutation is applied.
# --------------------------------------------------------------------------
MUTANTS = [
    # V4 -- the panel has to carry its own numbers
    ("V4a", "             + rf'float64 observed span = {log10_span_f64:.1e}'\n",
     "", 1),
    ("V4b", "             + rf'1 decade would need {decade_bits:.3e} bits'\n",
     "", 1),
    ("V4c", "plt.annotate('                 not features of this curve',\n"
     "             xy=(0.02, 0.02), xycoords='axes fraction', fontsize=8, "
     "color='#555555', va='bottom')\n", "", 1),

    # V5 -- the markers are certificate operating points, not curve events
    ("V5a", "label='certificate: 9000 bits (pivot 723 undetermined)'",
     "label='Pivot 723 Halt (v2)'", 1),
    ("V5b", "plt.axvline(x=18000, color='green', linestyle='--', "
     "label='certificate: 18000 bits (verified)')\n", "", 1),

    # V3 / V2 -- the title declares flatness, the x-axis names p
    ("V3", "-- numerically flat'", "-- exhibits decay'", 1),
    ("V2", "plt.xlabel('Computational Bit Precision ($p$)', fontsize=10)",
     "plt.xlabel('Iterations', fontsize=10)", 1),

    # V6 -- the drawn curve really is flat
    ("V6", "r_tail_log10 = [calculate_r_tail_log10(N=400, c=100, "
     "prec_bits=p) for p in precisions]",
     "r_tail_log10 = [calculate_r_tail_log10(N=400, c=100, prec_bits=p) + i "
     "for i, p in enumerate(precisions)]", 1),

    # V8 / V7 -- the two analytic figures
    ("V8", "decade_bits = 1.0 / (Delta_univ * np.log10(2.0))",
     "decade_bits = 1.5 / (Delta_univ * np.log10(2.0))", 1),
    ("V7", "log10_span = -(p_hi - p_lo) * Delta_univ * np.log10(2.0)",
     "log10_span = -(p_hi - p_lo) * Delta_univ * np.log10(3.0)", 1),

    # V9 -- the legend carries the curve and both markers
    ("V9", ", label=r'$\\log_{10}\\mathcal{R}_{\\text{tail}}$'", "", 1),
]

CONTROLS = [
    ("K1", "plt.figure(figsize=(12, 5))", "plt.figure(figsize=(14, 6))", 1, 0),
    ("K2", "plt.axvline(x=9000, color='blue'",
     "plt.axvline(x=9000, color='cyan'", 1, 0),
    ("K3", "# F1-N: the factor 2**(-p * Delta_univ) is numerically inert over "
     "this range.",
     "# F1-N: the factor 2**(-p * Delta_univ) is numerically inert.\n"
     "# It stays inert across the whole sweep below.", 1, 0),
]


def apply_case(path, orig, needle, replacement, count, cid):
    text = orig.decode("utf-8")
    if needle not in text:
        fail("%s: needle not present, so nothing was mutated: %r"
             % (cid, needle[:70]))
        return False
    mutated = text.replace(needle, replacement, count)
    if mutated == text:
        fail("%s: mutation was a no-op" % cid)
        return False
    with io.open(path, "wb") as fh:
        fh.write(mutated.encode("utf-8"))
    return True


def main():
    if not check(os.path.isfile(GATE), "missing gate: %s" % GATE):
        print("")
        print("HARNESS: FAIL -- gate absent")
        return 1
    path = os.path.join(ROOT, VISUAL)
    if not check(os.path.isfile(path), "missing document: %s" % VISUAL):
        print("")
        print("HARNESS: FAIL -- document absent")
        return 1
    with io.open(path, "rb") as fh:
        orig = fh.read()

    rc = run_gate()
    check(rc == 0, "baseline: the gate must pass on the shipped document, "
                   "got exit %d" % rc)

    results = []
    try:
        for entry in MUTANTS + CONTROLS:
            cid, needle, repl = entry[:3]
            want = entry[-1] if cid.startswith("K") else 1
            count = entry[3] if len(entry) > 3 else 1
            if not apply_case(path, orig, needle, repl, count, cid):
                results.append((cid, False, "not applied"))
                continue
            rc = run_gate()
            good = check(rc == want,
                         "%s: gate must exit %d, got exit %d"
                         % (cid, want, rc))
            results.append((cid, good, "exit %d want %d" % (rc, want)))
            with io.open(path, "wb") as fh:
                fh.write(orig)
            check(sha(orig) == sha(io.open(path, "rb").read()),
                  "%s: document did not return to its original bytes" % cid)
    finally:
        with io.open(path, "wb") as fh:
            fh.write(orig)

    rc = run_gate()
    check(rc == 0, "restored baseline: the gate must pass again, "
                   "got exit %d" % rc)
    check(sha(orig) == sha(io.open(path, "rb").read()),
          "%s left modified" % VISUAL)

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
