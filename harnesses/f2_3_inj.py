# FILE: harnesses/f2_3_inj.py
# PURPOSE: re-produce the F2-3 fault-injection counts for msaf_zeta_check.py.
#
# F2_REPORT 2.6 published 14/14 mutants and 3/3 controls but kept no harness
# (F2_REPORT 8.3).  This is that harness.
#
# The consumer (msaf_zeta_check.py) is run BEFORE the producer
# (zeta_pixel_producer.py) for every case, because the producer rewrites
# zeta_pixel_results.json unconditionally and would otherwise mask the whole
# artifact class.  A paper-claim mutant must fail BOTH gates; an artifact
# mutant must fail the consumer (the producer then regenerates a correct
# artifact, which is its job).  Both gates must exit 0 at the end.
#
# Exit codes: 0 = every case behaved as required and bytes restored
#             1 = a case was not caught, or a control stopped passing
#             2 = a tool or document the harness needs is missing

import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONSUMER = os.path.join(ROOT, "msaf_zeta_check.py")
PRODUCER = os.path.join(ROOT, "zeta_pixel_producer.py")
PY = sys.executable

DRAF = "DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md"
ARTIFACT = "zeta_pixel_results.json"

TARGET_MUTANTS = 14
TARGET_CONTROLS = 3

DELETE_FILE = "__DELETE_FILE__"
REINDENT = "__REINDENT__"

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL  %s" % msg)


def check(cond, msg):
    if not cond:
        fail(msg)
    return cond


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(proc):
    p = subprocess.run([PY, proc], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    return p.returncode


# --------------------------------------------------------------------------
# MUTANTS   (id, target file, needle, replacement[, count])
# CONTROLS  (id, target file, needle, replacement[, count], expected exit)
# The needle must be present before the mutation is applied.
# --------------------------------------------------------------------------
MUTANTS = [
    # --- paper claims -----------------------------------------------------
    # P1: |Delta zeta| moved one unit in its 7th significant figure
    ("P1", DRAF, "\\mathbf{1,456761 \\times 10^{-62}}$",
     "\\mathbf{1,456762 \\times 10^{-62}}$", 1),
    # P2: zeta(s_tergeser) real part moved one unit in its 7th sf
    ("P2", DRAF, "\\mathbf{1,438644 \\times 10^{-62}",
     "\\mathbf{1,438645 \\times 10^{-62}", 1),
    # P3: zeta(s_kritis) misrounded -- inside the 5 sf half-unit window
    ("P3", DRAF, "-6,1299 \\times 10^{-102}", "-6,1298 \\times 10^{-102}", 1),
    # P4: the |Delta zeta| claim deleted outright
    ("P4", DRAF,
     "*   Deviation Magnitude $|\\Delta\\zeta| = "
     "|\\zeta(s_{\\text{tergeser}}) - \\zeta(s_{\\text{kritis}})| "
     "\\approx \\mathbf{1,456761 \\times 10^{-62}}$\n", "", 1),

    # --- artifact ---------------------------------------------------------
    ("A1", ARTIFACT, DELETE_FILE, "", 1),
    ("A2", ARTIFACT, '"abs": "1.4567608138802497642477750106392022457372'
     '960339737e-62"',
     '"abs": "9.4567608138802497642477750106392022457372960339737e-62"', 1),
    ("A3", ARTIFACT, '"verdict": "PASS"', '"verdict": "FAIL"', 1),
    ("A4", ARTIFACT, '  "verdict": "PASS"\n}\n', '  "verdict": "PASS"\n', 1),
    ("A5", ARTIFACT, '"dps": 100,', '"dps": 50,', 1),
    ("A6", ARTIFACT, '"producer": "zeta_pixel_producer.py"',
     '"producer": "not_the_producer.py"', 1),
    ("A7", ARTIFACT,
     "14.1347251417346937904572519835624702707842571156992431756856",
     "14.1347251417346937904572519835624702707842571156992431756857", 1),
    ("A8", ARTIFACT,
     "-6.1298568645475636880359972673682941867518805033180e-102",
     "-9.1298568645475636880359972673682941867518805033180e-102", 1),
    ("A9", ARTIFACT,
     "1.4386442088496000836189224008166876391643010452394e-62",
     "1.4386442088496000836189224008166876391643010452395e-62", 1),
    ("A10", ARTIFACT,
     "14.1347251417346937904572519835624702707842571156992431756856",
     "14.13472514173469379045725198356247027078425711569924317568567", 1),
]

CONTROLS = [
    ("K1", ARTIFACT, '  "verdict": "PASS"',
     '  "unused_key": 42,\n  "verdict": "PASS"', 1, 0),
    ("K2", ARTIFACT, REINDENT, "", 1, 0),
    ("K3", DRAF,
     "A shift as small as $1\\ \\Delta_{\\text{univ}}$ immediately destroys "
     "the root orthogonality condition (the function value is no longer "
     "zero).",
     "A shift as small as $1\\ \\Delta_{\\text{univ}}$ immediately removes "
     "the root orthogonality condition (the function value stops being "
     "zero).", 1, 0),
]


def apply_case(path, orig, needle, replacement, count, cid):
    if needle == DELETE_FILE:
        os.remove(path)
        if os.path.isfile(path):
            fail("%s: could not delete %s" % (cid, os.path.basename(path)))
            return None
        return "deleted"
    text = orig.decode("utf-8")
    if needle == REINDENT:
        try:
            obj = json.loads(text)
        except Exception as exc:
            fail("%s: artifact is not readable JSON: %s" % (cid, exc))
            return None
        out = json.dumps(obj, indent=4, ensure_ascii=False) + "\n"
        if out == text:
            fail("%s: re-indent was a no-op" % cid)
            return None
        with io.open(path, "wb") as fh:
            fh.write(out.encode("utf-8"))
        return "reindented"
    if needle not in text:
        fail("%s: needle not present, so nothing was mutated: %r"
             % (cid, needle[:70]))
        return None
    mutated = text.replace(needle, replacement, count)
    if mutated == text:
        fail("%s: mutation was a no-op" % cid)
        return None
    with io.open(path, "wb") as fh:
        fh.write(mutated.encode("utf-8"))
    return mutated


def main():
    if not check(os.path.isfile(CONSUMER),
                 "missing consumer: %s" % CONSUMER):
        print("")
        print("HARNESS: FAIL -- consumer absent")
        return 1
    if not check(os.path.isfile(PRODUCER),
                 "missing producer: %s" % PRODUCER):
        print("")
        print("HARNESS: FAIL -- producer absent")
        return 1

    docs = {}
    for entry in MUTANTS + CONTROLS:
        fid = entry[1]
        path = os.path.join(ROOT, fid)
        if fid in docs:
            continue
        if not check(os.path.isfile(path), "missing document: %s" % fid):
            print("")
            print("HARNESS: FAIL -- document absent")
            return 1
        with io.open(path, "rb") as fh:
            docs[fid] = fh.read()

    rc_c = run(CONSUMER)
    rc_p = run(PRODUCER)
    check(rc_c == 0, "baseline: consumer must pass, got exit %d" % rc_c)
    check(rc_p == 0, "baseline: producer must pass, got exit %d" % rc_p)
    for fid, orig in docs.items():
        now = io.open(os.path.join(ROOT, fid), "rb").read()
        check(sha(orig) == sha(now),
              "baseline: %s must be byte-identical after a clean producer "
              "run" % fid)

    results = []
    try:
        for entry in MUTANTS + CONTROLS:
            cid, fid, needle, repl = entry[:4]
            want = entry[-1] if cid.startswith("K") else 1
            count = entry[4] if len(entry) > 4 else 1
            is_control = cid.startswith("K")
            path = os.path.join(ROOT, fid)
            orig = docs[fid]
            if apply_case(path, orig, needle, repl, count, cid) is None:
                results.append((cid, False, "not applied"))
                continue
            rc_c = run(CONSUMER)
            rc_p = run(PRODUCER)
            good = check(rc_c == want,
                         "%s: consumer must exit %d, got exit %d"
                         % (cid, want, rc_c))
            # A paper claim feeds both gates, so the producer must go red too.
            # An artifact mutant leaves the producer green: step 4 overwrites
            # the file unconditionally, which is exactly what the docstring of
            # msaf_zeta_check.py C9 says tamper detection is NOT the producer's
            # job.  The consumer is what has to catch it.
            want_p = want if fid == DRAF else 0
            good = check(rc_p == want_p,
                         "%s: producer must exit %d, got exit %d"
                         % (cid, want_p, rc_p)) and good
            results.append((cid, good, "consumer=%d producer=%d"
                            % (rc_c, rc_p)))
            for f, b in docs.items():
                with io.open(os.path.join(ROOT, f), "wb") as fh:
                    fh.write(b)
    finally:
        for fid, orig in docs.items():
            with io.open(os.path.join(ROOT, fid), "wb") as fh:
                fh.write(orig)

    rc_c = run(CONSUMER)
    rc_p = run(PRODUCER)
    check(rc_c == 0, "restored baseline: consumer must pass again, "
                     "got exit %d" % rc_c)
    check(rc_p == 0, "restored baseline: producer must pass again, "
                     "got exit %d" % rc_p)
    for fid, orig in docs.items():
        now = io.open(os.path.join(ROOT, fid), "rb").read()
        check(sha(orig) == sha(now), "%s left modified" % fid)

    mutants = [r for r in results if not r[0].startswith("K")]
    controls = [r for r in results if r[0].startswith("K")]
    m_ok = sum(1 for _, g, _ in mutants if g)
    c_ok = sum(1 for _, g, _ in controls if g)

    print("")
    for cid, good, note in results:
        print("  %s %s  %s" % ("ok  " if good else "FAIL  ", cid, note))
    print("")
    print("mutants  %d/%d   controls %d/%d"
          % (m_ok, len(mutants), c_ok, len(controls)))

    if failures:
        print("HARNESS: FAIL -- %d problem(s)" % len(failures))
        return 1
    if len(mutants) != TARGET_MUTANTS or len(controls) != TARGET_CONTROLS:
        print("HARNESS: FAIL -- expected %d/%d cases, table has %d/%d"
              % (TARGET_MUTANTS, TARGET_CONTROLS, len(mutants), len(controls)))
        return 1
    print("HARNESS: PASS -- %d/%d mutants, %d/%d controls"
          % (m_ok, TARGET_MUTANTS, c_ok, TARGET_CONTROLS))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print("FAIL  unexpected error: %s: %s" % (type(exc).__name__, exc))
        sys.exit(1)
