#!/usr/bin/env python3
"""Recompile Track C (`OMEGATrackC.lean`) against a real Mathlib and print the
axiom footprint.

WHY THIS EXISTS
    Fase A15 (2026-10-07) replaced the `rhoActual` literal in
    `OMEGATrackC.lean` with a rigorous ball-arithmetic bound.  The machine that
    made that edit had no Mathlib, so the file could not be recompiled and the
    literal rested on `track_c_make_smt.py` + Z3 + the anti-circularity audit
    instead.  That gap was registered as residual A15-R1.

    This script is what closes it.  It builds a throwaway lake project OUTSIDE
    the workspace, pins Mathlib to the release matching the Lean toolchain,
    compiles the *workspace file byte-for-byte* (verified by sha256), then
    prints the axiom footprint of all ten theorems and the `sorry` count.

WHAT IT DOES NOT DO
    - It does not rewrite `OMEGATrackC.lean`.  It copies it.
    - It does not install anything into the workspace.
    - It is deliberately NOT a suite gate: the suite is the offline contract,
      and this tool needs the network plus several GB of Mathlib.  The same
      reasoning that kept `url_liveness_check.py` out of the suite.

USAGE
    python trackc_recompile.py                  # build in a temp dir
    python trackc_recompile.py --keep           # leave the temp project behind
    python trackc_recompile.py --project DIR    # reuse a project dir

EXIT
    0  file compiled, zero sorry, zero axiom declarations, footprint printed
    1  a check failed (build error, sha256 mismatch, sorry/axiom found)
    2  no Lean toolchain / lake / network on this machine -- never a pass
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "OMEGATrackC.lean")

# Mathlib release that matches the Lean toolchain this corpus pins.  The tag is
# recorded as a resolved commit because Lake rejects `version = "v4.33.1"`:
# the tag string is not a semantic version it will accept.
MATHLIB_REPO = "https://github.com/leanprover-community/mathlib4"
MATHLIB_TAG = "v4.33.1"
LEAN_TOOLCHAIN = "leanprover/lean4:v4.33.1"

# The ten theorems of the module, in source order.  Kept explicit: a silent
# theorem added later must fail this list rather than escape the footprint
# report.
THEOREMS = [
    "two_abs_mul_le_add_sq",
    "enclosure_quad_bound",
    "certified_positivity",
    "measured_within_tolerance",
    "margin_at_least_74_orders",
    "margin_satisfies_master_theorem",
    "tolerance_fails_the_coarse_bound",
    "implied_constant_ge_81",
    "implied_constant_lt_82",
    "tolerance_positive",
]

# The footprint the 2026-10-02 run recorded for these theorems, before the
# literal changed.  A17's whole claim is that the *proofs* were untouched, so
# the old footprint is the control and a drift here is a finding.
EXPECTED_AXIOMS = "[propext, Classical.choice, Quot.sound]"

LAKEFILE = """name = "trackc"
version = "0.1.0"
defaultTargets = ["TrackC"]

[[require]]
name = "mathlib"
scope = "leanprover-community"
rev = "{rev}"

[[lean_lib]]
name = "TrackC"
"""


def fail(msg: str) -> None:
    print("FAIL  %s" % msg)


def ok(msg: str) -> None:
    print("ok    %s" % msg)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def strip_comments(src: str) -> str:
    """Remove Lean line and block comments.

    Needed because the module's own header legitimately *writes the word*
    "sorry" when it reports that there are none, and a naive scan counted that
    prose as a placeholder.  The kernel's own warning is the authority (see
    `run_lean`); this pass only makes the friendly message agree with it.
    """
    out, i, n = [], 0, len(src)
    depth = 0
    while i < n:
        two = src[i:i + 2]
        if depth == 0 and two == "/-":
            depth, i = 1, i + 2
            continue
        if depth:
            if two == "/-":
                depth, i = depth + 1, i + 2
                continue
            if two == "-/":
                depth, i = depth - 1, i + 2
                continue
            i += 1
            continue
        if two == "--":
            while i < n and src[i] != "\n":
                i += 1
            continue
        out.append(src[i])
        i += 1
    return "".join(out)


# Markers that mean the kernel found a hole.  A `lake build` that only builds
# the library module is not evidence that this file type-checked, so the file is
# compiled directly and its diagnostics are read.
LEAN_FAILURE_MARKERS = (
    "uses `sorry`",
    "uses sorryAx",
    "unsolved goals",
    "declaration uses 'sorry'",
)


def run_lean(lake: str, project: str, target: str, extra=()):
    """Compile one file in the project's environment; return (rc, out, err)."""
    argv = [lake, "env", "lean"] + list(extra) + [target]
    proc = subprocess.run(argv, cwd=project, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def find_tool(name: str):
    """Locate `lean`/`lake` from PATH or from a standard elan install."""
    found = shutil.which(name)
    if found:
        return found
    for base in (os.path.expanduser("~/.elan/bin"), r"C:\Users\usER\.elan\bin"):
        cand = os.path.join(base, name + (".exe" if os.name == "nt" else ""))
        if os.path.isfile(cand):
            return cand
    return None


def resolve_mathlib_rev(git: str) -> str | None:
    try:
        out = subprocess.run(
            [git, "ls-remote", "--tags", "--refs", "%s" % MATHLIB_REPO,
             MATHLIB_TAG],
            capture_output=True, text=True, timeout=300,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    return out.stdout.split()[0]


def fetch(project: str, lake: str) -> None:
    """`lake update`: resolve Mathlib and fetch the prebuilt cache."""
    proc = subprocess.run([lake, "update"], cwd=project, text=True,
                          capture_output=True)
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout[-4000:])
        sys.stderr.write(proc.stderr[-4000:])
        raise RuntimeError("lake update failed with exit %d" % proc.returncode)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=None,
                    help="project directory to reuse (default: a temp dir)")
    ap.add_argument("--keep", action="store_true",
                    help="do not delete the temporary project")
    args = ap.parse_args()

    if not os.path.isfile(TARGET):
        fail("OMEGATrackC.lean not found next to this script")
        return 2
    lean = find_tool("lean")
    lake = find_tool("lake")
    git = find_tool("git")
    if not lean or not lake:
        fail("no Lean toolchain or lake on this machine -- this is exit 2, "
             "never a pass")
        return 2

    src = open(TARGET, encoding="utf-8").read()

    # --- static checks that need no toolchain -------------------------------
    code = strip_comments(src)
    sorry = len(re.findall(r"\bsorry\b", code))
    axioms = re.findall(r"^\s*(?:axiom|constant)\s+\w+", code, re.M)
    if sorry:
        fail("%d sorry token(s) in OMEGATrackC.lean code (comments excluded)"
             % sorry)
        return 1
    ok("zero sorry tokens in code (comments excluded; the kernel confirms below)")
    if axioms:
        fail("%d axiom/constant declaration(s): %s" % (len(axioms), axioms))
        return 1
    ok("zero axiom declarations (every result is proved)")

    theorems = re.findall(r"^\s*(?:theorem|lemma)\s+(\w+)", src, re.M)
    missing = [t for t in THEOREMS if t not in theorems]
    if missing:
        fail("expected theorems missing from the file: %s" % missing)
        return 1
    ok("all %d expected theorems present" % len(THEOREMS))

    # The rationals type is U+211A DOUBLE-STRUCK CAPITAL Q, not ASCII `Q`; the
    # module also declares its own `Q` abbrev.  Match the glyph the file uses.
    literal = re.search(r"abbrev rhoActual\s*:\s*\u211a\s*:=\s*(\d+)\s*/\s*"
                        r"10\s*\^\s*(\d+)", src)
    if not literal:
        fail("rhoActual literal not found -- the module shape changed")
        return 1
    num, den = literal.group(1), literal.group(2)
    ok("rhoActual literal = %s / 10^%s = %.19e"
       % (num, den, int(num) / 10 ** int(den)))

    for other in ("rhoStar", "lambdaMin", "nDim"):
        if not re.search(r"abbrev %s\s*:" % other, src):
            fail("%s declaration not found -- the module shape changed" % other)
            return 1
    ok("rhoStar, lambdaMin and nDim declarations present")

    # --- toolchain work -----------------------------------------------------
    project = args.project
    temp = None
    if project is None:
        temp = tempfile.mkdtemp(prefix="msaf-trackc-")
        project = temp
    if not git:
        fail("no git on this machine -- the Mathlib pin cannot be resolved")
        return 2
    rev = resolve_mathlib_rev(git)
    if rev is None:
        fail("cannot resolve %s %s (no network?) -- exit 2, never a pass"
             % (MATHLIB_REPO, MATHLIB_TAG))
        return 2

    src_dir = os.path.join(project, "TrackC")
    os.makedirs(src_dir, exist_ok=True)
    with open(os.path.join(project, "lakefile.toml"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(LAKEFILE.format(rev=rev))
    with open(os.path.join(project, "lean-toolchain"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(LEAN_TOOLCHAIN + "\n")

    work = os.path.join(src_dir, "OMEGATrackC.lean")
    shutil.copyfile(TARGET, work)
    digest = sha256(work)
    if digest != sha256(TARGET):
        fail("copied file digest differs from the workspace file")
        return 1
    ok("byte-for-byte copy of the workspace file, sha256 %s" % digest)

    # A copy whose only edits are additive: one extra `import Mathlib` at the
    # top and the `#print axioms` lines at the bottom.  Removing the narrower
    # imports instead (a previous attempt here) shifted the file and unterminated
    # a block comment, which is exactly the kind of edit-then-hope this script
    # exists to avoid -- the workspace file is compiled untouched above.
    axfile = os.path.join(src_dir, "OMEGATrackC_axcheck.lean")
    axsrc = "import Mathlib\n" + src + "\n"
    axsrc += "\n".join("#print axioms OMEGA.%s" % t for t in THEOREMS) + "\n"
    with open(axfile, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(axsrc)

    try:
        fetch(project, lake)
    except RuntimeError as exc:
        fail(str(exc))
        return 2

    # --- the file itself, compiled untouched --------------------------------
    # `lake build` compiles the library module named in the lakefile, which is
    # not evidence that *this* file type-checked: an earlier version of this
    # script reported a green `lake build` while the module in question was a
    # one-line `import Mathlib`.  Compile the byte-identical copy directly.
    rc, out, err = run_lean(lake, project, work)
    diagnostics = (out + err).strip()
    if rc != 0 or diagnostics:
        # `lake env lean` prints warnings on stderr; any diagnostic at all is
        # reported, and a hole is a hard failure.
        holes = [m for m in LEAN_FAILURE_MARKERS if m in diagnostics]
        if holes:
            fail("kernel reported %s -- the file has an unproved declaration"
                 % ", ".join(repr(h) for h in holes))
        else:
            fail("compiling the file produced diagnostics (exit %d)" % rc)
        if diagnostics:
            print("  " + diagnostics[:2000].replace("\n", "\n  "))
        return 1
    ok("kernel compiled the file with no diagnostics and no holes "
       "(Mathlib %s @ %s, Lean toolchain %s)"
       % (MATHLIB_TAG, rev[:12], LEAN_TOOLCHAIN.split(":")[-1]))

    proc = subprocess.run([lake, "env", "lean", axfile], cwd=project,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout[-4000:])
        sys.stderr.write(proc.stderr[-4000:])
        fail("footprint check failed to run")
        return 1

    found = re.findall(r"'OMEGA\.(\w+)' depends on axioms: \[([^\]]*)\]",
                       proc.stdout)
    print("")
    print("  axiom footprint, %d theorems:" % len(found))
    drift = False
    for name, axioms_text in found:
        mark = "  "
        if axioms_text != EXPECTED_AXIOMS.strip("[]"):
            mark = "!!"
            drift = True
        print("  %s %-34s [%s]" % (mark, name, axioms_text))
    if len(found) != len(THEOREMS):
        fail("footprint printed for %d theorems, expected %d"
             % (len(found), len(THEOREMS)))
        return 1
    if drift:
        fail("axiom footprint drifted from the 2026-10-02 control")
        return 1
    ok("footprint matches the 2026-10-02 control on all %d theorems"
       % len(THEOREMS))

    if temp and not args.keep:
        shutil.rmtree(temp, ignore_errors=True)
    else:
        print("")
        print("project kept at %s" % project)

    print("")
    print("TRACKC_RECOMPILE: PASS -- compiled, zero sorry, footprint recorded")
    return 0


if __name__ == "__main__":
    sys.exit(main())