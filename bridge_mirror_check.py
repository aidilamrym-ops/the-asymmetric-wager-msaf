#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F2-4: the two registered MCP bridges must stay one file.

F0 residual #6 observed that `shp_asymmetric_wager` and `shp_bridge` read two
separate copies of ``shp_mcp_bridge_v4.py`` that are kept identical only by
hand, so "any future edit must be applied to both or routed through a single
source, otherwise one server silently reverts to the old contract."

This gate makes that hand-maintained property machine-checked:

  B1  opencode.jsonc parses and registers both servers
  B2  both registered script paths exist
  B3  both scripts are byte-identical            <- the residual's invariant
  B4  both carry the v4.2.0-PROOF-ONLY contract, the regression tests F0-4
      added, and neither reintroduces the removed simulation heuristic
  B5  the canonical server's write roots are all inside the workspace; the
      mirror's corpus root is checked for existence, and its write allowlist
      is reported whether or not it is declared (it is not enforced here --
      it belongs to a different server, and says so rather than passing)
  B6  `--test` passes on **both** copies

Both former deferrals are resolved: F2-5 repointed the mirror's
`SHP_MCP_CORPUS_ROOT` at a tree that exists, so B6 now runs the mirror's own
suite too.  The one remaining SKIP is the mirror's undeclared write allowlist,
recorded in F2_REPORT and explicitly not claimed.

Exit codes follow the Anti-Circularity Gate convention:
  0 = PASS, 1 = FAIL, 2 = TOOL NOT RUN.

Nothing here reports PASS on a tool that did not run: if the config or a
script cannot be read the verdict is TOOL NOT RUN, never PASS.
"""

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys

WORKSPACE = r"D:\THE ASYMMETRIC WAGER"
DEFAULT_CONFIG = r"C:\Users\usER\.config\opencode\opencode.jsonc"
CANONICAL_NAME = "shp_asymmetric_wager"
MIRROR_NAME = "shp_bridge"
PYTHON = sys.executable or r"C:\Python314\python.exe"

REQUIRED_MARKERS = (
    "v4.2.0-PROOF-ONLY",
    "PROOF-ONLY - NOT A SIMULATED",
    '"simulated": False',
    "[TEST 9] Testing PROOF-ONLY Refusal",
    "[TEST 10] Testing Fail-Closed Action",
)
FORBIDDEN_MARKERS = (
    "def _evaluate_simulated",
)

_results = []


def ok(msg):
    _results.append(("ok", msg))
    print("ok    " + msg)


def fail(msg):
    _results.append(("FAIL", msg))
    print("FAIL  " + msg)


def skip(msg):
    _results.append(("SKIP", msg))
    print("SKIP  " + msg)


def strip_json_comments(text):
    """Remove // and /* */ comments that are outside string literals."""
    out = []
    i, n, in_str, esc = 0, len(text), False, False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def load_config(path):
    try:
        raw = io.open(path, encoding="utf-8").read()
    except Exception as exc:
        return None, "cannot read %s: %s" % (path, exc)
    try:
        return json.loads(strip_json_comments(raw)), None
    except Exception as exc:
        return None, "cannot parse %s as JSONC: %s" % (path, exc)


def registration(cfg, name):
    mcp = cfg.get("mcp") or cfg.get("mcpServers") or {}
    return mcp.get(name)


def script_path(reg):
    if not isinstance(reg, dict):
        return None
    cmd = reg.get("command") or []
    if isinstance(cmd, str):
        cmd = cmd.split()
    for tok in cmd:
        if tok.endswith("shp_mcp_bridge_v4.py"):
            return tok
    return None


def env_of(reg, key):
    if not isinstance(reg, dict):
        return None
    env = reg.get("environment") or reg.get("env") or {}
    return env.get(key)


def inside_workspace(path):
    try:
        return os.path.normcase(os.path.abspath(path)).startswith(
            os.path.normcase(os.path.abspath(WORKSPACE)))
    except Exception:
        return False


def run_test(script, corpus_root, write_roots, timeout=180):
    env = dict(os.environ)
    for key in ("SHP_MCP_CORPUS_ROOT", "SHP_MCP_WRITE_ROOTS"):
        env.pop(key, None)
    if corpus_root:
        env["SHP_MCP_CORPUS_ROOT"] = corpus_root
    if write_roots:
        env["SHP_MCP_WRITE_ROOTS"] = os.pathsep.join(write_roots)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.run([PYTHON, "-u", script, "--test"],
                              capture_output=True, text=True,
                              encoding="utf-8", errors="replace",
                              env=env, timeout=timeout)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except Exception as exc:
        return None, str(exc)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--bridge-a", default=None,
                    help="override the canonical script path")
    ap.add_argument("--bridge-b", default=None,
                    help="override the mirror script path")
    args = ap.parse_args(argv)

    del _results[:]
    print("F2-4 BRIDGE MIRROR CHECK -- one file, one contract\n")

    cfg, err = load_config(args.config)
    if cfg is None:
        fail("B1 " + err)
        print("\nGATE: TOOL NOT RUN -- configuration unavailable.")
        return 2

    reg_a, reg_b = registration(cfg, CANONICAL_NAME), registration(cfg, MIRROR_NAME)
    if not isinstance(reg_a, dict) or not isinstance(reg_b, dict):
        missing = [n for n, r in ((CANONICAL_NAME, reg_a), (MIRROR_NAME, reg_b))
                   if not isinstance(r, dict)]
        fail("B1 registration(s) missing from %s: %s"
             % (os.path.basename(args.config), ", ".join(missing)))
    else:
        ok("B1 %s and %s are both registered in %s"
           % (CANONICAL_NAME, MIRROR_NAME, os.path.basename(args.config)))

    path_a = args.bridge_a or script_path(reg_a)
    path_b = args.bridge_b or script_path(reg_b)

    print("\n-- B2 both registered scripts exist ------------------------------")
    avail = {"canonical": False, "mirror": False}
    for label, p in (("canonical", path_a), ("mirror", path_b)):
        if not p:
            fail("B2 %s registration does not name shp_mcp_bridge_v4.py" % label)
        elif not os.path.isfile(p):
            # Decidable: the registration points at nothing.  This is a
            # failure of B2's condition, not a tool that failed to run.
            fail("B2 %s script absent: %s" % (label, p))
        else:
            avail[label] = True
            ok("B2 %s script present: %s" % (label, p))

    if not all(avail.values()):
        skip("B3 byte-identity: not checkable while a copy is missing")
        skip("B4 contract: not checkable on a missing copy")
        skip("B6 --test: not checkable while a copy is missing")
        return finish()
    blob_a = blob_b = None
    try:
        blob_a = open(path_a, "rb").read()
        blob_b = open(path_b, "rb").read()
    except Exception as exc:
        fail("B3 cannot read both scripts: %s" % exc)
        print("\nGATE: TOOL NOT RUN -- script bytes unavailable.")
        return 2
    print("\n-- B3 the two copies are byte-identical --------------------------")
    sha_a = hashlib.sha256(blob_a).hexdigest()
    sha_b = hashlib.sha256(blob_b).hexdigest()
    if sha_a == sha_b:
        ok("B3 byte-identical, sha256 %s... (%d bytes)" % (sha_a[:16], len(blob_a)))
    else:
        fail("B3 the copies have drifted: %s vs %s"
             % (sha_a[:16], sha_b[:16]))
        fail("B3 F0 residual #6 has recurred -- one server now runs a "
             "different contract than the other")

    print("\n-- B4 the PROOF-ONLY contract survives in both -------------------")
    for label, p, blob in (("canonical", path_a, blob_a),
                           ("mirror", path_b, blob_b)):
        try:
            text = blob.decode("utf-8")
        except Exception as exc:
            fail("B4 %s is not UTF-8: %s" % (label, exc))
            continue
        absent = [m for m in REQUIRED_MARKERS if m not in text]
        present = [m for m in FORBIDDEN_MARKERS if m in text]
        if absent:
            fail("B4 %s is missing required contract text: %s"
                 % (label, "; ".join(absent)))
        elif present:
            fail("B4 %s reintroduces the removed simulation heuristic: %s"
                 % (label, "; ".join(present)))
        else:
            ok("B4 %s carries the full v4.2.0-PROOF-ONLY contract "
               "(%d markers, %d forbidden absent)"
               % (label, len(REQUIRED_MARKERS), len(FORBIDDEN_MARKERS)))

    print("\n-- B5 registration environment -----------------------------------")
    roots = env_of(reg_a, "SHP_MCP_WRITE_ROOTS")
    roots = [r for r in (roots or "").split(os.pathsep) if r]
    if not roots:
        fail("B5 %s declares no SHP_MCP_WRITE_ROOTS -- the workspace-write "
             "contract is gone from the registration" % CANONICAL_NAME)
    else:
        outside = [r for r in roots if not inside_workspace(r)]
        if outside:
            fail("B5 %s has write root(s) outside the workspace: %s"
                 % (CANONICAL_NAME, ", ".join(outside)))
        else:
            ok("B5 %s write roots are all inside the workspace: %s"
               % (CANONICAL_NAME, ", ".join(roots)))
    mirror_root = env_of(reg_b, "SHP_MCP_CORPUS_ROOT")
    if mirror_root and not os.path.isdir(mirror_root):
        # F2-5 established the correct value, so an absent root is now a
        # regression, not an open question.  It was a SKIP before F2-5 for
        # the same reason an unanswered question is not a failed one.
        fail("B5 mirror corpus root %r does not exist -- F2-5 repointed it at "
             "a real tree, so this registration has regressed" % mirror_root)
    elif not mirror_root:
        fail("B5 mirror declares no SHP_MCP_CORPUS_ROOT at all")
    else:
        ok("B5 mirror corpus root present: %r" % mirror_root)
    # Reported unconditionally, not only while the corpus root is missing: the
    # note used to disappear exactly when the server became usable, which is
    # when it matters most.  This allowlist belongs to a different server, so
    # F2-4 does not grade it -- but it must never be assumed to be confined.
    mroots = [r for r in (env_of(reg_b, "SHP_MCP_WRITE_ROOTS") or "")
              .split(os.pathsep) if r]
    if not mroots:
        skip("B5 mirror write allowlist is UNSET -- the bridge falls back to "
             "its built-in list, which is not confined to its corpus root. "
             "Out of scope for F2-4: recorded in F2_REPORT, not enforced, "
             "NOT passed")
    elif mirror_root:
        base = os.path.normcase(os.path.abspath(mirror_root))
        m_out = [r for r in mroots
                 if not os.path.normcase(os.path.abspath(r)).startswith(base)]
        if m_out:
            skip("B5 mirror write root(s) lie outside its corpus root: %s -- "
                 "out of scope for F2-4, recorded, NOT passed"
                 % ", ".join(m_out))
        else:
            ok("B5 mirror write roots are inside its corpus root: %s"
               % ", ".join(mroots))

    print("\n-- B6 both copies still run their own test suite -----------------")
    rc_a, out_a = run_test(path_a, env_of(reg_a, "SHP_MCP_CORPUS_ROOT"),
                           [r for r in (env_of(reg_a, "SHP_MCP_WRITE_ROOTS") or "")
                            .split(os.pathsep) if r])
    if rc_a is None:
        fail("B6 canonical --test could not be run: %s" % out_a[:200])
    elif rc_a == 0:
        ok("B6 canonical --test exit 0")
    else:
        tail = [l.strip() for l in out_a.splitlines() if l.strip()]
        fail("B6 canonical --test exit %d: %s" % (rc_a, tail[-1][:140] if tail else ""))
    if mirror_root and not os.path.isdir(mirror_root):
        skip("B6 mirror --test not run: its corpus root does not exist (B5 "
             "already failed on this). Byte-identity in B3 still means the "
             "mirror is the file that passed --test on the canonical side.")
    else:
        rc_b, out_b = run_test(path_b, mirror_root,
                               [r for r in (env_of(reg_b, "SHP_MCP_WRITE_ROOTS") or "")
                                .split(os.pathsep) if r])
        if rc_b is None:
            fail("B6 mirror --test could not be run: %s" % out_b[:200])
        elif rc_b == 0:
            ok("B6 mirror --test exit 0")
        else:
            tail = [l.strip() for l in out_b.splitlines() if l.strip()]
            fail("B6 mirror --test exit %d: %s" % (rc_b, tail[-1][:140] if tail else ""))

    return finish()


def finish():
    n_ok = sum(1 for k, _ in _results if k == "ok")
    n_fail = sum(1 for k, _ in _results if k == "FAIL")
    n_skip = sum(1 for k, _ in _results if k == "SKIP")
    print("\n%d ok, %d FAIL, %d SKIP" % (n_ok, n_fail, n_skip))
    if n_fail:
        print("GATE: FAIL -- the two bridge copies no longer hold one contract.")
        return 1
    print("GATE: PASS -- one file, one contract (%d conditions met; %d reported "
          "but deliberately not enforced -- see F2_REPORT)." % (n_ok, n_skip))
    return 0


if __name__ == "__main__":
    sys.exit(main())
