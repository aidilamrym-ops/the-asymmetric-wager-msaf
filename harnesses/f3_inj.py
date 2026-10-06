# -*- coding: utf-8 -*-
"""Fault-injection harness for provenance_check.py (F3-1).

Discipline (learned the hard way in F2-7):
  * snapshot bytes -> mutate -> run -> restore -> ASSERT bytes identical
  * every case is independent and the harness is idempotent
  * expectations are read back from the gate output, not assumed
  * a missing document must produce FAILURES, never a traceback
Exit 0 = all mutants caught and all controls passed.
"""
import io, json, os, subprocess, sys, hashlib

W = r"D:\THE ASYMMETRIC WAGER"
PY = r"C:\Python314\python.exe"
GATE = os.path.join(W, "provenance_check.py")
JSONP = os.path.join(W, "external_constants.json")
REFSP = os.path.join(W, "REFERENCES.md")
DOC = os.path.join(W, "01_PARADOX_AND_SCALE.md")

fails = []


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load(path):
    return json.loads(io.open(path, encoding="utf-8").read())


def dump(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def run_gate():
    p = subprocess.run([PY, GATE], capture_output=True)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    return p.returncode, out


def mutate_json(fn):
    obj = load(JSONP)
    fn(obj)
    return dump(obj)


# ------------------------------------------------------------------ cases --
def q(obj, qid):
    for x in obj["quantities"]:
        if x["id"] == qid:
            return x
    raise KeyError(qid)


def site(obj, qid, idx):
    return q(obj, qid)["sites"][idx]


CASES = [
    ("M1  planck value changed",          [ (JSONP, mutate_json(lambda o: q(o, "PLANCK_LENGTH").__setitem__("value", "1.616256e-35"))) ], "P4"),
    ("M2  site doc_value detached",       [ (JSONP, mutate_json(lambda o: site(o, "PLANCK_LENGTH", 0).__setitem__("doc_value", "1.616255e-34"))) ], "P4"),
    ("M3  needle count wrong",            [ (JSONP, mutate_json(lambda o: site(o, "PLANCK_LENGTH", 1).__setitem__("count", 1))) ], "P3"),
    ("M4  site points at missing file",   [ (JSONP, mutate_json(lambda o: site(o, "PLANCK_LENGTH", 0).__setitem__("file", "NO_SUCH_FILE.md"))) ], "P3"),
    ("M5  evidence sha256 corrupted",     [ (JSONP, mutate_json(lambda o: o["evidence"][0].__setitem__("sha256", "0"*64))) ], "P2"),
    ("M6  authority removed",             [ (JSONP, mutate_json(lambda o: q(o, "PLANCK_LENGTH").pop("authority"))) ], "P1"),
    ("M7  uncertainty removed",           [ (JSONP, mutate_json(lambda o: q(o, "PLANCK_LENGTH").pop("uncertainty"))) ], "P1"),
    ("M8  all sites of a quantity gone",  [ (JSONP, mutate_json(lambda o: q(o, "ZETA_DERIVATIVE_FIRST_ZERO").__setitem__("sites", []))) ], "P1"),
    ("M9  derived value wrong",           [ (JSONP, mutate_json(lambda o: q(o, "UNIVERSE_PIXEL_CONSTANT").__setitem__("value", "1.9e-62"))) ], "P5"),
    ("M10 derived_from stripped",         [ (JSONP, mutate_json(lambda o: (q(o, "UNIVERSE_PIXEL_CONSTANT").pop("derived_from"), q(o, "UNIVERSE_PIXEL_CONSTANT").pop("recompute")))) ], "P1"),
    # F5-1 replaced the original M11 ("declared rel_dev wrong"): that mutant
    # relied on this site being a live declared_variance, and F5-1 moved it to
    # source_agree.  The equivalent weakness -- a site declaring a magnitude the
    # authority does not support -- is now probed by reasserting the pre-F5-1
    # value 1.63e-35 against the corrected needle 1.62e-35.
    ("M11 site doc_value set to the old 1.63", [ (JSONP, mutate_json(lambda o: site(o, "PLANCK_LENGTH", 1).__setitem__("doc_value", "1.63e-35"))) ], "P4"),
    ("M12 reference_fact value changed",  [ (JSONP, mutate_json(lambda o: o["reference_facts"][0].__setitem__("value", "3000175332801"))) ], "P8"),
    ("M13 evidence probe needle changed", [ (JSONP, mutate_json(lambda o: q(o, "PLANCK_LENGTH")["evidence_probe"].__setitem__("line_needles", ["NoSuchProbeLine", "1.616 255 e-35", "0.000 018 e-35"]))) ], "P6"),
    ("M14 evidence_id nulled silently",   [ (JSONP, mutate_json(lambda o: (q(o, "PLANCK_LENGTH").__setitem__("evidence_id", None), q(o, "PLANCK_LENGTH").pop("evidence_status", None)))) ], "P6"),
    ("M15 evidence byte count wrong",     [ (JSONP, mutate_json(lambda o: o["evidence"][0].__setitem__("bytes", 40800))) ], "P2"),
    ("M16 evidence local_copy missing",   [ (JSONP, mutate_json(lambda o: o["evidence"][0].__setitem__("local_copy", "provenance/evidence/missing.txt"))) ], "P2"),
    ("M17 exact=true but uncertainty set",[ (JSONP, mutate_json(lambda o: q(o, "PLANCK_LENGTH").__setitem__("exact", True))) ], "P1"),
    ("M18 zeta authoritative value off",  [ (JSONP, mutate_json(lambda o: q(o, "ZETA_DERIVATIVE_FIRST_ZERO").__setitem__("value", "0.793160433356506116013897565300"))) ], "P5"),
    ("M19 zeta needle not in document",   [ (JSONP, mutate_json(lambda o: site(o, "ZETA_DERIVATIVE_FIRST_ZERO", 0).__setitem__("needle", "0,7931604335"))) ], "P3"),
    ("M20 retrieval date removed",        [ (JSONP, mutate_json(lambda o: q(o, "PLANCK_LENGTH").pop("retrieved_utc"))) ], "P6"),
    ("M21 local_copy key dropped",        [ (JSONP, mutate_json(lambda o: o["evidence"][0].pop("local_copy"))) ], "P1"),
    ("M22 unknown evidence cited",        [ (JSONP, mutate_json(lambda o: o["reference_facts"][0].__setitem__("source_id", "UNKNOWN_EVIDENCE"))) ], "P1"),
    ("M23 measured reflagged derived",    [ (JSONP, mutate_json(lambda o: (q(o, "PLANCK_LENGTH").__setitem__("kind", "derived"), q(o, "PLANCK_LENGTH").pop("recompute", None)))) ], "P1"),
    ("M24 evidence sha256 key dropped",   [ (JSONP, mutate_json(lambda o: o["evidence"][0].pop("sha256"))) ], "P1"),
    ("M25 REFERENCES heading removed",    [ (REFSP, None) ], "P7"),
    ("M26 reference value removed",       [ (REFSP, None) ], "P8"),
    ("M27 reference heading removed",     [ (REFSP, None) ], "P7"),
    # B1-a (F3-R8 / F5-R2): evidence_probe used to be opt-in, so a measured
    # quantity could drop it and never have `value` read back out of the
    # snapshot at all.  M29 removes the probe from the one quantity whose
    # evidence is archived; M30 removes the waiver from the one whose evidence
    # is not.  Both must trip P6 now instead of passing in silence.
    ("M29 archived probe removed",    [ (JSONP, mutate_json(lambda o: q(o, "PLANCK_LENGTH").pop("evidence_probe"))) ], "P6"),
    ("M30 unarchived waiver removed", [ (JSONP, mutate_json(lambda o: q(o, "OBSERVABLE_UNIVERSE_DIAMETER").pop("probe_waived"))) ], "P6"),
]

REF_MUTATIONS = {
    "M25": lambda t: t.replace("\n### PLANCK_2018_VI\n", "\n"),
    "M26": lambda t: t.replace("`3000175332800`", "`<removed>`"),
    "M27": lambda t: t.replace("\n### RF_RH_HEIGHT_VERIFIED\n", "\n"),
}

CONTROLS = [
    ("C0  pristine", lambda files: None),
    ("C1  harmless metadata edit", None),
    ("C2  legitimate new reference_fact", None),
]


def control_bytes(name, saved):
    """Return {path: new_bytes} for a control case, or None."""
    if name.startswith("C1"):
        obj = load(JSONP)
        obj["generated_utc"] = "2099-01-01T00:00:00Z"
        return {JSONP: dump(obj)}
    if name.startswith("C2"):
        obj = load(JSONP)
        obj["reference_facts"].append({
            "id": "RF_CONTROL_EXTENSION",
            "value": "424242424242",
            "source_id": "PLATT_2017",
            "claim": "Control case: a legitimately appended reference fact.",
        })
        txt = io.open(REFSP, encoding="utf-8").read()
        txt += ("\n### RF_CONTROL_EXTENSION\n\n`424242424242`\n\n"
                "Appended by the F3-1 control case C2.\n")
        return {JSONP: dump(obj),
                REFSP: txt.encode("utf-8")}
    return None


def main():
    saved = {JSONP: open(JSONP, "rb").read(),
             REFSP: open(REFSP, "rb").read(),
             DOC: open(DOC, "rb").read()}

    # ---- baseline ------------------------------------------------------
    rc, out = run_gate()
    if rc != 0:
        print("HARNESS ABORT: baseline gate rc=%d\n%s" % (rc, out))
        return 1
    print("baseline: gate rc=0 (PASS)")
    base_json_sha, base_refs_sha = sha(JSONP), sha(REFSP)

    caught = 0
    total = 0

    # ---- mutants -------------------------------------------------------
    for label, edits, expect in CASES:
        total += 1
        try:
            if edits[0][0] == REFSP and edits[0][1] is None:
                mut = REF_MUTATIONS.get(label[:3])
                if mut is None:
                    raise KeyError("no REF_MUTATIONS entry for %r" % label)
                newb = mut(saved[REFSP].decode("utf-8")).encode("utf-8")
                plan = [(REFSP, newb)]
            else:
                plan = [(p, b) for p, b in edits]
            for p, b in plan:
                open(p, "wb").write(b)
            rc, out = run_gate()
            ok_rc = (rc == 1)
            ok_tag = (expect in out)
            ok_tb = ("Traceback" not in out)
            if ok_rc and ok_tag and ok_tb:
                caught += 1
                print("ok    %s -> rc=1, tripped %s, no traceback" % (label, expect))
            else:
                fails.append("%s: rc=%s want 1 | tag %s in output=%s | traceback-free=%s"
                             % (label, rc, expect, ok_tag, ok_tb))
                print("FAIL  %s" % fails[-1])
                for ln in out.splitlines():
                    if ln.startswith("FAIL"):
                        print("        %s" % ln[:170])
        finally:
            for p in saved:
                open(p, "wb").write(saved[p])
            for p, b in saved.items():
                if sha(p) != hashlib.sha256(b).hexdigest():
                    fails.append("RESTORE FAILED: %s" % p)
    print("")
    print("mutants caught: %d/%d" % (caught, total))

    # ---- controls ------------------------------------------------------
    ctrl_ok = 0
    for name, _fn in CONTROLS:
        total += 1
        plan = control_bytes(name, saved)
        try:
            if plan:
                for p, b in plan.items():
                    open(p, "wb").write(b)
            rc, out = run_gate()
            if rc == 0 and "GATE: PASS" in out and "Traceback" not in out:
                ctrl_ok += 1
                print("ok    %s -> rc=0 (PASS)" % name)
            else:
                fails.append("%s: rc=%d (want 0)" % (name, rc))
                print("FAIL  %s rc=%d" % (name, rc))
                for ln in out.splitlines():
                    if ln.startswith("FAIL"):
                        print("        %s" % ln[:170])
        finally:
            for p in saved:
                open(p, "wb").write(saved[p])
    print("")
    print("controls passed: %d/%d" % (ctrl_ok, len(CONTROLS)))

    # ---- missing-document hardening ------------------------------------
    total += 1
    try:
        os.rename(DOC, DOC + ".f3hidden")
        rc, out = run_gate()
        tb = "Traceback" in out
        if rc == 1 and "FAIL" in out and not tb:
            print("ok    M28 missing document -> rc=1, FAILURES reported, no traceback")
        else:
            fails.append("M28 missing document: rc=%d traceback=%s" % (rc, tb))
            print("FAIL  %s" % fails[-1])
    finally:
        if os.path.exists(DOC + ".f3hidden"):
            os.rename(DOC + ".f3hidden", DOC)
        for p in saved:
            open(p, "wb").write(saved[p])

    # ---- final integrity ------------------------------------------------
    print("")
    same = (sha(JSONP) == base_json_sha and sha(REFSP) == base_refs_sha
            and sha(DOC) == hashlib.sha256(saved[DOC]).hexdigest())
    if not same:
        fails.append("final byte-identity check failed")
    print("byte-identical after restore: %s" % same)

    rc, out = run_gate()
    if rc != 0:
        fails.append("final gate run rc=%d (want 0)" % rc)
    print("final gate rc=%d" % rc)

    print("")
    if fails:
        print("HARNESS: FAIL -- %d problem(s)" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("HARNESS: PASS -- %d/%d mutants caught, %d/%d controls passed, "
          "missing-document hardened, all files byte-identical"
          % (caught, total - len(CONTROLS) - 1, ctrl_ok, len(CONTROLS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
