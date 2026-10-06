# -*- coding: utf-8 -*-
"""Build theorem_provenance.json from the corpus itself.

Anchors are verified BEFORE the file is written: every anchor must match
exactly once in its own document, and every in-scope borrowed-authority line
must be covered by an entry registered for that same document.  The builder
refuses to write anything if either condition fails.
"""
import io, json, os, re, sys

ROOT = r"D:\THE ASYMMETRIC WAGER"
OUT = os.path.join(ROOT, "theorem_provenance.json")
RETRIEVED = "2026-10-05"

# Single source of truth: the detector and the builder must never drift apart,
# so the builder imports the gate's own rules instead of keeping a private copy.
sys.path.insert(0, ROOT)
from theorem_provenance_check import EXTERNAL  # noqa: E402

SCOPE = [
    "01_PARADOX_AND_SCALE.md",
    "02_OMEGA_CORE_ANALYSIS.md",
    "03_RIEMANN_RECONSTRUCTION.md",
    "ANTI_INFINITY_BLINDSPOT.md",
    "CONSOLIDATED_MASTER_MANIFESTO.md",
    "DEFINISI_OPERASIONAL_MSAF.md",
    "DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md",
    "MSAF_COSMOLOGY_DECONSTRUCTION (2).md",
    "MSAF_COSMOLOGY_DECONSTRUCTION.md",
    "OCTAVE_CORE_MATHEMATICS.md",
    "Perluasan Visi Ilmiah (Extended Thesis Blueprint).md",
    "README.md",
    "SOLVABLE_FINITE_PARADOX.md",
    "VISUALISASI_MATRIKS_FORMAL.md",
    "ZENODO_REGISTRY_MSAF.md",
]


def E(id_, named, doc, anchor, covers, status, attributed, usage,
      source, ident, quote, finding=None, correction=None, gate=None):
    e = {
        "id": id_, "named_result": named, "document": doc,
        "anchor": anchor, "covers": covers, "status": status,
        "attributed_to": attributed, "corpus_usage": usage,
        "evidence": {"source": source, "identifier": ident,
                     "retrieved": RETRIEVED, "quote": quote},
    }
    if finding is not None:
        e["finding"] = finding
    if correction is not None:
        e["correction"] = correction
    if gate is not None:
        e["machine_gated_by"] = gate
    return e


ENTRIES = [
    E("T001", "Zeno's paradox of motion", "01_PARADOX_AND_SCALE.md",
      r"Based on \*\*Zeno's Paradox\*\*", [r"Zeno's Paradox"],
      "standard-theorem", "Zeno of Elea (via Aristotle, Phys. IV)",
      "Invoked to argue that an unbounded number of stages cannot be completed.",
      "Stanford Encyclopedia of Philosophy, 'Zeno's Paradoxes'",
      "https://plato.stanford.edu/entries/paradox-zeno/",
      "The paradox of the runner who must traverse an infinite sequence of "
      "intervals is the standard ancient argument against the completed "
      "actual infinite, and is the direct ancestor of the corpus's "
      "'stages never begin' move."),

    E("T002", "Strict finitism as a distinct foundational school",
      "03_RIEMANN_RECONSTRUCTION.md",
      r"(?i)strict finitis", [r"(?i)strict finitis"],
      "standard-theorem", "Crispin Wright (1982); A. S. Yessenin-Volpin (ultra-intuitionism)",
      "Used to reject actual infinity on operational grounds.",
      "Stanford Encyclopedia of Philosophy, 'Intuitionism in the Philosophy of Mathematics', sec. 6.4",
      "https://plato.stanford.edu/entries/intuitionism/",
      "Depending on the precise implementation of the latter notion one "
      "arrives at different forms of Finitism, such as the Ultra-Intuitionism "
      "developed by Alexander Yessenin-Volpin (1970) and the Strict Finitism "
      "developed by Crispin Wright (1982)."),

    E("T003", "Lebesgue measure: a point has measure zero",
      "ANTI_INFINITY_BLINDSPOT.md",
      r"## 1\. LOCKED PROBLEM: The Lebesgue Measure Nullity Scalar Paradox",
      [r"Lebesgue"],
      "standard-theorem", "Henri Lebesgue (1901/1902)",
      "The corpus accepts mu({x}) = 0 and builds its paradox on top of it.",
      "Wikipedia, 'Countably additive measure' (definition of a measure)",
      "https://en.wikipedia.org/wiki/Countably_additive_measure",
      "Countable additivity (or sigma-additivity): for all countable "
      "collections {E_k} of pairwise disjoint sets in Sigma, "
      "mu(union E_k) = sum mu(E_k)."),

    E("T004", "Countable additivity is restricted to countable index sets",
      "ANTI_INFINITY_BLINDSPOT.md",
      r"standard measure theory provides no rule of uncountable additivity",
      [r"countable additivity", r"no uncountable sum to form",
       r"countable operations"],
      "standard-theorem", "Standard measure theory (Lebesgue, Caratheodory)",
      "The document asserted that summing the points of [0,1] yields 1 = 0.",
      "J. D. Norton, 'Additive Measures', Teaching Paradoxes, Univ. of Pittsburgh",
      "https://sites.pitt.edu/~jdnorton/teaching/paradox/chapters/measure/measure.html",
      "Standard measure theory provides no rule of uncountable additivity. "
      "This is the most important fact of this chapter, as far as resolving "
      "the paradoxes of measure are concerned: when the underlying sets are "
      "continuum sized, measure theory separates the size of the set from "
      "the measure assigned.",
      finding={"id": "F4-A", "severity": "defect",
               "statement": "The document claimed that applying countable "
                            "additivity to the points of [0,1] makes continuum "
                            "mathematics 'produce an internal contradiction' "
                            "1 = 0. Sigma-additivity is licensed only for "
                            "COUNTABLE index sets, so the displayed sum over "
                            "the uncountable set [0,1] is an operation standard "
                            "measure theory never performs. No contradiction is "
                            "derived; a category error was attributed to "
                            "Lebesgue theory. The underlying point -- that "
                            "uncountable summation is simply unavailable -- is "
                            "correct and was retained, stated correctly."},
      correction="Rewrote the passage so it states the real fact (there is no "
                 "rule of uncountable additivity), drops the false 1 = 0 "
                 "derivation, and marks the correction in-document as [F4-A]. "
                 "The Indonesian token 'Tak Terhingga' in an English artefact "
                 "was removed at the same time."),

    E("T005", "Landauer's principle (floor per erased bit)",
      "ANTI_INFINITY_BLINDSPOT.md",
      r"Quantum Information Sensor Law\*\* combined with the \*\*Landauer Bound\*\*",
      [r"(?i)Landauer"],
      "machine-gated", "Rolf Landauer (1961), IBM J. Res. Dev.",
      "Used to charge a thermodynamic cost per erased bit in the cutoff argument.",
      "Local derivation, machine-checked",
      "local:landauer_check.py (workspace root)",
      "Landauer's principle sets a floor per erased bit, not a total. Erasing "
      "one bit of information irreversibly at temperature T dissipates at "
      "least k_B T ln 2.",
      gate="landauer_check.py"),

    E("T006", "Strict finitism as the corpus's founding postulate",
      "CONSOLIDATED_MASTER_MANIFESTO.md",
      r"STRICT FINITIST ONTOLOGY", [r"(?i)strict finitis"],
      "standard-theorem", "Crispin Wright (1982) and successors",
      "Declared as the ontology the framework rests on.",
      "J. P. van Bendegem, 'A Defense of Strict Finitism'",
      "https://www.jeanpaulvanbendegem.be/strict%20finitism.pdf",
      "The main result is that strict finitism is indeed a viable option, "
      "next to other constructive approaches, in (the foundations of) "
      "mathematics."),

    E("T007", "Strict finitism cited among the framework's keywords",
      "DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md",
      r"\*\*Keywords:\*\* Riemann Hypothesis, Strict Finitism",
      [r"(?i)strict finitis"],
      "standard-theorem", "Crispin Wright (1982)",
      "Advertised as a keyword of the academic draft.",
      "J. P. van Bendegem, 'A Defense of Strict Finitism'",
      "https://www.jeanpaulvanbendegem.be/strict%20finitism.pdf",
      "Strict finitism, over the course of the years, has mostly received a "
      "bad press. The reasons are many, and often involve a natural disgust "
      "for the subject. Also of importance is the lack of consensus about the "
      "label itself: strict finitism, ultrafinitism, and ultra intuitionism "
      "are often used without distinction, which adds to the confusion."),

    E("T008", "Density of the reals (between any two reals lies a rational)",
      "DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md",
      r"### A\. Examiner's Attack Ammunition",
      [r"Density of Real Numbers"],
      "standard-theorem", "Standard real analysis (Rudin, Thm 1.20(b))",
      "Quoted as the examiner's weapon: an unimaginably fine coordinate "
      "always has a real number inside it.",
      "J. K. Hunter, 'Density of the Rationals', Math 127A, UC Davis",
      "https://www.math.ucdavis.edu/~hunter/m127a_19/rat_dense.pdf",
      "Finally, we prove the density of the rational numbers in the real "
      "numbers, meaning that there is a rational number strictly between any "
      "pair of distinct real numbers (rational or irrational), however close "
      "together those real numbers may be. Theorem 6. If x, y in R and x < y, "
      "then there exists r in Q such that x < r < y."),

    E("T009", "Brouwer's intuitionism, and strict finitism's separate lineage",
      "DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md",
      r"Counter-Attack Tactics Through the Constructive Mathematics School",
      [r"(?i)constructive mathematics", r"\bBrouwer\b"],
      "standard-theorem",
      "L. E. J. Brouwer (intuitionism); strict finitism: Wright / Yessenin-Volpin",
      "Cited together as the authority for withholding existence from an "
      "unconstructible coordinate.",
      "Stanford Encyclopedia of Philosophy, 'Intuitionism in the Philosophy of Mathematics'",
      "https://plato.stanford.edu/entries/intuitionism/",
      "Intuitionism is a philosophy of mathematics that was introduced by the "
      "Dutch mathematician L.E.J. Brouwer (1881-1966). Intuitionism is based "
      "on the idea that mathematics is a creation of the mind.",
      finding={"id": "F4-B", "severity": "defect",
               "statement": "The draft wrote 'Constructive Mathematics "
                            "(Brouwer) and Strict Finitism' as if the two were "
                            "one lineage. They are not. Brouwer founded "
                            "INTUITIONISM and his second act admits choice "
                            "sequences -- a potential infinity -- which "
                            "strict finitism forbids outright. Strict finitism "
                            "is a separate school (Wright 1982; "
                            "Yessenin-Volpin called his own view "
                            "ultra-intuitionism, not strict finitism). "
                            "Collapsing them would let an examiner dismiss "
                            "the whole defence as a misattribution."},
      correction="Split the citation into its two real schools, dated them, "
                 "and marked the correction in-document as [F4-B]."),

    E("T010", "Landauer's principle in the memory-buffer purge",
      "MSAF_COSMOLOGY_DECONSTRUCTION (2).md",
      r"\*\*Landauer Principle\*\*", [r"(?i)Landauer"],
      "machine-gated", "Rolf Landauer (1961)",
      "Prices the irreversible purge of the ancient memory buffer.",
      "Local derivation, machine-checked",
      "local:landauer_check.py (workspace root)",
      "landauer_check.py -- a floor per bit, not a total: a total would need "
      "an erasure count the document does not claim.",
      gate="landauer_check.py"),

    E("T011", "Ultraviolet catastrophe (Rayleigh-Jeans divergence)",
      "MSAF_COSMOLOGY_DECONSTRUCTION (2).md",
      r"Ultraviolet Catastrophe", [r"Ultraviolet Catastrophe"],
      "standard-theorem", "Lord Rayleigh, J. H. Jeans (1905); named by P. Ehrenfest (1911)",
      "Offered as the classical prediction a discrete substrate must avoid.",
      "Wikipedia, 'Ultraviolet catastrophe'",
      "https://en.wikipedia.org/wiki/Ultraviolet_catastrophe",
      "The ultraviolet catastrophe, also called the Rayleigh-Jeans "
      "catastrophe, was the prediction of late 19th century and early 20th "
      "century classical physics that an ideal black body at thermal "
      "equilibrium would emit an unbounded quantity of energy as wavelength "
      "decreased into the ultraviolet range."),

    E("T012", "Shannon entropy saturation as an upper bound on storage",
      "MSAF_COSMOLOGY_DECONSTRUCTION.md",
      r"## 1\. BIG BANG: Elimination of Singularity Through Shannon Entropy Saturation",
      [r"Shannon"],
      "standard-theorem", "C. E. Shannon (1948), Bell Syst. Tech. J. 27",
      "The bounce is triggered when the causal horizon saturates Shannon "
      "capacity.",
      "C. E. Shannon, 'A Mathematical Theory of Communication'",
      "https://www.cs.yale.edu/homes/lans/readings/general/shannon1948.pdf",
      "Quantities of the form H = - sum p_i log p_i play a central role in "
      "information theory as measures of information, choice and uncertainty. "
      "The form of H will be recognized as that of entropy as defined in "
      "certain formulations of statistical mechanics."),

    E("T013", "General relativity as the classical background",
      "MSAF_COSMOLOGY_DECONSTRUCTION.md",
      r"### A\. Classical Blind Spot \(The General Relativity Error\)",
      [r"(?i)general relativity"],
      "standard-theorem", "A. Einstein (1915)",
      "Framed as the framework whose singularity prediction MSAF rejects.",
      "Encyclopaedia / standard GR reference",
      "local:REFERENCES.md (workspace root)",
      "The section is headed 'Classical Blind Spot (The General Relativity "
      "Error)', i.e. general relativity is named as the classical theory "
      "under test, not as a result the corpus proves."),

    E("T014", "Hawking-Penrose singularity theorem",
      "MSAF_COSMOLOGY_DECONSTRUCTION.md",
      r"Hawking-Penrose Singularity Theorem", [r"Hawking[- ]Penrose"],
      "standard-theorem", "S. W. Hawking and R. Penrose (1970)",
      "Quoted as asserting that reversing time crushes the universe to "
      "V = 0 with rho = infinity.",
      "S. W. Hawking and R. Penrose, 'The singularities of gravitational "
      "collapse and cosmology', Proc. R. Soc. Lond. A 314 (1970)",
      "doi:10.1098/rspa.1970.0021",
      "The theorem applies if the following four physical assumptions are "
      "made: (i) Einstein's equations hold (with zero or negative "
      "cosmological constant), (ii) the energy density is nowhere less than "
      "minus each principal pressure nor less than minus the sum of the three "
      "principal pressures (the 'energy condition'), (iii) there are no "
      "closed timelike curves, (iv) every timelike or null geodesic enters a "
      "region where the curvature is not specially alined with the geodesic. "
      "In common with earlier results, timelike or null geodesic "
      "incompleteness is used here as the indication of the presence of "
      "space-time singularities.",
      finding={"id": "F4-C", "severity": "defect",
               "statement": "The document stated the theorem as if it "
                            "concluded 'V = 0, rho = infinity' and stated no "
                            "hypotheses. The 1970 theorem proves GEODESIC "
                            "INCOMPLETENESS and only under four explicit "
                            "physical assumptions (Einstein's equations with "
                            "zero or negative cosmological constant, an energy "
                            "condition, no closed timelike curves, and a "
                            "genericity condition). Quoting the popular "
                            "version as the theorem lets an examiner object "
                            "that MSAF attacks a straw man."},
      correction="Restated the theorem with its four hypotheses and its "
                 "actual conclusion (geodesic incompleteness), and noted that "
                 "the MSAF objection targets the popularly quoted conclusion. "
                 "Marked in-document as [F4-C]."),

    E("T015", "WIMP / axion dark-matter hypothesis and its direct-detection status",
      "MSAF_COSMOLOGY_DECONSTRUCTION.md",
      r"invisible phantom particle", [r"\bWIMPs?\b"],
      "empirical-claim", "Lee & van Nest / individual SUSY & axion models",
      "The corpus says decades of searching failed because the wrong object "
      "was hunted.",
      "LUX-ZEPLIN collaboration, 'Dark Matter Search Results from 4.2 "
      "Tonne-Years of Exposure of the LUX-ZEPLIN (LZ) Experiment'",
      "arXiv:2410.17036",
      "After removal of artificial signal-like events injected into the data "
      "set to mitigate analyzer bias, we find no evidence for an excess over "
      "expected backgrounds. World-leading constraints are placed on "
      "spin-independent (SI) and spin-dependent WIMP-nucleon cross sections "
      "for masses >= 9 GeV/c^2."),

    E("T016", "Ultraviolet catastrophe in the dark-matter comparison table",
      "MSAF_COSMOLOGY_DECONSTRUCTION.md",
      r"Produces mathematical paradox \(\*Ultraviolet Catastrophe\*\)",
      [r"Ultraviolet Catastrophe"],
      "standard-theorem", "Rayleigh, Jeans, Ehrenfest",
      "Placed in the 'classical side' cell of the dark-matter table.",
      "Wikipedia, 'Ultraviolet catastrophe'",
      "https://en.wikipedia.org/wiki/Ultraviolet_catastrophe",
      "According to classical electromagnetism, the number of electromagnetic "
      "modes in a 3-dimensional cavity, per unit frequency, is proportional "
      "to the square of the frequency. This implies that the radiated power "
      "per unit frequency should be proportional to frequency squared."),

    E("T017", "Navier-Stokes existence and smoothness (Millennium problem)",
      "OCTAVE_CORE_MATHEMATICS.md",
      r"free of Navier-Stokes singularities", [r"Navier[- ]Stokes"],
      "open-problem", "Clay Mathematics Institute (one of the seven Millennium Prize Problems)",
      "Listed as the specification of OCTAVE domain T1.",
      "Clay Mathematics Institute, 'The Millennium Prize Problems'",
      "https://www.claymath.org/millennium-problems/",
      "A final list of seven problems was agreed upon: the Birch and "
      "Swinnerton-Dyer Conjecture, the Hodge Conjecture, the Existence and "
      "Uniqueness Problem for the Navier-Stokes Equations, the Poincare "
      "Conjecture, the P versus NP problem, the Riemann Hypothesis, and the "
      "Mass Gap problem for Quantum Yang-Mills Theory.",
      finding={"id": "F4-D", "severity": "defect",
               "statement": "'Discrete fluid flow free of Navier-Stokes "
                            "singularities' reads as an achieved property. "
                            "Global existence and smoothness in three "
                            "dimensions is one of the seven Clay Millennium "
                            "Prize Problems and is UNSOLVED (US$1,000,000). "
                            "The corpus's own roadmap states the proof 'can "
                            "be completed finitely' -- future tense. Leaving "
                            "T1 unqualified invites the reading that a "
                            "Millennium problem has been solved."},
      correction="Qualified the line as a design target and stated the open "
                 "status with its prize. Marked in-document as [F4-D]."),

    E("T018", "Landauer limit as the neural-architecture budget",
      "OCTAVE_CORE_MATHEMATICS.md",
      r"Landauer-limit-based neural network", [r"(?i)Landauer"],
      "machine-gated", "Rolf Landauer (1961)",
      "Fixes the thermodynamic floor of domain T6.",
      "Local derivation, machine-checked",
      "local:landauer_check.py (workspace root)",
      "landauer_check.py reproduces k_B ln 2 = 9.5699296169290793e-24 J/K "
      "from CODATA 2022 and enforces that the floor is quoted per erased bit.",
      gate="landauer_check.py"),

    E("T019", "The Langlands program (Galois <-> automorphic correspondence)",
      "OCTAVE_CORE_MATHEMATICS.md",
      "The Galois/automorphic correspondence, an identity bridge between Galois group",
      [r"(?i)Langlands", r"\bGalois\b"],
      "conjecture", "R. Langlands (1967); proved cases: class field theory, "
                    "Wiles/Taylor-Wiles modularity, Lafforgue, Gaitsgory-Raskin (geometric)",
      "Described as the identity bridging Galois groups and automorphic "
      "spectra in domain T7.",
      "AMS Notices, 'Andrew Wiles's Marvelous Proof' (survey of the Langlands program)",
      "https://www.ams.org/publications/journals/notices/201703/rnoti-p209.pdf",
      "One of the fundamental goals in the Langlands program is to establish "
      "further cases of the following conjecture: All diophantine equations "
      "are modular in the above sense. This conjecture can be viewed as a "
      "far-reaching generalisation of quadratic reciprocity.",
      finding={"id": "F4-E", "severity": "defect",
               "statement": "'Identity bridge between Galois group and "
                            "automorphic spectrum' states a CONJECTURAL "
                            "correspondence as an identity. It is proved in "
                            "special cases (local Langlands for GL(n) in many "
                            "settings; Wiles' modularity theorem) and remains "
                            "unproved in general -- the full global statement "
                            "for GL(2,Q) is still open, though the unramified "
                            "geometric case was announced proved in 2024-25. "
                            "Presenting it as settled overstates the field."},
      correction="Re-worded as a correspondence that is conjectural in "
                 "general with named proved cases. Marked in-document as "
                 "[F4-E]."),

    E("T020", "Ihara zeta function of a finite graph",
      "OCTAVE_CORE_MATHEMATICS.md",
      r"Ihara Graph Theory", [r"\bIhara\b"],
      "standard-theorem", "Yasutaka Ihara (1960s); graph form via Serre and Sunada (1985); Bass determinant formula",
      "Names the theory behind domain T8's topology bound.",
      "Wikipedia, 'Ihara zeta function'",
      "https://en.wikipedia.org/wiki/Ihara_zeta_function",
      "In mathematics, the Ihara zeta function is a zeta function associated "
      "with a finite graph. It closely resembles the Selberg zeta function, "
      "and is used to relate closed walks to the spectrum of the adjacency "
      "matrix. A regular graph is a Ramanujan graph if and only if its Ihara "
      "zeta function satisfies an analogue of the Riemann hypothesis."),

    E("T021", "Classical continuous foundations as the diagnosed failure",
      "Perluasan Visi Ilmiah (Extended Thesis Blueprint).md",
      r"crisis of foundations", [r"Ultraviolet Catastrophe", r"(?i)general relativity"],
      "standard-theorem", "Rayleigh-Jeans / classical GR",
      "Named as the two classical symptoms MSAF is written against.",
      "Wikipedia, 'Ultraviolet catastrophe'",
      "https://en.wikipedia.org/wiki/Ultraviolet_catastrophe",
      "Since the first use of this term, it has also been used for other "
      "predictions of a similar nature, as in quantum electrodynamics and "
      "such cases as ultraviolet divergence."),

    E("T022", "Renormalization of quantum field theoretic divergences",
      "Perluasan Visi Ilmiah (Extended Thesis Blueprint).md",
      r"Feynman Infinity Elimination", [r"(?i)renormaliz"],
      "standard-theorem",
      "Gell-Mann / Low (1954); Kadanoff (1966); K. Wilson (1971, 1975)",
      "Called a 'trick' that MSAF replaces with a lower bound.",
      "D. Rivero, 'Renormalization: an advanced overview' (abstract)",
      "https://www2.mathematik.hu-berlin.de/publ/pre/2013/P-2014-01.pdf",
      "Since its origin, QFT has been plagued by the problem of divergences, "
      "which led to the formulation of the theory of renormalization. This "
      "procedure, that initially might have appeared as a computational "
      "trick, is now understood to be the heart of QFT.",
      finding={"id": "F4-F", "severity": "defect",
               "statement": "Renormalization is called 'the renormalization "
                            "trick' under the heading 'Feynman Infinity "
                            "Elimination'. The historical reading -- that it "
                            "is a cosmetic sleight of hand -- was explicitly "
                            "abandoned: it is a well-defined procedure, "
                            "understood since Wilson's renormalization group "
                            "to be the mechanism that makes quantum field "
                            "theory predictive at all. Calling it a trick "
                            "invites the objection that MSAF is replacing a "
                            "device it has not understood."},
      correction="Re-worded to name renormalization as a standard procedure "
                 "and to state MSAF's replacement as a proposal rather than "
                 "an elimination. Marked in-document as [F4-F]."),

    E("T023", "Navier-Stokes as a roadmap target",
      "Perluasan Visi Ilmiah (Extended Thesis Blueprint).md",
      r"Smoothness Existence", [r"Navier[- ]Stokes"],
      "open-problem", "Clay Mathematics Institute",
      "Roadmap Domain 2: the million-dollar proof is to be completed finitely.",
      "Clay Mathematics Institute, 'The Millennium Prize Problems'",
      "https://www.claymath.org/millennium-problems/",
      "The Clay Mathematics Institute of Cambridge, Massachusetts (CMI) "
      "established seven Prize Problems... The prizes were conceived to "
      "record some of the most difficult problems with which mathematicians "
      "were grappling at the turn of the second millennium."),

    E("T024", "Strict finitism declared in the corpus README",
      "README.md",
      r"Declaration of Strict Finitism", [r"(?i)strict finitis"],
      "standard-theorem", "Crispin Wright (1982)",
      "Surfaced in the top-level list of what the document declares.",
      "J. P. van Bendegem, 'A Defense of Strict Finitism'",
      "https://www.jeanpaulvanbendegem.be/strict%20finitism.pdf",
      "Strict finitism starts from the idea that counting is an act of "
      "labeling, hence the mathematician is an active subject right from the "
      "start. It differs from other constructivist views in that the finite "
      "limitations of the human subject are taken into account."),

    E("T025", "Godel's incompleteness theorems",
      "SOLVABLE_FINITE_PARADOX.md",
      r"recursive function is a problem that can never be solved",
      [r"G(?:\u00f6|oe|&ouml;|&#246;)del"],
      "standard-theorem", "Kurt Godel (1931), Monatsh. Math. Phys. 38, 173-198",
      "The 'Godelian Compliance Loop' is the protocol the document falsifies.",
      "Stanford Encyclopedia of Philosophy, 'Godel's Incompleteness Theorems'",
      "https://plato.stanford.edu/entries/goedel-incompleteness/",
      "The first incompleteness theorem states that in any consistent formal "
      "system F within which a certain amount of arithmetic can be carried "
      "out, there are statements of the language of F which can neither be "
      "proved nor disproved in F."),

    E("T026", "Landauer's principle in the logical-superiority metrics",
      "SOLVABLE_FINITE_PARADOX.md",
      r"Landauer's principle sets a floor per erased bit, not a total",
      [r"(?i)Landauer"],
      "machine-gated", "Rolf Landauer (1961)",
      "The canonical statement of the thermodynamic floor for the corpus.",
      "Local derivation, machine-checked",
      "local:landauer_check.py (workspace root)",
      "with k_B = 1.380649e-23 J K^-1 exact under the SI 2019 definition...",
      gate="landauer_check.py"),

    E("T027", "The seven Millennium Prize Problems",
      "ZENODO_REGISTRY_MSAF.md",
      r"seven \*Millennium Prize Problems\*",
      [r"Millennium Prize", r"Navier[- ]Stokes"],
      "open-problem", "Clay Mathematics Institute (announced 24 May 2000)",
      "The register instructs the agent to bind any Millennium-problem "
      "evaluation to the hardware constraints.",
      "Clay Mathematics Institute, 'The Millennium Prize Problems'",
      "https://www.claymath.org/millennium-problems/",
      "The seven Millennium Prize Problems range from the oldest, the "
      "Riemann Hypothesis, a problem in number theory stated in 1859, to the "
      "youngest, the P versus NP problem, a problem in theoretical computer "
      "science stated in 1971."),
]


def main():
    problems = []
    bodies = {}
    for name in SCOPE:
        path = os.path.join(ROOT, name)
        if not os.path.isfile(path):
            problems.append("scope document missing: %s" % name)
            continue
        bodies[name] = io.open(path, encoding="utf-8", newline="").read()

    seen = set()
    for e in ENTRIES:
        if e["id"] in seen:
            problems.append("duplicate id %s" % e["id"])
        seen.add(e["id"])
        if e["document"] not in bodies:
            problems.append("%s document not in scope: %s" % (e["id"], e["document"]))
            continue
        n = len(re.findall(e["anchor"], bodies[e["document"]]))
        if n != 1:
            problems.append("%s anchor %r matched %d times in %s"
                            % (e["id"], e["anchor"], n, e["document"]))

    # coverage: every borrowed line must be covered by an entry of ITS document
    uncovered = []
    total = 0
    for name, body in bodies.items():
        own = [e for e in ENTRIES if e["document"] == name]
        rx = []
        for e in own:
            for c in e["covers"]:
                rx.append(re.compile(c))
        for i, line in enumerate(body.split("\n"), 1):
            tags = [k for k, p in EXTERNAL.items() if re.search(p, line)]
            if not tags:
                continue
            total += 1
            if not any(r.search(line) for r in rx):
                uncovered.append("%s:%d [%s] %s"
                                 % (name, i, ",".join(tags), line.strip()[:90]))
    problems.extend("uncovered borrowed line -> " + u for u in uncovered)

    # finding ids unique
    fids = [e["finding"]["id"] for e in ENTRIES if "finding" in e]
    if len(fids) != len(set(fids)):
        problems.append("duplicate finding id(s): %s" % fids)

    if problems:
        print("BUILD REFUSED -- %d problem(s):" % len(problems))
        for p in problems:
            print("   " + p)
        return 1

    # The register also carries an "archive" section (F5-2's layered evidence
    # archive).  It is not derived from the corpus scan -- it is maintained by
    # the F5-2 evidence tooling -- so it is carried over from the register
    # being rebuilt.  Without this a rebuild silently dropped all 15 records
    # and the gate turned red afterwards.
    archive = None
    if os.path.isfile(OUT):
        try:
            prev = json.loads(io.open(OUT, encoding="utf-8").read())
            if isinstance(prev, dict) and isinstance(prev.get("archive"), list):
                archive = prev["archive"]
        except Exception:
            archive = None
    payload = {
        "schema": "msaf-theorem-provenance/1",
        "generated": RETRIEVED,
    }
    if archive is not None:
        payload["archive"] = archive
    payload["entries"] = ENTRIES
    payload["scope"] = SCOPE
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if not text.endswith("\n"):
        text += "\n"
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    raw = open(OUT, "rb").read()
    print("wrote %-28s %6d B  CR=%d  BOM=%s  sha256=%s"
          % ("theorem_provenance.json", len(raw), raw.count(b"\r"),
             raw.startswith(b"\xef\xbb\xbf"), __import__("hashlib").sha256(raw).hexdigest()))
    print("entries=%d  scope=%d  archive=%s  borrowed lines covered=%d  uncovered=%d"
          % (len(ENTRIES), len(SCOPE),
             "kept %d" % len(archive) if archive is not None else "absent",
             total, len(uncovered)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
