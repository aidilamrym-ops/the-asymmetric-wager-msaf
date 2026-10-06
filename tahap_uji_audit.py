# FILE: tahap_uji_audit.py
# PURPOSE: Fase A10 honesty gate over the two documents in
#          Theory_of_Everything_Derivations/tahap uji/.
#          Reads every condition OUT of those documents (and out of
#          external_constants.json / protocol_09.log where the condition is a
#          cross-reference), so deleting a sentence fails the gate rather than
#          quietly passing it.
# EXIT:    0 = every condition met
#          1 = at least one condition failed
#          2 = a required tool or artefact is missing (never a pass)
# REGISTERED: suite_check.py GATES, entry immediately before
#             report_claim_check.py and checksum_check.py (A10, 2026-10-07).

import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAC = os.path.join(HERE, "Theory_of_Everything_Derivations", "tahap uji",
                   "THE_VACUUM_CATASTROPHE_SOLUTION.md")
SIEVE = os.path.join(HERE, "Theory_of_Everything_Derivations", "tahap uji",
                     "THE_SOVEREIGN_SIEVE_PROTOCOL.md")
CONST = os.path.join(HERE, "external_constants.json")
P09LOG = os.path.join(HERE, "protocol_09.log")
LANDAUER = os.path.join(HERE, "landauer_check.py")
ZETA = os.path.join(HERE, "msaf_zeta_check.py")

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL  %s" % msg)


def ok(msg):
    print("ok    %s" % msg)


def check(cond, msg):
    if cond:
        ok(msg)
    else:
        fail(msg)
    return cond


def read(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


def main():
    for p in (VAC, SIEVE, CONST, P09LOG):
        if not os.path.isfile(p):
            print("FAIL  --  missing artefact: %s" % p)
            return 2

    vac = read(VAC)
    sieve = read(SIEVE)
    try:
        reg = json.loads(read(CONST))
    except Exception as exc:
        print("FAIL  --  external_constants.json unreadable: %s" % exc)
        return 2
    p09 = read(P09LOG)
    q_by_id = {q.get("id"): q for q in reg.get("quantities") or []
               if isinstance(q, dict)}

    # ---- V1 both documents are English -----------------------------------
    base = len(failures)
    indo = re.compile(r"\b(Memproses|Tak Terhingga|Terpaksa|Skakmat|"
                      r"Kecerdasan|Sains Dunia|dilarang|membuktikan)\b")
    check(not indo.search(vac),
          "V1  VACUUM document carries no Indonesian claim vocabulary")
    check(not indo.search(sieve),
          "V1  SIEVE document carries no Indonesian claim vocabulary")
    check("FILE: THE_VACUUM_CATASTROPHE_SOLUTION.md" in vac and
          "FILE: THE_SOVEREIGN_SIEVE_PROTOCOL.md" in sieve,
          "V1  both documents retain their FILE headers")
    print("%s V1  LANGUAGE                     delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---- V2 vacuum numbers match the register (OUT of documents) --------
    base = len(failures)
    needles = [
        ("REDUCED_PLANCK_CONSTANT", r"1\{,\}054571817 \\times 10\^\{-34\}"),
        ("SPEED_OF_LIGHT", r"2\{,\}99792458 \\times 10\^\{8\}"),
        ("DARK_ENERGY_DENSITY", r"6 \\times 10\^\{-10\}"),
        ("PLANCK_VACUUM_DENSITY", r"5\{,\}867696 \\times 10\^\{111\}"),
        ("PLANCK_FREQUENCY", r"1\{,\}854859 \\times 10\^\{43\}"),
        ("RECIPROCAL_UNIVERSE_PIXEL", r"5\{,\}444685 \\times 10\^\{61\}"),
    ]
    for qid, pat in needles:
        q = q_by_id.get(qid)
        if q is None:
            fail("V2  quantity %s missing from external_constants.json" % qid)
            continue
        site = None
        for s in q.get("sites") or []:
            if "THE_VACUUM_CATASTROPHE_SOLUTION.md" in str(s.get("file", "")):
                site = s
                break
        if site is None:
            fail("V2  %s has no site in the vacuum document" % qid)
            continue
        needle = site.get("needle") or ""
        count = vac.count(needle)
        expect = int(site.get("count") or 1)
        check(count == expect,
              "V2  %s needle %r occurs %d time(s) in vacuum doc (declared %d)"
              % (qid, needle, count, expect))
        # the registered value must appear in the document
        val = str(q.get("value") or "")
        mant = str(site.get("mantissa") or "").replace("{,", "").replace(",", "")
        check(mant in vac or val in vac,
              "V2  %s registered value %s is present in vacuum doc"
              % (qid, val))
    print("%s V2  VACUUM_NUMBERS              delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---- V3 vacuum does not claim equality / zero error ------------------
    base = len(failures)
    bad_eq = [
        (r"error\s*=\s*0", "error = 0"),
        (r"deviasi kesalahan mutlak bernilai\s*\*?\*?0", "zero absolute error"),
        (r"STATUS:\s*SATISFIABLE", "STATUS: SATISFIABLE as a result"),
        (r"renormalisasi kotor", "renormalisasi kotor"),
        (r"exactly onto\s*\\rho", "exact compression onto rho_observed"),
        (r"\\rho_\{\\text\{MSAF\}\}\\s*\\equiv\\s*\\rho_\{\\text\{observed\}\}",
         "MSAF density identically equals observed"),
    ]
    for pat, label in bad_eq:
        check(not re.search(pat, vac, re.I),
              "V3  vacuum doc does not claim %s" % label)
    check("remains open" in vac.lower() or "remains open" in vac,
          "V3  vacuum doc states the residual gap remains open")
    check("withdrawn" in vac.lower(),
          "V3  vacuum doc withdraws the former equality claim")
    print("%s V3  VACUUM_HONESTY              delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---- V4 dimensional honesty for 1/Delta_univ ------------------------
    base = len(failures)
    check("dimensionless" in vac.lower(),
          "V4  vacuum doc labels 1/Delta_univ dimensionless")
    check("not** a frequency" in vac or "not a frequency" in vac
          or "not** a frequency" in vac.replace("**", ""),
          "V4  vacuum doc forbids reading the reciprocal as a frequency")
    # if the reciprocal is used as omega, the Planck frequency must also appear
    if re.search(r"\\omega\s*=\s*1/\s*\\Delta", vac):
        check("PLANCK_FREQUENCY" in vac or "1{,}854859" in vac,
              "V4  any omega=1/Delta claim is paired with the Planck cutoff")
    print("%s V4  DIMENSIONAL                 delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---- V5 sieve: Landauer is a floor, not a crash proof ----------------
    base = len(failures)
    check("Landauer" in sieve,
          "V5  sieve doc names Landauer")
    check("lower bound" in sieve or "floor" in sieve,
          "V5  Landauer described as a lower bound / floor")
    check("not a proof that any particular computation crashes" in sieve
          or "not** a proof" in sieve,
          "V5  Landauer is not sold as a crash proof")
    check(os.path.isfile(LANDAUER),
          "V5  landauer_check.py exists as the Gate 1 machine gate")
    print("%s V5  LANDAUER                    delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---- V6 sieve: NS and RH are open, not proven here -------------------
    base = len(failures)
    check("Navier" in sieve and "open" in sieve.lower(),
          "V6  sieve doc marks Navier--Stokes as open")
    check("does **not** prove RH" in sieve or "does not prove RH" in sieve
          or "not** prove RH" in sieve,
          "V6  sieve doc does not claim to prove RH")
    check("Clay" in sieve,
          "V6  sieve doc names the Clay Millennium status of Navier--Stokes")
    check("terbukti mulus" not in sieve,
          "V6  sieve doc contains no 'terbukti mulus' claim")
    check(re.search(r"does \*\*not\*\* prove that solutions are", sieve) is not None,
          "V6  sieve doc explicitly denies proving Navier--Stokes smoothness")
    print("%s V6  OPEN_PROBLEMS               delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---- V7 sieve: Gate 3 meaning is not 'all SAT' -----------------------
    base = len(failures)
    check("unsat" in p09.lower(),
          "V7  protocol_09.log records an unsat script verdict")
    check("ctx=sat" in p09 or "context alone" in p09.lower()
          or "context alone" in sieve.lower(),
          "V7  context-alone sat is recorded (non-vacuous)")
    check(re.search(r"It does\s+\*\*not\*\* mean", sieve) is not None,
          "V7  sieve doc denies Gate 3 blesses every prose claim")
    check("unsat" in sieve.lower(),
          "V7  sieve doc records that the Protocol 09 claim is unsat")
    check("misread" in sieve.lower() or "misread" in sieve,
          "V7  sieve doc warns that SATISFIABLE-context has been misread")
    print("%s V7  GATE3_MEANING               delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---- V8 sieve: Gate 2 is recorded as not implemented -----------------
    base = len(failures)
    check("Gate 2" in sieve or "Gate 2" in sieve,
          "V8  sieve doc names Gate 2")
    check(re.search(r"Gate 2.*Not implemented|Not implemented.*Gate 2",
                    sieve, re.I | re.S),
          "V8  Gate 2 is recorded as not implemented")
    print("%s V8  GATE2_STATUS                delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---- V9 sieve: coercion language removed -----------------------------
    base = len(failures)
    check("dilarang" not in sieve and "Sovereign Matrix Command" not in sieve
          or "rewritten without coercion" in sieve.lower()
          or "not a proof" in sieve.lower(),
          "V9  former coercion doctrine is withdrawn or reframed")
    check("rhetorical" in sieve.lower(),
          "V9  trap diagram labelled rhetorical, not a proof")
    print("%s V9  COERCION                    delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---- V10 vacuum cross-reads provenance for rho_Lambda ---------------
    base = len(failures)
    ev_ids = {e.get("id") for e in reg.get("evidence") or []}
    check("WIKIPEDIA_DARK_ENERGY" in ev_ids,
          "V10 Wikipedia Dark energy evidence is registered")
    q = q_by_id.get("DARK_ENERGY_DENSITY") or {}
    check(q.get("evidence_id") == "WIKIPEDIA_DARK_ENERGY",
          "V10 DARK_ENERGY_DENSITY cites WIKIPEDIA_DARK_ENERGY")
    probe = q.get("evidence_probe") or {}
    check(bool(probe.get("line_needles")),
          "V10 DARK_ENERGY_DENSITY carries an evidence_probe")
    print("%s V10 RHO_LAMBDA_PROVENANCE      delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---- V11 live recompute of Planck vacuum density ---------------------
    base = len(failures)
    try:
        import mpmath as mp
        mp.mp.dps = 50
        hbar = mp.mpf(q_by_id["REDUCED_PLANCK_CONSTANT"]["value"])
        cval = mp.mpf(q_by_id["SPEED_OF_LIGHT"]["value"])
        lp = mp.mpf(q_by_id["PLANCK_LENGTH"]["value"])
        rho = hbar * cval / (8 * mp.pi ** 2 * lp ** 4)
        declared = mp.mpf(q_by_id["PLANCK_VACUUM_DENSITY"]["value"])
        # compare at 7 significant figures as declared
        rel = abs(rho - declared) / declared
        check(rel < 5e-7,
              "V11 recomputed rho_planck %s agrees with declared %s"
              % (mp.nstr(rho, 12), mp.nstr(declared, 12)))
        gap = rho / mp.mpf(q_by_id["DARK_ENERGY_DENSITY"]["value"])
        check(mp.log10(gap) > 120,
              "V11 residual ratio rho_planck/rho_Lambda has log10 > 120 "
              "(got %s)" % mp.nstr(mp.log10(gap), 6))
        om = cval / lp
        decl_om = mp.mpf(q_by_id["PLANCK_FREQUENCY"]["value"])
        check(abs(om - decl_om) / decl_om < 5e-7,
              "V11 recomputed omega_P %s agrees with declared %s"
              % (mp.nstr(om, 12), mp.nstr(decl_om, 12)))
    except ImportError:
        fail("V11 mpmath unavailable -- cannot recompute Planck vacuum density")
    except Exception as exc:
        fail("V11 recompute raised %s: %s" % (type(exc).__name__, exc))
    print("%s V11 LIVE_RECOMPUTE             delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---- summary ---------------------------------------------------------
    n_cond = 11
    if failures:
        print("tahap_uji_audit: FAIL -- %d condition(s) not met" % len(failures))
        return 1
    print("tahap_uji_audit: PASS -- %d/%d conditions met, documents honest"
          % (n_cond, n_cond))
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except Exception as exc:
        print("FAIL  unexpected error: %s: %s" % (type(exc).__name__, exc))
        rc = 2
    sys.exit(rc)
