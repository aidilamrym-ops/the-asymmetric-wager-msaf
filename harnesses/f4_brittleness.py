# -*- coding: utf-8 -*-
"""Audit how brittle each EXTERNAL authority pattern in the F4 gate is.

A pattern that only matches one spelling lets a real borrowed-authority claim
pass unregistered.  For every pattern we try natural paraphrases and report
the ones that would slip through.

Exit 0 = no miss (informational; this is a probe, not a gate).
"""
import io, os, re, sys

ROOT = r"D:\THE ASYMMETRIC WAGER"
sys.path.insert(0, ROOT)
import theorem_provenance_check as T

VARIANTS = {
    "ZENO":       ["Zeno's paradoxes", "the Zeno paradox", "Zeno argued",
                   "Zeno of Elea", "Zeno"],
    "DENSITY":    ["the rationals are dense", "dense in the real line",
                   "dense subset of R"],
    "COUNTADD":   ["countably additive", "countable additivity",
                   "sigma-additivity", "countable sums of measures"],
    "LEBESGUE":   ["Lebesgue measure", "Lebesgue integration"],
    "BROUWER":    ["Brouwer", "Brouwerian", "intuitionism", "intuitionistic"],
    "STRICTFIN":  ["strict finitism", "strict finitist"],
    "CONSTRMATH": ["constructive mathematics", "constructivism"],
    "HAWKPEN":    ["Hawking-Penrose", "Hawking and Penrose",
                   "Penrose-Hawking", "Hawking-Penrose singularity theorem",
                   "the Penrose and Hawking theorem"],
    "LANDAUER":   ["Landauer", "Landauer's principle", "Landauer limit"],
    "MILLENNIUM": ["Millennium Prize", "Clay Millennium", "Millennium Problem"],
    "NAVIER":     ["Navier-Stokes", "Navier Stokes", "Navier-Stokes equations"],
    "LANGLANDS":  ["Langlands", "Langlands program", "Langlands correspondence"],
    "IHARA":      ["Ihara", "Ihara zeta function"],
    "GALOIS":     ["Galois group", "Galois theory"],
    "RENORMAL":   ["renormalization", "renormalisation", "renormalization group"],
    "UVCATA":     ["ultraviolet catastrophe", "UV catastrophe"],
    "WIMP":       ["WIMP", "WIMPs", "weakly interacting massive particles"],
    "SHANNON":    ["Shannon", "Shannon entropy"],
    "RAYLEIGH":   ["Rayleigh", "Rayleigh-Jeans"],
    "GR":         ["general relativity", "General Relativity"],
    "GODEL":      ["G\u00f6del", "Godel", "G\u00f6del's incompleteness"],
}


def main():
    print("=" * 90)
    print("F4 PATTERN BRITTLENESS AUDIT -- natural paraphrases vs EXTERNAL rules")
    print("=" * 90)
    print("patterns defined: %d, variants tested: %d"
          % (len(T.EXTERNAL), sum(len(v) for v in VARIANTS.values())))
    print()

    missing = [k for k in VARIANTS if k not in T.EXTERNAL]
    untested = [k for k in T.EXTERNAL if k not in VARIANTS]
    if missing:
        print("!! variants defined for keys with no pattern: %s" % ", ".join(missing))
    if untested:
        print("!! patterns with no variants defined: %s" % ", ".join(untested))
    print()

    misses = 0
    for key in sorted(VARIANTS):
        pat = T.EXTERNAL.get(key)
        if pat is None:
            continue
        try:
            rx = re.compile(pat)
        except re.error as exc:
            print("FAIL  %-10s pattern does not compile: %s" % (key, exc))
            misses += 1
            continue
        bad = [v for v in VARIANTS[key] if not rx.search(v)]
        if bad:
            misses += len(bad)
            print("FAIL  %-10s %d/%d paraphrases slip through unregistered:"
                  % (key, len(bad), len(VARIANTS[key])))
            for b in bad:
                print("        - %r  does not match  %s" % (b, pat))
        else:
            print("ok    %-10s all %d paraphrases detected"
                  % (key, len(VARIANTS[key])))

    print()
    if misses:
        print("BRITTLENESS: %d paraphrases would go unregistered -- "
              "the coverage check P3 has holes." % misses)
        return 1
    print("BRITTLENESS: clean -- every paraphrase of every authority is caught.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
