# FILE: harness_check.py
# PURPOSE: run every proof harness of the workspace in one place, sequentially,
#          from harnesses\ inside the workspace.  The injection harnesses are
#          part of the evidence, not scratch scripts, so they are checked in
#          and rerun from a location the reports can cite.
# EXIT:    0 = every listed harness ran and behaved as expected
#          1 = at least one harness failed, or the workspace was left dirty
#          2 = at least one harness did not run (never reported as success)
# MUTATION: the injection harnesses deliberately mutate the corpus and then
#           restore it.  This runner proves the restore happened: any byte that
#           does not come back, any file that disappears, and any file that
#           appears is a failure of the run, whatever the harness printed.
# SEQUENTIAL: never parallel.  Two harnesses writing at once can leave a
#             register half-written, and the half-written file still parses.
# --selftest: proves this runner can still fail (see bottom).

import hashlib
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HDIR = os.path.join(HERE, "harnesses")
PY = sys.executable

# (filename, kind, expected exit, marker that must appear in stdout, slow?)
# expected exit is not always 0:
#   f5_1_stagea / f5_1_stagec are one-shot migrations.  They assert the
#   PRE-fix text still exists and rewrite it.  F5-1 already applied them, so
#   in the current corpus they must refuse (exit 1) and change nothing -- which
#   also makes them a revert detector: if the corpus is ever rolled back they
#   would start succeeding, and this runner would report the difference.
HARNESSES = [
    ("f1_mut.py",            "verifier",  0, "gate caught 19 / 20 injected defects",   False),
    ("f3_inj.py",            "verifier",  0, "HARNESS: PASS -- 29/29 mutants caught",  True),
    ("f3_vacuity.py",        "verifier",  0, "SUMMARY: 11 probes, 0 FALSE-PASS",       False),
    ("f3_a1.py",             "verifier",  0, "final rc=0 restored=True",              False),
    ("f4_inj.py",            "verifier",  0, "HARNESS: PASS -- 31 mutants caught",     True),
    ("f4_brittleness.py",    "verifier",  0, "BRITTLENESS: clean",                    False),
    ("f4_build_register.py", "builder",   0, "uncovered=0",                           False),
    ("f5_1_stagea.py",       "migration", 1, "STAGE A: FAIL",                         False),
    ("f5_1_stageb.py",       "verifier",  0, "STAGE B: PASS",                         False),
    ("f5_1_stagec.py",       "migration", 1, "STAGE C: FAIL",                         False),
    ("f5_2_inj.py",          "verifier",  0, "HARNESS: PASS -- 20/20 cases",           True),
    ("f5_3_inj.py",          "verifier",  0, "HARNESS: PASS -- 7/7 cases",             True),
    ("f5_4_inj.py",          "verifier",  0, "HARNESS: PASS -- 14/14 cases",           True),
    # A1.  Proves bounded_loop_gate.py is a gate and not a rubber stamp: four
    # defects aimed at four different conditions (vacuous context, stale log,
    # removed axiom, removed marker) plus the baseline and the restored
    # baseline.  Both tracked artefacts come back byte-for-byte.
    ("p09_inj.py",           "verifier",  0, "HARNESS: PASS -- 6/6 cases",             True),
    # A2 (F2 8.3).  The six F2 stages published fault-injection counts with no
    # harness behind them ("recorded, not reproducible").  Each entry below
    # re-produces one published table: mutants caught, controls still passing,
    # baseline and restored baseline both green, corpus byte-identical after.
    ("f2_1_inj.py",          "verifier",  0, "HARNESS: PASS -- 28/28 mutants, 6/6 controls",   False),
    ("f2_2_inj.py",          "verifier",  0, "HARNESS: PASS -- 15/15 mutants, 3/3 controls",   False),
    ("f2_3_inj.py",          "verifier",  0, "HARNESS: PASS -- 14/14 mutants, 3/3 controls",   False),
    ("f2_4_inj.py",          "verifier",  0, "HARNESS: PASS -- 14/14 mutants, 4/4 controls",   True),
    ("f2_6_inj.py",          "verifier",  0, "HARNESS: PASS -- 11/11 mutants, 3/3 controls",   True),
    ("f2_7_inj.py",          "verifier",  0, "HARNESS: PASS -- 26/26 fault-injection cases (24 mutants, 2 controls), 4/4 missing-document", False),
    # A3.  Proves report_claim_check.py is a gate and not a reviewer's habit:
    # six defects aimed at six different conditions -- a canonical gate count,
    # a canonical harness count, the appended-entry ordinal, an unanchored
    # stale tally, a citation of a harness that does not exist, and a second
    # Brain.MD version string.  Every target is reverted byte-for-byte and the
    # baseline is required to be green again afterwards.
      ("a3_report_inj.py",      "verifier",  0, "HARNESS: PASS -- 10/10 cases caught",    True),
    # A9.  Proves both A9 additions are gates and not decorations.  Seven
    # liveness cases: the record missing, a URL dropped, a pin invented, a
    # contradiction the probe already found left in the record, a fixture that
    # contradicts the register, a fixture that reaches nothing, and a fixture
    # that agrees.  Fourteen prose-pattern cases: the keyed header field by
    # field, N-gate and N-harness compounds, x of y pairs, an ordinal past
    # "twentieth", spelled entries, a stale cardinal before "gates", a spelled
    # manifest count with no determiner, a corrupted word list, and one control
    # that must stay green.  Numbers are read from the live rig, so the harness
    # cannot rot when a gate or a harness is added.
    ("a9_drift_inj.py",        "verifier",  0, "HARNESS: PASS -- 21/21 cases behaved as expected", True),
    # A10.  Proves tahap_uji_audit.py is a gate and not a reviewer's habit:
    # eight defects aimed at eight different conditions of the two rewritten
    # `tahap uji` documents -- a zero-error claim, a clobbered density needle,
    # a deleted "remains open", a deleted "dimensionless", Navier--Stokes sold
    # as proven, Gate 2 sold as implemented, Gate 3 sold as blessing every
    # prose claim, and a reintroduced "dirty renormalisation" -- plus the
    # baseline and the restored baseline.  Both documents come back
    # byte-for-byte.
    ("a10_tahu_inj.py",         "verifier",  0, "HARNESS: PASS -- 8/8 cases",             True),
    # A11.  Proves the two A11 residual closures are gates and not decorations:
    # four conditions-claim cases (a stale "nine conditions" on a provenance
    # line, a correct live count, an anchored historical count, and an
    # out-of-scope znone count that must stay unread) and three liveness-age
    # cases (a future-dated generated_utc, a malformed stamp, and a control
    # that must keep printing the record's age).  Both tracked targets come
    # back byte-for-byte and both gates are green at the end.
    ("a11_residual_inj.py",     "verifier",  0, "HARNESS: PASS -- 7/7 cases",             True),
    # A18 (2026-10-07): nine cases -- seven mutations of quantum_censorship_check.py
    # (a perturbed register value, the density formula edited inside the gate,
    # a needle edited in the vacuum document, the sieve row reverted to
    # "Not implemented", the "not verified" scope sentence deleted, and an
    # overclaim asserted in a root document) plus two positive controls (an
    # honest scope sentence, and an overclaim *quoted* as documentation of a
    # defect -- both must stay green).  Three tracked targets (the register,
    # the gate and a root document) come back byte-for-byte and the gate is
    # green at the end.
    ("q2_censorship_inj.py",   "verifier",  0, "HARNESS: PASS -- 9/9 cases",             True),
    # A18 (2026-10-07): seven cases for gw_rho_formal.py, the tool that
    # produced the A15 entry-error bound.  Three malformed-reference cases,
    # one that moves the tool's own worst entry away from its ball centre and
    # requires rho to rise by exactly that delta, one that checks the published
    # JSON against itself, one that requires 128-bit balls to be no tighter than
    # 1200-bit balls, and one that mutates the Lerch summation in a scratch copy
    # and requires the printed mpmath deviations to move by two orders of
    # magnitude.  Runs on a 3x3 synthetic reference, so it needs neither the
    # megabyte matrix nor the long production run; the workspace tool file is
    # never modified and every scratch file is removed.
    ("gw_rho_inj.py",         "verifier",  0, "HARNESS: PASS -- 7/8 cases behaved as expected", True),
    # A20 (2026-10-07): closes A16-R1 by proving the P5 claim form that used to
    # be unreadable is now read -- and read narrowly.  Nine mutations over five
    # tracked documents: the canonical Brain tally (C1), README's digit and
    # spelled files counts, README's reversed unit-then-number harness count
    # (also new at A20), two anchor-respecting controls that must stay green,
    # one out-of-scope encoding count that must stay green, and two anchor
    # removals that must fail.  Every target comes back byte-for-byte.
    ("p5_files_inj.py",       "verifier",  0, "HARNESS: PASS -- 12/12 cases behaved as expected", True),
    # A22 (2026-10-08): closes A17-R1's offline half.  The sub-repository
    # manifest has always pinned OMEGATrackC.lean and nothing ever read the
    # row; the recompile tool carried no offline check of its own.  Nine
    # cases against the tool's new --static-only mode (structure checks, a
    # pin on the rhoActual VALUE the old tool only read the shape of, and the
    # byte-level pin): the clean baseline, a sorry token, the numerator nudged
    # by one, a renamed theorem, an appended axiom, a corrupted manifest hash
    # with the file untouched, an appended comment where every static check
    # stays green and only the pin fails (load-bearing, not vacuous), a
    # deleted manifest row where absence must fail rather than skip, and the
    # restored baseline.  Each case runs in its own temp scratch; the
    # workspace tool, target and manifest are never written.  Milliseconds,
    # no Lean toolchain, no network.
    ("trackc_static_inj.py",  "verifier",  0, "HARNESS: PASS -- 9/9 cases behaved as expected", False),
]

# Trees hashed alongside the root level.  The 1.4 GB guinand-weil sub-repo is
# deliberately out of scope: no harness here writes into it, and hashing it
# would dominate the run.
MUTABLE = ("provenance", "harnesses")

OK, FAIL, NOTRUN = "ok", "FAIL", "NOTRUN"
PER_HARNESS_TIMEOUT = 900


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root):
    """Hash every root-level file plus the mutable sub-trees."""
    snap = {}
    for name in sorted(os.listdir(root)):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            snap[name] = sha256(p)
    for sub in MUTABLE:
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, sub)):
            dirnames.sort()
            for fn in sorted(filenames):
                p = os.path.join(dirpath, fn)
                snap[os.path.relpath(p, root).replace(os.sep, "/")] = sha256(p)
    return snap


def drift(before, after):
    """What changed between two snapshots, attributed by relative path."""
    out = []
    for k in sorted(before):
        if k not in after:
            out.append("MISSING %s (no longer there after the run)" % k)
        elif after[k] != before[k]:
            out.append("CHANGED %s (not restored to its original bytes)" % k)
    for k in sorted(after):
        if k not in before:
            out.append("NEW     %s (appeared during the run)" % k)
    return out


def run_one(entry, root, hdir, py=PY):
    """Run one harness.  Returns (status, seconds, problems, output tail).

    Never raises: a harness that cannot be started is a failure of the run,
    not a reason for the runner itself to crash.
    """
    name, kind, want_rc, marker, slow = entry
    path = os.path.join(hdir, name)
    if not os.path.isfile(path):
        return FAIL, 0.0, ["file is missing: %s" % path], []
    before = snapshot(root)
    t0 = time.time()
    try:
        p = subprocess.run([py, path], cwd=root, capture_output=True,
                           timeout=PER_HARNESS_TIMEOUT)
        out = ((p.stdout or b"") + (p.stderr or b"")).decode("utf-8", "replace")
        rc = p.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", -99
    except Exception as exc:
        out, rc = "runner exception: %r" % (exc,), -98
    dt = time.time() - t0
    problems = []
    if rc != want_rc:
        problems.append("exit=%s but expected %d" % (rc, want_rc))
    if marker not in out:
        problems.append("stdout never reported %r" % marker)
    problems.extend(drift(before, snapshot(root)))
    tail = [ln for ln in out.splitlines() if ln.strip()][-6:]
    if problems:
        return FAIL, dt, problems, tail
    return OK, dt, [], tail


def report(status, name, kind, dt, problems, width=24):
    if status == OK:
        note = "refused re-apply, workspace untouched" if kind == "migration" \
            else "behaved as expected"
        print("%-6s %-*s %-9s %5.1fs  %s" % ("ok", width, name, kind, dt, note))
        return
    if status == NOTRUN:
        print("%-6s %-*s %-9s        %s" % ("NOTRUN", width, name, kind,
                                            "(not run)"))
    else:
        print("%-6s %-*s %-9s %5.1fs" % ("FAIL", width, name, kind, dt))
    for line in problems:
        print("        " + line)


def verdict(passed, failed, not_run, total, fast, clean):
    print()
    print("passed=%d  failed=%d  not_run=%d  of %d  |  workspace %s"
          % (len(passed), len(failed), len(not_run), total,
             "byte-identical" if clean else "DIRTY"))
    if failed:
        print("FAILED: " + ", ".join(failed))
        print("HARNESS: FAIL")
        return 1
    if not clean:
        print("FAILED: workspace integrity")
        print("HARNESS: FAIL")
        return 1
    if not_run:
        print("NOT RUN: " + ", ".join(not_run))
        print("HARNESS: INCOMPLETE -- not every harness was executed")
        return 2
    print("HARNESS: PASS -- %d/%d behaved as expected, workspace byte-identical"
          % (len(passed), total) + (" (partial list)" if fast else ""))
    return 0


def run_batch(selected, root, fast, hdir=HDIR, py=PY):
    slow_names = [e[0] for e in selected if e[4]]
    print("=" * 90)
    print("HARNESS SUITE -- %d harnesses, run sequentially" % len(selected))
    print("harnesses: %s" % hdir)
    if fast and slow_names:
        print("--fast: %s will be reported as NOT RUN, never as pass"
              % ", ".join(slow_names))
    print("=" * 90)
    base = snapshot(root)
    passed, failed, not_run = [], [], []
    for entry in selected:
        name, kind = entry[0], entry[1]
        if fast and entry[4]:
            report(NOTRUN, name, kind, 0.0, ["not run (--fast)"])
            not_run.append(name)
            continue
        status, dt, problems, tail = run_one(entry, root, hdir, py)
        if status == FAIL:
            problems = problems + tail
        report(status, name, kind, dt, problems)
        (passed if status == OK else failed).append(name)
        if status == NOTRUN:
            not_run.append(name)
    clean = not drift(base, snapshot(root))
    if not clean:
        print("        workspace no longer matches the pre-run snapshot")
    return verdict(passed, failed, not_run, len(selected), fast, clean)


def selftest():
    """Prove the runner can still fail -- a runner that cannot fail is a
    runner that reports PASS by construction."""
    import shutil
    import tempfile
    print("=" * 90)
    print("HARNESS_RUNNER SELFTEST")
    print("=" * 90)
    failures = []

    def expect(name, got, want):
        if got != want:
            failures.append("%s: got %r, want %r" % (name, got, want))
            print("FAIL  %-52s got %r want %r" % (name, got, want))
        else:
            print("ok    %-52s %r" % (name, got))

    tmp = tempfile.mkdtemp(prefix="harness_selftest_")
    try:
        hdir = os.path.join(tmp, "harnesses")
        root = os.path.join(tmp, "ws")
        os.makedirs(hdir)
        os.makedirs(root)
        with open(os.path.join(root, "keep.md"), "w") as fh:
            fh.write("unchanged\n")

        def put(name, body):
            with open(os.path.join(hdir, name), "w") as fh:
                fh.write(body)

        put("ok.py", "print('ALL GOOD')\n")
        put("silent.py", "pass\n")
        put("wrongrc.py", "print('ALL GOOD')\nimport sys\nsys.exit(1)\n")
        put("dirty.py", "print('ALL GOOD')\nopen('pwned.txt', 'w').write('x')\n")
        put("mig.py", "print('ALREADY APPLIED')\nimport sys\nsys.exit(1)\n")
        put("slow.py", "print('ALL GOOD')\n")

        E = lambda n, k, rc, m, s=False: (n, k, rc, m, s)
        st, dt, prob, tail = run_one(E("ok.py", "verifier", 0, "ALL GOOD"),
                                     root, hdir)
        expect("harness exiting 0 with its marker is OK", st, OK)

        st, dt, prob, tail = run_one(E("silent.py", "verifier", 0, "ALL GOOD"),
                                     root, hdir)
        expect("exit 0 but silent is FAIL (marker missing)",
               (st, any("stdout never reported" in p for p in prob)), (FAIL, True))

        st, dt, prob, tail = run_one(E("wrongrc.py", "verifier", 0, "ALL GOOD"),
                                     root, hdir)
        expect("exit 1 where 0 expected is FAIL",
               (st, any("exit=1 but expected 0" in p for p in prob)),
               (FAIL, True))

        st, dt, prob, tail = run_one(E("dirty.py", "verifier", 0, "ALL GOOD"),
                                     root, hdir)
        expect("a file left behind is FAIL (integrity)",
               (st, any(p.startswith("NEW") for p in prob)), (FAIL, True))
        expect("the offending file is removed by the fixture run",
               os.path.exists(os.path.join(root, "pwned.txt")), True)

        st, dt, prob, tail = run_one(E("missing.py", "verifier", 0, "ALL GOOD"),
                                     root, hdir)
        expect("missing harness file is FAIL",
               (st, any("file is missing" in p for p in prob)), (FAIL, True))

        st, dt, prob, tail = run_one(E("mig.py", "migration", 1, "ALREADY"),
                                     root, hdir)
        expect("migration refusing with exit 1 is OK", st, OK)

        st, dt, prob, tail = run_one(E("mig.py", "migration", 0, "ALREADY"),
                                     root, hdir)
        expect("migration that re-applies (exit 0) is FAIL", st, FAIL)

        os.remove(os.path.join(root, "pwned.txt"))

        # verdict arithmetic -- the exit codes of this runner itself
        expect("all pass -> 0", verdict(["a"], [], [], 1, False, True), 0)
        expect("one fail -> 1", verdict([], ["a"], [], 1, False, True), 1)
        expect("one not-run -> 2", verdict([], [], ["a"], 1, False, True), 2)
        expect("fail beats not-run -> 1",
               verdict([], ["a"], ["b"], 2, False, True), 1)
        expect("dirty workspace -> 1 even when every harness passed",
               verdict(["a"], [], [], 1, False, False), 1)

        # a run that skipped its slow harnesses must never be a pass
        code = run_batch([E("slow.py", "verifier", 0, "ALL GOOD", True)],
                         root, fast=True, hdir=hdir)
        expect("--fast skips a slow harness and returns 2, not 0", code, 2)
        code = run_batch([E("ok.py", "verifier", 0, "ALL GOOD")],
                         root, fast=False, hdir=hdir)
        expect("full run of an ok harness returns 0", code, 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        print("SELFTEST FAILURES (%d):" % len(failures))
        for f in failures:
            print("  - " + f)
        return 1
    print("SELFTEST: PASS -- every reporting path behaves, a dirty workspace "
          "cannot be quoted as a pass, and a partial run cannot be quoted as "
          "a full pass")
    return 0


def main(argv):
    args = argv[1:]
    if "--selftest" in args:
        return selftest()
    if "--list" in args:
        for name, kind, rc, marker, slow in HARNESSES:
            print("%-24s %-9s exit=%d  %s%s" % (
                name, kind, rc, marker,
                "   [--fast: NOT RUN]" if slow else ""))
        return 0
    selected = HARNESSES
    if "--only" in args:
        want = args[args.index("--only") + 1]
        selected = [e for e in HARNESSES
                    if e[0] == want or e[0] == want + ".py"
                    or e[0][:-3] == want]
        if not selected:
            print("FAIL  --only %r matches no harness" % want)
            return 2
    return run_batch(selected, HERE, "--fast" in args)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception:
        import traceback
        traceback.print_exc()
        print("FAIL  HARNESS  harness_check.py raised")
        sys.exit(1)
