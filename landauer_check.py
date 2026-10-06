"""Gate the Landauer derivation of SOLVABLE_FINITE_PARADOX.md section 3.

Before F2 the thermodynamic half of the argument did not exist: the Landauer /
k_B / Delta E sentence had been removed by F0 for claiming an executed result,
and nothing put a derived number back in its place, so section 3's
"Thermodynamic Cost" row was honest but empty of argument.

This checker closes that gap the same way msaf_zeta_check.py closed the zeta
gap.  It reads the claims OUT OF THE DOCUMENT (so a claim that is deleted,
reworded or edited also fails), recomputes them with mpmath at 100 dps from the
exact SI value of k_B and from ln 2, and compares at the document's own
significant figures.

Checks
  L1  k_B ln 2                recomputed vs declared
  L2  dE at T = 2.725 K        recomputed vs declared table row
  L3  dE at T = 300 K          recomputed vs declared table row
  L4  internal consistency     each row's dE / T equals the declared k_B ln 2
  L5  every claim present      deleting the derivation or the table fails
  L6  no energy total          no total is asserted anywhere in the document

The same Landauer claim also appears in two other documents in this workspace,
so the checker reads them too.  These are cross-document checks (X):

  X   ANTI_INFINITY_BLINDSPOT.md                the infinite-total premise must be
                                                labelled an assumption, the derived
                                                constant must match, "process every
                                                bit" must be absent
  X   MSAF_COSMOLOGY_DECONSTRUCTION (2).md      the floor must be per bit, the
                                                withdrawn "absolutely" must stay
                                                withdrawn, and the number must match
                                                k_B ln2 recomputed against the
                                                temperature THIS document states --
                                                that temperature is parsed, never
                                                hard-coded here.

Only arithmetic on two exact inputs is checked.  No temperature is asserted to
be this workspace's operating temperature: every T value is a declared input of
the document it is read from, and no energy total is claimed in any of them.

Exit 0 = every claim verified.  Exit 1 = a claim is missing or wrong.
Exit 2 = tool not run (interpreter or document unavailable).

usage: python landauer_check.py
"""
import io
import os
import re
import sys

EXIT_NOT_RUN = 2
EXIT_FAIL = 1
EXIT_OK = 0

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "SOLVABLE_FINITE_PARADOX.md")

DPS = 100

# SI 2019 exact defining constant, also stated by the document.
K_B = "1.380649e-23"

failures = []


def fail(msg):
    failures.append(msg)
    print("  FAIL  %s" % msg)


def ok(msg):
    print("  ok    %s" % msg)


def tex_sci(match):
    """('9', '5699296', '-24') -> 9.5699296e-24; frac may be absent."""
    import mpmath as mp
    whole, frac, exp = match
    return mp.mpf("%s.%s" % (whole, frac or "0")) * (mp.mpf(10) ** int(exp))


def declared_nsig(match):
    """Significant figures the document printed: ('9', '5699296', ...) -> 8."""
    whole, frac, _ = match
    if frac is None:
        return len(whole.lstrip("0")) or 1
    if whole != "0":
        return len(whole) + len(frac)
    digits = (frac.lstrip("0") or frac)
    return len(digits) or 1


def rel_err(declared, computed):
    import mpmath as mp
    if declared == 0:
        return abs(computed)
    return abs(declared - computed) / abs(declared)


def agree(name, declared, computed, nsig):
    import mpmath as mp
    tol = mp.mpf(10) ** (-(nsig - 1))
    err = rel_err(declared, computed)
    if err <= tol:
        ok("%-26s %s  (rel err %.2e, tol 1e-%d)"
           % (name, mp.nstr(computed, nsig + 2), err, nsig - 1))
    else:
        fail("%s: declared %s, computed %s, rel err %.3e > tol 1e-%d"
             % (name, mp.nstr(declared, nsig + 2), mp.nstr(computed, nsig + 2),
                err, nsig - 1))


SCI = r"(\d+)(?:\{,\}(\d+))?\\times10\^\{(-?\d+)\}"
RE_KBLN2 = re.compile(r"k_B\\ln 2 = " + SCI)
RE_KB = re.compile(r"k_B = " + SCI)

# --- the same Landauer claim as it appears in the other two documents --------
CROSS_AIB = {
    "T_pattern": None,
    "present": [
        (r"assumption about the algorithm, not a measurement",
         "the infinite-total premise is labelled an assumption"),
        (r"9\{,\}5699296\\times10\^\{-24\}",
         "the derived constant k_B ln 2 is quoted"),
        (r"no energy total is claimed",
         "the no-total disclaimer is present"),
    ],
    "absent": [
        (r"(?i)to process every bit of information",
         "'process every bit' misstates Landauer, which charges erasure"),
        (r"(?i)total energy released .* would be unbounded \(\\(E = \\infty\\)\)",
         "the unbounded-total claim still stands without its premise"),
    ],
    "numbers": [],
}

CROSS_MSAF = {
    "T_pattern": r"T \\approx (\d+)\{,\}(\d+)\\text\{ K\}",
    "present": [
        (r"per erased bit", "the floor is stated per bit, not as a total"),
        (r"no energy total is", "the no-total disclaimer is present"),
        (r"conditional on the erasure being", "the overclaim is withdrawn"),
    ],
    "absent": [
        (r"(?i)absolutely emits", "the withdrawn 'absolutely' overclaim is back"),
        (r"(?i)total energy\s*=", "a total-energy figure is asserted"),
    ],
    "numbers": [
        r"(\d+)\{,\}(\d+) \\times 10\^\{(-?\d+)\}\\text\{ J\}",
    ],
}
RE_KB_LINE = re.compile(r"k_B = " + SCI + r"\\ \\mathrm")
RE_ROW = re.compile(
    r"^\| \\\((\d+(?:\{,\}\d+)?)\\ \\mathrm\{K\}\\\) \| \\\(" + SCI
    + r"\\ \\mathrm\{J\}\\\) \|$")


def main():
    import mpmath as mp

    if not os.path.isfile(DOC):
        print("TOOL NOT RUN: document not found: %s" % DOC)
        return EXIT_NOT_RUN
    try:
        text = io.open(DOC, encoding="utf-8").read()
    except Exception as exc:
        print("TOOL NOT RUN: cannot read %s: %s" % (DOC, exc))
        return EXIT_NOT_RUN

    mp.mp.dps = DPS

    print("LANDAUER CHECK -- %s" % os.path.basename(DOC))
    print("  k_B = %s J/K (SI 2019 exact), dps = %d" % (K_B, DPS))

    kb_decl = RE_KB.search(text)
    if not kb_decl:
        fail("L0: the document no longer states k_B -- cannot check anything")
    k_b = mp.mpf(K_B)
    if kb_decl:
        kb_doc = tex_sci(kb_decl.groups())
        if kb_doc != k_b:
            fail("L0: document states k_B = %s, SI exact value is %s"
                 % (mp.nstr(kb_doc, 20), mp.nstr(k_b, 20)))
        else:
            ok("%-26s %s" % ("k_B (exact input)", mp.nstr(k_b, 20)))

    # --- L1: k_B ln 2 ---
    m = RE_KBLN2.search(text)
    if not m:
        fail("L1: declared k_B ln 2 not found in the document")
    else:
        g = m.groups()
        agree("L1  k_B ln 2", tex_sci(g), k_b * mp.log(2), declared_nsig(g))

    # --- L2 / L3 / L4: table rows ---
    rows = []
    for line in text.split("\n"):
        rm = RE_ROW.match(line.strip())
        if rm:
            groups = rm.groups()
            t_txt, sci = groups[0], groups[1:]   # sci = (whole, frac, exp)
            t_val = mp.mpf(t_txt.replace("{,}", "."))
            rows.append((t_val, tex_sci(sci), declared_nsig(sci), t_txt))

    if len(rows) < 2:
        fail("L2/L3: expected 2 temperature rows in the table, found %d"
             % len(rows))
    else:
        for label, (t_val, d_e, nsig, t_txt) in zip(("L2", "L3"), rows[:2]):
            agree("%s  dE at T=%s K" % (label, t_txt), d_e,
                  k_b * mp.log(2) * t_val, nsig)

        # L4 -- internal consistency: each row's dE / T must reproduce the
        # declared k_B ln 2, so the table cannot drift from the derivation.
        m1 = RE_KBLN2.search(text)
        if m1:
            decl, n1 = tex_sci(m1.groups()), declared_nsig(m1.groups())
            for t_val, d_e, _nsig, t_txt in rows[:2]:
                if t_val != 0:
                    agree("L4  dE/T at T=%s" % t_txt, decl, d_e / t_val, n1)

    # --- L5: the argument must still be present ---
    required = [
        ("the Landauer inequality", r"\\Delta E \\;\\ge\\; k_B\\,T\\,\\ln 2"),
        ("the 'no total energy is claimed' sentence",
         r"no total energy is\s+claimed"),
        ("the step-count ceiling", r"N_\{\\text\{steps\}\}"),
        ("the premise is an assumption, not a measurement",
         r"assumption about the algorithm, not a measurement"),
        ("the temperatures are labelled inputs, not measurements",
         r"stated inputs\*\*, not measurements"),
    ]
    for name, pattern in required:
        if re.search(pattern, text):
            ok("L5  present: %s" % name)
        else:
            fail("L5: %s is missing from the document" % name)

    # --- L6: no energy TOTAL may be asserted anywhere ---
    forbidden = [
        (r"(?i)total\s+energy\s*(?:=|is\s+[0-9])",
         "a total-energy figure is asserted"),
        (r"(?i)zero\s+thermal\s+emission",
         "the withdrawn 'zero thermal emission' claim is back"),
        (r"(?i)total\s+(?:heat|energy)\s+of\s+[0-9]",
         "a computed total heat/energy figure is present"),
    ]
    hit = False
    for pattern, msg in forbidden:
        if re.search(pattern, text):
            fail("L6: %s" % msg)
            hit = True
    if not hit:
        ok("L6  no energy total is claimed anywhere in the document")

    # --- X1..X5: the same claim in the two other documents that carry it ---
    cross = [
        ("ANTI_INFINITY_BLINDSPOT.md", CROSS_AIB),
        ("MSAF_COSMOLOGY_DECONSTRUCTION (2).md", CROSS_MSAF),
    ]
    for fname, spec in cross:
        path = os.path.join(HERE, fname)
        if not os.path.isfile(path):
            fail("X?: %s is missing -- the cross-document fix is gone" % fname)
            continue
        try:
            body = io.open(path, encoding="utf-8").read()
        except Exception as exc:
            fail("X?: cannot read %s: %s" % (fname, exc))
            continue

        for pattern, why in spec["present"]:
            if re.search(pattern, body):
                ok("X   %s: %s" % (fname, why))
            else:
                fail("X   %s: %s is missing" % (fname, why))

        for pattern, why in spec["absent"]:
            if re.search(pattern, body):
                fail("X   %s: %s" % (fname, why))
            else:
                ok("X   %s: absent as required (%s)" % (fname, why))

        # numeric claim, if the document makes one
        T = None
        if spec.get("T_pattern"):
            tm = re.search(spec["T_pattern"], body)
            if tm:
                whole, frac = tm.group(1), tm.group(2)
                T = mp.mpf(int(whole) * 10 ** len(frac) + int(frac)) / 10 ** len(frac)
            else:
                fail("X   %s: the temperature the number is quoted at is not stated"
                     % fname)
        for pattern in spec.get("numbers", []):
            m = re.search(pattern, body)
            if not m:
                fail("X   %s: declared number not found (%s)" % (fname, pattern))
                continue
            if T is None:
                fail("X   %s: no temperature to check the number against" % fname)
                continue
            g = m.groups()
            agree("X   %s number" % fname[:18], tex_sci(g),
                  k_b * mp.log(2) * T, declared_nsig(g))

    print()
    if failures:
        print("LANDAUER CHECK: %d FAILURE(S)" % len(failures))
        return EXIT_FAIL
    print("LANDAUER CHECK: every section 3 Landauer claim reproduced.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
