# FILE: harnesses/a9_drift_inj.py
# PURPOSE: prove the A9 additions can fail.
#
# A9 closed two residuals and neither is allowed to close on a green run alone.
# F7-R3 said re-fetching was manual; F6-R5 said a rig quantity written in a
# form the pattern set did not match would pass unread. Both claims are now
# answered by new machinery, and new machinery that has only ever printed PASS
# is a tool that has been run, not a tool that has been tested.
#
# Group 1 -- liveness (F7-R3).  provenance/url_liveness.json is written by
# url_liveness_check.py and read by provenance_check.py P11.  Four defects must
# be rejected by P11, and the probe itself must fail on the two contradictions
# it exists to find and succeed on a fixture that agrees with the register:
#
#   L1 the record is missing          -> P11 names the file and the command
#   L2 one URL the register knows is
#      absent from the record         -> P11 names the missing URL
#   L3 the record invents its own pin -> P11 says the record may not invent one
#   L4 a contradiction the probe
#      already found is left in place -> P11 says fix the register or the source
#   L5 the fixture reports a status
#      the register does not record   -> probe exits 1
#   L6 every URL is unreachable       -> probe exits 2, never 0
#   L7 the fixture agrees with the
#      register                       -> probe exits 0 (control)
#
# Group 2 -- prose patterns (F6-R5).  Each defect is one more than whatever is
# true today, so the harness cannot rot when a gate or a harness is added:
#
#   P1..P4  the keyed header, field by field
#   P5, P6  N-gate and N-harness compounds
#   P7, P8  x of y pairs
#   P9      an ordinal past "twentieth", written at the start of a sentence
#   P10     "entries" spelled out
#   P11     a stale cardinal before "gates"
#   P12     a spelled manifest count with no determiner
#   P13     a corrupted word list -> the gate exits 2 rather than comparing
#           against numbers that are not the live values
#   C1      a correct keyed header -> the gate must stay green (control)
#
# Every mutation is applied, observed and reverted before the next begins, and
# the baseline must be green before the first case and again after the last,
# with every target byte-identical.
#
# EXIT:   0 = every case behaved, baseline green, bytes restored
#         1 = a case was not caught, or a baseline stopped passing
#         2 = a tool this harness needs is missing (never reported as success)

import io
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GATE = os.path.join(ROOT, "report_claim_check.py")
PROV = os.path.join(ROOT, "provenance_check.py")
LIVE = os.path.join(ROOT, "url_liveness_check.py")
RECORD = os.path.join(ROOT, "provenance", "url_liveness.json")
REPORT = "F4_REPORT.md"
PY = sys.executable
# --out must never land in the workspace root: checksum_check.py would
# swallow it on --update and P8 would then require Brain.MD to name it.
OUT_SMOKE = os.path.join(tempfile.gettempdir(), "a9_smoke.json")
OUT_CASE = os.path.join(tempfile.gettempdir(), "a9_case_out.json")

sys.path.insert(0, ROOT)
import harness_check                      # noqa: E402
import report_claim_check as rcc          # noqa: E402
import suite_check                        # noqa: E402
import url_liveness_check as ulc          # noqa: E402

GATES = len(suite_check.GATES)
HARNS = len(harness_check.HARNESSES)

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL  %s" % msg)


def read(name):
    with io.open(os.path.join(ROOT, name), "rb") as fh:
        return fh.read()


def write_raw(name, data):
    if b"\r" in data:
        raise SystemExit("BLOCKED %s: CR introduced" % name)
    with io.open(os.path.join(ROOT, name), "wb") as fh:
        fh.write(data)


def run_cmd(argv, timeout=300):
    p = subprocess.run(argv, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout,
                       cwd=ROOT)
    out = p.stdout or ""
    fails = [l for l in out.splitlines() if l.startswith("FAIL")]
    return p.returncode, fails, out


def judge(runner, fixture=None, out_path=None):
    """Run the tool a case is judged by.  Returns (rc, fails, verdict)."""
    if runner == "gate":
        rc, fails, out = run_cmd([PY, GATE])
        marks = [l for l in out.splitlines() if l.startswith("report_claim_check:")]
    elif runner == "prov":
        rc, fails, out = run_cmd([PY, PROV])
        marks = [l for l in out.splitlines() if l.startswith("GATE:")]
    elif runner == "live":
        rc, fails, out = run_cmd([PY, LIVE, "--fixture", fixture,
                                  "--out", out_path])
        marks = [l for l in out.splitlines()
                 if l.startswith("url_liveness_check:")]
    else:
        raise SystemExit("BLOCKED: unknown runner %r" % runner)
    return rc, fails, (marks[-1] if marks else "<no verdict>")


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


def append_line(name, line):
    data = read(name)
    text = data.decode("utf-8")
    if not text.endswith("\n"):
        raise SystemExit("BLOCKED %s: no trailing newline" % name)
    if line in text:
        raise SystemExit("BLOCKED %s: injected line already present" % name)
    write_raw(name, (text + "\n" + line + "\n").encode("utf-8"))


# ------------------------------------------------------------ fixtures ------
def base_fixture():
    """A fixture that says exactly what the register says."""
    exp = ulc.expectations()
    doc = {}
    for url, _srcs in ulc.collect_urls():
        e = exp.get(url) or {}
        status = e.get("expected_status")
        entry = {"status": 200 if status is None else status}
        if e.get("archived_sha256"):
            entry["body_sha256"] = e["archived_sha256"]
        doc[url] = entry
    return doc


def write_fixture(doc, tag):
    path = os.path.join(tempfile.gettempdir(), "a9_fixture_%s.json" % tag)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False)
                 + "\n")
    return path


def changed_status_fixture():
    """A fixture that contradicts the register on one URL."""
    doc = base_fixture()
    exp = ulc.expectations()
    target = None
    for url in sorted(doc):
        if (exp.get(url) or {}).get("expected_status") is not None:
            target = url
            break
    if target is None:
        raise SystemExit("BLOCKED: no URL carries an observed_status to contradict")
    doc[target]["status"] = 404 if doc[target]["status"] != 404 else 500
    return doc, target


def rewrite_record(transform):
    """Apply transform(doc) -> doc to the liveness record on disk."""
    with io.open(RECORD, encoding="utf-8") as fh:
        doc = json.load(fh)
    new = transform(json.loads(json.dumps(doc)))
    text = json.dumps(new, indent=2, ensure_ascii=False) + "\n"
    write_raw(RECORD, text.encode("utf-8"))


def drop_one_url(doc):
    if not doc.get("records"):
        raise SystemExit("BLOCKED: liveness record has no records")
    doc["records"] = doc["records"][:-1]
    return doc


def invent_pin(doc):
    for rec in doc.get("records") or []:
        if rec.get("archived_sha256"):
            rec["archived_sha256"] = "0" * 64
            return doc
    raise SystemExit("BLOCKED: no record carries an archived_sha256 to corrupt")


def leave_contradiction(doc):
    for rec in doc.get("records") or []:
        if rec.get("expected_status") is not None:
            rec["verdict"] = "CHANGED"
            rec["status"] = 404
            return doc
    raise SystemExit("BLOCKED: no record carries an expected_status")


# ---------------------------------------------------------------- cases -----
def cases():
    """Return the case list.

    Each entry is (label, needle, want_rc_or_None, apply, target_or_None,
    runner, fixture_path_or_None).  `apply` only mutates; the runner is then
    executed and the mutation reverted.
    """
    L, err = rcc.live_values()
    if L is None:
        raise SystemExit("BLOCKED: live values unavailable: %s" % err)
    gates, harns, rows, brain = L["gates"], L["harnesses"], L["rows"], L["brain"]
    header_good = ("`suite=%d harnesses=%d manifest=%d brain=%s`"
                   % (gates, harns, rows, brain))
    fix_changed = changed_status_fixture()[0]
    fix_base = base_fixture()
    fix_dead = dict((u, {"error": "fixture: unreachable"})
                    for u, _s in ulc.collect_urls())
    path_changed = write_fixture(fix_changed, "changed")
    path_base = write_fixture(fix_base, "base")
    path_dead = write_fixture(fix_dead, "dead")

    def wrong_header(g, h, m, b):
        # No date, phase tag or "then": P5 treats a dated claim as history and
        # lets it pass.  An injection that carries the gate's own escape hatch
        # is not a defect the gate is required to catch.
        return "A header `suite=%d harnesses=%d manifest=%d brain=%s`." % (g, h, m, b)

    return [
        # ---- group 1: liveness ----
        ("L1 record deleted",
         "P11  LIVENESS_RECORD: provenance/url_liveness.json is missing",
         1, lambda: os.remove(RECORD), RECORD, "prov", None),
        ("L2 URL dropped from record",
         "absent from the record",
         1, lambda: rewrite_record(drop_one_url), RECORD, "prov", None),
        ("L3 record invents its own pin",
         "may not invent its own pin",
         1, lambda: rewrite_record(invent_pin), RECORD, "prov", None),
        ("L4 contradiction left in record",
         "contradicting the register",
         1, lambda: rewrite_record(leave_contradiction), RECORD, "prov", None),
        ("L5 fixture contradicts the register",
         "contradict the register",
         1, lambda: None, None, "live", path_changed),
        ("L6 fixture reaches nothing",
         "TOOL NOT RUN",
         2, lambda: None, None, "live", path_dead),
        ("L7 fixture agrees (control)",
         "every URL still answers with the status",
         0, lambda: None, None, "live", path_base),
        # ---- group 2: prose patterns ----
        ("P1 keyed harnesses wrong",
         "harness count=",
         None, lambda: append_line(REPORT, wrong_header(gates, harns + 1, rows, brain)),
         REPORT, "gate", None),
        ("P2 keyed suite wrong",
         "gate count=",
         None, lambda: append_line(REPORT, wrong_header(gates + 1, harns, rows, brain)),
         REPORT, "gate", None),
        ("P3 keyed manifest wrong",
         "manifest rows=",
         None, lambda: append_line(REPORT, wrong_header(gates, harns, rows + 1, brain)),
         REPORT, "gate", None),
        ("P4 keyed brain wrong",
         "Brain.MD version=",
         None, lambda: append_line(REPORT, wrong_header(gates, harns, rows, "v9.9")),
         REPORT, "gate", None),
        ("P5 compound gate wrong",
         "gate count=",
         None, lambda: append_line(REPORT, "A %d-gate suite." % (gates + 1)),
         REPORT, "gate", None),
        ("P6 compound harness wrong",
         "harness count=",
         None, lambda: append_line(REPORT, "The %d-harness rig." % (harns + 1)),
         REPORT, "gate", None),
        ("P7 of-y gates wrong",
         "gate count=",
         None, lambda: append_line(REPORT, "%d of the %d gates."
                                   % (gates + 1, gates + 1)),
         REPORT, "gate", None),
        ("P8 of-y harnesses wrong",
         "harness count=",
         None, lambda: append_line(REPORT, "%d of the %d harnesses."
                                   % (harns + 1, harns + 1)),
         REPORT, "gate", None),
        ("P9 ordinal past twentieth",
         "suite gate ordinal=",
         None, lambda: append_line(REPORT, "The twenty-second gate."),
         REPORT, "gate", None),
        ("P10 spelled entries wrong",
         "runner entry count=",
         None, lambda: append_line(REPORT, "It enumerates ninety-nine entries."),
         REPORT, "gate", None),
        ("P11 stale cardinal before gates",
         "gate count=",
         None, lambda: append_line(REPORT, "The ninety-nine gates are a read-only contract."),
         REPORT, "gate", None),
        ("P12 spelled manifest rows, no determiner",
         "manifest rows=",
         None, lambda: append_line(REPORT, "The CHECKSUM manifest lists eighty tracked rows."),
         REPORT, "gate", None),
        ("P13 corrupted word list",
         "vocabulary is corrupted",
         2,
         lambda: sub_group(GATE, r"(for _w in _CARD_ONES\[1:10\]\))",
                           lambda m: "for _w in _CARD_ONES[1:])"),
         GATE, "gate", None),
        ("C1 correct keyed header (control)",
         None,
         0, lambda: append_line(REPORT, "A header %s." % header_good),
         REPORT, "gate", None),
    ]


def main():
    for path, label in ((GATE, "report_claim_check.py"),
                        (PROV, "provenance_check.py"),
                        (LIVE, "url_liveness_check.py"),
                        (RECORD, "provenance/url_liveness.json")):
        if not os.path.isfile(path):
            print("SKIP  %s is missing: %s" % (label, path))
            print("HARNESS: SKIP -- tool not run")
            return 2

    try:
        todo = cases()
    except SystemExit as exc:
        print("SKIP  %s" % exc)
        print("HARNESS: SKIP -- tool not run")
        return 2

    print("A9 drift injection harness -- %d cases" % len(todo))
    print("live values: suite=%d harnesses=%d" % (GATES, HARNS))

    rc, fails, verdict = judge("gate")
    if rc != 0:
        print("SKIP  report_claim_check baseline must pass, got exit %d (%s)"
              % (rc, verdict))
        for line in fails:
            print("      " + line)
        print("HARNESS: FAIL -- baseline not green, nothing was injected")
        return 1
    print("ok  report_claim_check baseline exit 0, %s" % verdict)

    rc, fails, verdict = judge("prov")
    if rc != 0:
        print("SKIP  provenance_check baseline must pass, got exit %d (%s)"
              % (rc, verdict))
        for line in fails:
            print("      " + line)
        print("HARNESS: FAIL -- provenance baseline not green")
        return 1
    print("ok  provenance_check baseline exit 0, %s" % verdict)

    smoke = write_fixture(base_fixture(), "smoke")
    rc, _fails, verdict = judge("live", smoke, OUT_SMOKE)
    if rc != 0:
        print("SKIP  url_liveness_check baseline must pass, got exit %d (%s)"
              % (rc, verdict))
        print("HARNESS: FAIL -- probe baseline not green")
        return 1
    print("ok  url_liveness_check baseline exit 0, %s" % verdict)

    caught = 0
    for label, needle, want_rc, apply, target, runner, fixture in todo:
        before = read(target) if target else None
        try:
            apply()
        except SystemExit as exc:
            fail("%s: could not be applied -- %s" % (label, exc))
            continue
        except Exception as exc:
            fail("%s: could not be applied -- %s: %s"
                 % (label, type(exc).__name__, exc))
            if target:
                write_raw(target, before)
            continue
        rc, fails, verdict = judge(runner, fixture, OUT_CASE)
        if target:
            write_raw(target, before)
        if want_rc is not None and rc != want_rc:
            fail("%s: wanted exit %d, got %d (%s)" % (label, want_rc, rc, verdict))
            continue
        if want_rc == 0:
            if needle and needle not in verdict and not any(needle in f for f in fails):
                fail("%s: control did not print %r (%s)" % (label, needle, verdict))
                continue
            if target and read(target) != before:
                fail("%s: target not byte-identical after revert" % label)
                continue
            caught += 1
            print("ok  %-42s control, exit 0" % label)
            continue
        if rc == 0:
            fail("%s: tool returned 0 -- the defect was NOT caught (%s)"
                 % (label, verdict))
            continue
        if needle and not any(needle in f for f in fails) and needle not in verdict:
            fail("%s: exit %d but never named %r (verdict %s)"
                 % (label, rc, needle, verdict))
            continue
        if target and read(target) != before:
            fail("%s: target not byte-identical after revert" % label)
            continue
        caught += 1
        print("ok  %-42s caught, exit %d" % (label, rc))

    rc, fails, verdict = judge("gate")
    if rc != 0:
        fail("restored report_claim_check baseline: exit %d (%s)" % (rc, verdict))
        for line in fails:
            print("      " + line)
    else:
        print("ok  restored report_claim_check baseline exit 0, %s" % verdict)

    rc, fails, verdict = judge("prov")
    if rc != 0:
        fail("restored provenance_check baseline: exit %d (%s)" % (rc, verdict))
        for line in fails:
            print("      " + line)
    else:
        print("ok  restored provenance_check baseline exit 0, %s" % verdict)

    if failures:
        print("HARNESS: FAIL -- %d/%d cases behaved as expected, %d defect(s)"
              % (caught, len(todo), len(failures)))
        return 1
    print("HARNESS: PASS -- %d/%d cases behaved as expected, every tool green "
          "before and after, every target byte-identical"
          % (caught, len(todo)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
