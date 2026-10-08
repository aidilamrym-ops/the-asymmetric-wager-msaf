# FILE: suite_check.py
# PURPOSE: run every gate of the workspace in one place, sequentially, so that
#          "the suite passed" can never mean "the ones I remembered to run".
# EXIT:    0 = every listed gate ran and returned 0
#          1 = at least one gate returned 1 (a definite failure)
#          2 = at least one gate did not run, or a gate returned 2
#              (TOOL NOT RUN is never reported as success)
# READ-ONLY: this runner never writes to the corpus.
# --with-harness: append harness_check.py as the sixteenth entry.  It is off
#          by default because the fifteen gates above are a read-only
#          contract, while the injection harnesses mutate the corpus and
#          restore it -- that difference must stay visible in the invocation,
#          not hidden in a default.  The flag is forwarded, so --fast reaches
#          the harness runner too.
# --selftest: proves this runner can still fail (see bottom).

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GW = os.path.join(HERE, "guinand-weil-rigorous-numerics-main")
HARNESS_RUNNER = os.path.join(HERE, "harness_check.py")
PY = sys.executable

# (label, program path, argv, approx seconds)
# gw_final_gate.py takes ~23 minutes; its five arguments are the documented
# invocation recorded in F4_REPORT.md R4.
GATES = [
    ("landauer_check.py",           os.path.join(HERE, "landauer_check.py"),           [],          60),
    ("znone_check.py",              os.path.join(HERE, "znone_check.py"),              [],          60),
    ("msaf_zeta_check.py",          os.path.join(HERE, "msaf_zeta_check.py"),          [],         120),
    ("provenance_check.py",         os.path.join(HERE, "provenance_check.py"),         [],          60),
    ("visual_check.py",             os.path.join(HERE, "visual_check.py"),             [],         180),
    ("bridge_mirror_check.py",      os.path.join(HERE, "bridge_mirror_check.py"),      [],          60),
    ("theorem_provenance_check.py", os.path.join(HERE, "theorem_provenance_check.py"), [],          60),
    ("gw_mont_pipeline_check.py",   os.path.join(GW, "gw_mont_pipeline_check.py"),     [],         600),
    ("gw_verify_production.py",     os.path.join(GW, "gw_verify_production.py"),       [],         300),
    ("gw_verify_results.py",        os.path.join(GW, "gw_verify_results.py"),          [],         300),
    ("gw_final_gate.py",            os.path.join(GW, "gw_final_gate.py"),
     ["100", "40", "160", "1000.0", "224"], 1500),
    # The encoding of Phi (F0 residual 1, A1; renamed A12): Protocol 09 as a finite-state
    # machine, proven as QF_LIA rather than asserted in prose.  Eight
    # conditions, all recomputed -- the script must be unsat, the context
    # alone must be sat (so it is not vacuous), context + not-claim must be
    # sat (so the context refutes the claim rather than everything), each of
    # the three core axioms must be load-bearing, and the circularity auditor
    # must return GENUINE.  Its log is bound to the script by sha256, so a
    # stale log cannot vouch for edited bytes.  Placed immediately before the
    # manifest gate so that anything it wrote would still be caught.
    ("bounded_loop_gate.py",        os.path.join(HERE, "bounded_loop_gate.py"),       [],         120),
    # A18 (2026-10-07): Gate 2 of the sieve protocol, the part arithmetic can
    # decide -- the micro-scale boundary identities (omega_P * l_P = c, the
    # Planck mass by two routes, the zero-point density) recomputed from
    # external_constants.json at 100 dps, plus the document cross-check and
    # the overclaim guard that keeps "quantum censorship is proven" out of
    # every document.  Sits beside Gate 1 because it is Gate 1's sibling:
    # both read their numbers out of documents and recompute them.
    ("quantum_censorship_check.py", os.path.join(HERE, "quantum_censorship_check.py"), [], 120),
    # A10 (2026-10-07): honesty gate over the two `tahap uji` documents.
    # Reads every condition out of those documents and out of
    # external_constants.json / bounded_loop.log, recomputes the Planck-cutoff
    # vacuum density at 50 dps, and fails on the dishonesty classes the A10
    # audit found (zero-error claims, "dirty renormalisation", NS sold as
    # proven, Gate 3 misread as "all SAT").  Placed ahead of the prose gate
    # and the manifest gate so its own verdict is re-hashed afterwards.
    ("tahap_uji_audit.py",          os.path.join(HERE, "tahap_uji_audit.py"),         [],          60),
    # Reads the prose.  Every other gate checks an artefact; this one checks
    # the sentences that describe the artefacts, because a correct gate behind
    # a stale sentence still lets a reader quote the wrong number.  Placed
    # ahead of the manifest gate so that its own verdict is re-hashed afterwards.
    ("report_claim_check.py",       os.path.join(HERE, "report_claim_check.py"),      [],          60),
    # Deliberately last.  It re-hashes the workspace root against
    # CHECKSUM.sha256, so placing it after every other gate turns the manifest
    # from a baseline snapshot into a mutation detector across the whole run:
    # any gate that had written a tracked file would show up here rather than
    # being silently absorbed.  Closes F0 residual 4 / F5 residual F5-R6.
    ("checksum_check.py",           os.path.join(HERE, "checksum_check.py"),           [],          30),
]

SLOW = "gw_final_gate.py"
OK, FAIL, NOTRUN = "ok", "FAIL", "NOTRUN"


def run_gate(label, path, gargv, approx, py=PY):
    """Run one gate.  Returns (status, seconds, tail-of-output).

    Never raises: a gate that cannot be started is a failure of the suite, not
    a reason for the suite itself to crash.
    """
    if not os.path.isfile(path):
        return FAIL, 0, "file is missing: %s" % path
    t0 = time.time()
    try:
        p = subprocess.run([py, path] + list(gargv),
                           cwd=os.path.dirname(path) or ".",
                           capture_output=True, timeout=max(int(approx) * 3, 300))
        out = ((p.stdout or b"") + (p.stderr or b"")).decode("utf-8", "replace")
        rc = p.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", -99
    except Exception as exc:
        out, rc = "runner exception: %r" % (exc,), -98
    dt = int(time.time() - t0)
    tail = out.splitlines()[-8:]
    if rc == 0:
        return OK, dt, tail
    if rc == 2:
        return NOTRUN, dt, tail
    return FAIL, dt, ["exit=%s" % rc] + tail


def report(status, label, dt, detail, width=30):
    if status == OK:
        print("%-6s %-*s exit=0  %4ds" % ("ok", width, label, dt))
    elif status == NOTRUN:
        print("%-6s %-*s        %4ds  (tool not run)" % ("NOTRUN", width, label, dt))
        for line in detail:
            print("        " + line)
    else:
        print("%-6s %-*s        %4ds" % ("FAIL", width, label, dt))
        for line in detail:
            print("        " + line)


def verdict(passed, failed, not_run, total, fast):
    print()
    print("passed=%d  failed=%d  not_run=%d  of %d" % (len(passed), len(failed),
                                                       len(not_run), total))
    if failed:
        print("FAILED: " + ", ".join(failed))
        print("SUITE: FAIL")
        return 1
    if not_run:
        print("NOT RUN: " + ", ".join(not_run))
        print("SUITE: INCOMPLETE -- not every gate was executed")
        return 2
    print("SUITE: PASS -- every listed gate returned 0"
          + (" (partial list)" if fast else ""))
    return 0


def run_suite(selected, fast):
    print("=" * 90)
    print("WORKSPACE SUITE -- %d gates, run sequentially" % len(selected))
    if fast:
        print("--fast: %s will be reported as NOT RUN, never as pass" % SLOW)
    print("=" * 90)
    passed, failed, not_run = [], [], []
    for label, path, gargv, approx in selected:
        if fast and label == SLOW:
            report(NOTRUN, label, 0, ["not run (--fast)"])
            not_run.append(label)
            continue
        status, dt, detail = run_gate(label, path, gargv, approx)
        report(status, label, dt, detail)
        (passed if status == OK else failed if status == FAIL else not_run).append(label)
    return verdict(passed, failed, not_run, len(selected), fast)


def selftest():
    """Prove the reporting paths still work -- a runner that cannot fail is a
    runner that reports PASS by construction."""
    import tempfile
    print("=" * 90)
    print("SUITE_RUNNER SELFTEST")
    print("=" * 90)
    failures = []

    def expect(name, got, want, note=""):
        if got != want:
            failures.append("%s: got %r, want %r %s" % (name, got, want, note))
            print("FAIL  %-46s got %r want %r" % (name, got, want))
        else:
            print("ok    %-46s %r" % (name, got))

    tmp = tempfile.mkdtemp(prefix="suite_selftest_")
    ok_g = os.path.join(tmp, "g_ok.py")
    bad_g = os.path.join(tmp, "g_bad.py")
    nr_g = os.path.join(tmp, "g_notrun.py")
    miss = os.path.join(tmp, "g_absent.py")
    for path, code in ((ok_g, 0), (bad_g, 1), (nr_g, 2)):
        with open(path, "w") as fh:
            fh.write("import sys; sys.exit(%d)\n" % code)

    expect("gate returning 0 is OK", run_gate("ok", ok_g, [], 1)[0], OK)
    expect("gate returning 1 is FAIL", run_gate("bad", bad_g, [], 1)[0], FAIL)
    expect("gate returning 2 is NOTRUN", run_gate("nr", nr_g, [], 1)[0], NOTRUN)
    expect("missing gate file is FAIL", run_gate("missing", miss, [], 1)[0], FAIL)

    st, dt, detail = run_gate("bad", bad_g, [], 1)
    expect("FAIL carries the exit code in its detail",
           any("exit=1" in str(x) for x in detail), True)

    # verdict arithmetic -- the exit codes of the suite itself
    expect("all pass -> 0", verdict(["a"], [], [], 1, False), 0)
    expect("one fail -> 1", verdict([], ["a"], [], 1, False), 1)
    expect("one not-run -> 2", verdict([], [], ["a"], 1, False), 2)
    expect("fail beats not-run -> 1", verdict([], ["a"], ["b"], 2, False), 1)

    # a run that skipped its slow gate must never be reported as a pass
    code = run_suite([(SLOW, os.path.join(GW, SLOW), ["100"], 1)], fast=True)
    expect("--fast skips gw_final_gate and returns 2, not 0", code, 2)

    print()
    if failures:
        print("SELFTEST FAILURES (%d):" % len(failures))
        for f in failures:
            print("  - " + f)
        return 1
    print("SELFTEST: PASS -- every reporting path behaves, and a partial run "
          "cannot be quoted as a full pass")
    return 0


def main(argv):
    args = argv[1:]
    if "--selftest" in args:
        return selftest()
    fast = "--fast" in args
    with_harness = "--with-harness" in args
    # the harness runner is opt-in, and --fast must reach it or it would be
    # silently run in full while the suite reported a partial run
    pool = list(GATES)
    if with_harness:
        pool.append(("harness_check.py", HARNESS_RUNNER,
                     ["--fast"] if fast else [], 300))
    if "--list" in args:
        for label, path, a, sec in pool:
            print("%-32s %s %s" % (label, path, " ".join(a)))
        return 0
    selected = pool
    if "--only" in args:
        want = args[args.index("--only") + 1]
        selected = [g for g in pool if g[0] == want]
        if not selected:
            print("FAIL  --only %r matches no gate" % want)
            return 2
    if fast and not any(g[0] == SLOW for g in selected):
        # a --fast run that never touched the slow gate is not a partial run
        pass
    return run_suite(selected, fast)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception:
        import traceback
        traceback.print_exc()
        print("FAIL  HARNESS  suite_check.py raised")
        sys.exit(1)
