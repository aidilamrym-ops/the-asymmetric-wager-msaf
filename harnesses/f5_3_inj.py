#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F5-3 injection harness: the [REF] marker binding of P10.

Every case mutates documents, runs both gates, and restores them. An
expected exit code is only accepted when the gate's own printed verdict
agrees with it, and every edit asserts its premise before writing.
"""
import io
import os
import re
import subprocess
import sys

R = r"D:\THE ASYMMETRIC WAGER"
PY = r"C:\Python314\python.exe"
F3 = "provenance_check.py"
F4 = "theorem_provenance_check.py"

DRAF = "DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md"
PARA = "01_PARADOX_AND_SCALE.md"
SKILL = "Skill.md"
REFS = "REFERENCES.md"
TARGETS = [DRAF, PARA, SKILL, REFS]

REF_RE = re.compile(r"\[REF-[A-Za-z0-9_.\-]+\]")
TOKEN = "<!-- [REF-NIST_CODATA_2022_TABLE] -->"
SKILL_NEEDLES = ["1{,}616255", "8{,}8 \\times", "1{,}836653"]


def read(name):
    with io.open(os.path.join(R, name), encoding="utf-8", newline="") as fh:
        return fh.read()


def write(name, text):
    data = text.encode("utf-8")
    if b"\r" in data:
        raise SystemExit("BLOCKED %s: CR introduced" % name)
    with io.open(os.path.join(R, name), "w", encoding="utf-8",
                 newline="") as fh:
        fh.write(text)


def edit_lines(name, needle, fn, count=1):
    """Apply fn to exactly the lines of `name` containing `needle`."""
    text = read(name)
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != count:
        raise SystemExit("BLOCKED %s: %r on %d line(s), wanted %d"
                         % (name, needle[:50], len(hits), count))
    for i in hits:
        lines[i] = fn(lines[i])
    write(name, "\n".join(lines))


def strip_markers(name):
    text = read(name)
    before = len(REF_RE.findall(text))
    out = re.sub(r"\s*<!--(?:\s*\[REF-[A-Za-z0-9_.\-]+\])+ -->", "", text)
    write(name, out)
    if len(REF_RE.findall(out)) != 0:
        raise SystemExit("BLOCKED %s: markers survived the strip" % name)
    return before


def run(script):
    p = subprocess.run([PY, os.path.join(R, script)],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       cwd=R, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    return p.returncode, p.stdout.decode("utf-8", "replace")


# ------------------------------------------------------------------ cases --
def c_r1():
    """A marker naming an evidence id that does not exist."""
    def fn(line):
        if "[REF-NO_SUCH_EVIDENCE]" in line:
            raise SystemExit("BLOCKED: already present")
        if TOKEN not in line:
            raise SystemExit("BLOCKED: premise token missing")
        return line.replace(TOKEN, "<!-- [REF-NIST_CODATA_2022_TABLE] "
                                   "[REF-NO_SUCH_EVIDENCE] -->")
    edit_lines(DRAF, "1,836653", fn)


def c_r2():
    """The right evidence id pasted onto the wrong line (l_P row, D_obs id)."""
    def fn(line):
        if "[REF-NIST_CODATA_2022_TABLE]" not in line:
            raise SystemExit("BLOCKED: premise token missing")
        return line.replace("[REF-NIST_CODATA_2022_TABLE]",
                            "[REF-PLANCK_2018_VI]")
    edit_lines(SKILL, "1{,}616255", fn)


def c_r3():
    strip_markers(PARA)


def c_r4():
    """Move a marker off its needle line onto a needle-free line."""
    text = read(SKILL)
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if "1{,}616255" in l]
    if len(hits) != 1:
        raise SystemExit("BLOCKED: l_P row on %d line(s)" % len(hits))
    i = hits[0]
    if TOKEN not in lines[i]:
        raise SystemExit("BLOCKED: l_P row has no marker")
    lines[i] = lines[i].replace(" " + TOKEN, "")
    target = None
    for k in range(len(lines) - 1, -1, -1):
        if not lines[k].strip():
            continue
        if any(n in lines[k] for n in SKILL_NEEDLES):
            continue
        target = k
        break
    if target is None:
        raise SystemExit("BLOCKED: no needle-free line found")
    lines[target] = lines[target] + " " + TOKEN
    write(SKILL, "\n".join(lines))


def c_r5():
    """A marker pasted into a document no site points at."""
    text = read(REFS)
    if REF_RE.search(text):
        raise SystemExit("BLOCKED: REFERENCES.md already carries a marker")
    write(REFS, text + "\n" + TOKEN + "\n")


CASES = [
    ("C0", "both gates pristine", 0, 0, None),
    ("C1", "both gates pristine again", 0, 0, None),
    ("R1", "marker names an evidence entry that does not exist",
     1, 0, c_r1),
    ("R2", "right evidence id, wrong line (l_P row marked as D_obs)",
     1, 0, c_r2),
    ("R3", "every marker stripped from one document", 1, 0, c_r3),
    ("R4", "marker moved off its needle line", 1, 0, c_r4),
    ("R5", "marker pasted into a document no site points at",
     1, 0, c_r5),
]


def main():
    saved = {n: read(n).encode("utf-8") for n in TARGETS}
    base3, out3 = run(F3)
    base4, out4 = run(F4)
    print("baseline: f3=%d f4=%d  markers seen in Skill.md: %d"
          % (base3, base4, len(REF_RE.findall(saved[SKILL].decode("utf-8")))))
    if base3 != 0 or base4 != 0 or "markers seen: 12" not in out3:
        print("BLOCKED: baseline not green or marker count wrong")
        return 1
    bad = 0
    try:
        for label, desc, want3, want4, apply in CASES:
            for n in TARGETS:
                write(n, saved[n].decode("utf-8"))
            if apply is not None:
                apply()
            c3, o3 = run(F3)
            c4, o4 = run(F4)
            agree3 = ("GATE: PASS" in o3) == (c3 == 0) and c3 in (0, 1)
            agree4 = (("THEOREM PROVENANCE CHECK" in o4) == (c4 == 0)
                      and c4 in (0, 1))
            # a failing case must fail at P10 itself, not at some other check
            at_p10 = want3 != 1 or "FAIL   P10  REF_MARKERS" in o3
            good = (c3 == want3 and c4 == want4 and agree3 and agree4
                    and at_p10)
            print("%s    %s %-52s -> f3=%d f4=%d (want %d/%d)%s%s"
                  % ("ok  " if good else "FAIL  ", label, desc,
                     c3, c4, want3, want4,
                     "" if agree3 and agree4 else "  [verdict/exit disagree]",
                     "" if at_p10 else "  [failed outside P10]"))
            if not good:
                bad += 1
    finally:
        for n in TARGETS:
            write(n, saved[n].decode("utf-8"))
    restored = all(read(n).encode("utf-8") == saved[n] for n in TARGETS)
    f3e, _ = run(F3)
    f4e, _ = run(F4)
    print("")
    print("documents restored byte-identical: %s" % restored)
    print("final: f3=%d f4=%d" % (f3e, f4e))
    print("")
    if bad == 0 and restored and f3e == 0 and f4e == 0:
        print("HARNESS: PASS -- %d/%d cases behaved as expected, documents "
              "byte-identical, both gates green at the end"
              % (len(CASES), len(CASES)))
        return 0
    print("HARNESS: FAIL -- %d of %d wrong, restore=%s, f3=%d f4=%d"
          % (bad, len(CASES), restored, f3e, f4e))
    return 1


if __name__ == "__main__":
    sys.exit(main())
