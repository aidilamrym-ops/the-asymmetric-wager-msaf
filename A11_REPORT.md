# A11 REPORT — Residual Closure

**Workspace:** `D:\THE ASYMMETRIC WAGER`
**Date:** 2026-10-07
**Predecessor:** `TAHU_A10_REPORT.md`, `F8_REPORT.md`
**Status:** F8-R1 and F8-R2 closed; A10-R1/R2/R3 and F8-R3/R4 remain open or deferred
**Language:** English (project artefact). $P_{\text{narrative}} = 0$.

---

## 0. What A11 is, and why it exists

A9 left two residual questions on `F8_REPORT.md` that no later phase answered:

1. **F8-R1** — `report_claim_check.py` never parsed the string form
   `N conditions` as a claim about `provenance_check.CONDITIONS`. A prose
   sentence saying the wrong count on a provenance line would pass unread.
2. **F8-R2** — `provenance/url_liveness.json` freshness was not gated at all.
   A weeks-old record still passed P11 with no age reported.

A11 closes both. It does **not** close A10-R1 (the $10^{120}$ vacuum gap),
A10-R2 (Gate 2 quantum censorship is not implemented), A10-R3 (RH / NS /
Langlands remain open in the literature), F8-R3 (sub-repo encoding is pinned
not fixed by design), or F8-R4 (A8 deferred). Those stay open in every
report that already names them.

---

## 1. F8-R1 — P9 CONDITIONS_CLAIM

**Rule.** In `report_claim_check.py`:

- Live value: `len(provenance_check.CONDITIONS)` (currently **11**).
- In-scope line: a root `.md` line matching
  `provenance_check` (word-boundary safe, so `theorem_provenance_check` does
  not count), `evidence snapshots`, `reference facts`, `P11 LIVENESS`,
  `len(CONDITIONS)`, or `external provenance for every constant`.
- Claim: `\b(N-digit|cardinal-word)\s+conditions\b` on that line.
- Verdict: equal to the live value, or a date / phase tag / "then" within one
  line (same escape hatch P5 already uses). Otherwise FAIL.

`theorem_provenance_check` has its own condition count and its own "nine
conditions" sentences; those are out of scope on purpose.

**Proof.** `harnesses/a11_residual_inj.py` group 1:

| case | mutation (as of A11, 2026-10-07) | expected |
|---|---|---|
| C1 | unanchored stale count on a provenance line (`nine conditions`) | P9 FAIL |
| C2 | live count on a provenance line (`11 conditions`) | control, PASS |
| C3 | historical count with date (`ten conditions as of F5 (2026-10-05)`) | history, PASS |
| C4 | out-of-scope line (`znone_check has nineteen conditions`) | PASS, not compared |

---

## 2. F8-R2 — P11 liveness age

**Rule.** In `provenance_check.py` P11:

- Parse `generated_utc` as UTC.
- Compute `age_days = now - generated_utc`.
- Print `age: N.NN days` on the P11 summary line.
- FAIL if the stamp is malformed or if `age_days < 0` (future-dated — an
  impossible stamp is a defect, not staleness).
- **No hard age limit.** The suite is the offline contract; a gate that fails
  by the clock would break that contract on a machine that has not re-run the
  probe. Operational practice is to re-run `url_liveness_check.py` when a
  source may have moved. This policy decision is recorded here so the next
  phase does not have to rediscover it.

**Proof.** `harnesses/a11_residual_inj.py` group 2:

| case | mutation (as of A11, 2026-10-07) | expected |
|---|---|---|
| A1 | `generated_utc` set to `2099-01-01T00:00:00Z` | P11 FAIL `future` |
| A2 | `generated_utc` set to `not-a-timestamp` | P11 FAIL `malformed` |
| A3 | baseline record untouched | control, PASS, `age:` printed |

---

## 3. Prose defects the new rules exposed

Implementing P9 immediately found stale current-state prose:

| site | defect | fix |
|---|---|---|
| `Brain.MD` provenance_check row | "Ten conditions P1..P10" as if current | "Eleven conditions P1..P11 (ten at F3; P11 added by A9)" |
| `F3_REPORT.md` §4 baseline | "8 conditions" unanchored | anchor "as of F3, 2026-10-05" |
| `F3_REPORT.md` §9 gate of record | "10 conditions" as current | updated to 11 with P11 noted and 10 kept as dated history |
| `F8_REPORT.md` §8 residual rows | F8-R1/F8-R2 still listed as open | marked CLOSED 2026-10-07 (A11) with pointers |

Historical counts that already carry a date (`as of F5`, `as of 2026-10-06`,
phase tags) are left alone — that is the escape hatch working as designed.

---

## 4. Constitution updates

| File | Change |
|---|---|
| `report_claim_check.py` | P9 CONDITIONS_CLAIM; `live_values()["conditions"]` |
| `provenance_check.py` | P11 measures and prints age; future/malformed FAIL; policy comment |
| `harnesses/a11_residual_inj.py` | new harness, `7/7` |
| `harness_check.py` | harness `a11_residual_inj.py` registered (23 → 24) |
| `Skill.md` | 23 → 24 proof harnesses |
| `Brain.MD` | v1.17; row for `A11_REPORT.md`; harness list + counts; P9 documented on `report_claim_check.py` row |
| `README.md` | offline contract A11; roadmap A11; open items F8-R1/R2 removed |
| `F8_REPORT.md` | residuals F8-R1/F8-R2 closed; verification matrix noted |
| `TAHU_A10_REPORT.md` | A10-R5 partially closed |
| `CHECKSUM.sha256` | regenerated (91 files: 57 root + 10 provenance + 24 harnesses) |

---

## 5. Verification

| check | command | result |
|---|---|---|
| conditions claim | `python report_claim_check.py` | `ok  P9 conditions claims -- 7 current-value, 9 dated history (len(CONDITIONS)=11)`; **PASS** |
| liveness age | `python provenance_check.py` | `ok   P11  LIVENESS_RECORD delta: 0 (urls: 25, ok: 23, diverged: 2, age: 0.29 days)`; `GATE: PASS -- 11 quantities, 9 evidence snapshots, 5 reference facts, 11 conditions`; exit 0 |
| harness (A11) | `python harnesses/a11_residual_inj.py` | `HARNESS: PASS -- 7/7 cases behaved as expected, targets byte-identical, both gates green at the end` |
| harness runner | `python harness_check.py` | `passed=24 failed=0 not_run=0 of 24`, workspace byte-identical |
| suite | `python suite_check.py --with-harness` | `passed=16 failed=0 not_run=0 of 16`; `SUITE: PASS -- every listed gate returned 0` |
| manifest | `python checksum_check.py` | `ok   CHECKSUM matched 91/91 listed, 91 on disk` |
| AC Gate | `gate.py` self-test / lean / claim / audit | self-test **13/13**; lean **PASS**; claim **PASS**; audit **PASS** `GENUINE=2` (`protocol_09.smt2` core=[11,12,13,15]; `track_c_side_conditions.smt2` core=[0]) |

Live rig after A11 (2026-10-07): suite=15, harnesses=24, manifest=91, brain=v1.17, `len(CONDITIONS)`=11.

> **Amendment, 2026-10-07 (A12).** The AC Gate claim on `protocol_09.smt2`
> above is historical; A12 renamed it to `bounded_loop.smt2` (same core
> `[11,12,13,15]`, same auditor verdict). Manifest is now 93 files;
> `Brain.MD` is v1.18; F8-R4 closed.

---

## 6. Anti-Circularity Gate

Run after the last corpus edit, before commit. This phase introduces no new
`.lean` or `.smt2` claim; the gate was run for completeness and to confirm no
placeholder or comment-only claim entered the corpus.

- self-test: 13/13 (negatives still fail)
- `gate.py lean` on `OMEGATrackC.lean`: PASS (`FAIL=0 NOT_RUN=0 SKIP=0`)
- `gate.py claim` on `protocol_09.smt2` + `track_c_side_conditions.smt2`: PASS
- `gate.py audit`: PASS — auditor returns `GENUINE` for both scripts

A PASS here means the checks ran and found nothing on the artefacts on disk.
It is not a mathematical result about RH, Navier–Stokes, or Langlands.

---

## 7. What remains open

| ID | Open item |
|---|---|
| A10-R1 | The $10^{120}$ vacuum gap is **not solved** |
| A10-R2 | Gate 2 (quantum censorship) remains **not implemented** |
| A10-R3 | RH, Navier–Stokes regularity and Langlands remain open in the literature regardless of any gate result here |
| F8-R3 | Sub-repo encoding remains pinned-not-fixed (by design of A9) |
| F8-R4 | A8 (`Tugas tambahan.md`) remains deferred |

Nothing in this phase claims that the cosmological constant problem, RH, or
Navier–Stokes has been solved.
