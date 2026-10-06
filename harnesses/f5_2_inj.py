#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F5-2 injection harness: the layered evidence archive must actually hold.

Proves every claim the new P9 conditions make:

  * a Layer A snapshot that is deleted, or has exactly one byte changed, is
    caught by hash or existence verification
  * a layer label that disagrees with its access class is caught
  * a layer B/C record that starts claiming content is caught
  * a missing licence basis, an unresolvable snapshot pointer, a snapshot
    aimed at a non-archived source, an unknown evidence pointer, a record
    dropped from the ledger and a record added but never cited are each caught
  * the other gate stays green for every mutation, so nothing breaks sideways

Pattern counts were measured in the live files before being written here, and
two controls prove the harness is not simply failing everything.

Exit 0 = every case behaved as expected and every file was restored
byte-identically.
"""

import io
import os
import subprocess
import sys

R = r"D:\THE ASYMMETRIC WAGER"
F3 = os.path.join(R, "provenance_check.py")
F4 = os.path.join(R, "theorem_provenance_check.py")
EC = os.path.join(R, "external_constants.json")
TP = os.path.join(R, "theorem_provenance.json")
EVID = os.path.join(R, "provenance", "evidence")
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


def sub(path, old, new, count=1):
    """Global replacement, refusing to proceed if the count differs."""
    def fn(text):
        n = text.count(old)
        if n != count:
            fails.append("%s: pattern %r occurs %d times, wanted %d"
                         % (os.path.basename(path), old[:60], n, count))
            return text
        return text.replace(old, new)
    return fn


def in_obj(path, marker, old, new, count=1):
    """Replacement confined to the object that contains `marker`."""
    def fn(text):
        try:
            i = text.index(marker)
        except ValueError:
            fails.append("%s: marker not found %r"
                         % (os.path.basename(path), marker[:60]))
            return text
        a = text.rindex("{", 0, i)
        depth, k = 0, a
        while k < len(text):
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        seg = text[a:k + 1]
        n = seg.count(old)
        if n != count:
            fails.append("%s: inside %r pattern %r occurs %d, wanted %d"
                         % (os.path.basename(path), marker[:40], old[:40],
                            n, count))
            return text
        return text[:a] + seg.replace(old, new) + text[k + 1:]
    return fn


def drop_file(name):
    p = os.path.join(EVID, name)
    saved = read(p)
    os.remove(p)
    return (p, saved)


def flip_byte(name, offset=100):
    p = os.path.join(EVID, name)
    saved = read(p)
    b = bytearray(saved)
    b[offset] = b[offset] ^ 0xFF
    write(p, bytes(b))
    return (p, saved)


IHARA = "https://en.wikipedia.org/wiki/Ihara_zeta_function"
PITT = ("https://sites.pitt.edu/~jdnorton/teaching/paradox/chapters/measure/"
        "measure.html")
SNAP = '"snapshot_evidence_id": "PLANCK_2018_VI_ARXIV"'

# (label, gate, expected rc for that gate, [side effects], [edits])
# side effects return (path, saved_bytes) for restoration.
CASES = [
    ("C0  both gates pristine", "both", 0, [], []),
    ("C1  both gates pristine again", "both", 0, [], []),

    # ---------------- F3: content that is claimed must be there ----------
    ("F1  delete the Planck arXiv snapshot", "f3", 1,
     [lambda: drop_file("arxiv_1807_06209_abs.html")],
     []),
    ("F2  flip one byte of the Springer snapshot", "f3", 1,
     [lambda: flip_byte("springer_mty2024_open_access.html")],
     []),
    ("F3  NIST relabelled layer A -> B (access unchanged)", "f3", 1, [],
     [(EC, sub(EC, '"layer": "A",\n      "license_basis": "NIST Library FAQ',
               '"layer": "B",\n      "license_basis": "NIST Library FAQ'))]),
    ("F4  Springer relabelled layer A -> C", "f3", 1, [],
     [(EC, sub(EC, '"layer": "A",\n      "license_basis": "CC BY"',
               '"layer": "C",\n      "license_basis": "CC BY"'))]),
    ("F5  NIST licence basis key removed", "f3", 1, [],
     [(EC, sub(EC, '"license_basis": "NIST Library FAQ',
               '"license_basis_x": "NIST Library FAQ'))]),
    ("F6  snapshot pointer aimed at an unknown id", "f3", 1, [],
     [(EC, sub(EC, SNAP, '"snapshot_evidence_id": "DOES_NOT_EXIST"', 2))]),
    ("F7  snapshot pointer aimed at a layer C source", "f3", 1, [],
     [(EC, sub(EC, SNAP, '"snapshot_evidence_id": "PLANCK_2018_VI"', 2))]),
    ("F8  layer B record starts claiming a local copy", "f3", 1, [],
     [(EC, in_obj(EC, '"id": "PLATT_2017"',
                  '"access": "publisher_landing_page"',
                  '"local_copy": "provenance/evidence/nist_allascii_2022.txt",\n'
                  '      "access": "publisher_landing_page"'))]),
    ("F9  quantity loses its evidence pointer", "f3", 1, [],
     [(EC, sub(EC, '"evidence_id": "PLANCK_2018_VI"',
               '"evidence_id": "GONE"', 1))]),

    # ---------------- F4: the ledger must be complete and honest ---------
    ("G1  delete a Layer A archive snapshot", "f4", 1,
     [lambda: drop_file("wikipedia_ihara_zeta_function.html")],
     []),
    ("G2  flip one byte of that snapshot", "f4", 1,
     [lambda: flip_byte("wikipedia_ihara_zeta_function.html")],
     []),
    ("G3  archive layer A -> B, access unchanged", "f4", 1, [],
     [(TP, in_obj(TP, '"identifier": "%s"' % IHARA,
                  '"layer": "A"', '"layer": "B"'))]),
    ("G4  archive layer set to an illegal value", "f4", 1, [],
     [(TP, in_obj(TP, '"identifier": "%s"' % PITT,
                  '"layer": "C"', '"layer": "Z"'))]),
    ("G5  archive licence basis key removed", "f4", 1, [],
     [(TP, in_obj(TP, '"identifier": "%s"' % IHARA,
                  '"license_basis"', '"license_basis_x"'))]),
    ("G6  Layer C record starts claiming a local copy", "f4", 1, [],
     [(TP, in_obj(TP, '"identifier": "%s"' % PITT,
                  '"access_class": "inaccessible"',
                  '"local_copy": "provenance/evidence/'
                  'nist_allascii_2022.txt",\n'
                  '      "access_class": "inaccessible"'))]),
    ("G7  archived identifier no longer matches any citation", "f4", 1, [],
     [(TP, in_obj(TP, '"identifier": "%s"' % IHARA,
                  '"identifier": "%s"' % IHARA,
                  '"identifier": "%sX"' % IHARA))]),
    ("G8  uncited record added to the archive", "f4", 1, [],
     [(TP, sub(TP, '"archive": [\n',
               '"archive": [\n'
               '    {\n'
               '      "identifier": "https://example.invalid/uncited",\n'
               '      "layer": "B",\n'
               '      "access_class": "publisher_landing_page",\n'
               '      "license_basis": "test record",\n'
               '      "retrieved_utc": "2026-10-05"\n'
               '    },\n'))]),
    ("G9  archive list removed from the register", "f4", 1, [],
     [(TP, sub(TP, '"archive": [', '"archiveXX": ['))]),
]


def main():
    saved = {EC: read(EC), TP: read(TP)}
    restores = []
    base3, _ = run(F3)
    base4, _ = run(F4)
    print("baseline: f3=%d f4=%d" % (base3, base4))
    if base3 != 0 or base4 != 0:
        print("HARNESS: baseline not green; aborting")
        return 1

    try:
        for label, gate, want, side, edits in CASES:
            # every case starts from a pristine workspace
            for p, blob in saved.items():
                write(p, blob)
            for path, blob in restores:
                write(path, blob)
            restores = []
            for make in side:
                restores.append(make())
            for path, fn in edits:
                write(path, fn(read(path).decode("utf-8")).encode("utf-8"))

            r3, o3 = run(F3)
            r4, o4 = run(F4)
            if gate == "f3":
                good = (r3 == want and r4 == 0)
                why = "f3=%d (want %d), f4=%d" % (r3, want, r4)
                detail = o3 + o4
            elif gate == "f4":
                good = (r4 == want and r3 == 0)
                why = "f4=%d (want %d), f3=%d" % (r4, want, r3)
                detail = o3 + o4
            else:
                good = (r3 == want and r4 == want)
                why = "f3=%d f4=%d (want %d)" % (r3, r4, want)
                detail = o3 + o4
            if r3 == 99 or r4 == 99 or "Traceback" in detail:
                good = False
                why += " CRASH"
            print("%s %-52s -> %s"
                  % ("ok   " if good else "FAIL ", label, why))
            if not good:
                fails.append("%s: %s" % (label, why))
                sys.stdout.write("\n".join(
                    "      " + l for l in detail.splitlines()
                    if "P9" in l or "FAIL " in l or "Traceback" in l)[:1400]
                    + "\n")
            for path, blob in restores:
                write(path, blob)
    finally:
        for p, blob in saved.items():
            write(p, blob)
        for p, blob in restores:
            write(p, blob)

    identical = all(read(p) == saved[p] for p in saved)
    print("")
    print("registers restored byte-identical: %s" % identical)
    if not identical:
        fails.append("registers not restored byte-identically")
    for n in ("arxiv_1807_06209_abs.html",
              "wikipedia_ihara_zeta_function.html",
              "springer_mty2024_open_access.html"):
        if not os.path.isfile(os.path.join(EVID, n)):
            fails.append("snapshot still missing: %s" % n)

    r3, _ = run(F3)
    r4, _ = run(F4)
    print("final: f3=%d f4=%d" % (r3, r4))
    if r3 != 0 or r4 != 0:
        fails.append("final gates f3=%d f4=%d" % (r3, r4))

    print("")
    if fails:
        print("HARNESS: FAIL -- %d problem(s)" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("HARNESS: PASS -- %d/%d cases behaved as expected, registers "
          "byte-identical, both gates green at the end"
          % (len(CASES), len(CASES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
