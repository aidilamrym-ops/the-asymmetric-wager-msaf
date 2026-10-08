# A13_REPORT.md — Fase A13 (2026-10-07)

**Phase:** A13 — `lean/DiscreteCoordinates.lean`: the Scale-Axiom coordinate lattice, formalised on Lean core.  
**Date:** 2026-10-07.  
**Commit:** `72188c4`.  
**Language:** English.  
**`P_narrative`:** 0.  
**Machine record:** `lean\DiscreteCoordinates.lean` is **outside the manifest scope** (`checksum_check.py` covers root files, `provenance\`, `harnesses\`), so this phase changed the manifest count not at all.

---

## 1. What this phase added

One file, `lean/DiscreteCoordinates.lean` (334 lines), containing the formal
counterpart of what the corpus claims about finite coordinate resolution.

The corpus has always stated the Scale Axiom in prose — a smallest step
`Δ_univ`, coordinates that cannot be closer than it, and an empty open zone
around every valid coordinate. A13 did not add a claim. It made one existing
claim checkable by a kernel, on the strongest setting available on this machine.

## 2. What the file states

| Object | Statement |
|---|---|
| `PixelScale` | structure with `n : Nat` and `n_pos : 0 < n` — a **finite** positive step count, not a limit |
| `PixelScale.Δ` | `1 / n` — the Scale Axiom made operational as a stipulated quantum |
| `IsValidCoordinate` | `∃ k : Nat, k ≤ s.n ∧ x = k * s.Δ` — the cap `k ≤ n` is what makes the budget finite |
| `MSAF.min_separation` | two distinct valid coordinates satisfy `s.Δ ≤ absR (x - y)` |
| `MSAF.no_valid_coord_in_open_zone` | for valid `x, x0`: `¬ (0 < absR (x - x0) ∧ absR (x - x0) < s.Δ)` |

Both theorems are statements about **the lattice model**, and the docstrings say
so in those words. `no_valid_coord_in_open_zone` says the *MSAF lattice* has no
point in that zone; it does not say the real interval is empty, and the file
does not claim it.

## 3. What the file explicitly does not claim

Stated in the module header, not left to be inferred:

- not a refutation of ℵ₀ or of classical analysis;
- not a proof that physical space is discrete — only that the *model* has a
  minimum separation;
- not a proof about RH, the Critical Line, Protocol 09, `R_tail` or
  `M_hat_N` (those live in `lean/ModularWall.lean`, A14);
- not an evaluation inside `Z_none`, which stays non-operational.

## 4. Machine result

| Check | Result |
|---|---|
| `lean DiscreteCoordinates.lean` | exit **0**, Lean 4.33.1 **core only** (no Mathlib, no Batteries, no imports) |
| `sorry` tokens | **0** (AC Gate `lean` reads this) |
| `#print axioms MSAF.min_separation` | `depends on axioms: [propext, Classical.choice, Quot.sound]` |
| `#print axioms MSAF.no_valid_coord_in_open_zone` | `depends on axioms: [propext, Classical.choice, Quot.sound]` |
| AC Gate self-test | `13/13` |
| AC Gate `lean` (this file) | `PASS` |
| AC Gate `claim` / `audit` | `PASS`; auditor `GENUINE=2` |
| `checksum_check.py` | `93/93` (unaffected — `lean\` is out of scope) |
| `report_claim_check.py` | `PASS` |

The axiom lines above were re-measured from the terminal at A16 with the file
copied to a scratch directory (`#print axioms` appended there, workspace bytes
untouched); they are quoted from that run, not recalled.

**Core-only is a deliberate choice, not a limitation left unstated.** Mathlib is
absent from this machine, so any file importing it would be a file nobody here
can compile — and an uncompiled Lean file is exactly the failure mode F0
recorded for `SOLVABLE_FINITE_PARADOX.md`. Writing on core `Rat` costs twenty
local arithmetic lemmas (`absR`, cast lemmas, `omega` normalisation) and buys a
file whose every line is kernel-checked **here, today**.

## 5. Files touched

| File | Change |
|---|---|
| `lean/DiscreteCoordinates.lean` | created |
| `Brain.MD` | row for `lean\` added; header pointer to the A13 file |

Not touched: every root artefact, every sub-repository, `CHECKSUM.sha256`
(manifest scope excludes `lean\`), `theorem_provenance.json`, `MACHINE RESULT`.

## 6. How to re-run this phase

```bat
lean lean\DiscreteCoordinates.lean
python suite_check.py
python suite_check.py --with-harness
python scripts\gate.py check ^
  lean\DiscreteCoordinates.lean ^
  lean\ModularWall.lean ^
  bounded_loop.smt2 ^
  guinand-weil-rigorous-numerics-main\track_c_side_conditions.smt2
```

## 7. Residuals left open

| Id | Statement |
|---|---|
| `A10-R1` | The $10^{120}$ vacuum gap is **not solved** |
| `A10-R2` | Gate 2 (quantum censorship) remains **not implemented** |
| `A10-R3` | RH, Navier–Stokes regularity and Langlands remain open in the literature regardless of any gate result here |
| `F8-R3` | Sub-repo encoding remains pinned-not-fixed (out of A9/A12 scope on purpose) |
| `A13-R1` | `lean\` sits outside the manifest scope, so neither Lean file is hash-pinned. Recorded here rather than silently accepted; closing it would mean widening `checksum_check.TREES`, which is an A-scale decision about manifest scope, not a bookkeeping fix. |

---

*End of A13_REPORT.md.*