# FILE: harnesses/f2_4_inj.py
# PURPOSE: re-produce the F2-4 fault-injection counts for bridge_mirror_check.py.
#
# F2_REPORT 4.4 published 13 mutants and 4 controls; F2_REPORT 5.6 re-ran the
# suite after F2-5 at 14/14 (the original 13 plus M14) and 4/4 controls.  No
# harness was kept for it (F2_REPORT 8.3).  This is that harness.
#
# Two differences from the ad-hoc script the counts came from, both strictly
# stronger, recorded here rather than hidden:
#
#   * Config mutants are injected into a TEMP COPY of opencode.jsonc and
#     passed with --config.  The live registration file is never written.
#   * Bridge mutants are injected into TEMP COPIES of both bridge scripts and
#     passed with --bridge-a/--bridge-b.  The live servers are never written.
#     The gate conditions B2..B6 are exercised identically; only the file the
#     gate reads differs, and the override flags exist for exactly this.
#
# Structural config mutants are built by parsing and re-dumping JSON, not by
# string substitution (F2_REPORT 4.5 defect 2: single backslashes silently
# mutated nothing against JSON-escaped paths).
#
# Exit codes: 0 = every case behaved as required and bytes restored
#             1 = a case was not caught, or a control stopped passing
#             2 = a tool or document the harness needs is missing

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GATE = os.path.join(ROOT, "bridge_mirror_check.py")
PY = sys.executable

LIVE_CONFIG = r"C:\Users\usER\.config\opencode\opencode.jsonc"
LIVE_A = os.path.join(ROOT, "mcp", "shp_mcp_bridge_v4.py")
LIVE_B = r"C:\Users\usER\oracle-toe\GUINAND_WEIL\shp_mcp_bridge_v4.py"

WORK = os.path.join(os.environ.get("TEMP", os.getcwd()), "opencode", "f2_4")
CFG = os.path.join(WORK, "opencode.jsonc")
TA = os.path.join(WORK, "bridge_canonical.py")
TB = os.path.join(WORK, "bridge_mirror.py")

TARGET_MUTANTS = 14
TARGET_CONTROLS = 4

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


def rd(p):
    with io.open(p, "rb") as fh:
        return fh.read()


def wr(p, data):
    with io.open(p, "wb") as fh:
        fh.write(data)


def json_op(text, kind, needle, repl):
    obj = json.loads(text)
    if kind == "json_drop":
        cur = obj
        parts = needle.split(".")
        for p in parts[:-1]:
            cur = cur[p]
        del cur[parts[-1]]
    elif kind == "json_set":
        cur = obj
        parts = needle.split(".")
        for p in parts[:-1]:
            cur = cur[p]
        cur[parts[-1]] = json.loads(repl)
    elif kind == "json_rename":
        cur = obj
        parts = needle.split(".")
        for p in parts[:-1]:
            cur = cur[p]
        cur[repl] = cur.pop(parts[-1])
    elif kind == "json_corrupt":
        # drop the object's closing brace, not the trailing newline: a file
        # that still parses would be a control dressed as a mutant
        if text.endswith("}\n"):
            return text[:-2]
        return text[:-1]
    elif kind == "json_reindent":
        return json.dumps(obj, indent=4, ensure_ascii=False) + "\n"
    elif kind == "json_minify":
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    else:
        raise ValueError("unknown json op %r" % kind)
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------
# (id, target, kind, needle, replacement, count, expected exit)
#   target  cfg | A | B | AB
#   kind    text | delete | nonutf8 | json_drop | json_set | json_rename |
#           json_corrupt | json_reindent | json_minify
# --------------------------------------------------------------------------
MUTANTS = [
    # --- the registration ------------------------------------------------
    ("M1", "cfg", "json_rename", "mcp.shp_bridge", "shp_bridge_renamed", 1, 1),
    ("M2", "cfg", "json_set", "mcp.shp_asymmetric_wager.command",
     r'["C:\\Python314\\python.exe", "-u", '
     r'"D:\\THE ASYMMETRIC WAGER\\mcp\\shp_mcp_bridge_v4.py.missing"]',
     1, 1),
    ("M3", "cfg", "json_set",
     "mcp.shp_asymmetric_wager.environment.SHP_MCP_WRITE_ROOTS",
     r'"D:\\THE ASYMMETRIC WAGER;C:\\"', 1, 1),
    ("M4", "cfg", "json_drop",
     "mcp.shp_asymmetric_wager.environment.SHP_MCP_WRITE_ROOTS", "", 1, 1),
    ("M5", "cfg", "json_corrupt", "", "", 1, 2),
    # M14 -- the F2-5 regression guard (F2_REPORT 5.5)
    ("M14", "cfg", "json_set", "mcp.shp_bridge.environment.SHP_MCP_CORPUS_ROOT",
     r'"D:\\THE ASYMMETRIC WAGER\\no_such_tree"', 1, 1),

    # --- the copies ------------------------------------------------------
    ("M6", "A", "text", "\n",
     "# F2-4 harness: drift, canonical copy only\n", 1, 1),
    ("M7", "B", "text", "\n",
     "# F2-4 harness: drift, mirror copy only\n", 1, 1),
    ("M8", "AB", "text", "\n",
     "\n\ndef _evaluate_simulated():\n    return None\n", 1, 1),
    ("M9", "AB", "text", "v4.2.0-PROOF-ONLY", "", -1, 1),
    ("M10", "AB", "text", "[TEST 9] Testing PROOF-ONLY Refusal", "", -1, 1),
    ("M11", "B", "delete", "", "", 1, 1),
    ("M12", "A", "delete", "", "", 1, 1),
    ("M13", "A", "nonutf8", "", "", 1, 1),
]

CONTROLS = [
    ("K1", "cfg", "json_reindent", "", "", 1, 0),
    ("K2", "cfg", "json_minify", "", "", 1, 0),
    ("K3", "cfg", "text", "{\n",
     "{\n  // F2-4 harness control: a comment the gate does not read\n", 1, 0),
    ("K4", "AB", "text", "\n",
     "\n# F2-4 harness control: identical comment in both copies\n", 1, 0),
]


def target_paths(target, cfg_bytes, a_bytes, b_bytes):
    if target == "cfg":
        return [(CFG, cfg_bytes)]
    if target == "A":
        return [(TA, a_bytes)]
    if target == "B":
        return [(TB, b_bytes)]
    return [(TA, a_bytes), (TB, b_bytes)]


def apply_case(path, orig, kind, needle, repl, count, cid):
    if kind == "delete":
        if not os.path.isfile(path):
            fail("%s: target already absent" % cid)
            return False
        os.remove(path)
        return True
    if kind == "nonutf8":
        wr(path, orig + b"\xff\xfe")
        return True
    text = orig.decode("utf-8")
    if kind.startswith("json_"):
        try:
            out = json_op(text, kind, needle, repl)
        except Exception as exc:
            fail("%s: json op failed: %s: %s" % (cid, type(exc).__name__, exc))
            return False
        if out == text:
            fail("%s: json op was a no-op" % cid)
            return False
        wr(path, out.encode("utf-8"))
        return True
    if kind == "text":
        # M6/M7/K4 target the trailing newline: append, do not insert mid-file.
        if needle == "\n" and count == 1:
            out = text + repl
        elif needle not in text:
            fail("%s: needle not present: %r" % (cid, needle[:70]))
            return False
        else:
            out = text.replace(needle, repl, count)
        if out == text:
            fail("%s: mutation was a no-op" % cid)
            return False
        wr(path, out.encode("utf-8"))
        return True
    fail("%s: unknown kind %r" % (cid, kind))
    return False


def run_gate(args=()):
    cmd = [PY, "-u", GATE] + list(args)
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600)
    return p.returncode


def gate_with_temp(target="AB"):
    # A config mutant must be reached through the config, so the bridge
    # overrides are NOT passed for it -- otherwise --bridge-a would bypass the
    # registration entirely and the mutant would be invisible.
    args = ["--config", CFG]
    if target != "cfg":
        args += ["--bridge-a", TA, "--bridge-b", TB]
    return run_gate(args)


def main():
    if not check(os.path.isfile(GATE), "missing gate: %s" % GATE):
        print("")
        print("HARNESS: FAIL -- gate absent")
        return 1

    live = {}
    for p in (LIVE_CONFIG, LIVE_A, LIVE_B):
        if not check(os.path.isfile(p), "missing live file: %s" % p):
            print("")
            print("HARNESS: FAIL -- live file absent")
            return 1
        live[p] = rd(p)

    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    wr(CFG, live[LIVE_CONFIG])
    wr(TA, live[LIVE_A])
    wr(TB, live[LIVE_B])
    snap = {CFG: rd(CFG), TA: rd(TA), TB: rd(TB)}

    rc = run_gate()
    check(rc == 0, "baseline: live gate must pass, got exit %d" % rc)
    rc = gate_with_temp("cfg")
    check(rc == 0, "baseline: gate on the temp config must pass, "
                   "got exit %d" % rc)
    rc = gate_with_temp("AB")
    check(rc == 0, "baseline: gate on the temp bridge copies must pass, "
                   "got exit %d" % rc)

    results = []
    for entry in MUTANTS + CONTROLS:
        cid, target, kind, needle, repl, count, want = entry
        applied = []
        for path, orig in target_paths(target, snap[CFG], snap[TA], snap[TB]):
            if apply_case(path, orig, kind, needle, repl, count, cid):
                applied.append(path)
            else:
                applied = None
                break
        if applied is None:
            results.append((cid, False, "not applied"))
        else:
            rc = gate_with_temp(target)
            good = check(rc == want,
                         "%s: gate must exit %d, got exit %d"
                         % (cid, want, rc))
            results.append((cid, good, "exit %d want %d" % (rc, want)))
        for path, orig in snap.items():
            wr(path, orig)
            if rd(path) != orig:
                fail("%s: %s did not return to its original bytes"
                     % (cid, os.path.basename(path)))

    for p, orig in live.items():
        if rd(p) != orig:
            fail("live file was written: %s" % p)

    rc = gate_with_temp("cfg")
    check(rc == 0, "restored baseline: gate on the temp config must pass "
                   "again, got exit %d" % rc)
    rc = gate_with_temp("AB")
    check(rc == 0, "restored baseline: gate on the temp bridge copies must "
                   "pass again, got exit %d" % rc)
    rc = run_gate()
    check(rc == 0, "restored baseline: live gate must pass again, "
                   "got exit %d" % rc)
    for path, orig in snap.items():
        if rd(path) != orig:
            fail("temp file left modified: %s" % path)
    for p, orig in live.items():
        if rd(p) != orig:
            fail("live file left modified: %s" % p)

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

    shutil.rmtree(WORK, ignore_errors=True)

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
