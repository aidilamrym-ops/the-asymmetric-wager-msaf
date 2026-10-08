"""Fault-injection harness for `quantum_censorship_check.py` (Gate 2).

Eight cases -- six mutations plus two positive controls -- aimed at the gate's
conditions, each reverted
byte-for-byte afterwards.  The pattern is the one A2 established: a published
count with no harness behind it is a claim nobody can falsify.

  M1  Q1  a register value is perturbed        -> identity check fails
  M2  Q3  the density formula's exponent is edited in the gate
                                                -> recompute disagrees
  M3  Q4  a needle is deleted from the vacuum document
                                                -> document cross-check fails
  M4  Q5  the sieve row reverts to "Not implemented"
                                                -> scope condition fails
  M5  Q5  the "quantum censorship is not verified" sentence is deleted
                                                -> honesty scope fails
  M6  Q6  an overclaim is injected into a root document
                                                -> overclaim guard fails
  M7  Q6  an honest scope sentence is injected    -> CONTROL: must stay PASS,
                                                proving the guard does not fire
                                                on the prose that keeps the
                                                corpus honest
  M8  Q6  a *quoted* overclaim is injected         -> CONTROL: must stay PASS,
                                                proving the guard reads
                                                assertions, not citations

Control: the unmutated workspace must pass, and after every mutation the target
file must be byte-identical to where it started.

usage: python harnesses/q2_censorship_inj.py
"""
import hashlib
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GATE = os.path.join(ROOT, "quantum_censorship_check.py")
REGISTER = os.path.join(ROOT, "external_constants.json")
SIEVE = os.path.join(ROOT, "Theory_of_Everything_Derivations", "tahap uji",
                     "THE_SOVEREIGN_SIEVE_PROTOCOL.md")
VACUUM = os.path.join(ROOT, "Theory_of_Everything_Derivations", "tahap uji",
                      "THE_VACUUM_CATASTROPHE_SOLUTION.md")
PROBE = os.path.join(ROOT, "ANTI_INFINITY_BLINDSPOT.md")

PY = sys.executable


def digest(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def run_gate():
    proc = subprocess.run([PY, GATE], cwd=ROOT, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def edit(path, pairs):
    with io.open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    for old, new in pairs:
        if old not in text:
            raise AssertionError("needle missing in %s: %r"
                                 % (os.path.basename(path), old[:60]))
        text = text.replace(old, new, 1)
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def restore(path, saved):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(saved)


results = []


def case(label, path, mutate, expect_fragment):
    saved = io.open(path, encoding="utf-8", newline="").read()
    before = digest(path)
    try:
        mutate()
        rc, out = run_gate()
        caught = rc == 1 and expect_fragment in out
        results.append((label, caught, rc, expect_fragment in out))
        print("  %s %-42s gate exit=%d, expected message %s"
              % ("ok  " if caught else "FAIL", label, rc,
                 "seen" if expect_fragment in out else "MISSING"))
        if not caught:
            for line in out.splitlines()[-8:]:
                print("        | %s" % line)
    finally:
        restore(path, saved)
        if digest(path) != before:
            print("        FAIL target not restored byte-identically: %s"
                  % os.path.basename(path))
            results.append((label + " (restore)", False, -1, False))


def main():
    print("Q2 CENSORSHIP INJECTION -- six mutations of %s"
          % os.path.basename(GATE))
    rc, out = run_gate()
    if rc != 0:
        print("FAIL  baseline: the gate does not pass on the clean workspace")
        for line in out.splitlines()[-10:]:
            print("      | %s" % line)
        return 1
    print("  ok   baseline: gate passes on the clean workspace")

    # M1 -- perturb a register value so omega_P * l_P = c stops holding.
    def m1():
        with io.open(REGISTER, encoding="utf-8", newline="") as fh:
            text = fh.read()
        edit(REGISTER, [('"value": "1.616255e-35"', '"value": "1.716255e-35"')])
    case("M1 register Planck length perturbed", REGISTER, m1,
         "Q1  omega_P * l_P vs c")

    # M2 -- edit the gate's own density formula, exponent 4 -> 3.
    def m2():
        edit(GATE, [("8 * mp.pi ** 2 * l_P ** 4", "8 * mp.pi ** 2 * l_P ** 3")])
    case("M2 density formula edited in the gate", GATE, m2,
         "Q3  hbar c / (8 pi^2 l_P^4)")

    # M3 -- delete the density needle from the vacuum document.
    def m3():
        edit(VACUUM, [("5{,}867696 \\times 10^{111}", "5{,}867696 \\times 10^{112}")])
    case("M3 registered needle edited in the document", VACUUM, m3,
         "no longer contains")

    # M4 -- put the sieve row back to "Not implemented".
    def m4():
        with io.open(SIEVE, encoding="utf-8", newline="") as fh:
            lines = fh.read().split("\n")
        for i, line in enumerate(lines):
            if line.startswith("| Gate 2 |"):
                lines[i] = ("| Gate 2 | Quantum censorship audit at micro scales "
                            "| **Not implemented.** No gate script checks this. |")
                break
        with io.open(SIEVE, "w", encoding="utf-8", newline="") as fh:
            fh.write("\n".join(lines))
    case("M4 sieve row reverts to 'Not implemented'", SIEVE, m4,
         "Q5")

    # M5 -- delete the sentence that says censorship is not verified.
    def m5():
        with io.open(SIEVE, encoding="utf-8", newline="") as fh:
            lines = fh.read().split("\n")
        for i, line in enumerate(lines):
            if line.startswith("| Gate 2 |"):
                lines[i] = ("| Gate 2 | Quantum censorship audit at micro scales "
                            "| **Implemented.** `quantum_censorship_check.py` "
                            "recomputes the boundary. |")
                break
        with io.open(SIEVE, "w", encoding="utf-8", newline="") as fh:
            fh.write("\n".join(lines))
    case("M5 'not verified' scope sentence deleted", SIEVE, m5, "Q5")

    # M6 -- inject the overclaim the gate exists to catch.
    def m6():
        with io.open(PROBE, encoding="utf-8", newline="") as fh:
            text = fh.read()
        text += ("\n\nUnder MSAF the micro-scale cutoff has been verified: quantum "
                 "censorship is proven for the resolution floor used here.\n")
        with io.open(PROBE, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    case("M6 overclaim injected into a root document", PROBE, m6, "Q6")

    # M7 -- POSITIVE CONTROL: the honest scope sentence must NOT trip the guard.
    # A guard that fires on the sentence that keeps the corpus honest is worse
    # than no guard, and this case is what proves the difference.
    def m7():
        with io.open(PROBE, encoding="utf-8", newline="") as fh:
            text = fh.read()
        text += ("\n\nQuantum censorship is not verified in this workspace; the "
                 "gate recomputes the micro-scale boundary and nothing else.\n"
                 "\nThe gate refuses any claim that quantum censorship is "
                 "established: that question needs a theory of quantum gravity.\n")
        with io.open(PROBE, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    saved_probe = io.open(PROBE, encoding="utf-8", newline="").read()
    before_probe = digest(PROBE)
    m7()
    rc, out = run_gate()
    clean = rc == 0 and "Q6" in out and "FAIL" not in out
    results.append(("M7 honest scope sentence must not trip the guard", clean,
                    rc, "Q6" in out))
    print("  %s %-42s gate exit=%d, overclaim guard stayed quiet"
          % ("ok  " if clean else "FAIL",
             "M7 honest scope sentence (control)", rc))
    restore(PROBE, saved_probe)
    if digest(PROBE) != before_probe:
        print("        FAIL control target not restored byte-identically")
        results.append(("M7 (restore)", False, -1, False))

    # M8 -- POSITIVE CONTROL: a *quoted* overclaim is documentation of a defect,
    # not an assertion of one.  Phase reports quote the sentences they refute.
    saved_probe2 = io.open(PROBE, encoding="utf-8", newline="").read()
    before_probe2 = digest(PROBE)
    with io.open(PROBE, "w", encoding="utf-8", newline="") as fh:
        fh.write(saved_probe2
                 + '\n\nA previous revision of this file said "quantum censorship '
                   'is proven for the resolution floor used here", which the gate '
                   'refuses.\n')
    rc, out = run_gate()
    quoted_ok = rc == 0
    results.append(("M8 quoted overclaim must not be counted (control)",
                    quoted_ok, rc, True))
    print("  %s %-42s gate exit=%d, quoted overclaim not counted"
          % ("ok  " if quoted_ok else "FAIL",
             "M8 quoted overclaim (control)", rc))
    restore(PROBE, saved_probe2)
    if digest(PROBE) != before_probe2:
        print("        FAIL quoted-control target not restored byte-identically")
        results.append(("M8 (restore)", False, -1, False))

    rc, out = run_gate()
    if rc != 0:
        print("FAIL  restored baseline: gate does not pass again")
        return 1
    print("  ok   restored baseline: gate passes again")

    passed = sum(1 for _, okk, _, _ in results if okk)
    print()
    print("HARNESS: %s -- %d/%d cases behaved as expected, every target "
          "byte-identical afterwards"
          % ("PASS" if passed == len(results) and results else "FAIL",
             passed, len(results)))
    return 0 if passed == len(results) and results else 1


if __name__ == "__main__":
    sys.exit(main())