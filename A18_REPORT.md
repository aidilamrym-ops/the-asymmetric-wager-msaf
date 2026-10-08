# A18_REPORT.md — Fase A18 (2026-10-07)

**Phase:** A18 — Gate 2 of the sieve protocol: implement the part arithmetic can decide, and bound what it may not claim.  
**Date:** 2026-10-07.  
**Language:** English.  
**`P_narrative`:** 0.  
**Closes:** `A10-R2`. **Adds:** `A18-R1`, `A18-R2` (§7).

---

## 1. The residual and the decision

`A10_REPORT.md` recorded defect **V-4** and residual `A10-R2`: the sieve
protocol presented three gates, and

> | Gate 2 | Quantum censorship audit at micro scales | **Not implemented.** No
> gate script in this workspace checks for local quantum black-hole formation.

Two readings of that residual were possible, and the corpus had to pick one:

- **(a) implement a gate that checks for local quantum black-hole formation;**
- **(b) declare it not machine-checkable and close the residual that way.**

Neither is available. Quantum censorship is a statement about quantum gravity;
this workspace has no theory of quantum gravity, so (a) would be a script that
verifies nothing while reporting PASS — the same defect V-4 was raised to
prevent, relocated. And (b) would leave a residual phrased as a *pending task*
forever, which is the "residual as a decision, a residual nobody is obliged to
pick up" pattern F7 closed.

**The third option**, taken here, is the one Gate 1 already set: Landauer is not
a proof that erasure releases heat, and `landauer_check.py` gates only the
*arithmetic of the floor*. So Gate 2 checks only the arithmetic of the boundary
on which the censorship question sits, and states in the same breath that the
question itself is not answered here.

The precedent is not a convenience; it is the reason the option set was not
binary. A10 accepted Gate 1 as implemented with a narrow scope. It would have
been incoherent to accept that and then call Gate 2 unimplementable.

## 2. What the gate computes

`quantum_censorship_check.py`, mpmath at 100 dps, every quantity recomputed from
`external_constants.json`:

| Condition | Claim | Measured |
|---|---|---|
| Q1 | $\omega_P\,\ell_P = c$ | rel err `1.84e-07` (tol 1e-6) |
| Q2a | $m_P = \hbar\,\omega_P/c^2$ | `2.176434776e-8 kg` vs CODATA `2.176434e-8` |
| Q2b | $m_P = \hbar/(c\,\ell_P)$ | `2.176434374e-8 kg` |
| Q2c | the two routes agree | rel err `1.84e-07` |
| Q3 | $\rho_{\text{Planck}} = \hbar c/(8\pi^2\ell_P^4)$ | `5.867696005e+111` vs registered `5.867696e111`, rel err `8.26e-10` |
| Q4 | the vacuum document still quotes the registered needles | one occurrence each |
| Q5 | the sieve row states this scope, names the script, and no longer says "Not implemented" | 3 conditions |
| Q6 | no document asserts the censorship result | every root `.md` plus both `tahap uji` documents |

Q1 is not decoration. $\omega_P$ is registered as the *derived* quotient
$c/\ell_P$; recomputing the product instead of trusting the derivation string
is what makes the register's own internal consistency testable. Q3 similarly
reproduces the registered zero-point density from its three inputs.

**One identity is stated rather than computed.** With $m_P=\sqrt{\hbar c/G}$ and
$\ell_P=\sqrt{\hbar G/c^3}$, the Schwarzschild radius of a Planck-mass particle is
$r_S = 2Gm_P/c^2 = 2\,\ell_P$ exactly. Evaluating that numerically would require
registering $G$, and a constant entered into the register solely to make one
line computable is a worse register than no constant at all. It is written in the
module docstring as algebra and not presented as a measurement.

## 3. What the gate refuses to claim

Stated in the module docstring, in the gate's own output line, and enforced by Q6:

- quantum censorship is **not** established here;
- nothing about horizons, or about any quantum-gravity proposition;
- **not** that the censorship question is answered *negatively* by a resolution
  floor. A question below the operational floor is *unevaluable* in this
  framework. That is a different claim from being false, and the corpus had
  already been bitten by that difference in F3's declared variance.

## 4. Six defects found while building it

Recorded because each one made the gate report something other than the truth
before it was fixed:

1. **A cross-check that read the wrong number.** The first Q4 searched a generic
   `N \times 10^{-k}` pattern in the vacuum document and matched the *reduced
   Planck constant* $\hbar$, which appears earlier in that same file — producing
   a failure whose numbers were off by 145 orders of magnitude. The gate now uses
   the exact needle each quantity's register entry already names (`sites[].needle`),
   so a document edit cannot be satisfied by an unrelated number.
2. **A regex that did not compile.** The Q5 scope pattern contained `**` inside
   a group, which is a quantifier in Python's `re`; the gate crashed with
   `multiple repeat` instead of failing. Patterns are now literal about the
   bold markers.
3. **A guard that fired on honest prose, twice.** Q6's reverse-order overclaim
   pattern first matched across 60 characters and caught this phase's own
   sentence "the arithmetic is verified; quantum censorship remains open"; after
   narrowing it, it caught this report, which *quotes* the overclaim it is
   retargeting a mutation into. A guard that punishes the sentences holding the
   corpus honest is worse than no guard, so Q6 now skips matches that are
   negated or inside a quoted span, and harness cases **M7** and **M8** are the
   positive controls: both must leave the gate at exit 0 while M6 still fails.

A fourth observation is not a defect but shaped one: measuring $\rho_{\text{Planck}}$
first suggested the register was wrong by a factor of 62 — the standard Planck
energy density is `4.63e113` J/m³ and the registered value is `5.87e111`. The
suspect turned out to be the reader: the registered authority is
$\hbar c/(8\pi^2\ell_P^4)$, and the `hc/(8\ell_P^4)` that looks like the
formula is a rendering artefact, not a definition. Recorded here because the
corpus's response to "this number looks wrong" should be to recompute from the
authority string, not to adjust the number.

A fifth defect appeared only when the phase ran the **whole** rig rather than the
new gate: `tahap_uji_audit.py` failed, because its V8 condition asserted "Gate 2
is recorded as not implemented". That assertion was true on 2026-10-07 and false
after A18, and the gate was right to fail — but the condition had to change
shape, not be deleted. Its intent (a gate must not be presented as passing while
it is not) is now asked in both directions: the row must name the script that
exists, must record the implemented arithmetic, must keep the "not verified"
scope sentence, and must not still say "Not implemented". `harnesses/a10_tahu_inj.py`
case **C6** had targeted the old sentence and stopped applying, so it was
retargeted to something stronger than before — mutating the scope sentence into
"quantum censorship itself is verified here and is settled", which is a real
overclaim rather than a stale status.

A sixth defect was found by asking a question the rig never asks: **what did
the commit actually ship?** `.gitignore:8` excludes
`Theory_of_Everything_Derivations/` entirely, so the sieve row this gate
audits is not in the repository at all. On a fresh clone this gate returns
exit 2 — TOOL NOT RUN, never a pass — and so has `tahap_uji_audit.py`, which
has read those documents since A10. Q5 now also requires the scope sentence
from `A18_REPORT.md`, which *is* tracked and hash-pinned, so the scope cannot
drift silently even when the source folder is missing; harness case **M9**
deletes that sentence and must fail. Q4, the document needles, still needs
the folder: that part is recorded as `A18-R4` rather than papered over, because
deciding whether third-party clippings belong in the repository is an operator
decision, not a phase decision.

The lesson is the F1 one again: a gate that only ever inspected the artefact it
was written with would never have noticed that its sibling's expectation had
expired.

## 5. Fault injection

`harnesses/q2_censorship_inj.py` — **9/9**, every target byte-identical
afterwards, gate green at both ends:

| Case | Mutation | Result |
|---|---|---|
| M1 | register's $\ell_P$ perturbed `1.616255e-35 → 1.716255e-35` | exit 1, Q1 identity fails |
| M2 | density formula edited inside the gate, $\ell_P^4 → \ell_P^3$ | exit 1, Q3 disagrees |
| M3 | needle in the vacuum document edited (`10^{111} → 10^{112}`) | exit 1, Q4 reports it no longer contains the needle |
| M4 | sieve row reverted to "Not implemented" | exit 1, Q5 scope fails |
| M5 | "not verified" scope sentence deleted | exit 1, Q5 scope fails |
| M6 | overclaim injected into a root document | exit 1, Q6 fires |
| M7 | **control**: honest scope sentence injected | **exit 0**, Q6 stays quiet |
| M8 | **control**: an overclaim *quoted* as documentation of a defect | **exit 0**, quoted text is not an assertion |
| M9 | the tracked scope sentence deleted from `A18_REPORT.md` | exit 1, the scope must ship with the repository |

## 6. Rig changes and their consequences

| Item | Before | After |
|---|---|---|
| suite gates | 15 | **16** |
| `--with-harness` entries | 16 | **17** |
| proof harnesses | 24 | **25** |
| manifest | 98 | **100** |

The new gate is registered immediately before `tahap_uji_audit.py` and after
`bounded_loop_gate.py` — Gate 2 beside Gate 1 in spirit (both read their numbers
out of documents) and, like every gate, strictly before `checksum_check.py` so
that anything it wrote would still be hashed. Because those three numbers are
`Skill.md`'s constitution, `Skill.md`, `Brain.MD` and `README.md` were updated in
the same phase; a gate count that changes without the constitution changing is
how C1 stops meaning anything.

## 7. Files touched

**Created:** `quantum_censorship_check.py`, `harnesses/q2_censorship_inj.py`,
`A18_REPORT.md`.  
**Edited:** `suite_check.py` (gate register), `harness_check.py` (harness
register), `Skill.md`, `Brain.MD`, `README.md`, `TAHU_A10_REPORT.md` (dated
closure of `A10-R2`), `F0_REPORT.md` (dated addendum), and the Gate 2 row of
`Theory_of_Everything_Derivations/tahap uji/THE_SOVEREIGN_SIEVE_PROTOCOL.md`.

The sieve row is prose inside a third-party-style clipping folder, and it was
edited rather than annotated because the row is the workspace's own machine
status table: leaving "Not implemented" in it would contradict the gate that now
exists. No other document in that folder was touched.

## 8. Machine result

Filled from this phase's own run, after all corpus edits:

| Check | Result |
|---|---|
| `python quantum_censorship_check.py` | exit **0**, every condition above |
| `python harnesses/q2_censorship_inj.py` | `HARNESS: PASS -- 9/9 cases`, targets byte-identical |
| `python report_claim_check.py` | `PASS` |
| `python checksum_check.py` | `100/100` |
| `python suite_check.py` | `16/16` |
| `python suite_check.py --with-harness` | `17/17` |
| `python harness_check.py` | `25/25`, workspace byte-identical |
| AC Gate self-test / `lean` / `claim` / `audit` | `13/13`, `PASS`, `PASS`, `GENUINE=2` |

## 9. Residuals left open

| Id | Statement |
|---|---|
| `A10-R1` | The $10^{120}$ vacuum gap is **not solved**; Gate 2 does not touch it — the two are independent, and a gate that recomputed the Planck cutoff density must not be read as having closed it |
| `A10-R3` | RH, Navier–Stokes regularity and Langlands remain open in the literature regardless of any gate result here |
| `F8-R3` | Sub-repo encoding remains pinned-not-fixed (out of A9/A12 scope on purpose) |
| `A13-R1` | `lean\` remains outside the manifest scope |
| `A14-R1` | The `lean\` theorems are statements about the model over exact rationals |
| `A15-R2` | The entry-error enclosure is of the supplied matrix only |
| `A16-R1` | `report_claim_check.py` cannot read a bare `N files` / `N-gate` claim |
| `A18-R4` | **The gate's document inputs are not in the repository.** `.gitignore:8` excludes `Theory_of_Everything_Derivations/` entirely, so on a fresh clone this gate — and `tahap_uji_audit.py`, which has read those documents since A10 — return exit 2, TOOL NOT RUN, never a pass. The pre-existing behaviour is deliberate (inputs absent ⇒ no verdict), but it means Gate 2 cannot be run by an examiner who cloned rather than received a workspace. Q5 therefore also requires the scope sentence from `A18_REPORT.md`, which is tracked and hash-pinned, and M9 proves that requirement bites. Q4 (the document needles) still needs the folder; closing this properly means deciding whether the `tahap uji` documents should be tracked at all — an operator decision about third-party clippings, not a phase decision. |
| `A18-R3` | **Q6 is quote-aware, so a wrapped overclaim is not counted.** A document that renders an assertion inside quotation marks or a code span escapes the guard, which is what lets phase reports quote defects. The threat model here is honest drift rather than an adversary, and the trade-off is deliberate -- but it is a real hole and it is recorded rather than left implicit. |
| `A17-R1` | `trackc_recompile.py` is not a suite gate, and `OMEGATrackC.lean` has no offline byte-level check |
| **`A18-R1`** | **Gate 2 is implemented for the micro-scale arithmetic only, and this document is the place where that scope is written down.** If a future phase widens the gate, this row and the sieve row are the two places that must change together, because the gate checks the sieve row and nothing checks this file. |
| **`A18-R2`** | **`G` is not in the register.** The identity $r_S(m_P)=2\ell_P$ is therefore algebraic here, and any future phase that wants a numeric collapse-scale claim must first register $G$ with CODATA provenance — at which point `provenance_check.py`'s condition count moves and `Skill.md`, `Brain.MD` and this corpus's reports must be amended in the same phase. |

---

*End of A18_REPORT.md.*