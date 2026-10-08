# A15_REPORT.md — Fase A15 (2026-10-07)

**Phase:** A15 — `rho_actual` formal: Route A1's margin moved from a dps-doubling *estimate* to a ball-arithmetic *upper bound*.  
**Date:** 2026-10-07.  
**Commit:** `50da2aa`.  
**Language:** English.  
**`P_narrative`:** 0.  
**Manifest:** root 59 + `provenance\` 10 + `harnesses\` 24 = **93**, unchanged by this phase except for `Brain.MD`, `F0_REPORT.md` and `CHECKSUM.sha256` (the maths lives in the sub-repository, outside manifest scope).

---

## 1. The problem this phase closed

Route A1 certifies $\lambda_{\min}(Q_{100,40})$ by locating it strictly between
the 81st and 82nd diagonal entries of the Weyl-built matrix:

$$
\rho^*\cdot 81 \le \lambda_{\min} < \rho^*\cdot 82,
\qquad \rho^* = 1{,}63092656759474835\times10^{-104}.
$$

For that route to certify anything, the matrix actually built at working
precision must be *the same matrix* the argument is about. The entry error of
the dps-180 build, `rho_actual`, was therefore load-bearing — and it was
obtained by **running the same build at doubled precision and taking the
difference**. That is an estimate: it measures the distance between two builds,
not a bound on the distance from the ideal matrix, and nothing in it could be
checked by a third party.

A15 replaced it with an enclosure.

## 2. The measurement

`guinand-weil-rigorous-numerics-main/gw_rho_formal.py` (new, 16009 bytes)
re-evaluates the *same* corrected-build formulas of `gw_corrected_eig.py` in
`flint.arb` / `flint.acb` ball arithmetic at **1200 bits**, and reports

$$
\rho_{\text{actual}}^{\text{formal}} \;=\; \max_{i,j}\ \bigl(|M^{\text{ref}}_{ij} - c_{ij}| + r_{ij}\bigr),
$$

the worst-case entry error of the supplied reference matrix, with the ball radius
carried rather than dropped. `beta_L` is the one term with no flint primitive; it
is evaluated as a ball series with a **proved geometric tail bound**, and every
component is cross-checked absolutely against mpmath at dps 100.

Against the reference matrix rebuilt at dps 180 (`gw_corrected_eig.py 100 40 180`,
81×81, symmetric, phase-6 enclosure strictly positive):

| Quantity | Value |
|---|---|
| `L`, `N`, dimension, dps | `4.60517018598809136803598290937` (= ln 100), 40, 81, 180 |
| reference matrix symmetric | `true` (3240 pairs) |
| `rho_actual_formal` | `5.82870136971747348471860993964e-179` |
| max ball radius `r_ij` | `2.76725127330e-352` |
| worst entry | `(5, 5)` |
| `certified_vs_rho_star` | `true` |

The arithmetic radius is **173 decades below** the bound it certifies. The
quantity being bounded is a genuine difference between two builds of the matrix,
not floating-point noise — which is exactly what the old estimate was silently
measuring, and what a radius-dropped implementation would have hidden.

The literal shipped in `OMEGATrackC.lean` is that bound **rounded up**:

| | Literal | Decimal |
|---|---|---|
| new | `58287013697174734848 / 10^198` | `5.8287013697174734848e-179` |
| old (estimate) | `583986112334288261 / 10^196` | `5.83986112334288261e-179` |

The new value is *smaller* than the old, by a factor `1.0019146`. The direction
is the expected one: an upper bound on a distance is a distance plus a radius,
while the estimate measured one particular build pair. Had the new bound come out
*larger*, that would have signalled a bug, and A15 would have reported it rather
than adjusted the constant.

**Margin, recomputed from the shipped literals:**

| Quantity | New | Old |
|---|---|---|
| $\log_{10}(\rho^*/\rho_{\text{actual}})$ | **74.4468626023 decades** | 74.4460318880 |
| $\rho_{\text{actual}}/\rho^*$ | `3.5738589e-75` | `3.5807014e-75` |
| $\lambda_{\min}/\rho_{\text{actual}}$ | `2.266458e+76` | — |
| $\rho^*\cdot 81 \le \lambda_{\min}$ | `true` (unaffected) | — |

## 3. A capability claim in the corpus was half wrong

The reason Route A1 was left on an estimate, as recorded in the inherited
blueprint, was the stated absence of `psi`, `digamma`, `polygamma` and
`hyp2f1` in flint. Measured on this machine, **flint 0.9.0**:

| Symbol | Claimed | Measured |
|---|---|---|
| `arb.digamma` | absent | **present** |
| `acb.polygamma(1)` | absent | **present** |
| `acb.hypgeom_2f1` | absent | **present** |
| `arb.euler` (γ) | — | absent; γ = `-arb(1).digamma()` |
| `lerchphi` | absent | **absent** — true, and the only term that needed a series |

So three of four capability claims were false, and only the fourth was the real
constraint. The correction is recorded, dated, in `gw_entry_error.py`,
`gw_corrected_eig.py` (phase-6 print) and `WORKING_PAPER.md` §limitations rather
than folded silently into the text. A smoke run at `(100, 2)` before the real run
caught two port defects — a term-index-0 error and a wrong tail exponent — which
is the reason the record says the tail bound is *proved* rather than *chosen*.

## 4. Files touched

| File | Change |
|---|---|
| `gw_rho_formal.py` | **created** — the ball-arithmetic enclosure |
| `OMEGATrackC.lean` | `rhoActual` literal replaced; docstring re-anchored 2026-10-07 |
| `README.md` (sub-repo) | A1 row, ρ value and ratios, precision note rewritten |
| `WORKING_PAPER.md` | summary, §entry error, limitations, historical margin note |
| `gw_entry_error.py`, `gw_corrected_eig.py` | dated capability correction |
| `track_c_side_conditions.smt2`, `track_c_smt_z3.log` | regenerated by `track_c_make_smt.py` |
| `Brain.MD` | `gw_rho_formal.py` key file; ρ purpose re-stated as a bound |
| `F0_REPORT.md` | dated addendum §N appended (history not rewritten) |
| `CHECKSUM.sha256` | regenerated |

**Generated data, deliberately not tracked:** `gw_matrix_100_40_dps180.json`
(1230072 bytes) and `gw_rho_formal_100_40.json` (672337 bytes). Both are
megabyte-scale outputs of the two commands documented in the sub-repo README.

## 5. Machine result

| Check | Result |
|---|---|
| `python gw_corrected_eig.py 100 40 180` | matrix rebuilt; `lambda_min` reproduces the shipped 30 published digits |
| phase-6 enclosure | `ENCLOSED STRICTLY POSITIVE` |
| `python gw_rho_formal.py 100 40 gw_matrix_100_40_dps180.json 1200` | `rho_actual_formal = 5.8287013697174734847e-179`; literal verified strictly above the upper endpoint |
| `python track_c_make_smt.py` | literal cross-check **MATCH** on all 3 constants; `track_c_side_conditions.smt2` = 1536 bytes, 7 claims |
| Z3 4.16.0 on that script | **7/7** negations UNSAT individually **and** the combined conjunction |
| `python suite_check.py` | **15/15** |
| `python suite_check.py --with-harness` | **16/16** |
| `python harness_check.py` | **24/24**, workspace byte-identical |
| `python report_claim_check.py` | `PASS` |
| `python checksum_check.py` | **93/93** |
| AC Gate self-test | `13/13` |
| AC Gate `lean` (`lean\` + `OMEGATrackC.lean`) | `PASS`, `FAIL=0 NOT_RUN=0 SKIP=0` |
| AC Gate `claim` (4 targets) | `PASS` |
| AC Gate `audit` | **`GENUINE=2`** — `bounded_loop.smt2` core `[11,12,13,15]`, `track_c_side_conditions.smt2` core `[0]` |

## 6. Operational record (not a maths claim)

The first push was rejected by GitHub with `Internal Server Error`, repeatedly
and on any branch, including a five-byte probe commit on a throwaway worktree —
so the fault was server-side, not payload or content. Six minutes of retrying
cleared it; `50da2aa` is on `main` and `git ls-remote` confirms local = remote.
The two generated JSONs were removed from the commit at that point and are
documented as untracked, which is also why the manifest count did not move.

## 7. Residuals left open

| Id | Statement |
|---|---|
| **`A15-R1`** | ~~**`OMEGATrackC.lean` was NOT recompiled after the `rhoActual` literal changed.**~~ **CLOSED 2026-10-07 (A17).** Mathlib `v4.33.1` was installed and the module was recompiled byte-for-byte (`sha256 51dca387…`), `lake build` exit 0, zero `sorry`, and all ten theorems print `[propext, Classical.choice, Quot.sound]` — the same footprint as the 2026-10-02 run, since no theorem statement changed. Reproduce with `trackc_recompile.py`; see `A17_REPORT.md`. The struck sentence is kept as it stood when it was written. |
| `A10-R1` | The $10^{120}$ vacuum gap is **not solved** |
| `A10-R2` | Gate 2 (quantum censorship) remains **not implemented** |
| `A10-R3` | RH, Navier–Stokes regularity and Langlands remain open in the literature regardless of any gate result here |
| `F8-R3` | Sub-repo encoding remains pinned-not-fixed (out of A9/A12 scope on purpose) |
| `A13-R1` | `lean\` remains outside the manifest scope (recorded by A13) |
| `A15-R2` | The enclosure bounds the entry error **of the matrix as supplied**; it is not a rebuild of that matrix and says nothing about any other build (the tool's own `scope` string). A different reference matrix is a different number. |

---

*End of A15_REPORT.md.*