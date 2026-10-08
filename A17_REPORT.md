# A17_REPORT.md — Fase A17 (2026-10-07)

**Phase:** A17 — install Mathlib, recompile `OMEGATrackC.lean`, close residual `A15-R1`.  
**Date:** 2026-10-07.  
**Language:** English.  
**`P_narrative`:** 0.  
**Closes:** `A15-R1`. **Adds:** `A17-R1` (below).

---

## 1. The residual

`A15_REPORT.md` §7 registered, in the corpus's own words, that
`OMEGATrackC.lean` **was not recompiled** after its `rhoActual` literal was
re-anchored from a dps-doubling estimate to a ball-arithmetic bound. The literal
rested on `track_c_make_smt.py`, Z3 and the anti-circularity audit — none of
which compile the module. A file that nobody can compile is precisely the failure
F0 recorded for `SOLVABLE_FINITE_PARADOX.md`, and it was recorded as open rather
than argued away.

## 2. What was installed

| Item | Value |
|---|---|
| Lean toolchain | `leanprover/lean4:v4.33.1` (already present) |
| Mathlib | release **`v4.33.1`**, commit `0df444a360eaa60ab8c11dca51a86af692955474` |
| Why that tag | Mathlib tags are not semver strings Lake accepts (`version = "v4.33.1"` is rejected), so the tag was resolved to its commit and pinned by `rev` |
| Cache | `lake update` fetched the prebuilt `.olean` cache: 8690 files |
| Location | a throwaway Lake project **outside the workspace** (`%TEMP%\opencode\msaf-trackc`); nothing was installed into `D:\THE ASYMMETRIC WAGER` |

Disk cost was met from 36 GB free on `C:`. No workspace file was touched to make
this work, and the temporary project is reproducible from the recorded recipe.

## 3. What was measured

The file compiled, and the file compiled **exactly**:

```
ok    zero sorry tokens in code (comments excluded; the kernel confirms below)
ok    zero axiom declarations (every result is proved)
ok    all 10 expected theorems present
ok    rhoActual literal = 58287013697174734848 / 10^198 = 5.8287013697174734925e-179
ok    rhoStar, lambdaMin and nDim declarations present
ok    byte-for-byte copy of the workspace file,
      sha256 21795fe82f75df07ab49ee58e346237f4030e442a3d6e68cb9f377c5e769085e
ok    kernel compiled the file with no diagnostics and no holes
      (Mathlib v4.33.1 @ 0df444a360ea, Lean toolchain v4.33.1)
```

Axiom footprint, all ten theorems, printed by the kernel:

```
two_abs_mul_le_add_sq            [propext, Classical.choice, Quot.sound]
enclosure_quad_bound             [propext, Classical.choice, Quot.sound]
certified_positivity             [propext, Classical.choice, Quot.sound]
measured_within_tolerance        [propext, Classical.choice, Quot.sound]
margin_at_least_74_orders        [propext, Classical.choice, Quot.sound]
margin_satisfies_master_theorem  [propext, Classical.choice, Quot.sound]
tolerance_fails_the_coarse_bound [propext, Classical.choice, Quot.sound]
implied_constant_ge_81           [propext, Classical.choice, Quot.sound]
implied_constant_lt_82           [propext, Classical.choice, Quot.sound]
tolerance_positive               [propext, Classical.choice, Quot.sound]
```

**This footprint is the control, not a fresh fact.** It is what the 2026-10-02 run
recorded before the literal changed, and it is unchanged — which is exactly the
expected result, because A15 changed one `abbrev`'s value and no theorem
statement. Had it drifted, the literal edit would have been blamed for a change
it did not make.

The substantive difference from 2026-10-02 is narrower and more important: the
seven numerical theorems are `by norm_num` over `rhoActual`, so **the kernel
itself evaluated the new ball-arithmetic bound** and confirmed the side
conditions, including `margin_at_least_74_orders : rhoActual * 10^74 ≤ rhoStar`.
A15 could only show that Z3 agreed with the literal; A17 shows Lean agreed with
it.

## 4. Two defects in my own verification, found by not trusting it

A phase that installs a toolchain should distrust the toolchain reports that
follow as much as it distrusts a number written by hand. Two of A17's own
claims did not survive that distrust, and both are recorded here rather than
edited out of the log:

1. **`lake build` was never evidence that this file compiled.** The lakefile
   target built the *library module* declared in it — a one-line
   `import Mathlib` — while the file under scrutiny sat uncompiled beside it,
   and the build still exited 0. The first version of `trackc_recompile.py`
   would have reported a green `lake build` for a file the kernel had never
   seen. The tool now runs `lake env lean` on the byte-identical copy and
   treats **any** diagnostic as failure; `lake build` is not in the path.
2. **The `sorry` scan was blind to prose.** The scanner counted the raw text,
   and this module's header legitimately *writes the word* when it reports
   there are none — so the honest file would have failed its own gate. The scan
   now strips Lean comments first, and the kernel's own `declaration uses
   'sorry'` warning is the authority; a control case (prose containing the word
   inside a comment) is part of the mutation set and must PASS.

A third observation, recorded because it nearly produced a false alarm: while
probing mutants, the mutated copies were written into the same temporary project
directory as the pristine one, and a later `sorry`-bearing copy was mistaken
for the artifact of record. The workspace file was never modified — its digest
was identical before and after — but the conclusion drawn from the wrong file
would have been wrong. `trackc_recompile.py` now copies, digests and compiles
in one step, and the log asserts the copy equals the file before compiling it.

## 5. The tool that makes this repeatable

`guinand-weil-rigorous-numerics-main/trackc_recompile.py` (new). It resolves the
Mathlib tag to a commit, builds a throwaway project outside the workspace,
verifies the copied file against the workspace file by sha256, compiles it,
prints the footprint of the ten named theorems, and exits **0 only if** the
footprint equals the 2026-10-02 control. Exit 1 on any failed check, exit 2 when
there is no toolchain or no network — never a pass.

It is deliberately **not** a suite gate. The suite is the offline contract;
this tool needs the network and several gigabytes. Same reasoning that kept
`url_liveness_check.py` out of the suite.

### 5.1 The gate can fail — six cases

| Mutation | Result |
|---|---|
| `rhoActual` declaration deleted | exit **1** — shape check refuses |
| `rhoStar` raised 12 decades (margin claim now false) | exit **1** — the kernel reports `unsolved goals`; this is the authoritative path |
| a `by norm_num` replaced by `by sorry` | exit **1** — caught twice: the static scan counts it *and* the kernel reports a hole |
| `simp only [not_lt]` replaced by `sorry` | exit **1** — same, one token |
| `tolerance_positive` deleted | exit **1** — `expected theorems missing` |
| **control**: prose containing the word “sorry” inside a comment | **exit 0** — the scanner must not read prose |

A tool that only ever prints PASS has not been tested. Each mutant was reverted
by deleting it; the workspace file's sha256 was unchanged before and after
(`51dca387…`), and `git status` shows no modification to it.

## 6. Files touched

| File | Change |
|---|---|
| `guinand-weil-rigorous-numerics-main/trackc_recompile.py` | **created** |
| `guinand-weil-rigorous-numerics-main/OMEGATrackC.lean` | header: A15's "not recompiled" paragraph replaced by the A17 record; **no declaration changed** |
| `guinand-weil-rigorous-numerics-main/README.md` | Track-C tool row, `A15-R1` status |
| `guinand-weil-rigorous-numerics-main/WORKING_PAPER.md` | limitations: the compile gap is closed |
| `Brain.MD` | purpose line, key files, `A17_REPORT.md` row, version bump |
| `README.md` (root) | `A15-R1` marked closed, roadmap row A17 |
| `A15_REPORT.md` | dated closure note on the residual row |
| `F0_REPORT.md` | dated addendum §O |
| `CHECKSUM.sha256` | regenerated |

Not touched: every literal and theorem statement in `OMEGATrackC.lean`,
`track_c_side_conditions.smt2`, `bounded_loop.smt2`, both `lean\` files,
`theorem_provenance.json`, `MACHINE RESULT`, Gate-2 needles.

## 7. Machine result

Filled from this phase's own run, after all corpus edits:

| Check | Result |
|---|---|
| `lake env lean` on the byte-identical copy | exit **0**, **no diagnostics at all**, Mathlib `v4.33.1` |
| `#print axioms` × 10 theorems | all `[propext, Classical.choice, Quot.sound]`, drift check PASS |
| `python trackc_recompile.py` | `TRACKC_RECOMPILE: PASS`, exit 0 |
| mutation probe (4 mutants) | 4/4 exit 1 |
| `lean lean\DiscreteCoordinates.lean` / `lean\ModularWall.lean` | exit 0 (unchanged, core-only, no Mathlib involved) |
| `python report_claim_check.py` | `PASS` |
| `python checksum_check.py` | `98/98` |
| `python suite_check.py` | `15/15` |
| `python suite_check.py --with-harness` | `16/16` |
| `python harness_check.py` | `24/24`, workspace byte-identical |
| AC Gate self-test / `lean` / `claim` / `audit` | `13/13`, `PASS`, `PASS`, `GENUINE=2` |

## 8. Residuals left open

| Id | Statement |
|---|---|
| `A10-R1` | The $10^{120}$ vacuum gap is **not solved** |
| `A10-R2` | Gate 2 (quantum censorship) remains **not implemented** |
| `A10-R3` | RH, Navier–Stokes regularity and Langlands remain open in the literature regardless of any gate result here |
| `F8-R3` | Sub-repo encoding remains pinned-not-fixed (out of A9/A12 scope on purpose) |
| `A13-R1` | `lean\` remains outside the manifest scope, so neither Lean file is hash-pinned |
| `A14-R1` | The `lean\` theorems are statements about the model over exact rationals |
| `A15-R2` | The enclosure bounds the entry error of the **supplied** matrix only |
| **`A17-R1`** | **`trackc_recompile.py` is not a suite gate and its result is not in the manifest.** It needs the network and several GB of Mathlib, so it cannot join the offline contract — but that means the file it certifies (`OMEGATrackC.lean`) has **no offline byte-level check at all**, exactly the gap `A13-R1` records for the `lean\` files. Recorded as a structural limit rather than solved; the honest options are (a) accept that Track C's provenance is tool-run, not hash-pinned, or (b) pin the module's sha256 inside `trackc_make_smt.py` so an offline gate fails if the file changes. Option (b) is a small change and is left for the next phase. |
| `A16-R1` | `report_claim_check.py` cannot read a bare `N files` / `N-gate` claim (`A16_REPORT.md` §8) |

---

*End of A17_REPORT.md.*