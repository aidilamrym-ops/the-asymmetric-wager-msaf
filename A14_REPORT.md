# A14_REPORT.md — Fase A14 (2026-10-07)

**Phase:** A14 — `lean/ModularWall.lean`: `M_hat_N` and `R_tail` as structural contracts, with the zero-fudging rule proved instead of asserted.  
**Date:** 2026-10-07.  
**Commit:** `972d59f`.  
**Language:** English.  
**`P_narrative`:** 0.  
**Manifest:** unchanged (93) — `lean\` is outside `checksum_check` scope, as recorded in `A13_REPORT.md` §7 `A13-R1`.

---

## 1. What this phase added

`lean/ModularWall.lean` (214 lines), standalone by design: it imports nothing
and does not import `DiscreteCoordinates`, so it compiles independently.

The corpus asserts "zero-fudging" in many places — uncertainty may grow, but the
midpoint never moves in favour of a proof. That sentence had never been proved.
A14 proves the two readings of it that Lean core can carry.

## 2. What the file states

| Object | Statement |
|---|---|
| `TailRadius` | `value : Rat` with `nonneg : 0 ≤ value` — the **contract** of `R_tail`; its numeric value is computed by OMEGA-CORE v2 / `msaf_visual.py`, not here |
| `UncertaintyBall` | `midpoint`, `radius`, `radius_nonneg : 0 ≤ radius` |
| `InBall` | `b.midpoint - b.radius ≤ y ∧ y ≤ b.midpoint + b.radius` |
| `modularWall` | `M_hat_N`: wraps `x` with the tail radius, midpoint **by construction** `x` |
| `midpoint_never_shifts` | `(modularWall x rt).midpoint = x` — structural zero-fudging, `rfl` |
| `interval_midpoint_zero_fudging` | `((x - r) + (x + r)) / 2 = x` — arithmetic zero-fudging: recomputing the midpoint **floating-point style** still returns `x` exactly |
| `wall_contains_midpoint` | `InBall (modularWall x rt) x` |
| `interval_nonempty` | `0 ≤ r → x - r ≤ x + r` |

The third theorem is the one worth reading twice. The first two show the
midpoint does not shift; `interval_midpoint_zero_fudging` shows that *the
operation that could silently shift it* — `(lo + hi)/2` — returns exactly `x` on
exact rationals. Zero-fudging is therefore a property of the arithmetic, not a
convention about where to put the point.

## 3. What the file explicitly does not claim

Stated in the module header:

- **not** a proof that `R_tail` is small, flat (F1-N), or bounded by any
  explicit constant — numerical flatness lives in OMEGA-CORE / `visual_check`;
- not a claim about RH, the Critical Line, or the continuum;
- not an evaluation inside `Z_none` (non-operational);
- not a refutation of anything; not a proof about physical space;
- not an evaluation of `R_tail`'s closed-form exponential — Lean 4 core has no
  `Real.exp`, so only the contract is modelled.

## 4. Machine result

| Check | Result |
|---|---|
| `lean ModularWall.lean` | exit **0**, Lean 4.33.1 core only |
| `sorry` tokens | **0** |
| `#print axioms MSAF.ModularWall.midpoint_never_shifts` | `depends on axioms: [propext, Quot.sound]` |
| `#print axioms ...interval_midpoint_zero_fudging` | `depends on axioms: [propext, Classical.choice, Quot.sound]` |
| `#print axioms ...wall_contains_midpoint` | `depends on axioms: [propext, Classical.choice, Quot.sound]` |
| `#print axioms ...interval_nonempty` | `depends on axioms: [propext, Classical.choice, Quot.sound]` |
| AC Gate self-test | `13/13` |
| AC Gate `lean` (this file) | `PASS` |
| AC Gate `claim` / `audit` | `PASS`; auditor `GENUINE=2` |
| `checksum_check.py` | `93/93` |

A measurement worth recording: `midpoint_never_shifts` needs **no**
`Classical.choice` — it is a definitional `rfl`, so its axiom set is the smallest
in the corpus. The other three do use choice, through the `Decidable.em`
branches in `sub_left_le` / `le_add_of_nonneg`. That is expected on core Lean
and is why the file carries no `noncomputable` markers: everything is computable.

The axiom lines were re-measured from the terminal at A16 with the file copied
to a scratch directory (`#print axioms` appended there, workspace bytes
untouched).

## 5. Files touched

| File | Change |
|---|---|
| `lean/ModularWall.lean` | created |
| `Brain.MD` | row for the A14 file |

Not touched: root artefacts, sub-repositories, `CHECKSUM.sha256`,
`OMEGATrackC.lean` (which is the Track-C file and was re-anchored in A15),
`theorem_provenance.json`, `MACHINE RESULT`.

## 6. How to re-run this phase

```bat
lean lean\ModularWall.lean
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
| `A13-R1` | `lean\` remains outside the manifest scope, so neither Lean file is hash-pinned (recorded by A13; still open) |
| `A14-R1` | The theorems above are theorems about the **model**, over exact rationals. They say nothing about the numerics that instantiate `R_tail` with a real value; the two halves are connected in the prose corpus, not in a proof. Recorded rather than papered over. |

---

*End of A14_REPORT.md.*