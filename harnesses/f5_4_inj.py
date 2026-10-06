#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F5-4 injection harness: numeric (not textual) equality in P8.

Residual R7 of F3/F4: token_present() was deliberately fail-closed, so an
equal value written with extra trailing zeros after a decimal point
(`5.5590` for `5.559`) was reported as missing even though it is the same
number. F5-4 keeps the exact spelling as the first test and adds an exact
Decimal equality fallback.

This harness proves both halves of that trade:

  * the acceptance targets actually pass now (A1..A3), and
  * every number the exact matcher used to catch is still caught (F1..F9),
    including integer padding, which is NEVER an equal value.

Expectations below were derived by counting occurrences in the live files
first (preflight), not assumed.

Exit code: 0 = all cases behaved as expected, 1 = at least one did not.
"""

import io
import os
import re
import subprocess
import sys

R = r"D:\THE ASYMMETRIC WAGER"
DOC = os.path.join(R, "REFERENCES.md")
JSONP = os.path.join(R, "external_constants.json")
GATE = os.path.join(R, "provenance_check.py")
F4GATE = os.path.join(R, "theorem_provenance_check.py")
PY = r"C:\Python314\python.exe"

fails = []


def read(p):
    with io.open(p, "rb") as f:
        return f.read()


def write(p, b):
    with io.open(p, "wb") as f:
        f.write(b)


def run(script):
    try:
        p = subprocess.run([PY, script], capture_output=True, timeout=600)
    except Exception as exc:
        return 99, "EXCEPTION %r" % (exc,)
    out = (p.stdout or b"") + (p.stderr or b"")
    return p.returncode, out.decode("utf-8", "replace")


def doc_repl(old, new):
    """Replace the complete number `old` in REFERENCES.md. Count verified."""
    def f(b):
        t = b.decode("utf-8")
        n = len(re.findall(r"(?<![\d.])%s(?!\d)" % re.escape(old), t))
        if n != 1:
            fails.append("preflight: %r occurs %d times in REFERENCES.md"
                         % (old, n))
            return b
        return t.replace(old, new, 1).encode("utf-8")
    return f


def json_repl(old, new):
    """Replace the registered value `old` in external_constants.json."""
    def f(b):
        t = b.decode("utf-8")
        needle = '"value": "%s"' % old
        n = t.count(needle)
        if n != 1:
            fails.append("preflight: %r occurs %d times in the register"
                         % (needle, n))
            return b
        return t.replace(needle, '"value": "%s"' % new, 1).encode("utf-8")
    return f


def append_note(b):
    return b + b"\n<!-- harmless control edit, removed on restore -->\n"


CASES = [
    ("C0  pristine control", [], "PASS"),
    ("C1  harmless note appended", [(DOC, append_note)], "PASS"),

    # --- acceptance targets: equal as numbers, so they must now pass ------
    ("A1  doc 5.559 -> 5.5590", [(DOC, doc_repl("5.559", "5.5590"))], "PASS"),
    ("A2  doc 5.559 -> 5.5590000",
     [(DOC, doc_repl("5.559", "5.5590000"))], "PASS"),
    ("A3  register 5.559 -> 5.5590",
     [(JSONP, json_repl("5.559", "5.5590"))], "PASS"),

    # --- regression guards: unequal numbers must still fail P8 -----------
    ("F1  doc 5.559 -> 5.5591", [(DOC, doc_repl("5.559", "5.5591"))], "P8"),
    ("F2  doc 5.559 -> 55.59", [(DOC, doc_repl("5.559", "55.59"))], "P8"),
    ("F3  register 5.559 -> 5.559123",
     [(JSONP, json_repl("5.559", "5.559123"))], "P8"),
    ("F4  register 5.559 -> 5.5591",
     [(JSONP, json_repl("5.559", "5.5591"))], "P8"),
    ("F5  doc 5.559 -> 5.559123",
     [(DOC, doc_repl("5.559", "5.559123"))], "P8"),
    ("F6  register 103800788359 -> 1038007883590",
     [(JSONP, json_repl("103800788359", "1038007883590"))], "P8"),
    ("F7  doc 103800788359 -> 1038007883590",
     [(DOC, doc_repl("103800788359", "1038007883590"))], "P8"),
    ("F8  register 3000175332800 -> 930001753328009",
     [(JSONP, json_repl("3000175332800", "930001753328009"))], "P8"),
    ("F9  doc 5.559 removed", [(DOC, doc_repl("5.559", ""))], "P8"),
]


def verdict(rc, out, want):
    if rc == 99 or "Traceback" in out:
        return False, "CRASH (rc=%d)" % rc
    tripped_p8 = re.search(r"FAIL\s+P8\s+REFERENCE_FACT_VALUE", out) is not None
    if want == "PASS":
        if rc == 0:
            return True, "rc=0 (PASS), no traceback"
        return False, "rc=%d expected 0; p8=%s" % (rc, tripped_p8)
    if rc == 1 and tripped_p8:
        return True, "rc=1, tripped P8, no traceback"
    return False, "rc=%d expected 1 with P8 trip (got p8=%s)" % (rc, tripped_p8)


def main():
    saved = {DOC: read(DOC), JSONP: read(JSONP)}
    base_rc, base_out = run(GATE)
    print("baseline: gate rc=%d (%s)"
          % (base_rc, "PASS" if base_rc == 0 else "FAIL"))
    if base_rc != 0:
        print(base_out)
        print("HARNESS: baseline gate is not green; aborting")
        return 1

    try:
        for label, edits, want in CASES:
            for path, fn in edits:
                write(path, fn(saved[path]))
            rc, out = run(GATE)
            ok, why = verdict(rc, out, want)
            print("%s %-46s -> %s" % ("ok   " if ok else "FAIL ", label, why))
            if not ok:
                fails.append("%s: %s" % (label, why))
                sys.stdout.write("\n".join(
                    "      " + l for l in out.splitlines()
                    if "P8" in l or "Traceback" in l)[:1500] + "\n")
            for path in saved:
                write(path, saved[path])
    finally:
        for path, blob in saved.items():
            write(path, blob)

    identical = all(read(p) == saved[p] for p in saved)
    print("")
    print("byte-identical after restore: %s" % identical)
    if not identical:
        fails.append("restore was not byte-identical")

    fin_rc, fin_out = run(GATE)
    print("final gate rc=%d" % fin_rc)
    if fin_rc != 0:
        fails.append("final gate rc=%d" % fin_rc)

    rc4, out4 = run(F4GATE)
    print("cross-check theorem_provenance_check rc=%d" % rc4)
    if rc4 != 0:
        fails.append("theorem_provenance_check rc=%d" % rc4)

    print("")
    if fails:
        print("HARNESS: FAIL -- %d problem(s)" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("HARNESS: PASS -- %d/%d cases behaved as expected, "
          "restore byte-identical, final gates green"
          % (len(CASES), len(CASES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
