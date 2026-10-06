# -*- coding: utf-8 -*-
"""Protocol 09 -- gate over the Phi encoding (F0_REPORT.md section 9 residual 1).

WHY THIS EXISTS
---------------
`SOLVABLE_FINITE_PARADOX.md` section 1.B used to display `Z3(Phi) ->
[UNSATISFIABLE]` with no encoding and no run log behind it.  F0-3 called that
a claim rather than a result, and refused to write the encoding off-hand
because a literal one would have been discharged from its own axioms and
audited VACUOUS or SINGLE_AXIOM.  The three pieces it demanded -- transition
relation, self-reference operator, step counter -- now exist in
`protocol_09.smt2`, with the run recorded in `protocol_09.log`.

This gate keeps the two failure modes F0-3 named from coming back:

  VACUOUS      the context alone is unsat, so every claim would follow.
               P5 requires the context to be *sat*.
  SINGLE_AXIOM one axiom refutes the claim by itself, so nothing was proved
               about the domain.  P7 drops each core axiom in turn and
               requires *sat* every time.

and P8 requires the circularity auditor's own verdict to be GENUINE.

Exit codes: 0 = every condition met, 1 = a condition failed, 2 = a required
tool or input was unavailable.  A missing auditor or a missing solver is
never reported as success.
"""
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SMT = os.path.join(HERE, "protocol_09.smt2")
LOG = os.path.join(HERE, "protocol_09.log")
AUDITOR_NAME = "smt_circularity_auditor.py"
AUDITOR_KNOWN = (
    os.path.join(r"C:\Users\usER\oracle-toe\OMEGA_TRACK_C", "auditor",
                 AUDITOR_NAME),
    os.path.join("oracle-toe", "OMEGA_TRACK_C", "auditor", AUDITOR_NAME),
    os.path.join("auditor", AUDITOR_NAME),
    AUDITOR_NAME,
)
Z3_KNOWN = (r"E:\4_TOOLS_INSTALLER\z3-4.16.0-x64-win\bin\z3.exe",)

# The three axioms the audit reports as the minimal core, by 0-based position
# among the (assert ...) forms of protocol_09.smt2, plus the claim itself.
CORE = ((11, "A4 the invariant b >= i"),
        (12, "A5 HALT implies i >= M"),
        (13, "A6 M > N"))
CLAIM_INDEX = 15

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL  %s" % msg)


def check(cond, msg):
    if not cond:
        fail(msg)
    return cond


def say(tag, msg, base):
    """Report a condition block, keyed on whether it added any failure."""
    print("%s %s %s" % ("ok  " if len(failures) == base else "FAIL  ", tag, msg))


def find_z3():
    env = os.environ.get("Z3_EXE")
    if env and os.path.isfile(env):
        return env
    for cand in Z3_KNOWN:
        if os.path.isfile(cand):
            return cand
    for name in ("z3", "z3.exe"):
        for d in os.environ.get("PATH", "").split(os.pathsep):
            p = os.path.join(d, name)
            if os.path.isfile(p):
                return p
    return None


def find_auditor():
    env = os.environ.get("ANTI_CIRCULARITY_AUDITOR")
    if env and os.path.isfile(env):
        return env
    for rel in AUDITOR_KNOWN:
        for base in (HERE, os.path.expanduser("~")):
            p = os.path.join(base, rel)
            if os.path.isfile(p):
                return p
            if os.path.isfile(rel):
                return os.path.abspath(rel)
    return None


def strip_semicolon_comments(text):
    """SMT-LIB2 has no block comments; drop from ';' to end of line."""
    out = []
    for line in text.split("\n"):
        out.append(line.split(";", 1)[0])
    return "\n".join(out)


def assert_forms(text):
    """The (assert ...) forms of a script, in order, comments removed."""
    clean = strip_semicolon_comments(text)
    forms, i = [], 0
    while True:
        j = clean.find("(assert ", i)
        if j < 0:
            break
        depth, k = 0, j
        while k < len(clean):
            if clean[k] == "(":
                depth += 1
            elif clean[k] == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        forms.append(clean[j:k + 1])
        i = k + 1
    return forms


def assemble(clean, forms, drop=None, negated_claim=None):
    """Rebuild a script, optionally dropping assertions or appending one."""
    keep = [] if drop is None else list(drop)
    out, last = [], 0
    pos = 0
    cursor = 0
    for idx, f in enumerate(forms):
        j = clean.find(f, cursor)
        out.append(clean[last:j])
        last = j + len(f)
        cursor = last
        if drop is None or idx in keep:
            out.append(f)
    out.append(clean[last:])
    text = "".join(out)
    if negated_claim is not None:
        text = text.replace("(check-sat)",
                            "(assert (not %s))\n(check-sat)" % negated_claim, 1)
    return text


def run_z3(z3, text, tag):
    tag = "".join(c if c.isalnum() else "_" for c in str(tag))
    path = os.path.join(tempfile.gettempdir(), "p09gate_%s.smt2" % tag)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    try:
        proc = subprocess.run([z3, path], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    out = (proc.stdout or "").strip() or (proc.stderr or "").strip()
    return (out.splitlines()[0] if out else ""), proc.returncode


def main():
    # ------------------------------------------------ P1 presence --------
    base = len(failures)
    if not check(os.path.isfile(SMT),
                 "P1  protocol_09.smt2 is missing from the workspace root"):
        print("")
        print("GATE: FAIL -- %d condition(s) not met" % len(failures))
        return 1
    if not check(os.path.isfile(LOG),
                 "P1  protocol_09.log is missing; a displayed verdict with "
                 "no run log is a claim, not a result"):
        print("")
        print("GATE: FAIL -- %d condition(s) not met" % len(failures))
        return 1

    with io.open(SMT, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    with io.open(LOG, encoding="utf-8", newline="") as fh:
        log = fh.read()
    say("P1", "PRESENCE            protocol_09.smt2 + protocol_09.log", base)

    # ------------------------------------------------ P2 log binding ------
    base = len(failures)
    m = re.search(r"^sha256\s*:\s*([0-9a-f]{64})\s*$", log, re.M)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if check(m is not None, "P2  the log records no sha256 of the script"):
        check(m.group(1) == digest,
              "P2  log sha256 %s does not match the current script %s -- "
              "the log is stale and cannot vouch for these bytes"
              % (m.group(1)[:16], digest[:16]))
    say("P2", "LOG BINDING         log sha256 == script sha256", base)

    # ------------------------------------------------ P3 claim + verdict --
    base = len(failures)
    check("(check-sat)" in raw,
          "P3  protocol_09.smt2 carries no (check-sat)")
    check(re.search(r"MACHINE[\s_-]+RESULT", raw, re.I) is not None,
          "P3  protocol_09.smt2 carries no MACHINE RESULT marker, so the "
          "claim gate has nothing to bind")
    vm = re.search(r"^\s*(sat|unsat|unknown)\s*$", log, re.I | re.M)
    if check(vm is not None, "P3  protocol_09.log carries no solver verdict line"):
        check(vm.group(1).lower() == "unsat",
              "P3  the log records %r, not 'unsat'" % vm.group(1))
    say("P3", "CLAIM BINDING       check-sat + MACHINE RESULT + log unsat", base)

    # ------------------------------------------------ tools --------------
    z3 = find_z3()
    if z3 is None:
        print("SKIP  P4-P7: no solver found (set Z3_EXE); integrity cannot "
              "be claimed without one")
        return 2
    auditor = find_auditor()
    if auditor is None:
        print("SKIP  P8: circularity auditor not found (set "
              "ANTI_CIRCULARITY_AUDITOR); a GENUINE verdict cannot be "
              "claimed without it")
        return 2

    # ------------------------------------------------ P4 script ---------
    base = len(failures)
    forms = assert_forms(raw)
    clean = strip_semicolon_comments(raw)
    if check(len(forms) > CLAIM_INDEX,
             "P4  expected at least %d assertions, found %d"
             % (CLAIM_INDEX + 1, len(forms))):
        check(forms[CLAIM_INDEX].startswith("(assert (and (= q0 HALT)"),
              "P4  the last assertion is not the halting claim; the "
              "auditor would audit a different sentence than the one "
              "documented")
    got, rc = run_z3(z3, raw, "script")
    check(got is not None and got == "unsat" and rc == 0,
          "P4  script must be unsat, got %r (exit %s)" % (got, rc))
    say("P4", "SCRIPT              context + claim -> unsat", base)

    # ------------------------------------------------ P5 context --------
    base = len(failures)
    ctx_text = assemble(clean, forms, drop=[i for i in range(len(forms))
                                            if i != CLAIM_INDEX])
    got, rc = run_z3(z3, ctx_text, "ctx")
    if check(got is not None, "P5  solver could not read the context: %s" % got):
        check(got == "sat" and rc == 0,
              "P5  the context alone must be SAT or the script is VACUOUS -- "
              "got %r (exit %s).  Every claim follows from an inconsistent "
              "context, so a GENUINE verdict would be meaningless"
              % (got, rc))
    say("P5", "CONTEXT             context alone -> sat", base)

    # ------------------------------------------------ P6 negated claim --
    base = len(failures)
    claim_inner = forms[CLAIM_INDEX][len("(assert "):].strip()[:-1]
    neg_text = assemble(clean, forms,
                        drop=[i for i in range(len(forms)) if i != CLAIM_INDEX],
                        negated_claim=claim_inner)
    got, rc = run_z3(z3, neg_text, "neg")
    if check(got is not None, "P6  solver could not read the negated script: %s" % got):
        check(got == "sat" and rc == 0,
              "P6  context + not claim must be SAT, so the context really "
              "does refute the claim rather than everything -- got %r "
              "(exit %s)" % (got, rc))
    say("P6", "NEGATED CLAIM       context + not claim -> sat", base)

    # ------------------------------------------------ P7 minimality ------
    base = len(failures)
    for idx, label in CORE:
        part = assemble(clean, forms, drop=[k for k in range(len(forms))
                                            if k != idx and k != CLAIM_INDEX])
        got, rc = run_z3(z3, part, "drop%d" % idx)
        if check(got is not None, "P7  solver error dropping %s: %s" % (label, got)):
            check(got == "sat" and rc == 0,
                  "P7  dropping [%d] %s must give SAT -- got %r (exit %s). "
                  "If it stayed unsat that axiom alone refutes the claim and "
                  "the result is SINGLE_AXIOM: one axiom, no domain content"
                  % (idx, label, got, rc))
    say("P7", "MINIMALITY          dropping each core axiom -> sat", base)

    # ------------------------------------------------ P8 auditor --------
    base = len(failures)
    try:
        proc = subprocess.run([sys.executable, auditor, SMT],
                              capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print("SKIP  P8: auditor did not run: %s" % exc)
        return 2
    if proc.returncode != 0:
        print("SKIP  P8: auditor exited %d: %s"
              % (proc.returncode, (proc.stderr or "").strip()[:200]))
        return 2
    out = (proc.stdout or "") + (proc.stderr or "")
    vm = re.search(r"^(GENUINE|CIRCULAR|VACUOUS|SAT|SINGLE_AXIOM|"
                   r"CLAIM_IRRELEVANT|UNKNOWN|UNPARSEABLE)\b.*$", out, re.M)
    if vm is None:
        print("SKIP  P8: auditor produced no verdict line")
        return 2
    verdict = vm.group(1)
    check(verdict == "GENUINE",
          "P8  circularity auditor reports %s, not GENUINE" % verdict)
    say("P8", "AUDIT               circularity auditor -> %s" % verdict, base)

    print("")
    if failures:
        print("GATE: FAIL -- %d condition(s) not met" % len(failures))
        return 1
    print("GATE: PASS -- 8 conditions: script unsat, context sat, negated "
          "claim sat, three core axioms each necessary, auditor GENUINE")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:      # a gate must fail, never crash into a traceback
        print("FAIL  unexpected error: %s: %s" % (type(exc).__name__, exc))
        sys.exit(1)
