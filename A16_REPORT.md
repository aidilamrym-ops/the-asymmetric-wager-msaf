# A16_REPORT.md — Fase A16 (2026-10-07)

**Phase:** A16 — Bookkeeping closure for A13, A14 and A15.  
**Date:** 2026-10-07.  
**Operator instruction:** "lalu planing kedepannya bagaimana?" followed by selection of *A16 bookkeeping dulu*.  
**Language:** English.  
**`P_narrative`:** 0.

---

## 1. Why this phase exists

A13, A14 and A15 were each completed, verified and pushed, and each left the
corpus with **no prose record at all**. The README roadmap stopped at A12, the
README open-item table knew nothing of `A15-R1` (the honest statement that
`OMEGATrackC.lean` was not recompiled), and `lean\` — two kernel-checked Lean
files — was not hash-pinned and not registered anywhere an examiner would look.

Three phases of verified work, invisible in the documents. That is exactly the
failure mode `report_claim_check.py` and `harness_check.py` exist to prevent in
code; this phase applies the same standard to the phase records.

A16 adds no mathematics. It makes the corpus say what it already does.

## 2. What was written

| File | Content |
|---|---|
| `A13_REPORT.md` | `lean/DiscreteCoordinates.lean`: `PixelScale`, `Δ = 1/n`, `IsValidCoordinate`, `min_separation`, `no_valid_coord_in_open_zone`; measured axiom sets; what the file explicitly does not claim; `A13-R1` registered |
| `A14_REPORT.md` | `lean/ModularWall.lean`: `TailRadius`, `UncertaintyBall`, `InBall`, `modularWall`, `midpoint_never_shifts`, `interval_midpoint_zero_fudging`, `wall_contains_midpoint`, `interval_nonempty`; `A14-R1` registered |
| `A15_REPORT.md` | `rho_actual` as a ball-arithmetic bound: method, old→new literal table, margin, the corrected flint-capability record, the push incident, `A15-R1`/`A15-R2` registered |
| `A16_REPORT.md` | this file |

The A13 and A14 axiom sets were **re-measured** for this phase by copying each
file to a scratch directory outside the workspace, appending `#print axioms`,
and running `lean` there — workspace bytes untouched:

```
'MSAF.min_separation' depends on axioms: [propext, Classical.choice, Quot.sound]
'MSAF.no_valid_coord_in_open_zone' depends on axioms: [propext, Classical.choice, Quot.sound]
'MSAF.ModularWall.midpoint_never_shifts' depends on axioms: [propext, Quot.sound]
'MSAF.ModularWall.interval_midpoint_zero_fudging' depends on axioms: [propext, Classical.choice, Quot.sound]
'MSAF.ModularWall.wall_contains_midpoint' depends on axioms: [propext, Classical.choice, Quot.sound]
'MSAF.ModularWall.interval_nonempty' depends on axioms: [propext, Classical.choice, Quot.sound]
```

The measurement corrected a detail the A15 working notes had carried: because
`midpoint_never_shifts` is a definitional `rfl`, it does **not** use
`Classical.choice`. Its axiom set is the smallest anywhere in the corpus.

Every numeric claim in `A15_REPORT.md` §2 was likewise recomputed from the
shipped literals with exact `fractions.Fraction`, not carried over from the
working session:

```
margin rho*/rho NEW = 74.4468626023 decades
margin rho*/rho OLD = 74.4460318880 decades
rho_new/rho_star = 3.5738589e-75      rho_old/rho_star = 3.5807014e-75
lam/rho_new = 2.266458e+76            rho_star*401/lam = 4.950617283950617065
```

That recomputation **overturned one figure** the working notes carried
(`λ/(ρ*·401) = 5.652014e73`); the verified value is `2.019950e-01`, and the
report states the verified one. A number copied from memory into a permanent
document is exactly what `P_narrative = 0` forbids.

## 3. Residuals registered

| Id | Statement | Where |
|---|---|---|
| `A13-R1` | `lean\` is outside the manifest scope, so neither Lean file is hash-pinned | `A13_REPORT.md` §7, `README.md` §4.3, `Brain.MD` |
| `A14-R1` | The Lean theorems are statements about the **model** over exact rationals; nothing connects them to the numerics that instantiate `R_tail` | `A14_REPORT.md` §7, `README.md` §4.3 |
| `A15-R1` | `OMEGATrackC.lean` was not recompiled after the `rhoActual` literal changed (no Mathlib); the literal is verified by `track_c_make_smt.py` 3-way MATCH, Z3 7/7 and the AC Gate instead | `A15_REPORT.md` §7, `README.md` §4.3, `Brain.MD` |
| `A15-R2` | The enclosure bounds the entry error **of the supplied matrix** and transfers to no other build | `A15_REPORT.md` §7, `README.md` §4.3 |

None of these is closable by writing. `A13-R1` needs a decision about manifest
scope; `A15-R1` needs Mathlib installed; `A14-R1` and `A15-R2` are statements
about what the artefacts do not say, and stay open as long as they are true.

## 4. Stale figures the gates did not catch

Two reader-facing numbers were wrong and no gate pattern matched them, because
`report_claim_check.py` reads manifest claims as *rows*, gates as *counts*, and
never as a bare `N files` / `N-gate` compound in a diagram:

| Location | Was | Now |
|---|---|---|
| `README.md` §6.1 diagram | `Gates (14 offline suite gates…)` | `15` |
| `README.md` §6.1 diagram | `Fault-injection harnesses (22…)` | `24` |
| `Brain.MD:17` | `14-gate/22-harness rig`, `roadmap F0–A9`, `F8-R1..R4` | `15-gate/24-harness rig`, `F0–A16`, live residual list |

The `Brain.MD` line had been passing P5 only because the same line contained the
string `F0`, which the anchor rules accept as a date. **A gate that passes a
wrong sentence because an unrelated word on that line looks like a timestamp is a
gate with a blind spot, and this phase recorded that fact rather than only fixing
the sentence.**

## 5. Numbers that moved, and where

| Figure | Before | After | Locations updated |
|---|---|---|---|
| manifest files | 93 | **97** | `README.md` §4.1, `Brain.MD` (`checksum_check.py` row; C1 `BRAIN_ROWS` enforces the bold figure live) |
| root files in scope | 59 | **63** | `Brain.MD` (same row, with the phase history retained) |
| suite gates | 15 | 15 | unchanged; two stale *prose* figures corrected in §4 above |
| proof harnesses | 24 | 24 | unchanged; one stale prose figure corrected in §4 above |
| `Brain.MD` version | v1.18 | **v1.19** | footer; `A12_REPORT.md` §4 "current-state pointers" line updated to match, since that line states the present |

`Skill.md` was **not** touched: it states gate and harness counts, neither of
which moved, and C1 hard-equality therefore holds untouched.

## 6. Blast radius

**Created:** `A13_REPORT.md`, `A14_REPORT.md`, `A15_REPORT.md`, `A16_REPORT.md`.  
**Edited:** `README.md`, `Brain.MD`, `A12_REPORT.md` (one pointer line), `CHECKSUM.sha256`.  
**Not touched:** every sub-repository, `F0`–`F11` report bodies, `Skill.md`, `AGENTS.md`, `informasi mentah\` (user inbox, untracked by design), `theorem_provenance.json`, `MACHINE RESULT`, Gate-2 honesty needles.

## 7. Machine result

Filled from this phase's own run, after all corpus edits:

| Check | Result |
|---|---|
| `lean lean\DiscreteCoordinates.lean` / `lean\ModularWall.lean` | exit 0 both, `#print axioms` as quoted in §2 |
| `python checksum_check.py --update` | manifest written, 97 files (at A16) |
| `python report_claim_check.py` | `PASS` |
| `python checksum_check.py` | `97/97` |
| `python suite_check.py` | `15/15` |
| `python suite_check.py --with-harness` | `16/16` |
| `python harness_check.py` | `24/24`, workspace byte-identical |
| AC Gate self-test | `13/13` |
| AC Gate `lean` (`lean\` + `OMEGATrackC.lean`) | `PASS` |
| AC Gate `claim` (4 targets) | `PASS` |
| AC Gate `audit` (2 scripts) | `GENUINE=2` |

Two gate findings were produced **during** this phase and fixed, rather than
discarded: P6 caught the new `Brain.MD` footer naming `gw_rho_formal.py` on a
line that also names `harnesses\`, and C1 caught the manifest figure before
`A16_REPORT.md` existed. A gate that finds nothing in a phase that edited eleven
prose lines is a gate that is not reading.

## 8. Residuals left open

| Id | Statement |
|---|---|
| `A10-R1` | The $10^{120}$ vacuum gap is **not solved** |
| `A10-R2` | Gate 2 (quantum censorship) remains **not implemented** |
| `A10-R3` | RH, Navier–Stokes regularity and Langlands remain open in the literature regardless of any gate result here |
| `F8-R3` | Sub-repo encoding remains pinned-not-fixed (out of A9/A12 scope on purpose) |
| `A13-R1` | `lean\` outside manifest scope (see §3) |
| `A14-R1` | Model theorems vs numerics (see §3) |
| `A15-R1` | `OMEGATrackC.lean` not recompiled (see §3) |
| `A15-R2` | Enclosure is of the supplied matrix only (see §3) |
| `A16-R1` | **CLOSED 2026-10-07 (A20).** ~~`report_claim_check.py` cannot read a bare `N files` / `N-gate` claim outside a `rows`/`gates=` pattern~~ -- P5 now reads digit, bold and spelled `N files` under a manifest-line scope, the compound gate through the constitution's bold, and the reversed `harnesses: N` form. The pattern immediately found two genuinely stale sentences, both anchored in the same phase (this report's results table, F0's A18 summary), and `harnesses`p5_files_inj.py`` holds the boundaries: `12/12`, with an out-of-scope encoding count and an anchored history line both required to stay green. |

---

*End of A16_REPORT.md.*