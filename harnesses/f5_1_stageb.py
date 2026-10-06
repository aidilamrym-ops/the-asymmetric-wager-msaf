# -*- coding: utf-8 -*-
"""F5-1 stage B: prove the fix is enforced, not merely agreed.

A correction is worthless if the gate would also have passed before it.  Three
reverts are applied one at a time and the gate must fail every time:

  B1  document reverted to 1.63, register correct  -> P3 (needle count)
  B2  register reverted to 1.63, document correct  -> P3 (needle count)
  B3  BOTH reverted, i.e. the exact pre-F5-1 state -> P4 (doc_value vs authority)

B3 is the decisive one: that state passed the gate before F5-1 (it was a
declared variance) and must fail now.

Snapshot / mutate / run / restore / verify, strictly sequential.
"""
import hashlib
import io
import os
import subprocess
import sys

ROOT = r"D:\THE ASYMMETRIC WAGER"
DOC = os.path.join(ROOT, "01_PARADOX_AND_SCALE.md")
JSONP = os.path.join(ROOT, "external_constants.json")
GATE = os.path.join(ROOT, "provenance_check.py")
PY = r"C:\Python314\python.exe"
FILES = [DOC, JSONP]
fails = []
rows = []

GOOD_DOC = r"1.62 \times 10^{-35}"
BAD_DOC = r"1.63 \times 10^{-35}"
GOOD_J = '"needle": "1.62 \\\\times 10^{-35}",\n          "mantissa": "1.62",'
BAD_J = '"needle": "1.63 \\\\times 10^{-35}",\n          "mantissa": "1.63",'
GOOD_DV = '"mode": "source_agree",\n          "doc_value": "1.62e-35",'
BAD_DV = '"mode": "source_agree",\n          "doc_value": "1.63e-35",'


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def run():
    p = subprocess.run([PY, GATE], cwd=ROOT, capture_output=True)
    out = ((p.stdout or b"") + (p.stderr or b"")).decode("utf-8", "replace")
    return p.returncode, out


def show(out, tag):
    return [l.strip() for l in out.splitlines()
            if l.startswith("FAIL") and tag in l][:2]


def probe(name, want_code, want_tag, mutate):
    base = {f: open(f, "rb").read() for f in FILES}
    try:
        mutate()
        rc, out = run()
        bad = (rc != want_code) or (want_tag not in out)
        if bad:
            fails.append("%s: expected exit %d reported by %s, got exit %d\n%s"
                         % (name, want_code, want_tag, rc, out[-900:]))
            rows.append("FAIL  %-52s expected %d/%s got %d"
                        % (name, want_code, want_tag, rc))
        else:
            rows.append("ok    %-52s exit=%d, reported by %s"
                        % (name, rc, want_tag))
            for line in show(out, want_tag):
                rows.append("        | " + line)
    finally:
        for f in FILES:
            open(f, "wb").write(base[f])
        after = {f: sha(f) for f in FILES}
        for f in FILES:
            if after[f] != hashlib.sha256(base[f]).hexdigest():
                fails.append("%s: %s not restored" % (name, os.path.basename(f)))


def m_doc_to_163():
    b = open(DOC, "rb").read().decode("utf-8")
    assert b.count(GOOD_DOC) == 2, "doc baseline changed"
    open(DOC, "wb").write(b.replace(GOOD_DOC, BAD_DOC).encode("utf-8"))


def m_reg_needle_to_163():
    b = open(JSONP, "rb").read().decode("utf-8")
    assert b.count(GOOD_J) == 1, "register needle baseline changed"
    open(JSONP, "wb").write(b.replace(GOOD_J, BAD_J).encode("utf-8"))


def m_reg_docvalue_to_163():
    b = open(JSONP, "rb").read().decode("utf-8")
    assert b.count(GOOD_DV) == 1, "register doc_value baseline changed"
    open(JSONP, "wb").write(b.replace(GOOD_DV, BAD_DV).encode("utf-8"))


def m_both():
    m_doc_to_163()
    m_reg_needle_to_163()
    m_reg_docvalue_to_163()


print("=" * 90)
print("F5-1 STAGE B -- the pre-fix state must now FAIL the gate")
print("=" * 90)

rc0, out0 = run()
if rc0 != 0:
    fails.append("baseline should pass before probing, got %d\n%s" % (rc0, out0[-900:]))
    rows.append("FAIL  %-52s baseline exit=%d" % ("baseline (corrected) exit=0", rc0))
else:
    rows.append("ok    %-52s exit=0" % "baseline (corrected) exit=0")

probe("B1 document reverted to 1.63", 1, "P3", m_doc_to_163)
probe("B2 register reverted to 1.63", 1, "P3", m_reg_needle_to_163)
probe("B3 register doc_value set to 1.63", 1, "P4", m_reg_docvalue_to_163)
probe("B4 BOTH reverted (exact pre-F5-1 state)", 1, "P4", m_both)

rc0, out0 = run()
if rc0 != 0:
    fails.append("baseline should pass after restore, got %d\n%s" % (rc0, out0[-900:]))
    rows.append("FAIL  %-52s exit=%d" % ("baseline after restore exit=0", rc0))
else:
    rows.append("ok    %-52s exit=0" % "baseline after restore exit=0")

print()
for r in rows:
    print("  " + r)
print()
if fails:
    print("FAILURES (%d):" % len(fails))
    for f in fails:
        print("  - " + f)
    print("STAGE B: FAIL")
    sys.exit(1)
print("STAGE B: PASS -- every revert is caught, baseline intact, files byte-identical")
sys.exit(0)
