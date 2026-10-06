# -*- coding: utf-8 -*-
"""F5-1 stage A: correct the Planck-length rounding in the corpus.

01_PARADOX_AND_SCALE.md carried 1.63e-35 where the correct 3-s.f. rounding of
the CODATA 2022 value 1.616255e-35 is 1.62e-35.  F3-1 recorded the variance
openly; F5-1 is the phase permitted to edit that file.

Every replacement asserts the expected occurrence count before writing, and
every file is verified UTF-8 / LF / no-BOM afterwards.
"""
import hashlib
import io
import os
import sys

ROOT = r"D:\THE ASYMMETRIC WAGER"
DOC = os.path.join(ROOT, "01_PARADOX_AND_SCALE.md")
JSONP = os.path.join(ROOT, "external_constants.json")
fails = []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def read(p):
    b = open(p, "rb").read()
    if b.startswith(b"\xef\xbb\xbf"):
        fails.append("%s already has a BOM" % p)
    if b"\r" in b:
        fails.append("%s already contains CR" % p)
    return b.decode("utf-8")


def write(p, text):
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    b = open(p, "rb").read()
    if b.startswith(b"\xef\xbb\xbf") or b"\r" in b:
        fails.append("%s: encoding violated after write" % p)
    try:
        b.decode("utf-8")
    except Exception as exc:
        fails.append("%s: not UTF-8 after write: %r" % (p, exc))


def replace(text, old, new, want, what):
    n = text.count(old)
    if n != want:
        fails.append("%s: expected %d occurrences of %r, found %d" % (what, want, old, n))
        return text, False
    return text.replace(old, new), True


print("=" * 90)
print("F5-1 STAGE A -- correct ell_P rounding: 1.63e-35 -> 1.62e-35")
print("=" * 90)

# ---------------------------------------------------------------- document
before_doc = sha(DOC)
text = read(DOC)
text, ok = replace(text, r"1.63 \times 10^{-35}", r"1.62 \times 10^{-35}", 2,
                   "01_PARADOX_AND_SCALE.md")
if ok:
    write(DOC, text)
    print("ok    01_PARADOX_AND_SCALE.md      2 occurrences corrected  sha %s -> %s"
          % (before_doc[:16], sha(DOC)[:16]))

# ---------------------------------------------------------------- register
before_js = sha(JSONP)
raw = read(JSONP)

OLD = '''          "needle": "1.63 \\\\times 10^{-35}",
          "mantissa": "1.63",
          "exponent": -35,
          "count": 2,
          "mode": "declared_variance",
          "doc_value": "1.63e-35",
          "source_value": "1.616255e-35",
          "correct_rounding": "1.62e-35",
          "rounding_sf": 3,
          "rel_dev": 8.504e-3,
          "rel_dev_sf": 4,
          "note": "Found by F3-1 on 2026-10-05. Correct 3-s.f. rounding of the CODATA 2022 value is 1.62e-35, not 1.63e-35. Recorded openly, not silently corrected; downstream N_steps is unaffected at the 2 s.f. the corpus declares."'''

NEW = '''          "needle": "1.62 \\\\times 10^{-35}",
          "mantissa": "1.62",
          "exponent": -35,
          "count": 2,
          "mode": "source_agree",
          "doc_value": "1.62e-35",
          "note": "Corrected by F5-1 on 2026-10-05. Until then this site read 1.63e-35, a declared variance of 8.504e-3 (+0.8504 percent) from the CODATA 2022 value 1.616255e-35, which F3-1 recorded openly instead of editing silently. Both 1.62e-35 and 1.63e-35 reproduce N_steps at the 2 s.f. the corpus declares, so no downstream figure moved. The site now carries the correct 3 s.f. rounding and P4 compares it against the authoritative value."'''

if raw.count(OLD) != 1:
    fails.append("external_constants.json: expected exactly 1 variance block, found %d"
                 % raw.count(OLD))
else:
    write(JSONP, raw.replace(OLD, NEW))
    print("ok    external_constants.json     site mode declared_variance -> source_agree"
          "  sha %s -> %s" % (before_js[:16], sha(JSONP)[:16]))

# ---------------------------------------------------------------- verify
import json
try:
    d = json.loads(io.open(JSONP, encoding="utf-8").read())
    site = [s for q in d["quantities"] if q.get("id") == "PLANCK_LENGTH"
            for s in q.get("sites", []) if "01_PARADOX" in str(s.get("file"))]
    if len(site) != 1:
        fails.append("could not locate the 01_PARADOX site after the edit")
    else:
        s = site[0]
        print("ok    site after edit: mode=%s mantissa=%s count=%s doc_value=%s"
              % (s.get("mode"), s.get("mantissa"), s.get("count"), s.get("doc_value")))
        for k in ("source_value", "correct_rounding", "rounding_sf", "rel_dev", "rel_dev_sf"):
            if k in s:
                fails.append("stale field %r left behind" % k)
        if s.get("mode") == "declared_variance":
            fails.append("mode is still declared_variance")
except Exception as exc:
    fails.append("register no longer parses: %r" % exc)

print()
if fails:
    print("FAILURES (%d):" % len(fails))
    for f in fails:
        print("  - " + f)
    print("STAGE A: FAIL")
    sys.exit(1)
print("STAGE A: PASS")
sys.exit(0)
