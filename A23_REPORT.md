# FILE: A23_REPORT.md
# Fase A23 — deep literature survey of residual A10-R1 (the 10^120 vacuum gap).
# Date: 2026-10-08.  Language: English.

---

## 1. Scope and status

This phase is a **documented literature survey**, not a solution attempt. Its
deliverable is this report: a map of what the physics literature has proposed
against the cosmological constant problem, what each proposal's stated limits
are, and how the residual `A10-R1` stands after reading it.

**`A10-R1` remains OPEN after this phase.** Nothing in the survey closes it,
and this report claims no new physics. Every mechanism below is described as
its own authors or reviewers state it, with a citation; where the literature
disagrees, the disagreement is recorded rather than resolved. Web sources were
accessed 2026-10-08.

Method: targeted searches over the problem framing (Weinberg's no-go and the
old/new problem split), each major approach class (symmetry, adjustment,
unimodular, sequestering, degravitation/nonlocal, modified gravity, landscape,
swampland, quantum gravity, entropy/holographic, causal sets, dynamical dark
energy), and the current status statements (PDG 2025, 2025 reviews). Sources
are listed in section 8.

## 2. The problem as this corpus measures it

| Quantity | Registered value | Source |
|---|---|---|
| `PLANCK_VACUUM_DENSITY` | `5.867696e111 J/m^3` (live recompute `5.867696004847416...e111`) | `external_constants.json`, mode `planck_vacuum_cutoff` (`TAHU_A10_REPORT.md` §4) |
| `DARK_ENERGY_DENSITY` | `6e-10 J/m^3` | `WIKIPEDIA_DARK_ENERGY` (Layer A) |
| Ratio | `rho_Planck / rho_Lambda ~ 9.8e120`; `log10 ~ 120.99` | live recompute, `TAHU_A10_REPORT.md` §3.1/§4 |

Machine gates that hold these figures: `tahap_uji_audit.py` (suite gate,
condition V-classes incl. `rho_Lambda` provenance and the live recompute) and
`quantum_censorship_check.py` (A18: Gate 2's arithmetic — Planck-scale
identities and the registered zero-point density). The corpus's own position,
unchanged: **the integral diverges; a finite Planck cutoff is a cutoff, not a
cosmological-constant solution** (`A10-R1` verbatim in `TAHU_A10_REPORT.md`
§7).

The headline exponent is cutoff-dependent in the literature itself: a hard
Planck-cutoff sum gives 120–122 orders of magnitude, while the expected value
of the vacuum energy in dimensional regularisation is quoted near 50–56
orders (Wikipedia, *Cosmological constant problem*, citing Martin 2012; the
corpus number is explicitly the Planck-cutoff figure, which is the one
Weinberg's 1989 framing made famous). The Les Houches 2025 lectures state the
same puzzle as `lambda ~ 10^-122` in Planck units (arXiv:2509.00688).

## 3. The problem's accepted taxonomy

* **Old problem (radiative instability):** quantum corrections shift the
  vacuum energy by `O(m^4)` per new threshold; the bare term must be retuned
  to ~120 decimal places at every order (Padilla, arXiv:1502.05296; Burgess
  notes; Noble 2015 spells the same for the unimodular case).
* **New problem (magnitude and coincidence):** why is the surviving value
  ~`(2.3 meV)^4`, of the same order as the present matter density
  (Weinberg, *The cosmological constant problems*, astro-ph/9610044; PDG 2025).
* **Is vacuum energy even a physical, gravitating quantity?** — the third
  strand: normal ordering / renormalisation as a redefinition (the 2019
  *Symmetry* paper argues the bare value is unobservable; Unruh and
  collaborators argue the problem dissolves when the vacuum is modelled as a
  fluctuating quantum field; Brodsky–Shrock light-front quantisation gives a
  trivial vacuum; see Wikipedia's survey for these positions). This corpus
  followed the mainstream EFT reading in A10: the renormalised value is a
  measured input, and the divergent integral is stated as divergent.
* **Weinberg's no-go (1989):** under FLRW assumptions with ordinary scalar
  fields, adjustment mechanisms cannot cancel `rho_V` without fine-tuning as
  mysterious as the original problem — "so far no one has found a way out of
  this one" (Weinberg, astro-ph/9610044). Every later proposal below is best
  read as an attempted loophole.
* **Scale of the discrepancy:** 120 orders in density = 30 orders in energy
  scale (Trodden–Carroll TASI).

## 4. Survey of approach classes

### 4.1 Symmetry cancellation, supersymmetry
Exact supersymmetry cancels boson/fermion zero-point energies; broken SUSY
leaves `~M_SUSY^4`, solving the problem only "halfway" on a logarithmic scale
(Trodden–Carroll TASI). No known symmetry sets `rho_V = 0` and stays
technically natural ('t Hooft criterion, Burgess notes). Witten's 1995
supersymmetric cancellation idea remains speculative (Weinberg,
astro-ph/9610044). **Status: not a solution.**

### 4.2 Adjustment and relaxation mechanisms
Abbott (Phys. Lett. B 150, 427 (1985)) introduced a compensating scalar
sector that relaxes an initially large positive `Lambda` to near zero with
naturally small parameters — but the paper itself states it "is not clear how
to incorporate this mechanism into a realistic cosmology" (it produces no
matter to fill the relaxed spacetime). Weinberg's no-go (1989) blocks the
general class; Linde's universe multiplication, Coleman's wormholes, the fat
graviton and SLED are reviewed with their difficulties in Padilla
(arXiv:1502.05296). **Status: blocked under stated assumptions; no accepted
loophole.**

### 4.3 Unimodular gravity and constrained gravity
Unimodular gravity promotes `Lambda` to an integration constant not sourced by
a constant vacuum density. The mainstream assessment is that classical UG is
equivalent to GR with an integration-constant `Lambda`, so the radiative
instability simply moves into the integration constant's boundary value:
Noble (Eur. Phys. J. C 75 (2015), doi:10.1140/epjc/s10052-015-3767-0)
states there is "no sense in which it can bring a new perspective"; the 2022
status report (Class. Quantum Grav., doi:10.1088/1361-6382/aca386) finds no
difference between UG and GR beyond the CC treatment. Opposing results exist:
Unruh et al. (Phys. Rev. D 80, 084003 (2009)) argue quantised UG does not
source the huge quantum contributions; the review by Jiroušek et al.
(arXiv:2301.01662) shows the answer hinges on how the initial data / the
four-volume constraint is set — when the Lagrange multiplier's initial value
is fixed by hand the decoupling is spoiled, when it is left free (equivalently
a global constraint on the spacetime four-volume) the old problem is
alleviated, which makes UG closely related to sequestering. Álvarez
(Eur. Phys. J. C 84 (2024), doi:10.1140/epjc/s10052-024-12651-7) shows the
value is fixed by boundary conditions, not by the vacuum energy.
**Status: contested; not an accepted solution.**

### 4.4 Vacuum energy sequestering
Kaloper–Padilla (PRL 112, 091304 (2014); PRD 90, 084023 (2014)) promote the
classical `Lambda` and the sector-scale ratio `lambda` to global variables
with an outside-the-integral term `sigma(Lambda, lambda)`. Diffeomorphism
invariance then forces the vacuum energy of a protected matter sector (taken
to include the Standard Model) to drop out of the field equations at every
loop order; the residual is a radiatively-stable cosmic average, small in an
old, large universe. Stated consequences: spacetime must be finite in
4-volume (future collapse), `w_DE ~ -1` is a transient, phase-transition
contributions are automatically small. Stated limits: graviton loops are
excluded from the protected sector; the mechanism is nonlocal
("acausality" defended in the paper); it is not empirically tested.
**Status: a serious candidate that addresses the old problem under its
assumptions; not established, no observation yet.**

### 4.5 Degravitation and nonlocal IR modifications
Dvali–Hofmann–Khoury (Phys. Rev. D 76, 084006 (2007)) promote `G_N` to a
high-pass filter that degravitates sources with wavelength `>> L` (such as the
cosmological constant); consistency without ghosts forces the graviton to be
massive or a resonance of width `~1/L`, and whether a non-empty consistent
theory exists in that window is left open. Semi-classical realisations via
nonlocal effective actions are developed in arXiv:1003.3010; the JCAP 2009
"afterglow" study (`Degravitation, inflation and the cosmological constant as
an afterglow`) finds `Lambda ~ l_P^2/L^2` suppression but states the
coincidence problem still needs additional tuning. Carroll–Remmen
(Phys. Rev. D 95, 123504 (2017)) cancel the cosmological constant from the
equations with a nonlocal constraint (spacetime average of the Lagrangian set
to zero) plus a free four-form gauge field, consistent with cosmological
bounds. **Status: active model-building; no consensus solution.**

### 4.6 Modified gravity with self-tuning, screening
The 2023 review *Modified Gravity Approaches to the Cosmological Constant
Problem* (Universe 9(2), 63, mdpi.com/2218-1997/9/2/63) organises the field
around loopholes to the no-go theorems: constrained gravity, massive gravity,
Horndeski (breaking vacuum translational invariance), extra dimensions — all
requiring screening mechanisms to survive solar-system tests. Observations
bite: GW170817 fixed the gravitational-wave speed to `c`, the DGP model is
ruled out by several tests, and `f(R)` models are squeezed so close to GR they
cannot accelerate without a separate dark-energy component (PDG 2025 Dark
Energy review). **Status: no fully realised modified-gravity explanation of
acceleration is empirically viable as of PDG 2025.**

### 4.7 String landscape and anthropic selection
Bousso–Polchinski (JHEP 0006:006 (2000), hep-th/0004134) showed flux vacua
give a dense discretuum of vacuum energies; KKLT (Kachru–Kallosh–Linde–Trivedi,
Phys. Rev. D 68, 046005 (2003)) supplies metastable de Sitter vacua on top.
Weinberg's 1987 anthropic bound on `rho_V` from structure formation, sharpened
after 1998, lands near the observed value; Bousso (hep-th/0603249,
hep-th/0610211) reviews the environmental program and its measure problem:
vacuum counting, cosmological dynamics (eternal inflation) and selection
weights are all debated, and Douglas (Universe 5, 176 (2019)) records the
criticisms — including that there is still no nonperturbative construction of
string de Sitter space. The Causal Entropic Principle (Bousso, Freivogel,
Leichenauer, Thomas, hep-th/0702115) weights vacua by entropy production in
the causal diamond and finds the observed `rho_Λ` in the preferred range,
noting the discretuum must be dense enough to hit a target of ~`10^-123`
Planck units (i.e. `N >> 10^123` vacua if randomly spaced).
**Status: the only framework that naturally contains a dense spectrum of
small vacuum energies — but it explains selection, not a first-principles
value, and its measure problem is open.**

### 4.8 Swampland programme and the Trans-Planckian Censorship
Obied–Ooguri–Spodyneiko–Vafa (arXiv:1806.08362) conjecture `|nabla V| >= c V`
for any consistent quantum gravity, which forbids metastable de Sitter vacua
— in tension with a strictly positive constant `Lambda`. Bedroya–Vafa's
Trans-Planckian Censorship Conjecture (arXiv:1909.11063, JHEP 09 (2020) 123)
requires sub-Planckian fluctuations never to cross the Hubble horizon; for
`Lambda ~ 2.9e-122` it bounds the lifetime of any de Sitter phase to
`<~ 2.4 trillion years` and implies `inf V <= 0`. Brahma (Phys. Rev. D 101,
046013 (2020)) derives TCC from the swampland distance conjecture plus the
species bound. **Status: conjectural and debated; if right, dark energy is not
an eternal cosmological constant — it constrains the answer but does not
compute `10^-122` from the Standard Model.**

### 4.9 Quantum-gravity approaches
Asymptotic safety gives a non-Gaussian UV fixed point for dimensionless `G`
and `Lambda` (functional-RG and lattice/CDT evidence reviewed in
arXiv:2509.26352, 2025); one conformal-mode treatment (arXiv:1408.0276)
reports a fixed point predicting `Lambda = 0` on all scales, and a resummed
quantum-gravity estimate (arXiv:1409.1557) quotes `rho_Lambda ~ (2.4 meV)^4`
close to the observed value — a claim, not a consensus result, and flagged by
its own authors as needing firmer grounding. These works restore predictivity
of quantum gravity; none of them derives the observed small `Lambda` as an
accepted prediction. **Status: UV-completion candidates; the cosmological
constant problem is not settled by them.**

### 4.10 Entropy, holographic and emergent-gravity proposals
Padmanabhan's programme: gravity's dynamics as horizon thermodynamics makes
the bulk vacuum energy irrelevant and `Lambda` an integration constant
(gr-qc/0408051; astro-ph/0603114); the emergent-gravity paradigm postulates
`CosMIn = 4pi`, the number of modes crossing the Hubble radius between
inflation and acceleration, which then fixes the observed value
(arXiv:1404.2284), and links late acceleration to the drive toward
holographic equipartition (arXiv:1206.4916), with `Lambda L_P^2 ~ 3 e^(-4N)`
for ~70 e-folds of inflation. The holographic principle in the
't Hooft–Susskind sense bounds the degrees of freedom by the area, which by
construction removes the volume-divergent zero-point sum. **Status: a
coherent paradigm with an order-of-magnitude success for `10^-122`; the
`CosMIn = 4pi` postulate is itself the input, so the value is reproduced
rather than derived from field-theory inputs.**

### 4.11 Causal sets
Sorkin's heuristic prediction: in a causal set, 4-volume `V` and `Lambda` are
conjugate (`delta Lambda delta V ~ hbar`) and sprinkling fluctuations
`delta V ~ sqrt(V)` give `delta Lambda ~ 1/sqrt(V) ~ H^2` at the Hubble scale
— an "ever-present" fluctuating cosmological term with mean zero, magnitude
`~10^-120` in Planck units, predicted before the 1998 observations (AIP Conf.
Proc. 957, 142 (2007); gr-qc/0309009; model tested in Dodelson–Sorkin-type
work, arXiv:0706.0041 discusses the argument and its caveats). It predicts
`w != -1` and past sign changes, and rests on the mean value being zero for
reasons "still to be discovered". **Status: an order-of-magnitude match
resting on heuristic steps pending a quantum causet dynamics; the smallness
of `Lambda` is called "a riddle", not derived.**

### 4.12 Dynamical dark energy (quintessence) does not solve the old problem
Weinberg (astro-ph/9610044): "Quintessence does not help with either" problem;
PDG 2025: a scalar field can mimic `Lambda` but "still requires finding a way
to make the cosmological constant zero or at least negligibly small". Current
data (DESI 2025, Nature Astronomy *The future of Lambda-CDM*, 2025) hint at
possible time-dependence of dark energy, which would displace the constant-`Lambda`
interpretation without removing the old problem underneath.

## 5. Why `A10-R1` survives the survey

1. **Weinberg's no-go bar stands.** Every adjustment/self-tuning proposal
   above either evades a stated assumption (global constraint, modified IR
   graviton, extra fields) or is contested; no evasion has observational
   confirmation.
2. **Radiative stability is the dividing line.** Burgess's minimal criteria
   and Padilla's framing (technical naturalness under change of effective
   description) are not met by tuning-based accounts, and the symmetry-based
   accounts that would meet them are not realised in nature.
3. **The 2025 status statements still call it open.** PDG 2025 lists the
   unnaturally small magnitude as unexplained; the Royal Society 2025 review
   (Scali, Phil. Trans. R. Soc. A 383, 20230292) calls it "the greatest
   puzzle"; no cited 2025 source claims a solution.
4. **Nothing computes the corpus's own number.** `5.867696e111 J/m^3` versus
   `6e-10 J/m^3` — the `log10 ~ 120.99` gap — is reproduced by every approach
   as the starting datum, not eliminated by any accepted result.

## 6. Relation to MSAF (explicit non-closure)

* What this corpus has, machine-gated: the registered constants, the
  Planck-cutoff recomputation (`rho_Planck = hbar c / (8 pi^2 l_P^4)`, 50 dps,
  `provenance_check.py` recompute mode), the ratio `log10 ~ 120.99`, and the
  honesty conditions that forbid calling the gap solved
  (`tahap_uji_audit.py`, `quantum_censorship_check.py`).
* What the corpus does not have and this phase does not add: any mechanism of
  the classes in section 4, any derivation of the meV scale, or any way to
  adjudicate between those classes. Scale arithmetic can state the gap
  precisely; it cannot cancel a vacuum energy, because cancellation is a
  statement about a theory of quantum gravity, not about scale bookkeeping.
* The `A10-R1` wording therefore stands verbatim after A23: *the `10^120`
  vacuum gap is **not solved**; a finite Planck cutoff is a cutoff, not a
  cosmological-constant solution.* Closing it would require, minimally, a
  technically natural mechanism with an empirical consequence — none exists as
  of this survey.
* `Z_none` and Potential Infinity are untouched by this phase: nothing here
  evaluates anything at actual infinity, and the divergent vacuum integral is
  reported as divergent (A10 rewrite), consistent with the mainstream EFT
  reading cited in section 3.

## 7. Machine record

| Command | Result |
|---|---|
| `python checksum_check.py --update` then `python checksum_check.py` | manifest regenerated at **105 rows** (this report added), verified `105/105` |
| `python report_claim_check.py` | **PASS** (incl. P5 against the live manifest, P6 harness registry, P8 Brain file map) |
| `python harness_check.py` | **28/28**, workspace byte-identical (unchanged by this phase — no code added) |
| `python suite_check.py --with-harness` | **17/17**, `SUITE: PASS` |
| AC Gate: `run_tests.py` / `gate.py lean` / `gate.py claim` (4 formal targets) / `gate.py audit` | self-test **13/13**; lean **PASS**; claim **PASS** (FAIL=0 NOT_RUN=0); audit **PASS** (`GENUINE=2`) |

Counts at A23: 16 suite gates, 17 entries with `--with-harness`, 28 proof
harnesses, workspace manifest 105 rows, sub-repository manifest 118 rows
(A22). No gate, harness or manifest-structure change occurred in this phase.

## 8. Residuals

| ID | Status after A23 |
|---|---|
| `A10-R1` | **OPEN.** This phase surveyed the literature against it and closed nothing; the residual is unchanged. |
| `A10-R3` | OPEN (RH / NS / Langlands; untouched by A23). |
| `A17-R1` | CLOSED 2026-10-08 (A22). |
| others | Unchanged from A22 (`F8-R3`, `A13-R1`, `A14-R1`, `A15-R2`, `A18-R1..R4`). |

Not claimed: no theory of the cosmological constant is endorsed, no value of
`rho_Lambda` is predicted from MSAF axioms, and no part of the survey is
reproduced computationally here — it is a reading record with citations.

## 9. References (accessed 2026-10-08)

1. S. Weinberg, *The cosmological constant problem*, Rev. Mod. Phys. 61, 1
   (1989), doi:10.1103/RevModPhys.61.1.
2. S. Weinberg, *The cosmological constant problems*, astro-ph/9610044
   (Talk, 1996/1997); INSPIRE literature 527322.
3. A. Padilla, *Lectures on the Cosmological Constant Problem*,
   arXiv:1502.05296.
4. C. P. Burgess, *Micro-physics* (cosmological constant problem notes),
   physics.mcmaster.ca/~cburgess/Notes/CCProb.pdf.
5. L. F. Abbott, *A mechanism for reducing the value of the cosmological
   constant*, Phys. Lett. B 150, 427 (1985).
6. N. Kaloper, A. Padilla, *Sequestering the Standard Model Vacuum Energy*,
   Phys. Rev. Lett. 112, 091304 (2014), arXiv:1309.6562.
7. N. Kaloper, A. Padilla, *Vacuum energy sequestering: The framework and its
   cosmological consequences*, Phys. Rev. D 90, 084023 (2014),
   arXiv:1406.0711.
8. G. Dvali, S. Hofmann, J. Khoury, *Degravitation of the cosmological
   constant and graviton width*, Phys. Rev. D 76, 084006 (2007),
   hep-th/0703027.
9. S. M. Carroll, G. N. Remmen, *A nonlocal approach to the cosmological
   constant problem*, Phys. Rev. D 95, 123504 (2017).
10. *Modified Gravity Approaches to the Cosmological Constant Problem*,
    Universe 9(2), 63 (2023), mdpi.com/2218-1997/9/2/63.
11. *A note on classical and quantum unimodular gravity*, Eur. Phys. J. C 75
    (2015), doi:10.1140/epjc/s10052-015-3767-0.
12. *Unimodular gravity vs general relativity: a status report*, Class.
    Quantum Grav. (2022), doi:10.1088/1361-6382/aca386.
13. *Quantization of unimodular gravity and the cosmological constant
    problems*, Phys. Rev. D 80, 084003 (2009).
14. P. Jiroušek et al., *Unimodular approaches to the cosmological constant
    problem*, arXiv:2301.01662.
15. E. Álvarez, *The origin of the cosmological constant in unimodular
    gravity*, Eur. Phys. J. C 84 (2024),
    doi:10.1140/epjc/s10052-024-12651-7.
16. R. Bousso, *The Cosmological Constant and the String Landscape*,
    hep-th/0603249.
17. R. Bousso, *Precision cosmology and the landscape*, hep-th/0610211.
18. R. Bousso, J. Polchinski, JHEP 0006:006 (2000), hep-th/0004134.
19. S. Kachru, R. Kallosh, A. Linde, S. Trivedi, Phys. Rev. D 68, 046005
    (2003), hep-th/0301240.
20. M. R. Douglas, *The String Theory Landscape*, Universe 5, 176 (2019).
21. R. Bousso, B. Freivogel, S. Leichenauer, A. Thomas, *Predicting the
    Cosmological Constant from the Causal Entropic Principle*, hep-th/0702115.
22. G. Obied, H. Ooguri, L. Spodyneiko, C. Vafa, *De Sitter Space and the
    Swampland*, arXiv:1806.08362.
23. A. Bedroya, C. Vafa, *Trans-Planckian Censorship and the Swampland*,
    arXiv:1909.11063, JHEP 09 (2020) 123.
24. S. Brahma, *Trans-Planckian censorship conjecture from the swampland
    distance conjecture*, Phys. Rev. D 101, 046013 (2020).
25. *Asymptotic safety and the cosmological constant*, arXiv:1408.0276.
26. *Asymptotically safe quantum gravity: functional and lattice
    perspectives*, arXiv:2509.26352 (2025).
27. *Resummed Quantum Gravity Prediction for the Cosmological Constant and
    Constraints on SUSY GUTS*, arXiv:1409.1557.
28. T. Padmanabhan, *Cosmological Constant from the Emergent Gravity
    Perspective*, arXiv:1404.2284.
29. T. Padmanabhan, *Emergence and Expansion of Cosmic Space as due to the
    Quest for Holographic Equipartition*, arXiv:1206.4916.
30. T. Padmanabhan, *Gravity as elasticity of spacetime*, gr-qc/0408051.
31. R. D. Sorkin, *Is the cosmological "constant" a nonlocal quantum residue
    of discreteness of the causal set type?*, AIP Conf. Proc. 957, 142 (2007).
32. R. D. Sorkin, causal-set order-of-magnitude prediction for `Lambda`,
    gr-qc/0309009.
33. *On Cosmological Constant in Causal Set Theory*, arXiv:0706.0041.
34. Particle Data Group, *Dark Energy*, Review of Particle Physics 2025,
    pdg.lbl.gov/2025/reviews/rpp2025-rev-dark-energy.pdf.
35. F. Scali, *The cosmological constant problem: from Newtonian cosmology to
    the greatest puzzle of modern theoretical cosmology*, Phil. Trans. R. Soc.
    A 383, 20230292 (2025).
36. *Dark Energy* (Les Houches "Dark Universe" lectures, 2025),
    arXiv:2509.00688.
37. *The future of Lambda-CDM*, Nature Astronomy 9, 1418 (2025).
38. *Whether an Enormously Large Energy Density of the Quantum Vacuum Is
    Catastrophic*, Symmetry 11, 314 (2019).
39. *Vacuum Energy Density Measured from Cosmological Data*, osti.gov
    (record 1839578) — `rho_Lambda = (60.3 +/- 1.3)e-31 g/cm^3`, 2.2%.
40. M. Trodden, S. M. Carroll, *TASI Lectures: Introduction to Cosmology*,
    ned.ipac.caltech.edu/level5/Sept03/Trodden/.
41. S. M. Carroll, *Dark Energy and the Preposterous Universe*,
    ned.ipac.caltech.edu/level5/March01/Carroll/.
42. J. Baez, *Vacuum energy density*, math.ucr.edu/home/baez/vacuum.html.
43. *Cosmological constant problem*, Wikipedia (CC BY-SA).
44. *Degravitation, inflation and the cosmological constant as an afterglow*,
    JCAP 0901:017 (2009).
45. *On Semi-classical Degravitation and the Cosmological Constant
    Problems*, arXiv:1003.3010.
46. Weinberg's 1987 anthropic bound, Phys. Rev. Lett. 59, 2607 (1987).
