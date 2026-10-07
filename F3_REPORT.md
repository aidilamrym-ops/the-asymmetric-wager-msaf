# F3 REPORT — External Provenance Layer

**Workspace:** `D:\THE ASYMMETRIC WAGER`
**Date:** 2026-10-05
**Predecessor:** `F2_REPORT.md`
**Status:** F3-1 complete; R1 and R2 closed 2026-10-05 by the vacuity fix; other residuals in §8
**Language:** English (project artefact). $P_{\text{narrative}} = 0$.

---

## 0. What F3 is, and why it exists

`F2_REPORT.md` §0 records that no file in this workspace defines phases F0–F4.
F3 is therefore derived the same way F2 was: from a gap that survived every
earlier phase and that is *not* covered by any existing gate.

The gap is provenance. Every constant this corpus uses from outside itself —
$\ell_P$, $D_{\text{obs}}$, $|\zeta'(\rho_1)|$ — appeared inside the documents
with **no bibliography anywhere in the root tree**. There are 21 root-level
markdown files and zero reference lists. `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md`
is written for an examining board and cites nothing outside the corpus.
`gw_check_refs.py` checks references *inside the engine source*, not to the
world outside it.

The numbers were right. The provenance was absent. That is the celah F3 enters:
not by changing a claim, but by making every borrowed number answer for its
authority, edition, uncertainty, retrieval date and a hashable snapshot.

**Non-goals.** F3 does not touch the corpus's thesis. It does not edit any
file inside `guinand-weil-rigorous-numerics-main`, so `CHECKSUM.sha256` is
unaffected. It does not duplicate `msaf_zeta_check.py`, `landauer_check.py` or
`gw_verify_production.py`; those remain the gates of record for their subjects.

---

## 1. Scope and method

1. Survey the root corpus for every externally sourced quantity and record the
   exact line and literal text where each is asserted.
2. Retrieve an authoritative snapshot and hash it, so verification can be
   repeated offline.
3. Record the external state of the field where the corpus implicitly
   contradicts a published result by never citing it.
4. Gate all of the above with a new script that reads the claims **out of the
   documents**, re-derives the derived quantities independently, and fails on
   any missing link.
5. Prove the gate by fault injection with isolated restore.

---

## 2. Findings

### F3-A — No bibliography in the root corpus
21 root `.md` files, zero reference lists. Closed by `REFERENCES.md` (§3).

### F3-B — $D_{\text{obs}}$ had no source, no edition, no uncertainty
$D_{\text{obs}} = 8.8\times10^{26}$ m is the **numerator of
$\Delta_{\text{univ}}$** and it carried no provenance at all. It is a
$\Lambda$CDM comoving diameter, i.e. model dependent and not a directly
measured length; the corpus already declares that only 2 significant figures
are justified. Now recorded with the underlying cosmology
(Planck 2018 VI, DOI `10.1051/0004-6361/201833910`) and with the honest
statement that **no evidence snapshot for it is archived** — a declared gap,
not a hidden one.

### F3-C — Documented variance in $\ell_P$ (found, recorded, closed by F5-1)
| site | as written |
|---|---|
| `Skill.md` canon row | `1{,}616255 \times 10^{-35}` — agrees with CODATA 2022 at 7 s.f. |
| `01_PARADOX_AND_SCALE.md` L25 and L29 | `1.63 \times 10^{-35}` |

The correct 3-significant-figure rounding of the CODATA 2022 value
`1.616255e-35` is **`1.62e-35`**, not `1.63e-35`. Relative deviation:
`8.504e-3` (+0.8504 %).

This does **not** change the downstream result: both `1.62e-35` and `1.63e-35`
reproduce $N_{\text{steps}} \approx 5{,}4\times10^{61}$ at the two significant
figures the corpus declares for $N_{\text{steps}}$. Per the retraction rule
(no silent edits) the variance is **declared** in `REFERENCES.md` and enforced
by the gate: if either side is edited without the other, the gate fails.
Remediation was deferred to a phase permitted to edit `01_PARADOX_AND_SCALE.md`; **F5-1 closed it on 2026-10-05** by correcting both sites to `1.62 \times 10^{-35}` and switching the register from `declared_variance` to `source_agree`. The pre-fix state now fails the gate (stage-B probe B4: `P4 SITE_VALUE ... disagrees with the authoritative value 1.616255e-35 at 3 s.f.`).

### F3-D — $\ell_P$ appears at two different precisions
7 s.f. in `Skill.md` / `DRAF_AKADEMIS`, 3 s.f. in `01_PARADOX_AND_SCALE.md`.
Not contradictory, but previously undeclared. Now declared.

### F3-E — The external state of the Riemann Hypothesis was never recorded
The corpus repositions RH as a Scale Axiom but never records what public
computation has established. A reader could take the corpus as contradicting
results it simply never cited. Now recorded in `REFERENCES.md` §3:
verification to height `3000175332800` covering `12363153437138` zeros
(Platt–Trudgian, arXiv `2004.09765`), and the zero-free region constants
`5.573412` (2015) and `5.559` (2024).

### F3-F — No edition or uncertainty on any constant
`1.616255e-35` was quoted without saying CODATA 2018 or 2022, without the
uncertainty `0.000 018 e-35`, and without a retrieval date. Both editions carry
the same central value; that identity is now a recorded fact rather than an
assumption.

---

## 3. Artefacts

| file | bytes | sha256 |
|---|---:|---|
| `REFERENCES.md` | 8760 | `64b2f259eef176a8159d0e8fc1420861679a3dd2e93f3b7416c7625394e22514` |
| `external_constants.json` | 8014 | `92022e274523405d4bd1be76bc6b76f62d3d0b10b8d18cf9f199e61fa3b65083` |
| `provenance_check.py` | 20691 | `38595799a38a8aba41752407e4b2ed96b64514e36d92bf17b62379d5a0a953e6` |
| `provenance/evidence/nist_allascii_2022.txt` | 40801 | `77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67` |
| `Brain.MD` (registration row + run instruction) | 21222 | `3bb62a6d2ec96c13395625bd74fbaf844288d26e30d9d4f5c783dd302031a965` |

All five are **new or root-level**; none is inside the sub-repository, so
`CHECKSUM.sha256` (113 rows as the manifest stood at F3 on 2026-10-05) is
untouched.

Evidence snapshot provenance: `https://physics.nist.gov/cuu/Constants/Table/allascii.txt`,
40801 bytes, retrieved 2026-10-05, SHA-256 `77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67`.
Its declared values were confirmed to match the corpus: `Planck length
1.616 255 e-35 0.000 018 e-35 m`, `Boltzmann constant 1.380 649 e-23 (exact)
J K^-1`, `speed of light 299 792 458 (exact) m s^-1`.

---

## 4. Gate design — `provenance_check.py`

Exit code **0 = PASS, 1 = FAIL, 2 = TOOL NOT RUN**. Line prefixes `ok  ` /
`FAIL  ` / `SKIP  `, summary `GATE: ...`.

| # | condition | what it proves |
|---|---|---|
| P1 | SCHEMA | every quantity carries authority, retrieval date, uncertainty, at least one site; `kind=derived` declares `derived_from` or `recompute`; `exact=true` forces `uncertainty='exact'`; every `source_id` resolves |
| P2 | EVIDENCE_HASH | the archived snapshot's byte count and SHA-256 match the declaration |
| P3 | SITE_FOUND | the literal needle occurs in the document exactly the declared number of times, and encodes the declared mantissa and exponent |
| P4 | SITE_VALUE | the needle decodes to `doc_value`; `source_agree` sites agree with the authoritative value; `declared_variance` sites reproduce their own `rel_dev` and `correct_rounding` |
| P5 | DERIVED | $\Delta_{\text{univ}}=\ell_P/D_{\text{obs}}$ and $|\zeta'(\rho_1)|$ recomputed independently at 100 dps |
| P6 | PROVENANCE | authority + retrieval date present; `evidence_id` resolves or a declared `evidence_status` substitutes; the probe finds the claimed value **on the `Planck length` line** of the archived table |
| P7 | REFERENCES_COVERAGE | `REFERENCES.md` carries a `### <ID>` heading for all 15 identifiers (4 quantities + 6 evidence + 5 reference facts) |
| P8 | REFERENCE_FACT_VALUE | every reference-fact value actually appears in `REFERENCES.md` |

**Tolerance rule.** `agrees()` uses $0.5\times10^{-\text{s.f.}}$ relative —
derived from the declared significant-figure count of the value being compared,
never a hand-picked constant. This matters: see F3-G.

**Two bounds on that declared count, added 2026-10-05 (F3-K).** The count is
not free input. `P1` requires it to be an integer in `1..40` (`SF_CAP` = 40
because `P5` feeds `agrees()` `mp.nstr(x, 40)`, so a larger declaration demands
digits this gate never computes), and requires it to equal
`sig_digits(value)` — the precision actually written in the declared value.
Without the second condition `sig_figs` on a *measured* quantity was
decoration: `P4` compares at `sig_digits(doc_value)` and never reads it, so the
field could be silently lowered while the gate stayed green.

**P8 is a token match, not a substring test** (`token_present`): the value must
occur as a complete number, so `5.559` is no longer satisfied by `5.559123`.
The exact spelling is tried first and keeps its fail-closed behaviour. Since
**F5-4** an exact `Decimal` equality fallback runs only when that misses, so an
equal value written with different trailing zeros after a decimal point
(`5.5590` for `5.559`) is recognised as the same number instead of being
reported as missing. Nothing is padded or truncated to force a match:
`1038007883590` is ten times `103800788359`, so integer padding still fails, and
a false FAIL remains visible where a false PASS would not. Proved by
`f5_4_inj.py`: 14/14 cases (3 acceptance, 9 regression, 2 control).

**Normalisation.** `1{,}616255` and `1,836653` are both mapped to decimal
before comparison, so the corpus's LaTeX and prose conventions are handled
without special cases.

**Baseline output (as of F3, 2026-10-05):**
```
GATE: PASS -- 4 quantities, 6 evidence snapshots, 5 reference facts, 8 conditions
exit=0
```

---

## 5. Proof — fault injection

Harness: `harnesses\f3_inj.py`, run 2026-10-05. Discipline: snapshot bytes
→ mutate one thing → run → restore → **assert bytes identical**. Every case is
independent; the harness is idempotent.

**27/27 mutants caught**, each tripping its intended condition with no traceback:

| case | mutation | tripped |
|---|---|---|
| M1 | authoritative $\ell_P$ value altered | P4 |
| M2 | site `doc_value` detached from the needle | P4 |
| M3 | declared needle count wrong | P3 |
| M4 | site points at a nonexistent document | P3 |
| M5 | evidence SHA-256 corrupted | P2 |
| M6 | `authority` removed | P1 |
| M7 | `uncertainty` removed | P1 |
| M8 | every site of a quantity removed | P1 |
| M9 | derived value altered | P5 |
| M10 | `derived_from` stripped | P1 |
| M11 | declared `rel_dev` altered | P4 |
| M12 | reference-fact value altered | P8 |
| M13 | evidence probe needle altered | P6 |
| M14 | `evidence_id` nulled without declaring a status | P6 |
| M15 | evidence byte count altered | P2 |
| M16 | evidence local copy missing | P2 |
| M17 | `exact=true` with a non-`exact` uncertainty | P1 |
| M18 | authoritative $|\zeta'(\rho_1)|$ altered | P5 |
| M19 | needle not present in the document | P3 |
| M20 | retrieval date removed | P6 |
| M21 | `local_copy` key dropped | P1 |
| M22 | unknown evidence cited | P1 |
| M23 | measured quantity reflagged `derived` | P1 |
| M24 | evidence `sha256` key dropped | P1 |
| M25 | `### PLANCK_2018_VI` heading removed | P7 |
| M26 | reference value removed from `REFERENCES.md` | P8 |
| M27 | reference-fact heading removed | P7 |

**3/3 controls passed:** C0 pristine (exit 0), C1 harmless metadata edit
(`generated_utc`, exit 0), C2 a legitimately appended reference fact with its
own heading and value (exit 0 — proves the schema accepts real extension).

**M28 — missing document:** `01_PARADOX_AND_SCALE.md` renamed away, gate
reported `FAILURES` and exited 1 with **no traceback**, then restored to
byte-identical. This is the F1 hardening rule satisfied.

**Final integrity:** byte-identical after restore for every touched file; final
gate run exit 0.

### 5.1 The vacuity probe — a second harness, run after §7's residuals were written

M1–M27 are **alteration and removal** mutants: they change a fact and ask
whether the gate notices. None of them asks whether the gate's *tolerance* can
be switched off. Residuals R1 and R2 in §8 said it could. The probe
`harnesses\f3_vacuity.py` (plus `f3_a1.py`) tested that directly by editing
`external_constants.json` and `REFERENCES.md` in place under a
snapshot/mutate/run/restore/verify discipline, one probe at a time.

**Before the fix: 11 probes, 7 FALSE-PASS.**

| probe | edit | result before | after |
|---|---|---|---|
| H1a | `sig_figs = 0` | caught (by accident: `bool(0)` is false, reported as "missing") | caught, correctly reported as out of range |
| H1b | `sig_figs = -1` | **FALSE-PASS** — tolerance 5000 % | caught |
| H1c | `sig_figs = 1` | **FALSE-PASS** — `sig_figs` unused for measured quantities | caught by the `sig_digits(value)` equality |
| H1d | `sig_figs = 'abc'` | **FALSE-PASS** | caught, type error reported |
| H1e | `sig_figs = None` | caught | caught |
| H1f | `sig_figs = 999999` | **FALSE-PASS** | caught |
| H1g/H1h | wrong value at sf 1 / 0 | caught (by the mantissa and P5 cross-checks) | caught |
| H2a | `5.559` → `5.559123` in `REFERENCES.md` | **FALSE-PASS** | caught by the token match |
| H2b | `3000175332800` → `930001753328009` | **FALSE-PASS** | caught |
| H2c | `103800788359` → `1038007883590` | **FALSE-PASS** | caught |
| A1a | derived quantity `sig_figs = -1` | **FALSE-PASS** — `P5` compared at 5000 % | caught |
| A1b/A1e | derived `sig_figs = 'abc'` | caught, but only by the top-level handler (`ValueError` on `int()`), aborting the rest of the report | caught in `P1`, report completes |
| A1c | derived `sig_figs = 1` | **FALSE-PASS** — `P5` at 50 % tolerance | caught |
| A1d | derived `sig_figs = None` | caught (raised `TypeError` into the top-level handler) | caught in `P1` |

**After the fix: 16/16 caught, 0 FALSE-PASS, 0 CRASH**, both probes'
baselines exit 0 and every touched file is byte-identical after restore.

Note what the probe did **not** find: a wrong value made to pass by loosening
`sig_figs` alone. `H1g` was already caught, because `P3` pins the needle's
mantissa and `P5` re-derives the quotient independently. The holes were
therefore not in the arithmetic but in the *metadata that governs how loosely
the arithmetic is judged* — exactly the class of defect a fault-injection count
of "27/27" does not cover, since none of those 27 mutants edits a tolerance.

---

## 6. Defects found while building, and how they were caught

### F3-G — Tolerance was 10× too loose (caught by the gate itself)
`agrees()` was first written as `5 × 10^(1-sf)` instead of `0.5 × 10^(1-sf)`.
The very first run failed on:

```
FAIL  P4  SITE_VALUE: PLANCK_LENGTH#1 is declared a variance but doc_value
          equals the correct rounding
```

Under the loose tolerance `1.63e-35` and `1.62e-35` "agreed" at 3 significant
figures, so the invariant *a declared variance must not equal the correct
rounding* mis-fired. The declared-variance condition therefore served as a
self-test on the tolerance. Fixed to `5 × 10^(-sf)`; all subsequent runs used
the corrected rule.

### F3-H — Harness keyed on a label that did not match
`REF_MUTATIONS` was keyed by the full case label; a spacing mismatch produced
`KeyError` on M25. The harness's `finally` restore ran and the baseline was
re-verified before continuing, so no file was left mutated. Fixed by keying on
the 3-character case id.

### F3-I — Bogus `evidence_id` (caught before the first gate run)
The first draft pointed `OBSERVABLE_UNIVERSE_DIAMETER` at
`PLATT_TRUDGIAN_2021`, an unrelated paper. Replaced with a dedicated
`PLANCK_2018_VI` evidence entry.

### F3-K — The gate could be made vacuous by editing metadata (found 2026-10-05)
The `27/27` fault-injection result in §5 proved that a *changed fact* is caught.
It did not prove that the *tolerance itself* is anchored. Residuals R1/R2 said
it was not, and the vacuity probe confirmed **7 FALSE-PASS** before the fix.
Three changes closed them: `P1` now validates `sig_figs` by type, by the
`1..40` range and against `sig_digits(value)`; `P5` refuses a count `P1` has
condemned instead of letting `int()` raise mid-report; and `P8` moved from
`val in flat` to a token-bounded match. The original `27/27` still passes
afterwards, so the fix loosened nothing that used to hold.

### F3-L — Two file-mutating harnesses run in parallel (operator defect, 2026-10-05)
`f3_vacuity.py` and `f3_a1.py` were launched in the same batch while both
snapshot, mutate and restore `external_constants.json`. One probe reported
`restored=False` at its final check. Integrity was re-verified afterwards
against the recorded baseline hash `92022e2745…` and both files were correct,
because each probe's `finally` wrote the original bytes back. The lesson is
recorded rather than glossed: **harnesses that write to a shared file must be
run sequentially**, and a restore assertion that reports `False` must be
treated as a real signal and investigated, not read past.

### F3-J — Malformed line written into the gate
A mangled `check(... ) if False else None` expression was written into P4.
Removed during the first edit pass; the gate has not been run in a state
containing it.

---

## 7. Blind-spot review (recorded, not hidden)

1. ~~**No minimum `sig_figs` is enforced.**~~ **CLOSED 2026-10-05 (F3-K).**
   `P1` now requires an integer in `1..40` equal to `sig_digits(value)`;
   proved by the vacuity probe (§5.1), 16/16 caught.
2. ~~**P8 is a substring test.**~~ **CLOSED 2026-10-05 (F3-K).** `P8` now uses
   a token-bounded match; the three substring false-passes of §5.1 are caught.
   ~~Residual: a value written with extra trailing zeros now fails.~~
   **CLOSED 2026-10-05 (F5-4)** — an exact `Decimal` equality fallback accepts
   `5.5590` for `5.559` while `f5_4_inj.py` still catches all nine unequal
   cases, including integer padding; see §8 R7.
3. **The needle format is assumed.** A document rewritten to `×10^` or `*10^`
   would stop matching — this fails closed (P3), not open, which is the
   correct direction.
4. **P7 heading match is exact.** A heading such as `### ID - note` fails P7.
   Fail-safe, but it means `REFERENCES.md` structure is load-bearing.
5. **Two quantities have no archived evidence.** `OBSERVABLE_UNIVERSE_DIAMETER`
   has a landing-page record only, and `ZETA_DERIVATIVE_FIRST_ZERO` is
   recomputed on this machine. Both are declared via `evidence_id` /
   `evidence_status` rather than papered over.
6. **The $|\zeta'(\rho_1)|$ recompute is independent of the corpus but not of
   this machine's `mpmath`.** Recorded; `msaf_zeta_check.py` remains the gate
   of record for the surrounding Section 2 claims.
7. **No witness that the snapshot is *current*.** The gate proves the file is
   the one retrieved on 2026-10-05; it does not check whether CODATA has since
   published a newer adjustment. That requires a network call and is out of
   scope for an offline gate.

---

## 8. Residual

| # | item | state |
|---|---|---|
| R1 | Enforce a minimum `sig_figs` in P1 | **CLOSED 2026-10-05 (F3-K)** — integer, `1..40`, and equal to `sig_digits(value)`; vacuity probe 16/16 |
| R2 | Strengthen P8 from substring to token match | **CLOSED 2026-10-05 (F3-K)** — token-bounded; H2a/H2b/H2c now caught |
| R3 | Archive a cosmological-parameter evidence snapshot for $D_{\text{obs}}$ | **CLOSED 2026-10-05 (F5-2)** — the canonical DOI returns HTTP 403 from this machine and is now recorded honestly as layer **C**; the arXiv preprint of the same article (`arXiv:1807.06209`) is archived as `PLANCK_2018_VI_ARXIV`, 78846 bytes, sha256 `a8f46f86…e7c4d`, hash-verified by P2 and pointed at by `OBSERVABLE_UNIVERSE_DIAMETER.snapshot_evidence_id` |
| R4 | Decide the F3-C remediation (change `1.63` to `1.62` in `01_PARADOX_AND_SCALE.md`) | **CLOSED 2026-10-05 (F5-1)** — both sites corrected, register `declared_variance` -> `source_agree`, and reverting either side fails P3/P4 (probes B1--B4) |
| R5 | Add $k_B$ to the register | **CLOSED 2026-10-05 (A3)** — `BOLTZMANN_CONSTANT` added to `external_constants.json` (measured, `exact: true`, `uncertainty: "exact"`, `sig_figs: 7`), site `SOLVABLE_FINITE_PARADOX.md` L83 carrying the `REF-NIST_CODATA_2022_TABLE` marker, `evidence_probe` reading NIST L62 where the value `1.380 649 e-23` and the `(exact)` marker sit on the same line, and `### BOLTZMANN_CONSTANT` in `REFERENCES.md`. `landauer_check.py` remains the gate of record for the Landauer arithmetic that *uses* $k_B$; the register answers where it is quoted instead |
| R6 | Phase B: insert `[REF]` markers into the corpus documents | **CLOSED 2026-10-05 (F5-3)** — 11 markers over 8 lines in the 3 documents the register points at (`Skill.md`, `01_PARADOX_AND_SCALE.md`, `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md`), each inside an HTML comment so the rendered document is unchanged; bound by `P10 REF_MARKERS` in three directions (RESOLVES / REQUIRED / PLACED) plus a stray-marker sweep over every root `.md`. `f5_3_inj.py` 7/7 |
| R7 | P8 now fails an equal value written with extra trailing zeros (`5.5590` for `5.559`) | **CLOSED 2026-10-05 (F5-4)** — exact `Decimal` equality fallback after the exact-spelling test; `f5_4_inj.py` 14/14 (3 acceptance pass, 9 unequal values still fail P8, 2 controls), `f3_vacuity` 11/11 and `f3_inj` 27/27 unchanged |
| R8 | `sig_figs` for a *measured* quantity still has no independent authority check: it must equal the digits in `value`, but nothing checks `value` itself against the evidence snapshot at that precision | **CLOSED 2026-10-05 (B1-a)** — `evidence_probe` was opt-in, so a measured quantity could omit it and never have `value` read against the snapshot; P6 now makes the tie mandatory for every non-derived quantity (probe must exist and pass when the cited evidence is archived, a non-empty `probe_waived` reason when it is not, silence is a FAIL). `harnesses\f3_inj.py` M29/M30 both trip P6; 29/29 mutants, 3/3 controls |

Rows in §8 marked **CLOSED** carry their own proof; nothing marked *open* or *deferred* is asserted as solved.

---

## 9. Verification matrix

| check | command | result |
|---|---|---|
| gate of record | `python provenance_check.py` | exit **0**, `GATE: PASS -- 5 quantities, 8 evidence snapshots, 5 reference facts, 11 conditions` (the 9th is `P9 LAYER_CONSISTENCY` from F5-2, the 10th is `P10 REF_MARKERS` from F5-3, the 11th is `P11 LIVENESS_RECORD` from A9; 4 quantities and 7 snapshots at F5-2, 5 quantities since A3, 8 snapshots since A7; **10 conditions as of F5/F7**, 11 since A9) |
| layered-archive injection (F5-2) | `harnesses\f5_2_inj.py` | exit **0**, `HARNESS: PASS -- 20/20 cases behaved as expected, registers byte-identical, both gates green at the end`: deleted and one-byte-corrupted snapshots, illegal layer labels, a layer B/C record claiming content, a missing licence basis, unresolvable and layer-C snapshot pointers, a dropped and an uncited archive record — each caught by the gate it targets, with the other gate staying green |
| marker injection (F5-3) | `harnesses\f5_3_inj.py` | exit **0**, `HARNESS: PASS -- 7/7 cases behaved as expected, documents byte-identical, both gates green at the end`: a phantom marker, the right id on the wrong line, every marker stripped, a marker moved off its needle line, a marker pasted into a document no site points at — each reported by `P10 REF_MARKERS` itself, never by another condition. Before the markers were inserted the same gate read `FAIL -- 11 condition(s) not met`, which is the "missing marker" direction pre-validated |
| markers, by hand | byte inspection | `markers seen: 11, stray: 0`, 8 marked lines, 3 documents, `CR = 0`, no BOM; re-running the inserter on an already marked file changes **0 bytes** |
| vacuity probe (F3-K) | `harnesses\f3_vacuity.py`, `f3_a1.py` | **before fix: 7 FALSE-PASS**; **after fix: 16/16 caught, 0 FALSE-PASS, 0 CRASH**, baselines exit 0, byte-identical restore |
| fault injection | `python harnesses\f3_inj.py` | exit **0**, `HARNESS: PASS -- 27/27 mutants caught, 3/3 controls passed, missing-document hardened, all files byte-identical` (re-run after the F3-K fix: unchanged) |
| encoding, all new files | byte inspection | no BOM, `CR = 0`, UTF-8 strict |
| regression suite, root gates | `landauer_check`, `znone_check`, `zeta_pixel_producer`, `msaf_zeta_check`, `bridge_mirror_check`, `visual_check`, `msaf_visual`, `provenance_check` | all exit **0** |
| regression suite, sub-repo gates | `gw_check_refs`, `gw_verify_results`, `gw_verify_production` | exit 0, 0, 0 |
| `CHECKSUM.sha256` | row count | 113 tracked rows, `TOTAL FILES : 113`, mtime unchanged |
| Anti-Circularity Gate | self-test, `gate lean`, `gate claim`, `gate check` | self-test **13/13**; all three gates **PASS** (`FAIL=0 NOT_RUN=0 SKIP=0`); auditor `GENUINE`, `core=[0]`. F3 introduces no `.lean` or `.smt2` claim, so the gate is run for completeness and to confirm no placeholder or comment-only claim entered the corpus. |

---

## 10. What F3 bought

1. The corpus is **citable**: `REFERENCES.md` exists, every borrowed number has
   an authority, an edition, a retrieval date and a hashable snapshot.
2. The one number that had no source at all, $D_{\text{obs}}$, now has one —
   and its model-dependence is stated rather than implied. F5-2 went further:
   the canonical DOI is unreachable from this machine (HTTP 403) and is
   labelled layer **C** instead of being implied to be archived, while the
   arXiv preprint of the same article is stored, hashed and pointed at, which
   closes R3.
3. The one place where the corpus's own figure is not a correct rounding is
   **declared and machine-enforced**, not quietly fixed and not left for an
   examiner to discover.
4. Every external claim is now gated. Before F3 the gates covered internal
   mathematics only; this is the first gate over the boundary between the
   corpus and the outside world.
5. The gate's own tolerance is now anchored rather than merely asserted. The
   first `27/27` result proved facts are checked; the vacuity probe proved the
   *strictness* cannot be edited away, which is a different claim and needed a
   different harness. Both are recorded in §5 and §5.1.
