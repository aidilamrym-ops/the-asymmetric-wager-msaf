"""Gate the single canonical definition of Z_none across every document that names it.

F1-L (CONFIRMED, NOTED) recorded that two different objects shared one label:

  * Skill.md and DEFINISI_OPERASIONAL_MSAF.md defined the zone as the open pixel
        Z_none = { x : 0 < |x - x0| < Delta_univ }
  * the DRAF sensitivity table labelled the five integer pixel shifts
        x = x0 + n * Delta_univ,  n = 1..5
    as the "NON-EXISTENCE ZONE".

Those sets are disjoint.  Every table row sits at distance >= Delta_univ, so the
strict inequality excludes every one of them; the zone itself is non-operational
and is never evaluated, so it has no rows at all.  The manifesto meanwhile
defined the zone as "domain of space below 10^-62", which is a magnitude, not a
set.  msaf_visual.py titled its stem plot "Zone of Non-Existence" over the same
n = 1..5 sweep.

F2-2 fixes this by naming one definition of record and pointing everything else
at it.  This checker makes that fix stick: it reads the set out of the glossary,
normalises it, and requires every other document to reproduce the normalised set
exactly or not to claim one.  A document that drifts back to a paraphrase fails.

Checks
  Z1  canonical definition present and strict in DEFINISI_OPERASIONAL_MSAF.md
  Z2  Skill.md reproduces the canonical set
  Z3  CONSOLIDATED_MASTER_MANIFESTO.md reproduces the canonical set
  Z4  no document may still carry the ambiguous "NON-EXISTENCE ZONE" label
  Z5  the DRAF sweep rows must say OUTSIDE the zone, all five of them, n = 1..5
  Z6  the DRAF reading note that separates the sweep from the zone is present
  Z7  msaf_visual.py titles its plot as a sweep outside the zone
  Z8  the zone stays non-operational: the prohibition is stated

Exit 0 = every claim verified.  Exit 1 = a definition drifted or a label is back.
Exit 2 = tool not run (a required document is unavailable).

usage: python znone_check.py
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXIT_OK, EXIT_FAIL, EXIT_NOTRUN = 0, 1, 2

GLOSSARY = "DEFINISI_OPERASIONAL_MSAF.md"
SKILL = "Skill.md"
MANIFESTO = "CONSOLIDATED_MASTER_MANIFESTO.md"
DRAF = "DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md"
VISUAL = "msaf_visual.py"

# The normalised form of the canonical set.  After stripping whitespace,
# |, \lvert, \rvert and renaming x_0 -> x0 and \Delta_{\text{univ}} -> D,
# every correct rendering collapses to this substring.
CANON = "0<x-x0<D"      # normalise() strips |, \lvert and \rvert, so no pipes here

failures = []
passes = 0


def ok(msg):
    global passes
    passes += 1
    print("  ok    %s" % msg)


def fail(msg):
    failures.append(msg)
    print("  FAIL  %s" % msg)


def load(name):
    path = os.path.join(HERE, name)
    if not os.path.isfile(path):
        fail("%s is missing -- cannot check anything" % name)
        return None
    try:
        return io.open(path, encoding="utf-8").read()
    except Exception as exc:
        fail("%s is unreadable: %s" % (name, exc))
        return None


def normalise(s):
    s = re.sub(r"\s+", "", s)
    for token in ("\\lvert", "\\rvert", "\\left|", "\\right|", "|"):
        s = s.replace(token, "")
    s = s.replace("x_0", "x0").replace("x0", "x0")
    s = s.replace("\\Delta_{\\text{univ}}", "D").replace("\\Delta_{univ}", "D")
    s = s.replace("\\Delta\\_{\\text{univ}}", "D")
    return s


def has_canon(body):
    return CANON in normalise(body)


def main():
    print("=" * 78)
    print("Z_NONE DEFINITION GATE")
    print("=" * 78)

    glossary = load(GLOSSARY)
    skill = load(SKILL)
    manifesto = load(MANIFESTO)
    draf = load(DRAF)
    visual = load(VISUAL)
    if None in (glossary, skill, manifesto, draf, visual):
        print("\nZ_NONE CHECK: TOOL NOT RUN -- %d failure(s)" % len(failures))
        return EXIT_NOTRUN if not failures else EXIT_FAIL

    print("\n--- Z1 the canonical definition, and it must be strict ---------")
    if has_canon(glossary):
        ok("Z1  %s reproduces 0 < |x - x0| < D" % GLOSSARY)
    else:
        fail("Z1  %s no longer states the canonical set" % GLOSSARY)
    norm = normalise(glossary)
    # Test only the Z_none expression: the glossary also states an unrelated
    # \ell_P <= \Delta <= D_obs bound, and a whole-document <= scan trips on it.
    # "\le" must not be matched inside "\left" either.
    if re.search(r"0(?:<=|\\le)x-x0|x-x0(?:<=|\\le)D", norm):
        fail("Z1  the canonical inequality is no longer strict on both ends -- "
             "an <= would admit the anchor or the pixel boundary")
    else:
        ok("Z1  both inequalities are strict (0 < ... < D)")
    if re.search(r"canonical definition of record", glossary):
        ok("Z1  the glossary declares itself the definition of record")
    else:
        fail("Z1  the glossary no longer declares itself the definition of record")

    print("\n--- Z2/Z3 every document that names the set must reproduce it --")
    for name, body in ((SKILL, skill), (MANIFESTO, manifesto)):
        if has_canon(body):
            ok("%s reproduces the canonical set" % name[:30])
        else:
            fail("%s does not reproduce the canonical set -- it has drifted "
                 "to a paraphrase" % name)

    print("\n--- Z4 the ambiguous label must be gone everywhere --------------")
    for name, body in ((DRAF, draf), (VISUAL, visual), (SKILL, skill),
                       (MANIFESTO, manifesto), (GLOSSARY, glossary)):
        if "NON-EXISTENCE ZONE" in body:
            fail("Z4  %s still carries the ambiguous 'NON-EXISTENCE ZONE' label"
                 % name)
        else:
            ok("Z4  %s: no ambiguous label" % name[:44])

    print("\n--- Z5 the DRAF sweep rows are OUTSIDE the zone, n = 1..5 -------")
    rows = []
    for ln in draf.split("\n"):
        f = ln.split("\t")
        if len(f) == 4 and "OUTSIDE" in f[3]:
            m = re.match(r"\s*([0-9]+)", f[1])
            rows.append(int(m.group(1)) if m else None)
    if rows == [1, 2, 3, 4, 5]:
        ok("Z5  five sweep rows, n = 1..5, all labelled OUTSIDE the zone")
    elif rows:
        fail("Z5  sweep rows found but not exactly n = 1..5 in order: %r" % rows)
    else:
        fail("Z5  no OUTSIDE sweep rows found in the DRAF table")
    claiming = [ln for ln in draf.split("\n")
                if len(ln.split("\t")) == 4
                and re.search(r"\bIN\s+\$?\\mathcal", ln.split("\t")[3])]
    if claiming:
        fail("Z5  %d row(s) claim membership of the zone" % len(claiming))
    else:
        ok("Z5  no row claims membership of the zone")

    print("\n--- Z6 the reading note that separates sweep from zone ---------")
    for probe, why in (
        (r"No row of the table above\s+\n?\s*lies \*?inside", "the no-row-inside statement"),
        (r"non-operational.*?no rows", "the reason the zone has no rows"),
        (r"n = 1\\ldots5", "the sweep is identified as n = 1..5"),
    ):
        if re.search(probe, draf, re.S):
            ok("Z6  %s" % why)
        else:
            fail("Z6  %s is missing from the DRAF reading note" % why)

    print("\n--- Z7 msaf_visual titles the plot honestly --------------------")
    # Only plt.title() calls count: the fix record in the comment above
    # deliberately quotes the withdrawn title, exactly as a retraction does.
    # The file has two subplots, so there is more than one title by design.
    titles = [ln for ln in visual.split("\n") if "plt.title(" in ln]
    bad = [t for t in titles if "Zone of Non-Existence" in t]
    if bad:
        fail("Z7  the stem plot is still titled 'Zone of Non-Existence' "
             "over points that are outside it")
    elif titles:
        ok("Z7  no title calls the sweep the zone")
    else:
        fail("Z7  msaf_visual.py has no plt.title() at all")
    # In the source file the title is written with doubled backslashes,
    # because it is a raw matplotlib string: Z}_{\\text{none}}
    if any("OUTSIDE" in t and "Z}_{\\\\text{none}}" in t for t in titles):
        ok("Z7  one of the titles is a sweep outside the zone")
    else:
        fail("Z7  no title describes the sweep as outside the zone")

    print("\n--- Z8 the zone stays non-operational --------------------------")
    # Keyed on the actual prohibition sentences, not on the word
    # "non-operational": that word also sits in Skill.md's table row, so a
    # check for it alone let a mutant delete the real rule in Skill.md line 64
    # and still pass.
    Z8_RULES = (
        (SKILL, skill, r"No evaluating functions/limits/eigenvalues inside",
         "the rule against evaluating inside the zone"),
        (GLOSSARY, glossary,
         r"strictly forbidden from evaluating functions",
         "the Data Access Status prohibition"),
    )
    for name, body, probe, why in Z8_RULES:
        if re.search(probe, body, re.I):
            ok("Z8  %s: %s" % (name[:44], why))
        else:
            fail("Z8  %s no longer states %s" % (name, why))

    print("\n" + "=" * 78)
    if failures:
        print("Z_NONE CHECK: FAIL -- %d condition(s) not met:" % len(failures))
        for f in failures:
            print("  - %s" % f)
        print("TOOL STATUS: text comparison only; no solver involved.")
        return EXIT_FAIL
    print("Z_NONE CHECK: %d conditions met -- one definition, everywhere." % passes)
    print("TOOL STATUS: text comparison only; no solver involved.")
    print("lean/coqc/isabelle/dkcheck/z3 NOT RUN.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
