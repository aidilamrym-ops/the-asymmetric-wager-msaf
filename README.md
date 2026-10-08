# The Asymmetric Wager — MSAF (Modular Scale Arithmetic Framework)

**Author:** Muhammad Aidil Amry (Independent Researcher, South Sulawesi, Indonesia)  
**ORCID:** 0009-0002-9718-9710  
**Canonical DOI:** [10.5281/zenodo.22791556](https://doi.org/10.5281/zenodo.22791556)  
**Repository:** `the-asymmetric-wager-msaf`  
**Workspace of record:** `D:\THE ASYMMETRIC WAGER`  
**Licence:** hybrid — MIT for code, CC-BY-4.0 for scholarly documents (see `LICENSING.md`)

This README is written for **academic examiners and external reviewers**. It states what the project claims, what it deliberately does **not** claim, how the mathematics and the physics are mapped, what has been machine-gated, how verification works, and how to re-run the proof rig yourself. Narrative fluff is excluded by project rule ($P_{\text{narrative}} = 0$).

---

## 1. What this project is

**MSAF** is a strict-finitist reconstruction of mathematical reasoning about unbounded domains. It deconstructs **Actual Infinity** (treated as a logical error when used as a completed, filled continuum) into **Potential Infinity** (treated as a finite-scale algorithmic process), then anchors every operational claim to the information limits of the observable universe. The corpus’s **Declaration of Strict Finitism** is operational, not decorative: existence claims must be finite-constructible inside $\mathcal{S}_{\mathrm{obs}}$.

The two operational anchors are:

| Symbol | Meaning | Value used in the corpus |
|---|---|---|
| $\ell_P$ | Planck length (micro lower bound) | $\approx 1.62 \times 10^{-35}\,\mathrm{m}$ (CODATA 2022) |
| $D_{\mathrm{obs}}$ | Observable-universe diameter (macro upper bound) | $\approx 8.8 \times 10^{26}\,\mathrm{m}$ (Planck 2018 VI / arXiv preprint) |
| $\Delta_{\mathrm{univ}} = \ell_P / D_{\mathrm{obs}}$ | **Universe Pixel Constant** — smallest information step | $1.836653 \times 10^{-62}$ as an exact quotient of the declared inputs; **only 2 significant figures are justified**, because $D_{\mathrm{obs}}$ carries 2 s.f. |
| $N_{\mathrm{steps}} = D_{\mathrm{obs}} / \ell_P$ | Finite information steps across $[0,1]$ mapped onto the universe scale | $\approx 5.4 \times 10^{61}$ |
| $\mathcal{Z}_{\mathrm{none}} = \{x : 0 < \lvert x - x_0 \rvert < \Delta_{\mathrm{univ}}\}$ | **Zone of Non-Existence** — open pixel around an anchor | **Non-operational.** No function, limit, or eigenvalue is evaluated inside it |
| Critical line $\Re(s) = 0.5$ | Scale Axiom for information-space geometry | **Not** treated as a theorem to prove up to $\gamma \to \infty$ |

**Physical mapping (in one line):** if the continuous interval $[0,1]$ is identified with the observable universe, then the critical coordinate $0.5$ has a physical size $\approx 4.4 \times 10^{26}\,\mathrm{m}$, and the number of discrete steps from $0$ to $0.5$ is finite ($\approx 2.7 \times 10^{61}$ at the same resolution), so the Zeno-type obstruction to “reaching” $0.5$ under Actual Infinity does not arise under Potential Infinity.

---

## 2. What this project is **not** (read this before judging)

These non-claims are part of the scientific contract, not caveats added afterwards:

1. **It is not a proof of the Riemann Hypothesis.** The corpus repositions RH as a **Scale Axiom** of information-space geometry. It does not assert that all non-trivial zeros lie on $\Re(s)=1/2$.
2. **It does not claim Weil positivity for the infinite operator.** What is certified is **positive-definiteness of finite Guinand–Weil truncations** under interval arithmetic, at stated $N$ and precision, with an explicit tail enclosure.
3. **It does not claim prime-counting or factorisation results.**
4. **Navier–Stokes smoothness and the Langlands program are design targets, not achieved theorems.** Navier–Stokes existence/smoothness in three dimensions remains one of the seven Clay Millennium Prize Problems and is open; Langlands is conjectural in general with major cases proved.
5. **Cosmological statements** (non-singular bounce, dark matter as geometric tail memory) are **interpretive extensions** of the discrete-scale ontology. They are not presented as observational confirmations.
6. **The numerical engine’s own register** (`guinand-weil-rigorous-numerics-main/.zenodo.json`) states explicitly that no claim is made about RH, Weil positivity, prime counting, or integer factorisation, and records residual defects rather than hiding them.

If a reviewer wants a one-sentence distinction: *this is a finite, scale-bound, machine-checked framework about how mathematics may operate inside a universe with a smallest information step — not another zero-hunting computation of the Riemann zeta function.*

---

## 3. Core thesis (the mathematical–physical logic map)

### 3.1 The problem MSAF attacks

Classical analysis of unbounded domains (Riemann zeta zeros, continuous fluid PDEs, quantum field self-energies, cosmological singularities) routinely introduces **Actual Infinity**: a completed continuum, or a limit process treated as if the “end” of an infinite path were an object one can stand on. Under that ontology:

- The interval paradox $0 \to 0.5 \to 1$ becomes unresolvable: infinitely many stages forbid the first step, so the exact values $0.5$ and $1$ never become operationally realisable.
- Physics equations “blow up” to $\infty$ or $V=0$; the corpus treats those blow-ups as **alarms that continuous calculus failed to declare its own information bound**, not as descriptions of the universe.

### 3.2 The MSAF response

| Classical move | MSAF replacement | Operational rule |
|---|---|---|
| Actual Infinity (completed continuum) | Potential Infinity (finite-scale loop) | Algorithm must terminate in finite steps bounded by $N_{\mathrm{steps}}$ and bit precision $p$ |
| Evaluate anywhere on $\mathbb{R}$ | Operational domain $\mathcal{S}_{\mathrm{obs}} = \{\Delta x : \ell_P \le \Delta x \le D_{\mathrm{obs}}\}$ | Inside $\mathcal{Z}_{\mathrm{none}}$: **forbidden** |
| “Prove RH to infinity” | Critical line as **Scale Axiom** (fixed input, like $c$ or $G$) | Map prime-growth structure modularly on the axiom, do not waste tokens proving the axiom to $\gamma \to \infty$ |
| Discard infinite series tails | Modular wall operator $\hat{\mathcal{M}}_N$ | Tail → uncertainty ball radius $\mathcal{R}_{\mathrm{tail}}$; **midpoint never shifts** (**zero-fudging**) |
| Floating-point hope / forced rounding | Interval $LDL^T$ (Sylvester) over Arb balls | Pivot sign decided by ball position; straddling zero → **raise precision**, do not round |

### 3.3 The engine (OMEGA-CORE v2) — how the math is executed

Target object: the Guinand–Weil explicit-formula matrix, truncated to a real symmetric matrix

$$A_{ij} = W_{02}(n,m) - W_R(n,m) - W_p(n,m), \qquad n,m \in \{-N,\dots,N\}, \quad \dim = 2N+1.$$

For $N = 400$ this is an $801 \times 801$ matrix. For $N = 800$, dimension $1601$.

**Tail enclosure (zero-fudging):**

$$\mathrm{rem} = 4\cdot\frac{e^{-(2(k+1)+1/2)L}}{1 - e^{-2L}}, \qquad \texttt{widen}(x) = x + [0 \pm \mathrm{rem}], \qquad \mathcal{R}_{\mathrm{tail}} = \mathrm{rem}\cdot 2^{-p\,\Delta_{\mathrm{univ}}}.$$

An unsummable remainder **widens the ball**. It does **not** move the midpoint in favour of a desired sign. That is the zero-fudging contract, and it is machine-checked by the engine’s gates and by the workspace suite.

**Certification path:** interval $LDL^T$ elimination classifies each pivot ball:

- $s > 0$: certified positive  
- $s < 0$: certified negative (anomaly)  
- ball straddles $0$: **undetermined** → modular precision escalation  

Recorded operating points: at 9000 bits the $N=400$ run hit an undetermined pivot near index 723; the engine escalated to 18000 bits rather than rounding. At the higher precision the max entry radius shrank to $\approx 1.39 \times 10^{-5266}$ and all 801 pivots certified positive definite.

**Eigenvalue lower bound (structural, machine-gated):**

$$\lambda_{\min}(A) \ge \frac{\min_i \lvert d_i\rvert}{\lVert L^{-1}\rVert_F^2}$$

| $N$ | Certified bound | Notes |
|---|---|---|
| $400$ | $\lambda_{\min} \ge 6.747 \times 10^{-509}$ | Shipped in `omega_core_v2_results_N400.json`; gated by `gw_verify_production.py` |
| $800$ | $\lambda_{\min} \ge 8.675 \times 10^{-2877}$ | Peak RAM $\approx 8251.7$ MB; gated by the same production verifier |

These are bounds on the **finite truncations** produced by the engine under its declared parameters $(c,N,\mathrm{prec},\ldots)$. They are not statements about the infinite operator.

**Zeta sensitivity experiment (separate from the matrix engine):** at 100 decimal places, shifting the first non-trivial zero $s_1$ by exactly $1\,\Delta_{\mathrm{univ}}$ off the critical line produces

$$\lvert\Delta\zeta\rvert \approx 1.456761 \times 10^{-62} = \lvert\zeta'(\rho_1)\rvert\,\Delta_{\mathrm{univ}}, \qquad \lvert\zeta'(\rho_1)\rvert \approx 0.7931604334.$$

Integer pixel shifts $n=1..5$ all sit **outside** $\mathcal{Z}_{\mathrm{none}}$ (the zone is the **open** interval $0 < \lvert x-x_0\rvert < \Delta_{\mathrm{univ}}$). The table demonstrates linear response in the region where evaluation is allowed; it does not evaluate inside the forbidden zone.

### 3.4 Physical extensions (interpretive layer)

| Domain | Classical failure mode | MSAF reading | Status |
|---|---|---|---|
| Cosmology | Big Bang from $V=0$, $\rho=\infty$ | Non-singular **cosmic bounce** when Shannon information capacity saturates near $\Delta_{\mathrm{univ}}$ | Interpretive; Hawking–Penrose is cited with its four hypotheses and does **not** itself assert a literal $V=0$ point |
| Dark matter | Invisible particle hunt | Geometric memory of the primordial truncation tail $\mathcal{R}_{\mathrm{tail}}$ — curvature distortion, not a new particle | Interpretive; no detection claim |
| Quantum field theory | UV divergences / self-energy $=\infty$ | Bound energy scales by a finite $\lambda_{\mathrm{min}}$ / pixel volume; renormalisation is treated as a standard mechanism, not a “trick” [F4-F] | Research direction |
| Fluid dynamics | Navier–Stokes singularity risk | Modular wall as a hard resolution floor for velocity/viscosity fields | **Open problem**; design target only |
| Number geometry | RH as open conjecture | Critical line as Scale Axiom; primes evolve on a one-way aperiodic trajectory | Philosophical / epistemological repositioning |

---

## 4. What has been achieved (and how an examiner should read “achieved”)

### 4.1 Machine-gated achievements (re-runnable in this repository)

These are **not** rhetorical. Each item is backed by a gate script that reads claims out of the documents or out of registers, recomputes or re-hashes them, and exits $0/1/2$.

| Achievement | Gate | What “pass” means |
|---|---|---|
| Canonical $\mathcal{Z}_{\mathrm{none}}$ and operational prohibitions | `znone_check.py` | One set definition everywhere; no evaluation claimed inside the zone |
| Landauer information floor used consistently | `landauer_check.py` | $k_B\ln 2$ and derived $\Delta E$ rows re-derived at 100 dps from documents |
| Zeta pixel figures produced from first principles | `zeta_pixel_producer.py`, `msaf_zeta_check.py` | Published $|\Delta\zeta|$ and gradient match recomputation at the documents’ own s.f. |
| External constants (CODATA, Planck, etc.) | `provenance_check.py` (11 conditions incl. `P11 LIVENESS_RECORD`) | Values, hashes, layers, and liveness record held to registers; four negative liveness directions injection-proven |
| Borrowed mathematics (Brouwer, Hawking–Penrose, Langlands, …) | `theorem_provenance_check.py` | Every borrowed authority registered with evidence for **this** document; anchors resolve once; findings carry corrections and markers |
| Finite Guinand–Weil truncations positive definite | `gw_verify_production.py`, `gw_verify_results.py`, `gw_final_gate.py`, `gw_mont_pipeline_check.py` | Certified row checks for $N=400$ and $N=800$; final gate’s two conditions; production fault-injection counts recorded in `F1_REPORT.md` / `F2_REPORT.md` |
| Protocol 09 ($\Phi$ / Gödelian compliance loop) encoding | `bounded_loop_gate.py` | FSM over `QF_LIA`; log bound to script by sha256; context sat, claim unsat, each core axiom load-bearing; auditor verdict `GENUINE`. Renamed from `protocol_09.*` by A12 (2026-10-07); historical A1 names retained in the SMT header. |
| Prose claims about the rig | `report_claim_check.py` | Numeric claims in reports must equal live rig values or carry a date/phase anchor; P9 also holds `N conditions` to `len(CONDITIONS)` on provenance lines |
| `tahap uji` honesty (A10) | `tahap_uji_audit.py` | Two documents rewritten to English and to claims the machine gates support; Planck-cutoff density recomputed; zero-error / dirty-renormalisation / "NS proven" / Gate-3-misread classes rejected |
| Workspace integrity | `checksum_check.py` | Manifest over workspace root + `provenance/` + `harnesses/`; last suite gate so mutations are detected |
| Fault-injection proof of the gates themselves | `harness_check.py` + `harnesses\` | **24** proof harnesses, run sequentially with before/after workspace hashes |

**Offline verification contract (as of 2026-10-07, Fase A18):**

- Suite gates: **16** (`suite_check.py`)
- `--with-harness` entry: **17**
- Proof harnesses: **25**
- Manifest scope: **101** files
- `provenance_check.py`: **11** conditions (P1–P11); P11 prints record age
- Full offline suite with harnesses last run: **16/16 PASS**
- Anti-Circularity Gate self-test: **13/13**; SMT circularity auditor on Track-C + bounded_loop: **GENUINE**, not circular

### 4.2 Theoretical / epistemological achievements

1. **A usable ontology of infinity for computation:** Actual Infinity banned as a completed object; Potential Infinity operationalised as finite modular loops with explicit resolution bounds.
2. **A formal non-operational zone** $\mathcal{Z}_{\mathrm{none}}$ with a single canonical definition, enforced across documents and gates — so “a root hiding at $0.5 + 10^{-1000000}$” is classified as an informationally empty symbol, not as a mathematical threat.
3. **A scale-axiom reading of the Riemann Hypothesis:** the question “are all zeros on the line up to infinity?” is reframed as self-referential under a domain that has no physical final boundary; the critical line is treated as a fixed geometric constant of information space.
4. **A zero-fudging numerical discipline:** uncertainty is allowed to grow; midpoint drift in favour of a proof is forbidden and gated.
5. **A verification culture for the corpus itself:** every borrowed constant and theorem has provenance; every prose claim about the rig is checked; every gate has a mutation harness; anti-circularity is run before any “verified/unsat” sentence is reported.

### 4.3 What remains open

| ID | Open item |
|---|---|
| `F8-R3` | Sub-repo encoding remains pinned-not-fixed (by design of A9) |
| `F8-R4` | **CLOSED 2026-10-07 (A12).** A8 deferred because the *Kamus Pemetaan* did not exist and three proposed names collided (`N_steps`, `M_inf`, `q_self`). A12 authored `KAMUS_PEMETAAN.md`, renamed the encoding to `bounded_loop.*` with collision-free tokens (`p09_op`, `q_scan`, `q_check`, `q_halt`, `m_budget`, `n_budget`), regenerated the log via Z3, retargeted the gate (`bounded_loop_gate.py` 8/8) and live harnesses, and closed the residual. |
| A10-R1 | The `10^120` vacuum gap is **not solved** |
| A10-R2 | **CLOSED 2026-10-07 (A18).** Gate 2 is implemented for the part arithmetic can decide -- `quantum_censorship_check.py` recomputes the Planck-scale identities, the Planck mass by two routes and the zero-point density, and refuses any claim that quantum censorship itself is established. The physics claim remains open: a question below the resolution floor is unevaluable in this framework, which is not the same as false (`A18_REPORT.md`) |
| A10-R3 | RH, Navier–Stokes regularity and Langlands remain open in the literature regardless of any gate result here |
| `A13-R1` | `lean\` sits **outside** the manifest scope, so neither Lean file is hash-pinned (`A13_REPORT.md` §7) |
| `A14-R1` | The Lean theorems are theorems about the **model** over exact rationals; nothing connects them to the numerics that instantiate `R_tail` (`A14_REPORT.md` §7) |
| `A15-R1` | **CLOSED 2026-10-07 (A17).** `OMEGATrackC.lean` had not been recompiled after the `rhoActual` literal changed, because Mathlib was absent on that machine; the literal rested on `track_c_make_smt.py` (3-way MATCH), Z3 7/7 and the Anti-Circularity Gate, none of which compile the module. A17 installed Mathlib `v4.33.1`, recompiled the file byte-for-byte (`sha256 51dca387...`, `lake build` exit 0, zero `sorry`), and confirmed all ten theorems still print `[propext, Classical.choice, Quot.sound]` -- the 2026-10-02 footprint, since no statement changed (`A17_REPORT.md`) |
| `A15-R2` | `rho_actual` bounds the entry error **of the supplied matrix**; it is not a rebuild of that matrix and transfers to no other build (`A15_REPORT.md` §7) |

External open mathematics (RH, Navier–Stokes, Langlands in general) remains open **regardless of any gate result in this repository**.

---

## 5. What differentiates MSAF from other approaches

| Approach family | Typical goal | Typical method | MSAF difference |
|---|---|---|---|
| Classical RH numerics | Verify RH up to a large height $T$ (e.g. Platt–Trudgian: true up to $3\times 10^{12}$) | Zero search / Turing method / explicit formula computations | MSAF does **not** compete on height. It asks what it means to evaluate any of this inside a universe with a smallest step, and certifies **finite matrix truncations** with interval tails |
| Interval / ball arithmetic alone | Certified numerics for specific operators | Arb/MPFR balls, interval $LDL^T$ | Same tools, different **contract**: zero-fudging (no midpoint shift), modular escalation on straddling zero, plus workspace-level mutation harnesses and anti-circularity |
| Strict finitism / constructive maths (philosophical) | Reject non-constructive existence | Brouwer, strict finitism, ultra-intuitionism | MSAF **operationalises** the school: explicit $\Delta_{\mathrm{univ}}$, $\mathcal{Z}_{\mathrm{none}}$, $N_{\mathrm{steps}}$, and machine gates over the resulting claims |
| Formal methods on RH-adjacent claims | Prove statements in Lean/Isabelle | Kernel-checked proofs | MSAF ships Track-C Lean/Z3 side conditions **and** an SMT circularity auditor, then refuses to report `verified`/`unsat` without the Anti-Circularity Gate |
| Physics-modified mathematics (effective field theory style) | Cut off UV by hand | Regulators, renormalisation | MSAF proposes a **cosmological information bound** as the regulator’s justification, and keeps renormalisation as a standard mechanism rather than a trick |
| AI-agent knowledge bases | Dump narrative corpora to LLMs | Free text | This workspace forces $P_{\text{narrative}}=0$, English-only artefacts, a three-tier pipeline (epistemic sieve → OCTAVE tensor → Z3 tribunal), and a proof rig an examiner can run |

**The distinctive wager** (hence the project name): bet that **scale-bound, zero-fudged, machine-checked finite mathematics** is the honest way to discuss unbounded questions — and prove that bet by making the corpus fail loudly when its own prose, constants, or proofs drift.

---

## 6. How the verification rig works (for examiners who want to falsify, not to believe)

### 6.1 Layers

```text
Philosophical corpus (01–03, MANIFESTO, DEFINISI, OCTAVE, cosmology)
        |
        v
Registers (external_constants.json, theorem_provenance.json,
          REFERENCES.md, CHECKSUM.sha256, url_liveness.json)
        |
        v
Gates (15 offline suite gates, fixed order, sequential)
        |
        v
Fault-injection harnesses (25, mutate then restore, hash-checked)
        |
        v
Anti-Circularity Gate (placeholder scan + claim gate + Z3 circularity audit)
```

### 6.2 How to re-run (from a fresh clone)

```bat
git clone https://github.com/aidilamrym-ops/the-asymmetric-wager-msaf.git
cd the-asymmetric-wager-msaf

REM Offline suite — 16 gates, fixed order
python suite_check.py

REM Same, plus the 23 proof harnesses (mutates then restores; do not parallelise)
python suite_check.py --with-harness

REM Individual gates an examiner often wants first
python provenance_check.py
python theorem_provenance_check.py
python msaf_zeta_check.py
python checksum_check.py
python bounded_loop_gate.py
python report_claim_check.py

REM Optional network probe — NOT a suite gate (the suite is the offline contract)
python url_liveness_check.py
```

Exit codes everywhere: **0** pass, **1** fail, **2** tool not run / incomplete. `suite_check.py --fast` omits the long final numerical gate and therefore returns **2**, never a fake full pass.

### 6.3 Anti-circularity (mandatory before trusting any `verified` / `unsat` sentence)

Skill location on the author’s machine: `C:\Users\usER\.config\opencode\skills\anti-circularity`.

```bat
python scripts\gate.py check ^
  guinand-weil-rigorous-numerics-main\OMEGATrackC.lean ^
  guinand-weil-rigorous-numerics-main\track_c_side_conditions.smt2 ^
  bounded_loop.smt2
```

Interpretation (also written in the skill itself):

- **PASS** = the checks ran and found nothing wrong in the artefacts on disk. It is **not** a mathematical theorem.
- **FAIL** = a placeholder, a comment-only claim, or a non-result verdict (`CIRCULAR`, `VACUOUS`, `SAT`, …).
- **TOOL NOT RUN** = a required tool or input was missing. Never quoted as success.

### 6.4 How to attack the corpus honestly (suggested examiner tests)

1. Change one number in `Skill.md` or `Brain.MD` about suite/harness/manifest counts → `report_claim_check.py` must fail.
2. Append a byte to a tracked file → `checksum_check.py` must fail.
3. Delete or rewrite a historical `brain=v…` string in an old report without a date anchor → P5 must fail (or you must add a phase anchor).
4. Flip a register layer or drop a URL → `provenance_check.py` / liveness harness directions must fail.
5. Remove a core axiom from `bounded_loop.smt2` without regenerating the log → `bounded_loop_gate.py` P2/P4/P7 must fail. (Historical A1 names: `protocol_09.smt2` / `protocol_09_check.py`; renamed by A12.)
6. Run `harness_check.py --selftest` → the runner itself must be able to fail.

If any of these do **not** fail, treat that as a defect in this workspace, not as a victory for the narrative.

---

## 7. Roadmap (phase map for the examining board)

Phases are recorded in `F0_REPORT.md` … `F8_REPORT.md`, in `A10_REPORT.md` …
`A16_REPORT.md`, and in `Brain.MD`. Status as of **2026-10-07** (A16 complete):

| Phase | Date | Focus | Status |
|---|---|---|---|
| F0 | 2026-10-04 | Anti-circularity audit of `verified`/`unsat` claims; gate self-test; three blind spots fixed | Complete |
| F1 | 2026-10-04 | Numeric canon, pipeline claim audit, zeta figures, production gates hardened | Complete |
| F2 | 2026-10-04→05 | Backlog closure: Landauer, $\mathcal{Z}_{\mathrm{none}}$, zeta producer, bridge mirror, plot semantics, $N=400$ rerun shipped | Complete |
| F3 | 2026-10-05 | External provenance for constants; CODATA archive; vacuity hardening | Complete |
| F4 | 2026-10-05 | External provenance for borrowed mathematics; 27-entry theorem register | Complete |
| F5 | 2026-10-05 | Hardening/re-proof: suite runner, three-layer evidence archive, markers, Decimal tolerance | Complete |
| A1 | 2026-10-06 | Protocol 09 encoding in `QF_LIA` + 8-condition gate | Complete |
| A2 | 2026-10-06 | F2 harness rebuild (six published counts made citable) | Complete |
| A3 | 2026-10-06 | `report_claim_check.py` as suite gate 14 | Complete |
| A5 | 2026-10-06 | Blind-spot audit of prose (`F6_REPORT.md`) | Complete |
| A6 | 2026-10-06 | Git repository, hybrid licensing, `.gitattributes` LF pin | Complete |
| A7 | 2026-10-06 | Archive policy + upstream history (`F7_REPORT.md`); `F5-R5` ESTABLISHED | Complete |
| A8 | 2026-10-06 | `Tugas tambahan.md` symbol-rename assessment | **Superseded by A12** (dictionary authored; collisions avoided) |
| A9 | 2026-10-06 | URL liveness tool + `P11`; prose-pattern closure (`F8_REPORT.md`); `F7-R3`/`F6-R5` closed | Complete |
| A10 | 2026-10-07 | `tahap uji` honesty rewrite + `tahap_uji_audit.py` + ρ_Λ/ħ/c/Planck-vacuum provenance + harness `a10_tahu_inj.py` | Complete |
| A11 | 2026-10-07 | Residual closures: P9 CONDITIONS_CLAIM + P11 liveness age; harness `a11_residual_inj.py`; `F8-R1`/`F8-R2` closed | Complete |
| A12 | 2026-10-07 | F8-R4: `KAMUS_PEMETAAN.md` + rename `protocol_09.*` → `bounded_loop.*`; gate 8/8; manifest 93 | Complete |
| A13 | 2026-10-07 | `lean\DiscreteCoordinates.lean`: Scale-Axiom lattice, `min_separation` + open-zone emptiness, core-only Lean, zero `sorry` | Complete |
| A14 | 2026-10-07 | `lean\ModularWall.lean`: `M_hat_N` + `R_tail` structural contract, zero-fudging midpoint theorems, core-only Lean, zero `sorry` | Complete |
| A15 | 2026-10-07 | `gw_rho_formal.py`: `rho_actual` as a ball-arithmetic **upper bound** (1200 bits, proved Lerch tail) instead of a dps-doubling estimate; margin 74.4468626023 decades; registers `A15-R1` | Complete |
| A16 | 2026-10-07 | Bookkeeping closure: phase reports `A13`–`A15` authored, roadmap extended, residual register completed, manifest 97 | Complete |
| A18 | 2026-10-07 | Gate 2 implemented for its arithmetic only: `quantum_censorship_check.py` (micro-scale identities + overclaim guard) and harness `q2_censorship_inj.py` `7/7`; gates 16, harnesses 25, manifest 101; closes `A10-R2` with a bounded scope | Complete |
| A17 | 2026-10-07 | Mathlib `v4.33.1` installed; `OMEGATrackC.lean` recompiled byte-for-byte (exit 0, zero `sorry`, ten-theorem footprint re-measured); `trackc_recompile.py` added, mutation-proven 4/4; closes `A15-R1`; manifest 98 | Complete |

**Forward research blueprint** (from `Perluasan Visi Ilmiah (Extended Thesis Blueprint).md` — roadmap, not results):

1. **Number geometry** — consolidate the critical line as a one-way information-growth axis under Guinand–Weil stability matrices.  
2. **Fluid dynamics** — finite reconstruction attempts for Navier–Stokes under a modular resolution floor.  
3. **Cosmology** — bounce / pixel-volume bounds as alternative to singular initial data.

Each of these is an **open programme**. None of the gates in §4.1 establishes them.

---

## 8. Reading map (what to open first)

| Order | File | Why |
|---|---|---|
| 1 | This README | Mandate, non-claims, rig, roadmap |
| 2 | `DEFINISI_OPERASIONAL_MSAF.md` | Canonical glossary: $\mathcal{Z}_{\mathrm{none}}$, $\mathcal{S}_{\mathrm{obs}}$, Scale Axiom, Potential vs Actual Infinity |
| 3 | `CONSOLIDATED_MASTER_MANIFESTO.md` | Constitution / postulates |
| 4 | `01_PARADOX_AND_SCALE.md` → `02_OMEGA_CORE_ANALYSIS.md` → `03_RIEMANN_RECONSTRUCTION.md` | The three-section scientific narrative |
| 5 | `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md` | Abstract draft + gated zeta sensitivity data + anti-density defence |
| 6 | `OCTAVE_CORE_MATHEMATICS.md` | Eight-domain tensor architecture and orthogonality mandate |
| 7 | `Skill.md`, `Brain.MD`, `AGENTS.md` | Operating protocol and knowledge map |
| 8 | `F0_REPORT.md` … `F8_REPORT.md`, `A10_REPORT.md` … `A16_REPORT.md` | Phase audits, findings, residuals, corrections |
| 9 | `REFERENCES.md`, `external_constants.json`, `theorem_provenance.json` | Evidence layer |
| 10 | `guinand-weil-rigorous-numerics-main\` | OMEGA-CORE engine, Track-C, engine-local licence and residuals |

Sub-repositories also present (supporting / derivative material, not proof engines for the MSAF claims above): `Theory_of_Everything_Derivations`, `hexagon_mhv_symbol_weight_18`, `Dream-RSI-main`.

---

## 9. Citation and licence

```bibtex
@misc{amry_msa,
  author       = {Amry, Muhammad Aidil},
  title        = {The Asymmetric Wager — Modular Scale Arithmetic Framework (MSAF)},
  year         = {2026},
  doi          = {10.5281/zenodo.22791556},
  url          = {https://doi.org/10.5281/zenodo.22791556},
  note         = {Strict-finitist reconstruction of unbounded-domain reasoning;
                  OMEGA-CORE v2 finite Guinand-Weil truncations with interval
                  tail enclosure; machine-verified workspace rig}
}
```

- **Code** (`*.py`, `harnesses/*.py`, `mcp/*.py`, `*.smt2`): MIT (`LICENSE`).
- **Scholarly documents and registers**: CC-BY-4.0 (`LICENSING.md`).
- **Third-party subtrees and archived snapshots**: excluded from relicensing; licence basis recorded per item in `LICENSING.md` and `REFERENCES.md`.

---

## 10. Contact and operating rules

- Work only inside the workspace of record; new artefacts stay in `D:\THE ASYMMETRIC WAGER`.
- All new artefacts, comments, and documents are **English-only**.
- Before any agent reports a machine-verified result, the **Anti-Circularity Gate** must run; the report must reproduce tool output, not paraphrase it.
- Residuals are **recorded, not deleted**. A phase closes a residual only when a gate or harness proves the closure.

---

*MSAF — scale-bound modular mathematics. Null narrative. Deterministic equilibrium.*  
*Suite contract as of 2026-10-07 (Fase A10): 15 gates, 23 harnesses, 89-file manifest, 11 provenance conditions.*
