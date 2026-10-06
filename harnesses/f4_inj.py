# -*- coding: utf-8 -*-
"""F4 fault-injection harness: prove theorem_provenance_check.py can fail.

Each probe names the check tag it is aimed at (P1..P8); the harness asserts
both the exit code and that the failing check is the one that reported.
Controls (missing register, ghost scope entry) must NOT return 1.

Snapshot / restore is byte-identical; probes run strictly sequentially
(F3-L: never run two file-writing probes in parallel).

Exit 0 = every mutant caught, every control behaved, files restored.
"""
import io, json, os, subprocess, sys

ROOT = r"D:\THE ASYMMETRIC WAGER"
REGISTER = os.path.join(ROOT, "theorem_provenance.json")
CHECK = os.path.join(ROOT, "theorem_provenance_check.py")
DOC_P3 = os.path.join(ROOT, "02_OMEGA_CORE_ANALYSIS.md")   # in scope, no entry
DOC_P5 = os.path.join(ROOT, "ANTI_INFINITY_BLINDSPOT.md")
PY = r"C:\Python314\python.exe"
FILES = [REGISTER, DOC_P3, DOC_P5]

failures = []
results = []


def sha(path):
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run_gate():
    p = subprocess.run([PY, CHECK], cwd=ROOT, capture_output=True)
    out = (p.stdout or b"") + (p.stderr or b"")
    return p.returncode, out.decode("utf-8", "replace")


def load():
    return io.open(REGISTER, encoding="utf-8", newline="").read()


def save(text):
    with io.open(REGISTER, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def mutate_register(fn):
    reg = json.loads(load())
    fn(reg)
    save(json.dumps(reg, ensure_ascii=False, indent=2) + "\n")


def probe(tag, name, expect_code, apply_fn, restore_fn):
    """Apply, run, assert the exit code AND the reporting tag, restore."""
    before = {f: sha(f) for f in FILES}
    label = "%s: %s" % (tag, name)
    applied = False
    try:
        apply_fn()
        applied = True
        code, out = run_gate()
        if code != expect_code:
            failures.append("%s: expected exit %d, got %d\n%s"
                            % (label, expect_code, code, out[-1500:]))
            results.append("FAIL  %-58s expected %d got %d" % (label, expect_code, code))
        elif expect_code == 1 and tag not in out:
            failures.append("%s: exited 1 but %r never reported it\n%s"
                            % (label, tag, out[-1500:]))
            results.append("FAIL  %-58s right code, wrong check" % label)
        elif expect_code == 1:
            results.append("ok    %-58s exit=1, reported by %s" % (name, tag))
        else:
            results.append("ok    %-58s exit=%d (control)" % (name, code))
    finally:
        try:
            restore_fn()
        except Exception as exc:
            failures.append("%s: restore raised %r" % (label, exc))
        if applied:
            after = {f: sha(f) for f in FILES}
            for f in FILES:
                if before[f] != after[f]:
                    failures.append("%s: %s NOT restored (byte drift)"
                                    % (label, os.path.basename(f)))


def main():
    print("=" * 96)
    print("F4 FAULT INJECTION -- theorem_provenance_check.py")
    print("=" * 96)

    original = {f: open(f, "rb").read() for f in FILES}
    orig_reg = load()
    doc_p3_orig = io.open(DOC_P3, encoding="utf-8", newline="").read()
    doc_p5_orig = io.open(DOC_P5, encoding="utf-8", newline="").read()

    def restore_reg():
        save(orig_reg)

    def restore_p3():
        with io.open(DOC_P3, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc_p3_orig)

    def restore_p5():
        with io.open(DOC_P5, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc_p5_orig)

    # ---------------------------------------------------------- controls
    print("\n--- controls (must NOT be exit 1) ---")

    def c_absent():
        os.rename(REGISTER, REGISTER + ".bak")

    def c_absent_restore():
        if os.path.exists(REGISTER + ".bak"):
            os.rename(REGISTER + ".bak", REGISTER)

    probe("TOOL NOT RUN", "register absent", 2, c_absent, c_absent_restore)

    probe("TOOL NOT RUN", "scope names a ghost document", 2,
          lambda: mutate_register(lambda r: r["scope"].append("NO_SUCH_DOCUMENT.md")),
          restore_reg)

    probe("P1  REGISTER_SCHEMA", "malformed register -> FAIL not traceback", 1,
          lambda: save("{ this is not json ]["), restore_reg)

    probe("P1  REGISTER_SCHEMA", "register is a list -> FAIL", 1,
          lambda: save("[1, 2, 3]\n"), restore_reg)

    # ------------------------------------------------------------- P1
    print("\n--- P1 REGISTER_SCHEMA ---")

    probe("P1  REGISTER_SCHEMA", "entry missing 'status'", 1,
          lambda: mutate_register(lambda r: r["entries"][3].pop("status")), restore_reg)

    probe("P1  REGISTER_SCHEMA", "status outside the enum", 1,
          lambda: mutate_register(
              lambda r: r["entries"][3].__setitem__("status", "proven")), restore_reg)

    probe("P1  REGISTER_SCHEMA", "id not of the form Tnnn", 1,
          lambda: mutate_register(
              lambda r: r["entries"][5].__setitem__("id", "theorem-5")), restore_reg)

    probe("P1  REGISTER_SCHEMA", "duplicate id", 1,
          lambda: mutate_register(
              lambda r: r["entries"][5].__setitem__("id", r["entries"][0]["id"])),
          restore_reg)

    probe("P1  REGISTER_SCHEMA", "unparseable covers regex", 1,
          lambda: mutate_register(
              lambda r: r["entries"][0]["covers"].__setitem__(0, "(unclosed[")),
          restore_reg)

    probe("P1  REGISTER_SCHEMA", "scope is a string", 1,
          lambda: mutate_register(lambda r: r.__setitem__("scope", "not-a-list")),
          restore_reg)

    probe("P1  REGISTER_SCHEMA", "finding severity outside the enum", 1,
          lambda: mutate_register(
              lambda r: r["entries"][3]["finding"].__setitem__("severity", "grave")),
          restore_reg)

    # ------------------------------------------------------------- P2
    print("\n--- P2 ANCHOR_RESOLVES ---")

    probe("P2  ANCHOR_RESOLVES", "anchor matches 0 times", 1,
          lambda: mutate_register(lambda r: r["entries"][0].__setitem__(
              "anchor", "this phrase exists nowhere in the document")), restore_reg)

    probe("P2  ANCHOR_RESOLVES", "anchor matches many times", 1,
          lambda: mutate_register(
              lambda r: r["entries"][0].__setitem__("anchor", "the")), restore_reg)

    probe("P2  ANCHOR_RESOLVES", "entry points at the wrong file", 1,
          lambda: mutate_register(lambda r: r["entries"][0].__setitem__(
              "document", "02_OMEGA_CORE_ANALYSIS.md")), restore_reg)

    # ------------------------------------------------------------- P3
    print("\n--- P3 COVERAGE ---")

    def p3_append(text):
        with io.open(DOC_P3, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n" + text + "\n")

    probe("P3  COVERAGE", "unregistered Brouwer claim injected", 1,
          lambda: p3_append("Held up for the examiner: Brouwer himself would refuse this."),
          restore_p3)

    probe("P3  COVERAGE", "unregistered Navier-Stokes claim", 1,
          lambda: p3_append("Also: the Navier-Stokes equations are settled here."),
          restore_p3)

    probe("P3  COVERAGE", "unregistered Hawking-Penrose claim", 1,
          lambda: p3_append("Read straight off Hawking and Penroses singularity theorem."),
          restore_p3)

    # ------------------------------------------------------------- P4
    print("\n--- P4 EVIDENCE ---")

    probe("P4  EVIDENCE", "quote below the placeholder floor", 1,
          lambda: mutate_register(
              lambda r: r["entries"][0]["evidence"].__setitem__("quote", "yes")),
          restore_reg)

    probe("P4  EVIDENCE", "identifier carries no arXiv/DOI/URL marker", 1,
          lambda: mutate_register(
              lambda r: r["entries"][1]["evidence"].__setitem__("identifier", "a book")),
          restore_reg)

    probe("P4  EVIDENCE", "retrieval date not YYYY-MM-DD", 1,
          lambda: mutate_register(lambda r: r["entries"][2]["evidence"]
                                  .__setitem__("retrieved", "05 October 2026")),
          restore_reg)

    probe("P4  EVIDENCE", "placeholder source", 1,
          lambda: mutate_register(
              lambda r: r["entries"][4]["evidence"].__setitem__("source", "TODO")),
          restore_reg)

    probe("P4  EVIDENCE", "evidence object emptied", 1,
          lambda: mutate_register(lambda r: r["entries"][6].__setitem__("evidence", {})),
          restore_reg)

    # ------------------------------------------------------------- P5
    print("\n--- P5 DEFECT_CLOSED ---")

    def p5_marker_gone():
        with io.open(DOC_P5, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc_p5_orig.replace("[F4-A]", "[X4-A]"))
    probe("P5  DEFECT_CLOSED", "correction marker removed from the document", 1,
          p5_marker_gone, restore_p5)

    def p5_no_correction():
        def drop(r):
            for e in r["entries"]:
                if e["id"] == "T004":
                    e.pop("correction", None)
        mutate_register(drop)
    probe("P5  DEFECT_CLOSED", "defect recorded with no correction", 1,
          p5_no_correction, restore_reg)

    def p5_downgrade():
        def down(r):
            for e in r["entries"]:
                if e["id"] == "T017":
                    e["finding"]["severity"] = "note"
                    e.pop("correction", None)
        mutate_register(down)
    probe("P5  DEFECT_CLOSED", "severity downgraded to dodge the fix", 1,
          p5_downgrade, restore_reg)

    def p5_downgrade_only():
        def down(r):
            for e in r["entries"]:
                if e["id"] == "T017":
                    e["finding"]["severity"] = "none"
                    e.pop("correction", None)
        mutate_register(down)
    probe("P8  MARKER_LEDGER", "severity set to none and correction dropped", 1,
          p5_downgrade_only, restore_reg)

    # ------------------------------------------------------------- P6
    print("\n--- P6 MACHINE_GATE_LINK ---")

    def p6_ghost():
        def setg(r):
            for e in r["entries"]:
                if e["id"] == "T005":
                    e["machine_gated_by"] = "no_such_gate.py"
        mutate_register(setg)
    probe("P6  MACHINE_GATE_LINK", "cross-link points at a missing gate", 1,
          p6_ghost, restore_reg)

    # ------------------------------------------------------------- P7
    print("\n--- P7 FINDING_SHAPE ---")

    def p7_dup():
        def dup(r):
            for e in r["entries"]:
                if e["id"] == "T009":
                    e["finding"]["id"] = "F4-A"
        mutate_register(dup)
    probe("P7  FINDING_SHAPE", "duplicate finding id", 1, p7_dup, restore_reg)

    def p7_mismatch():
        def mis(r):
            for e in r["entries"]:
                if e["id"] == "T001":
                    e["finding"] = {"id": "F4-Z", "severity": "none"}
                    e["correction"] = "not needed but written anyway"
        mutate_register(mis)
    probe("P7  FINDING_SHAPE", "correction on severity=none", 1, p7_mismatch, restore_reg)

    # ------------------------------------------------------------- P8
    print("\n--- P8 MARKER_LEDGER ---")

    def p8_marker_stripped():
        with io.open(DOC_P5, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc_p5_orig.replace("[F4-A]", ""))
    probe("P8  MARKER_LEDGER", "marker stripped from the document, register keeps it", 1,
          p8_marker_stripped, restore_p5)

    def p8_drop_entry():
        def drop(r):
            r["entries"][:] = [e for e in r["entries"] if e["id"] != "T004"]
        mutate_register(drop)
    probe("P8  MARKER_LEDGER", "register entry dropped, document keeps its marker", 1,
          p8_drop_entry, restore_reg)

    # ------------------------------------------------------------- final
    print("\n--- restoration + final gate ---")
    for f in FILES:
        if open(f, "rb").read() != original[f]:
            failures.append("FINAL: %s differs from the snapshot" % os.path.basename(f))
    code, out = run_gate()
    if code != 0:
        failures.append("FINAL: gate should exit 0 after restore, got %d\n%s" % (code, out))
    else:
        print("ok    final gate exit=0 after every restore")

    print()
    for r in results:
        print("  " + r)
    print()
    if failures:
        print("FAILURES (%d):" % len(failures))
        for f in failures:
            print("  - " + f)
        print("HARNESS: FAIL")
        return 1
    print("HARNESS: PASS -- %d mutants caught by their own check, 4 controls "
          "behaved, all files byte-identical after restore" % len(results))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback
        traceback.print_exc()
        print("HARNESS CRASH")
        sys.exit(2)
