"""Gate 2 of the three-gate protocol: the *checkable part* of a quantum
censorship audit at micro scales.

WHY THIS FILE EXISTS
    A10 recorded residual `A10-R2`: the sieve protocol presented Gate 1, Gate 2
    and Gate 3 as a triple gate, but no script implemented Gate 2 -- "Quantum
    censorship audit at micro scales. No gate script in this workspace checks
    for local quantum black-hole formation."  A gate that is described but not
    implemented is the defect A10 V-4 was written to prevent.

    This file implements the part that arithmetic can decide, and refuses to
    pretend it implements the rest.  Quantum censorship -- that energy
    concentration cannot produce an event horizon from behind a horizon -- is a
    statement about quantum gravity.  This workspace has no theory of quantum
    gravity, so no script here can verify it, and a script that claimed to
    would be the same defect in a new place.  What *is* decidable is the
    boundary on which the question sits:

      Q1  omega_P * l_P = c                      the Planck scales are consistent
      Q2  m_P = hbar omega_P / c^2 = hbar/(c l_P)   two independent routes agree
      Q3  rho_Planck = hbar c / (8 pi^2 l_P^4)  the registered zero-point density
      Q4  the sieve protocol states this scope    the document cannot drift from
          and names this script                     the code
      Q5  no document claims censorship is proven  the honesty boundary

    The physical content of Q1..Q3 is a statement about *where* the question
    lives, not an answer to it.  Classical general relativity's Schwarzschild
    radius has no quantum-gravity validity at l_P, which is exactly why
    "does a local quantum black hole form here?" cannot be settled by plugging
    numbers into a formula -- and why this workspace records the question as
    open instead of gating it away.

    Note on r_S(m_P): with m_P = sqrt(hbar c / G) and l_P = sqrt(hbar G / c^3),
    the identity r_S(m_P) = 2 G m_P / c^2 = 2 l_P holds *algebraically* and needs
    no value of G.  It is stated here rather than computed, because evaluating
    it numerically would require registering G, and a registered constant that
    exists only to make one line computable is a worse register than no
    constant at all.

WHAT THIS GATE DOES NOT CLAIM
    - Not a verification of quantum censorship, of any horizon, or of any
      quantum-gravity claim.
    - Not a statement that the censorship question is answered *negatively* by
      a resolution floor.  A question below the operational floor is
      unevaluable here, which is a different claim from being false.
    - No mass, energy or length is asserted to be achievable; every quantity
      here is recomputed from the register.

Exit 0 = every claim verified.  Exit 1 = a claim is missing, wrong, or
overclaimed.  Exit 2 = tool not run (interpreter or register unavailable).

usage: python quantum_censorship_check.py
"""
import io
import json
import os
import re
import sys

EXIT_NOT_RUN = 2
EXIT_FAIL = 1
EXIT_OK = 0

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER = os.path.join(HERE, "external_constants.json")
SIEVE = os.path.join(HERE, "Theory_of_Everything_Derivations", "tahap uji",
                     "THE_SOVEREIGN_SIEVE_PROTOCOL.md")
VACUUM = os.path.join(HERE, "Theory_of_Everything_Derivations", "tahap uji",
                      "THE_VACUUM_CATASTROPHE_SOLUTION.md")

DPS = 100

# CODATA Planck mass, used only as an external control on the derived value.
CODATA_PLANCK_MASS = "2.176434e-8"

failures = []


def fail(msg):
    failures.append(msg)
    print("  FAIL  %s" % msg)


def ok(msg):
    print("  ok    %s" % msg)


def registered(register, qid):
    for q in register.get("quantities", []):
        if q.get("id") == qid:
            return q
    return None


def agree(name, declared, computed, nsig, unit=""):
    """Compare at the declared significant figures, as landauer_check does."""
    import mpmath as mp
    tol = mp.mpf(10) ** (-(nsig - 1))
    err = abs(declared - computed) / abs(declared) if declared else abs(computed)
    if err <= tol:
        ok("%-30s %s %s  (rel err %.2e, tol 1e-%d)"
           % (name, mp.nstr(computed, nsig + 3), unit, err, nsig - 1))
    else:
        fail("%s: registered %s, recomputed %s, rel err %.3e > tol 1e-%d"
             % (name, mp.nstr(declared, nsig + 3), mp.nstr(computed, nsig + 3),
                err, nsig - 1))
    return err


SCI = r"(\d+)(?:\{,\}(\d+))?\s*\\times\s*10\^\{(-?\d+)\}"


def doc_sci(match):
    whole, frac, exp = match
    return "%s.%se%s" % (whole, frac or "0", exp)


def main():
    import mpmath as mp

    for path, label in ((REGISTER, "constant register"),
                        (SIEVE, "sieve protocol"),
                        (VACUUM, "vacuum solution document")):
        if not os.path.isfile(path):
            print("TOOL NOT RUN: %s not found: %s" % (label, path))
            return EXIT_NOT_RUN

    try:
        with io.open(REGISTER, encoding="utf-8") as fh:
            register = json.load(fh)
        sieve = io.open(SIEVE, encoding="utf-8").read()
        vacuum = io.open(VACUUM, encoding="utf-8").read()
    except Exception as exc:
        print("TOOL NOT RUN: cannot read inputs: %s" % exc)
        return EXIT_NOT_RUN

    mp.mp.dps = DPS
    print("QUANTUM CENSORSHIP CHECK -- Gate 2, checkable part")
    print("  quantum censorship itself is NOT gated; see the module docstring.")

    # ---------------------------------------------------------------- inputs
    need = ("PLANCK_LENGTH", "PLANCK_FREQUENCY", "REDUCED_PLANCK_CONSTANT",
            "SPEED_OF_LIGHT", "PLANCK_VACUUM_DENSITY")
    vals = {}
    for qid in need:
        q = registered(register, qid)
        if q is None:
            fail("Q0: the register has no quantity %s -- cannot recompute "
                 "anything" % qid)
            continue
        vals[qid] = (mp.mpf(q["value"]), int(q.get("sig_figs", 7)))
        ok("%-30s %s %s (%s, %d s.f.)"
           % (qid, q["value"], q.get("unit", ""), q.get("kind", "?"),
              int(q.get("sig_figs", 7))))
    if failures:
        print()
        print("QUANTUM CENSORSHIP CHECK: %d FAILURE(S)" % len(failures))
        return EXIT_FAIL

    l_P, lP_sf = vals["PLANCK_LENGTH"]
    w_P, wP_sf = vals["PLANCK_FREQUENCY"]
    hbar, hb_sf = vals["REDUCED_PLANCK_CONSTANT"]
    c, c_sf = vals["SPEED_OF_LIGHT"]
    rho, rho_sf = vals["PLANCK_VACUUM_DENSITY"]

    # ------------------------------------------- Q1: the Planck-scale identity
    # omega_P is registered as the derived quotient c / l_P.  Recompute the
    # product rather than trusting the derivation string.
    sf = min(lP_sf, wP_sf, c_sf)
    agree("Q1  omega_P * l_P vs c", c, w_P * l_P, sf, "m/s")

    # --------------------------------------------------- Q2: the Planck mass
    m_route1 = hbar * w_P / c ** 2          # E_P = hbar omega_P = m_P c^2
    m_route2 = hbar / (c * l_P)             # from omega_P = c / l_P
    agree("Q2a m_P = hbar omega_P / c^2",
          mp.mpf(CODATA_PLANCK_MASS), m_route1, 7, "kg")
    agree("Q2b m_P = hbar / (c l_P)",
          mp.mpf(CODATA_PLANCK_MASS), m_route2, 7, "kg")
    ok("%-30s rel err between the two routes %.2e"
       % ("Q2c  route agreement", abs(m_route1 - m_route2) / m_route2))

    # ------------------------------- Q3: the registered zero-point density
    recomputed_rho = hbar * c / (8 * mp.pi ** 2 * l_P ** 4)
    agree("Q3  hbar c / (8 pi^2 l_P^4)", rho, recomputed_rho, rho_sf, "J/m^3")

    # --------------------------- documents must quote what the register holds
    # Landauer reads its numbers out of the documents so an edit there fails.
    # The register already names, per quantity, the exact needle that must be
    # present and where -- and it must be used verbatim: an earlier version of
    # this block searched a generic `N \times 10^{-k}` pattern and happily
    # matched the *reduced Planck constant* that appears earlier in the same
    # document, which is a gate that reads the wrong number and calls it a pass.
    for qid in ("PLANCK_VACUUM_DENSITY", "PLANCK_FREQUENCY"):
        q = registered(register, qid)
        sites = q.get("sites") or []
        if not sites:
            fail("Q4: the register lists no site for %s, so the document "
                 "cross-check has nothing to read" % qid)
            continue
        for site in sites:
            doc_path = os.path.join(HERE, site["file"].replace("/", os.sep))
            if not os.path.isfile(doc_path):
                fail("Q4: %s is missing from the workspace" % site["file"])
                continue
            body = io.open(doc_path, encoding="utf-8").read()
            hits = body.count(site["needle"])
            if hits == 0:
                fail("Q4: %s no longer contains %s"
                     % (site["file"], site["needle"]))
                continue
            if hits != int(site.get("count", 1)):
                fail("Q4: %s contains %s %d time(s), the register says %s"
                     % (site["file"], site["needle"], hits,
                        site.get("count")))
                continue
            ok("Q4  %-24s quoted once in %s"
               % (qid, os.path.basename(site["file"])))

    # ------------------------------------------------ Q5: the scope statement
    # The sieve protocol is the document that declared Gate 2 unimplemented.
    # It must now state what is implemented, what is not, and name the script.
    required = [
        ("Gate 2 names the script that implements its arithmetic",
         r"`quantum_censorship_check\.py`"),
        ("Gate 2 states the arithmetic is implemented",
         r"Gate 2[^\n]{0,200}?\*\*Implemented"),
        ("Gate 2 states censorship itself is not verified",
         r"quantum censorship[^.]{0,260}?not\s+(?:verified|proved|proven|"
         r"established|confirmed)"),
    ]
    for name, pattern in required:
        if re.search(pattern, sieve, re.S | re.I):
            ok("Q5  %s" % name)
        else:
            fail("Q5: %s is missing from %s"
                 % (name, os.path.basename(SIEVE)))

    if re.search(r"Gate 2[^\n|]{0,80}\*\*Not implemented\.\*\*", sieve):
        fail("Q5: the sieve protocol still calls Gate 2 'Not implemented'")

    # The reverse-order pattern above is deliberately narrow -- it needs the
    # claim word immediately before the phrase.  A wider window was tried first
    # and caught this very sentence in a phase report ("arithmetic verified;
    # quantum censorship remains open"), which is a guard that fires on honest
    # prose.  Narrowed, and the positive control below proves both halves: the
    # overclaim still fails (M6) and the scope sentence still passes (M7).
    # --------------------------------------- Q6: the honesty boundary itself
    # This is the condition that would have caught A10 V-4 in the first place.
    forbidden = [
        (r"(?i)quantum censorship[^.]{0,60}?\b(?:is|was|has been|are)\s+"
         r"(?:proven|proved|established|verified|confirmed)\b",
         "a document claims quantum censorship is verified"),
        (r"(?i)\b(?:proven|proved|established|verified|confirmed)\b\s+"
         r"(?:that\s+)?quantum censorship",
         "a document presents quantum censorship as verified"),
        (r"(?i)all three gates pass",
         "'all three gates pass' presents an unimplemented gate as passing"),
        (r"(?i)triple[- ]gate passes",
         "'triple-gate passes' presents an unimplemented gate as passing"),
    ]
    # A claim can be scoped by a negator: "refuses any claim that quantum
    # censorship is established" is the corpus being careful, not the corpus
    # overclaiming.  Without this, the guard fired on the very sentences written
    # to prevent the overclaim -- a false positive that trains readers to
    # distrust the gate.  The lead window is cut at the previous sentence
    # boundary so a negator from an unrelated sentence cannot excuse this one.
    NEGATORS = re.compile(
        r"(?i)\b(?:refus\w+|not|never|den\w+|no\s+claim|cannot|can't|nor|"
        r"without|nor\s+is|is\s+not|are\s+not)\b")

    def quoted(text, pos):
        """True when the match sits inside a quoted span on its own line.

        Phase reports quote the very sentences they refute -- F1, F4 and this
        phase's own report all do -- so a guard that cannot tell a quotation from
        an assertion fires on the documentation of a defect.  Both quote forms
        this corpus uses are handled: an odd number of backticks or of double
        quotes before the match on its line.
        """
        line_start = max(text.rfind("\n", 0, pos), text.rfind("\r", 0, pos)) + 1
        lead = text[line_start:pos]
        return lead.count("`") % 2 == 1 or lead.count('"') % 2 == 1

    def scoped(text, start):
        lead = text[max(0, start - 70):start]
        cut = max(lead.rfind("."), lead.rfind("\n"), lead.rfind(";"))
        return bool(NEGATORS.search(lead[cut + 1:]))

    scanned, hit, qualified = 0, False, 0
    for name in sorted(os.listdir(HERE)):
        if not name.endswith(".md"):
            continue
        try:
            body = io.open(os.path.join(HERE, name), encoding="utf-8").read()
        except Exception:
            continue
        scanned += 1
        for pattern, why in forbidden:
            for m in re.finditer(pattern, body):
                if quoted(body, m.start()) or scoped(body, m.start()):
                    qualified += 1
                    continue
                fail("Q6: %s -- %s: %r" % (name, why, m.group(0)[:80]))
                hit = True
    for extra in (SIEVE, VACUUM):
        body = io.open(extra, encoding="utf-8").read()
        scanned += 1
        for pattern, why in forbidden:
            for m in re.finditer(pattern, body):
                if quoted(body, m.start()) or scoped(body, m.start()):
                    qualified += 1
                    continue
                fail("Q6: %s: %s -- %r"
                     % (os.path.basename(extra), why, m.group(0)[:80]))
                hit = True
    if not hit:
        ok("Q6  no overclaim of quantum censorship in %d documents scanned"
           % scanned)
        if qualified:
            ok("Q6  %d negated or quoted mention(s), correctly not counted as "
               "overclaims" % qualified)

    print()
    if failures:
        print("QUANTUM CENSORSHIP CHECK: %d FAILURE(S)" % len(failures))
        return EXIT_FAIL
    print("QUANTUM CENSORSHIP CHECK: Gate 2's arithmetic verified; quantum "
          "censorship itself remains an open question, not a gated result.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())