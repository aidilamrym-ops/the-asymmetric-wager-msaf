# FILE: harnesses/trackc_static_inj.py
# PURPOSE: A22 (2026-10-08) proves the OFFLINE half of trackc_recompile.py is
#          a check and not a decoration.  A17 registered two clauses as
#          residual A17-R1: the recompile tool was in no rig at all, and
#          OMEGATrackC.lean had no offline byte-level check -- the
#          sub-repository manifest pinned the file and nothing ever read the
#          row.  The tool now carries --static-only (structure, literal VALUE
#          pin, byte-level pin against CHECKSUM.sha256) that needs no
#          toolchain, no network and no temp project, and this harness holds
#          it to seven mutations plus a clean baseline and a restored
#          baseline:
#            M1  a `sorry` token injected into the code
#            M2  the rhoActual numerator nudged by one (shape intact, value
#                drifted -- the check A22 added, since the old tool only read
#                the literal's shape)
#            M3  one expected theorem renamed away
#            M4  an `axiom` declaration appended
#            M5  the manifest row's hash corrupted (file untouched) -- proves
#                the pin compares BOTH sides
#            M6  a comment appended (structure untouched, hash changed) --
#                proves the pin is load-bearing and not vacuous: every static
#                check stays green while only the pin fails
#            M7  the manifest row deleted -- absence must fail, never skip
#          Every case runs in its own temp scratch copy of the three files;
#          the workspace tool, target and manifest are never written, and all
#          scratches are removed.  Needs neither the megabyte matrix nor the
#          Lean toolchain: a static run is milliseconds.

import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SUB = os.path.join(ROOT, "guinand-weil-rigorous-numerics-main")
TOOL = os.path.join(SUB, "trackc_recompile.py")
TARGET = os.path.join(SUB, "OMEGATrackC.lean")
MANIFEST = os.path.join(SUB, "CHECKSUM.sha256")
PY = sys.executable

results = []
created = []


def record(name, ok, detail):
    results.append(bool(ok))
    print("  %s %-62s %s" % ("ok  " if ok else "FAIL", name, detail))


def build(mutator=None):
    scratch = tempfile.mkdtemp(prefix="a22-trackc-")
    created.append(scratch)
    shutil.copyfile(TOOL, os.path.join(scratch, "trackc_recompile.py"))
    shutil.copyfile(TARGET, os.path.join(scratch, "OMEGATrackC.lean"))
    shutil.copyfile(MANIFEST, os.path.join(scratch, "CHECKSUM.sha256"))
    if mutator is not None:
        mutator(scratch)
    return scratch


def run(scratch):
    p = subprocess.run(
        [PY, os.path.join(scratch, "trackc_recompile.py"), "--static-only"],
        cwd=scratch, capture_output=True, text=True, timeout=180)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def edit(scratch, fname, old, new, count=1):
    path = os.path.join(scratch, fname)
    src = io.open(path, encoding="utf-8", newline="").read()
    n = src.count(old)
    if n != count:
        return "needle %r found %d times, expected %d" % (old[:40], n, count)
    io.open(path, "w", encoding="utf-8", newline="").write(
        src.replace(old, new, count))
    return None


BASE_STATIC = [
    "zero sorry tokens",
    "zero axiom declarations",
    "all 10 expected theorems present",
    "58287013697174734848 / 10^198 = 5.8287013697174734848E-179",
    "rhoStar, lambdaMin and nDim declarations present",
    "byte-level pin: OMEGATrackC.lean matches the sub-repository manifest",
    "TRACKC_RECOMPILE: STATIC PASS",
]


def main():
    print("A22 TRACKC STATIC INJECTION -- nine cases against "
          "trackc_recompile.py --static-only")

    # --- baseline ------------------------------------------------------------
    scratch = build()
    rc, out = run(scratch)
    missing = [m for m in BASE_STATIC if m not in out]
    record("baseline: offline checks green, exit 0",
           rc == 0 and not missing,
           "exit=%d%s" % (rc, ", missing %r" % missing if missing else ""))

    # --- M1: a sorry token ---------------------------------------------------
    def m1(s):
        return edit(s, "OMEGATrackC.lean",
                    "abbrev rhoActual", "\nsorry\n\nabbrev rhoActual")

    scratch = build(m1)
    rc, out = run(scratch)
    record("M1 sorry token injected -> exit 1, named",
           rc == 1 and "sorry token(s)" in out,
           "exit=%d, %s" % (rc, "named" if "sorry token(s)" in out
                            else "never reported the sorry token"))

    # --- M2: literal value drifted, shape intact ----------------------------
    def m2(s):
        return edit(s, "OMEGATrackC.lean",
                    ":= 58287013697174734848 / 10 ^ 198",
                    ":= 58287013697174734847 / 10 ^ 198")

    scratch = build(m2)
    rc, out = run(scratch)
    record("M2 rhoActual numerator nudged -> exit 1, value pin names it",
           rc == 1 and "the value drifted" in out,
           "exit=%d, %s" % (rc, "named" if "the value drifted" in out
                            else "shape check swallowed the value drift"))

    # --- M3: an expected theorem renamed away --------------------------------
    def m3(s):
        return edit(s, "OMEGATrackC.lean",
                    "theorem tolerance_positive",
                    "theorem tolerance_positive_scratch")

    scratch = build(m3)
    rc, out = run(scratch)
    record("M3 theorem renamed away -> exit 1, missing listed",
           rc == 1 and "expected theorems missing" in out,
           "exit=%d, %s" % (rc, "named" if "expected theorems missing" in out
                            else "never reported the missing theorem"))

    # --- M4: an axiom declaration appended ------------------------------------
    def m4(s):
        path = os.path.join(s, "OMEGATrackC.lean")
        with io.open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\naxiom a22_scratch_axiom : True\n")

    scratch = build(m4)
    rc, out = run(scratch)
    record("M4 axiom declaration appended -> exit 1, counted",
           rc == 1 and "axiom/constant declaration(s)" in out,
           "exit=%d, %s" % (rc, "named" if "axiom/constant declaration(s)" in out
                            else "never reported the axiom"))

    # --- M5: manifest hash corrupted, file untouched --------------------------
    def m5(s):
        path = os.path.join(s, "CHECKSUM.sha256")
        src = io.open(path, encoding="utf-8", newline="").read()
        lines = src.split("\n")
        hit = 0
        for i, ln in enumerate(lines):
            if ln.startswith("SHA-256") and ln.rstrip().endswith(
                    "OMEGATrackC.lean"):
                p = ln.split(None, 3)
                lines[i] = "SHA-256  deadbeef" + p[1][8:] + "%12s  %s" % (
                    p[2], p[3])
                hit += 1
        if hit != 1:
            return "OMEGATrackC.lean row found %d times in scratch manifest" % hit
        io.open(path, "w", encoding="utf-8", newline="").write("\n".join(lines))
        return None

    scratch = build(m5)
    rc, out = run(scratch)
    statics_green = ("zero sorry tokens" in out and "all 10 expected" in out)
    record("M5 manifest hash corrupted -> exit 1, pin names both sides",
           rc == 1 and "byte-level pin mismatch" in out
           and "manifest says sha256 deadbeef" in out and statics_green,
           "exit=%d, %s, statics %s" % (
               rc,
               "named" if "manifest says sha256 deadbeef" in out else "silent",
               "green (isolated)" if statics_green else "NOT green"))

    # --- M6: comment appended, structure untouched ----------------------------
    def m6(s):
        path = os.path.join(s, "OMEGATrackC.lean")
        with io.open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n-- A22 scratch note: structure intact, hash changed\n")

    scratch = build(m6)
    rc, out = run(scratch)
    statics_green = ("zero sorry tokens" in out and "all 10 expected" in out
                     and "byte-level pin:" not in out)
    record("M6 comment appended -> statics green, ONLY the pin fails",
           rc == 1 and "byte-level pin mismatch" in out and statics_green,
           "exit=%d, %s" % (rc, "pin alone failed (load-bearing)"
                            if statics_green and "byte-level pin mismatch" in out
                            else "unexpected companion failure"))

    # --- M7: manifest row deleted ---------------------------------------------
    def m7(s):
        path = os.path.join(s, "CHECKSUM.sha256")
        src = io.open(path, encoding="utf-8", newline="").read()
        kept = [ln for ln in src.split("\n")
                if not (ln.startswith("SHA-256")
                        and ln.rstrip().endswith("OMEGATrackC.lean"))]
        removed = src.count("\n") + 1 - len(kept)
        if removed != 1:
            return "row removal count %d" % removed
        io.open(path, "w", encoding="utf-8", newline="").write("\n".join(kept))
        return None

    scratch = build(m7)
    rc, out = run(scratch)
    record("M7 manifest row deleted -> exit 1, absence fails",
           rc == 1 and "has no row in the sub-repository manifest" in out,
           "exit=%d, %s" % (rc, "named" if "has no row" in out
                            else "absence was treated as a skip"))

    # --- restored baseline ----------------------------------------------------
    scratch = build()
    rc, out = run(scratch)
    missing = [m for m in BASE_STATIC if m not in out]
    record("restored baseline: offline checks green again",
           rc == 0 and not missing,
           "exit=%d%s" % (rc, ", missing %r" % missing if missing else ""))

    for s in created:
        shutil.rmtree(s, ignore_errors=True)

    passed = sum(1 for r in results if r)
    print("")
    print("HARNESS: PASS -- %d/%d cases behaved as expected"
          % (passed, len(results)) if passed == len(results)
          else "HARNESS: FAIL -- %d/%d cases behaved as expected"
          % (passed, len(results)))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())