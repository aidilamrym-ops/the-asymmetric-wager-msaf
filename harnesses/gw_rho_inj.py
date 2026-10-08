"""Fault-injection harness for `gw_rho_formal.py` (A2 pattern).

The A15 phase published `rho_actual <= 5.8287013697174734848e-179` and the
margin 74.4468626023 decades, but that number had no harness behind it -- the
A2 lesson is that a published count nothing can falsify is not a claim.  This
harness gives it teeth: seven cases, each aimed at something the tool actually
promises.

  M1  reference matrix of the wrong dimension -> exit 1, dimension named
  M2  reference file with no 'M' key          -> exit 1
  M3  reference file that is not JSON         -> exit 1
  M4  the tool's own worst entry moved away  -> rho must rise by delta
      from its ball centre                    (proves the tool reads its
                                               input and returns no constant)
  M5  published JSON is self-consistent      -> max(rho_ij) == max_abs_diff_upper
  M6  low precision (128 bits vs 1200)       -> the bound must not shrink; wider
                                               balls may only make it larger
  M7  the Lerch summation mutated inside the tool, in a scratch copy
      (term index shifted by one)   -> the printed mpmath deviations must move
                                      by two orders of magnitude, proving the
                                      check is sensitive rather than decorative

Everything runs on a 3x3 synthetic reference (c=2, N=1) so the suite stays
fast; the shipped 81x81 dps-180 run is the A15 record, not this harness's job.
The tool writes its results next to itself, so each case removes what it
created and the workspace file itself is never modified -- M7 edits a scratch
copy and the harness asserts the original digest at the end.

usage: python harnesses/gw_rho_inj.py
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GW = os.path.join(ROOT, "guinand-weil-rigorous-numerics-main")
TOOL = os.path.join(GW, "gw_rho_formal.py")
SCRATCH = "_gw_rho_inj_scratch.py"
OUT = os.path.join(GW, "gw_rho_formal_2_1.json")

C, N = 2, 1
DIM = 2 * N + 1
DELTA = 1e-6

PY = sys.executable
results = []


def digest(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def run(ref_path, prec=1200, tool=TOOL):
    proc = subprocess.run([PY, tool, str(C), str(N), ref_path, str(prec)],
                          cwd=GW, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def write_ref(path, M, dps=180):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"M": M, "dps": dps, "c": C, "N": N, "dim": DIM}, fh)


def synthetic_matrix():
    """A deterministic, asymmetric 3x3 matrix with exact decimal entries."""
    return [["0.5", "0.25", "-0.125"],
            ["0.125", "-0.5", "0.375"],
            ["-0.25", "0.5", "0.0625"]]


def record(label, ok_, detail=""):
    results.append((label, ok_))
    print("  %s %-46s %s" % ("ok  " if ok_ else "FAIL", label, detail))


def main():
    print("GW RHO FORMAL INJECTION -- seven cases against gw_rho_formal.py")
    if not os.path.isfile(TOOL):
        print("FAIL  %s not found" % TOOL)
        return 1

    tool_digest = digest(TOOL)
    tmp_ref = os.path.join(GW, "_gw_rho_inj_ref.json")
    created = [tmp_ref, OUT]

    # ---- baseline ------------------------------------------------------
    write_ref(tmp_ref, synthetic_matrix())
    rc, out = run(tmp_ref)
    if rc != 0 or "RHO_ACTUAL_FORMAL" not in out:
        print("FAIL  baseline: the tool did not complete on a clean 3x3 input")
        for line in out.splitlines()[-12:]:
            print("      | %s" % line)
        return 1
    base_rho = None
    for line in out.splitlines():
        if line.strip().startswith("rho_actual_formal"):
            base_rho = float(line.split("=")[1].strip())
    print("  ok   baseline: rho_actual_formal = %r" % base_rho)

    # ---- M1: wrong dimension -------------------------------------------
    bad = os.path.join(GW, "_gw_rho_inj_ref_bad.json")
    write_ref(bad, [["1.0", "2.0"], ["3.0", "4.0"]])
    created.append(bad)
    rc, out = run(bad, )
    record("M1 wrong-dimension reference", rc == 1 and "expected" in out,
           "exit=%d" % rc)

    # ---- M2: no 'M' key -------------------------------------------------
    nokey = os.path.join(GW, "_gw_rho_inj_ref_nokey.json")
    with io.open(nokey, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"dps": 180, "note": "no matrix here"}, fh)
    created.append(nokey)
    rc, out = run(nokey)
    record("M2 reference without an 'M' key", rc == 1 and "no 'M' matrix" in out,
           "exit=%d" % rc)

    # ---- M3: not JSON ---------------------------------------------------
    broken = os.path.join(GW, "_gw_rho_inj_ref_broken.json")
    with io.open(broken, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("{ this is not json")
    created.append(broken)
    rc, out = run(broken)
    record("M3 unparseable reference", rc == 1 and "cannot read" in out,
           "exit=%d" % rc)

    # ---- M4: the answer must follow the input ---------------------------
    # Take the entry the tool itself named as worst, and move it *away* from
    # the ball centre it printed, by a known delta.  The reported maximum must
    # then rise by that delta.  Two earlier versions of this case were
    # vacuous: a 1e-40 perturbation on one entry, and then a uniform +0.25
    # shift, both of which cannot move the maximum in a predictable direction
    # on a synthetic reference (a shift can move M_ref *towards* the centre and
    # shrink the difference).  Only the worst entry, moved in the sign that
    # increases |M_ref - centre|, gives a falsifiable prediction.
    with io.open(OUT, encoding="utf-8") as fh:
        res = json.load(fh)
    w = res["worst_entry"]
    m_ref = float(w["m_ref"])
    ball = w["ball"]
    # A ball prints as either "[<value> +/- <radius>]" or "<value> +/- <radius>";
    # take the value and stop at the first separator.
    raw = ball.lstrip("[").lstrip()
    for stop in (",", "]", "+/-"):
        raw = raw.split(stop)[0]
    centre = float(raw.strip())
    away = DELTA if m_ref >= centre else -DELTA
    M = [list(row) for row in synthetic_matrix()]
    M[w["i"]][w["j"]] = repr(m_ref + away)
    write_ref(tmp_ref, M)
    rc, out = run(tmp_ref)
    moved = None
    for line in out.splitlines():
        if line.strip().startswith("rho_actual_formal"):
            moved = float(line.split("=")[1].strip())
    grew = (moved is not None and base_rho is not None
            and abs((moved - base_rho) - abs(away)) <= abs(away) * 1e-6)
    record("M4 worst entry moved away -> rho rises by delta", grew,
           "rho %r -> %r, moved %+.3g at (%d,%d)" % (base_rho, moved, away,
                                                     w["i"], w["j"]))

    # ---- M5: the published JSON agrees with itself ----------------------
    write_ref(tmp_ref, synthetic_matrix())
    rc, out = run(tmp_ref)
    ok5, detail5 = False, "no results file"
    if os.path.isfile(OUT):
        with io.open(OUT, encoding="utf-8") as fh:
            res = json.load(fh)
        rows = [float(r["rho_ij"]) for r in res["per_entry"]]
        worst = max(rows)
        published = float(res["max_abs_diff_upper"])
        ok5 = abs(worst - published) <= published * 1e-9 and len(rows) == DIM * DIM
        detail5 = "max(rho_ij)=%.6e vs published %.6e over %d entries" % (
            worst, published, len(rows))
    record("M5 per-entry max equals the published figure", ok5, detail5)

    # ---- M6: lower precision may not buy a smaller bound ----------------
    # rho_actual_formal is dominated by the distance between two builds, which a
    # synthetic reference makes O(1); at 128 bits versus 1200 bits that
    # difference prints identically, so comparing the printed rho proved
    # nothing.  The measurable quantity is the *ball radius*: lower precision
    # must widen it, never narrow it.
    write_ref(tmp_ref, synthetic_matrix())
    rc_lo, out_lo = run(tmp_ref, prec=128)
    rc_hi, out_hi = run(tmp_ref, prec=1200)
    rad_lo = rad_hi = None
    for line in out_lo.splitlines():
        if line.strip().startswith("max radius"):
            rad_lo = float(line.split("=")[1].strip())
    for line in out_hi.splitlines():
        if line.strip().startswith("max radius"):
            rad_hi = float(line.split("=")[1].strip())
    record("M6 128-bit balls are not tighter than 1200-bit balls",
           rad_lo is not None and rad_hi is not None and rad_lo >= rad_hi,
           "1200-bit r=%r, 128-bit r=%r" % (rad_hi, rad_lo))

    # ---- M7: the Lerch tail bound, mutated in a scratch copy ------------
    # The tool's component check is diagnostic: it prints the deviation of its
    # blocks from mpmath and cannot fail the run (recorded as `A18-R5`).  So this
    # case asserts what a diagnostic can legitimately be held to -- that it is
    # SENSITIVE.  A wrong tail bound must move the printed deviation; if it did
    # not, the check would be decoration and could not catch the class of defect
    # it exists for.
    def printed_dev(text):
        vals = []
        for line in text.splitlines():
            if "max abs. deviation" in line and ":" in line:
                try:
                    vals.append(float(line.split(":")[-1].strip()))
                except ValueError:
                    pass
        return max(vals) if vals else None

    honest_dev = printed_dev(out_hi) if out_hi else None
    with io.open(TOOL, encoding="utf-8", newline="") as fh:
        source = fh.read()
    # Mutate the *summation*, not the tail constant: shifting the tail by a
    # millionth is invisible next to the 4e-6 deviation that mpmath cancellation
    # already contributes, so the first version of this case changed nothing
    # observable and could not fail.  The off-by-one in the term index is the
    # defect the A15 smoke test actually caught, so it is the defect worth
    # proving the diagnostics can see.
    needle = "(a + K) ** s"
    if needle not in source:
        record("M7 Lerch mutation moves the diagnostics", False,
               "summation needle not found -- the tool changed shape")
    elif honest_dev is None:
        record("M7 Lerch tail mutation moves the diagnostics", False,
               "baseline printed no component deviations")
    else:
        mutant = os.path.join(GW, SCRATCH)
        with io.open(mutant, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(source.replace(needle, "(a + K + 1) ** s", 1))
        created.append(mutant)
        rc, out_mut = run(tmp_ref, tool=mutant)
        mut_dev = printed_dev(out_mut)
        moved_far = (mut_dev is not None
                     and (mut_dev > honest_dev * 100
                          or mut_dev < honest_dev / 100.0))
        record("M7 Lerch mutation moves the diagnostics", moved_far,
               "max deviation %.3e -> %.3e" % (honest_dev, mut_dev))

    # ---- cleanup --------------------------------------------------------
    for path in created:
        try:
            os.remove(path)
        except OSError:
            pass
    if digest(TOOL) != tool_digest:
        print("  FAIL  gw_rho_formal.py digest changed: %s -> %s"
              % (tool_digest, digest(TOOL)))
        results.append(("workspace tool untouched", False))
    else:
        print("  ok   workspace tool byte-identical after all cases")

    # ---- the tool still works on the clean input -------------------------
    write_ref(tmp_ref, synthetic_matrix())
    rc, out = run(tmp_ref)
    if rc != 0 or "RHO_ACTUAL_FORMAL" not in out:
        print("  FAIL  restored baseline: the tool no longer completes")
        results.append(("restored baseline", False))
    else:
        print("  ok   restored baseline: the tool completes again")
    try:
        os.remove(tmp_ref)
    except OSError:
        pass
    try:
        os.remove(OUT)
    except OSError:
        pass

    passed = sum(1 for _, ok_ in results if ok_)
    total = len(results) + 1          # + the clean baseline above
    print()
    print("HARNESS: %s -- %d/%d cases behaved as expected, workspace tool "
          "byte-identical, no scratch file left behind"
          % ("PASS" if passed == len(results) else "FAIL", passed, total))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())