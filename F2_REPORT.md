# F2 REPORT — Backlog-Closure Phase

Date: 2026-10-04 → 2026-10-05; §8.3 closed 2026-10-06
Workspace: `D:\THE ASYMMETRIC WAGER`
Status: F2-1 … F2-7 complete — all seven stages built, blind-spot-audited and re-proven; every published injection count now has a harness behind it (§8.3.1)
Gates of record: `landauer_check.py`, `znone_check.py`, `msaf_zeta_check.py`, `zeta_pixel_producer.py`, `bridge_mirror_check.py`, `visual_check.py`, `gw_verify_production.py` (F2-7, complete — exit 0 against the shipped N = 400 artefact)
Harnesses of record: `harnesses/f2_1_inj.py`, `f2_2_inj.py`, `f2_3_inj.py`, `f2_4_inj.py`, `f2_6_inj.py`, `f2_7_inj.py` (F2 has no harness of its own for F2-5 — that stage changed one line of a registration file and was proven by re-running the F2-4 suite, §5.6)

---

## 0. What F2 is, and why it is not numbered from a plan file

No file in this workspace defines phases F0–F4. F2 is therefore **derived from
the residual sections that the finished phases explicitly handed over**:

| # | Source | Item |
|---|---|---|
| F2-1 | F1 §5.5 | `SOLVABLE_FINITE_PARADOX.md` Landauer / `k_B` / `Delta E` sentence removed in F0, never re-derived |
| F2-2 | F1 §5.3 | `Z_none` labelling — one canonical definition, DRAF table re-labelled |
| F2-3 | F1 §5.1 | F1-H producer script for `Re`, `Im`, `|Delta zeta|` |
| F2-4 | F0 §9.6 | Two byte-identical copies of `shp_mcp_bridge_v4.py` need a single guard |
| F2-5 | F0 §9.5 | Root `shp_bridge` — operator decision |
| F2-6 | F1 §5.4 | Plot semantics of the `p` axis |
| F2-7 | F1 §5.2 | F1-D — regenerate an `N = 400` run so `lambda_min` is machine-gated |
| — | F1 §5.2 (F1-D, second half) | The `GW_STATUS` "stayed in HEAD" claim: requires a `.git`, which this tree does not have. Not closable in F2, and creating a repository inside an operator's tree is an operator decision |

Each stage is worked, then blind-spot-audited, then **re-proven after the fix**.
This report grows one section per stage.

---

## 1. F2-1 — the Landauer floor, re-derived instead of re-asserted

### 1.1 The defect

F0 deleted the thermodynamic sentence from `SOLVABLE_FINITE_PARADOX.md` §3
because it claimed an executed result that did not exist. The deletion was
correct, but it left §3's *Thermodynamic Cost* row **honest and empty**: the
argument was gone and nothing replaced it. `F1_REPORT.md` §5.5 recorded this as
residual and did not close it.

### 1.2 What §3 now states

The derivation uses only two exact inputs — the SI-2019 exact
`k_B = 1.380649 x 10^-23 J/K` and `ln 2` — and two temperatures that the
document itself declares as **inputs, not measurements**:

| quantity | value |
|---|---|
| `k_B ln 2` | `9,5699296 x 10^-24 J/K` |
| floor at `T = 2,725 K` | `2,6078058 x 10^-23 J` |
| floor at `T = 300 K` | `2,8709789 x 10^-21 J` |
| floor at `T = 300 K`, expressed per kelvin | `2,8709789 x 10^-21 / 300 = k_B ln 2` |

Explicitly stated and gated:

- Landauer is a floor **per erased bit**, not a total.
- **No energy total is claimed**, because no erasure count exists for either
  side of the argument.
- The premise "each evaluation performs at least one irreversible erasure" is
  an **assumption about the algorithm, not a measurement**.
- §1.B now links to §3 instead of leaving the argument dangling.

### 1.3 Blind-spot review of F2-1 — what else was wrong

The defect was not confined to one file. The same claim appears in two other
shipped documents, and both were defective in their own way:

| site | defect found | fix |
|---|---|---|
| `ANTI_INFINITY_BLINDSPOT.md` §2.B | "to process every bit … a minimum energy dissipation is required" — Landauer charges **irreversible erasure**, not processing; the unbounded-total conclusion was stated with **no premise** | rewritten to charge erasure, to state `n · k_B T ln 2` diverges *provided* each evaluation erases at least one bit, and to label that premise an assumption |
| `MSAF_COSMOLOGY_DECONSTRUCTION (2).md` §1.B | the purge "**absolutely** emits a minimal heat dissipation" — the bound is conditional on irreversibility; no number, no total disclaimer | *absolutely* withdrawn on the record, floor evaluated at the document's own `T = 2,725 K`, floor-per-bit stated, no total claimed |

Sections §2 and §4 of `SOLVABLE_FINITE_PARADOX.md` were checked and carry **no**
thermodynamic claim — the F1 wording "§1.B/§2/§3/§4" was broader than the
defect actually was. That is recorded in `F1_REPORT.md` §5.5 rather than edited
away.

### 1.4 Second blind spot — `Brain.MD` mislabels a document for deletion

While auditing F2-1, `Brain.MD` line 31 was read back and said:

> Shorter duplicate (~3.8 KB vs 5.2 KB) — prefer the suffixless version.

That is **false** and dangerous. Measured:

| | `MSAF_COSMOLOGY_DECONSTRUCTION.md` | `MSAF_COSMOLOGY_DECONSTRUCTION (2).md` |
|---|---|---|
| first heading | `# FILE: MSAF_COSMOLOGY_DECONSTRUCTION.md` | `# SUPPLEMENT: CMB_INFORMATION_ANALYSIS.md` |
| sections | Big Bang, Dark Matter (11 headings) | CMB, anisotropy (8 headings) |
| shared headings | **0** | **0** |
| Jaccard over ≥5-letter words | **0.178** | |

The `(2)` suffix is a download artefact. No `CMB_INFORMATION_ANALYSIS.md` exists
anywhere else, so `(2).md` is the **only** copy of that supplement. Following
Brain.MD's instruction would have deleted a distinct document. `Brain.MD` is now
corrected and warns against exactly that.

### 1.5 The gate

`landauer_check.py` reads the claims **out of the documents** — a claim that is
deleted, reworded or edited also fails — recomputes at 100 dps with mpmath from
the exact SI `k_B`, and compares at the document's own significant figures.

| check | what it does |
|---|---|
| L1 | `k_B ln 2` declared vs recomputed |
| L2 / L3 | each `dE` table row recomputed at its own stated `T` |
| L4 | each row's `dE / T` equals the declared `k_B ln 2` |
| L5 | every required sentence present (inequality, no-total, step ceiling, premise label, inputs label) |
| L6 | no energy total asserted anywhere in the document |
| X — `ANTI_INFINITY_BLINDSPOT.md` | premise labelled, derived constant matches, "process every bit" absent |
| X — `MSAF_COSMOLOGY_DECONSTRUCTION (2).md` | floor per bit, withdrawal present, *absolutely* absent, number matches `k_B ln2 x T` where **`T` is parsed from that document, never hard-coded here** |

Exit 0 = every claim verified; 1 = a claim is missing or wrong; 2 = tool not
run. Current run: **23 ok, 0 failures, exit 0**.

### 1.6 Proof

**Gate output**

```
ok    k_B (exact input)          1.380649e-23
ok    L1  k_B ln 2               9.569929617e-24  (rel err 1.77e-09, tol 1e-7)
ok    L2  dE at T=2{,}725 K      2.607805821e-23  (rel err 7.90e-09, tol 1e-7)
ok    L3  dE at T=300 K          2.870978885e-21  (rel err 5.20e-09, tol 1e-7)
ok    L4  dE/T at T=2{,}725      9.569929541e-24  (rel err 6.14e-09, tol 1e-7)
ok    L4  dE/T at T=300          9.569929667e-24  (rel err 6.97e-09, tol 1e-7)
ok    L5/L6 (5 claims present, no total asserted)
ok    X   (10 cross-document checks across 2 documents)
LANDAUER CHECK: every section 3 Landauer claim reproduced.   exit=0
```

**Fault injection — every mutant applied to one document at a time, restored
byte-identical before the next mutant ran.**

| set | mutants | caught |
|---|---|---|
| `SOLVABLE_FINITE_PARADOX.md` | tamper `k_B ln 2` mantissa and exponent; tamper each `dE` row; tamper `k_B`; delete the no-total sentence; delete the inputs label; assert a total; resurrect *zero thermal emission*; delete the derivation block; delete the inequality; drop a table row; reword the premise | **15 / 15** |
| cross-document | delete the premise label; resurrect *process every bit*; delete the premise paragraph; delete the disclaimer; tamper the constant; resurrect *absolutely emits*; delete *per erased bit*; delete the disclaimer; tamper the floor; assert a total; delete the added paragraph; delete the withdrawal; change `T` without recomputing | **13 / 13** |
| **total** | | **28 / 28** |

Controls — mutations that must **not** trip the gate, and the reverse:

| control | required | observed |
|---|---|---|
| delete the derivation heading only (no claim removed) | PASS | exit 0 |
| delete the §1.B cross-reference (navigation, not a claim) | PASS | exit 0 |
| change `T` to `3,000 K` **and** recompute the floor | PASS | exit 0 |
| change `T` to `1,500 K` **and** recompute the floor | PASS | exit 0 |
| change `T` **without** recomputing | FAIL | exit 1 |
| delete the temperature entirely | FAIL | exit 1 |
| **total** | | **6 / 6** |

All three documents were byte-identical to their pre-injection bytes after every
mutant, and the gate returned exit 0 at the end of each run.

Reproducible: `harnesses/f2_1_inj.py` — the same 28 mutants and the same 6
controls, plus a green baseline and a green restored baseline, re-run
2026-10-06.

### 1.7 Defects found *in the gate while building it*, and fixed

Recorded because they are the same class of error this phase exists to remove:

1. Regex anchors had extra spaces around `\(` / `\)`, so a claim could not match.
2. `replace("{,", ".")` left a stray `}` in parsed numbers.
3. Label order L2/L4/L3 was mis-sequenced and mis-reported.
4. `declared_nsig` mis-counted significant figures.
5. Dead code `RE_KB_LINE` left in place; removed.
6. Cross-document unpack expected 3 values from 2-tuples — `ValueError`.
7. The exponent group was missing from the MSAF number pattern — `ValueError`.
8. **`T` was hard-coded `2.725` for the MSAF check.** Caught by mutant "change
   `T` without recomputing": the gate reported nothing. `T` is now **parsed from
   the document under test**. This was a genuine false-pass path.

### 1.8 Encoding

Every file touched in F2-1 verified: UTF-8 strict decode OK, **no BOM, zero
CR bytes (pure LF)**.

| file | bytes |
|---|---|
| `SOLVABLE_FINITE_PARADOX.md` | 9257 |
| `landauer_check.py` | 11773 |
| `ANTI_INFINITY_BLINDSPOT.md` | 5208 |
| `MSAF_COSMOLOGY_DECONSTRUCTION (2).md` | 4412 |
| `Brain.MD` | 17120 |
| `F1_REPORT.md` | 34579 |

### 1.9 Change record

| file | change |
|---|---|
| `SOLVABLE_FINITE_PARADOX.md` | §3 derivation block added; *Thermodynamic Cost* row rewritten; §1.B linked |
| `ANTI_INFINITY_BLINDSPOT.md` | §2.B quote rewritten: erasure not processing, premise labelled, constant quoted |
| `MSAF_COSMOLOGY_DECONSTRUCTION (2).md` | *absolutely* withdrawn; floor evaluated at the document's `T`; per-bit and no-total statements added |
| `landauer_check.py` | new gate, 23 checks over 3 documents |
| `Brain.MD` | `(2).md` de-duplicated claim corrected; `SOLVABLE` entry updated for F2-1; `landauer_check.py` entry and pipeline step added |
| `F1_REPORT.md` | §5.5 marked **CLOSED by F2-1** (not deleted); two retraction rows added; §7 exit amended |

---

## 2. F2-2 — one definition of `Z_none`, and every other document points at it

### 2.1 The defect was sharper than F1-L recorded

`F1_REPORT.md` §F1-L filed this as *label ambiguity*: `Skill.md` defines the
zone as `0 < |x - x0| < Delta_univ` while the DRAF table calls shifts 1..5 the
"NON-EXISTENCE ZONE". Auditing it for F2-2 showed it is not ambiguity but a
**contradiction**:

> Row *n* of the table sits at `|x - x0| = n * Delta_univ` with `n >= 1`.
> The definition is strict on both ends. Therefore **no row of the table is a
> member of the set the table is named after.**

The zone is non-operational and is never evaluated — which is precisely why it
has no rows. The table cannot contain it by construction.

### 2.2 Four sites, not one

| site | was | now |
|---|---|---|
| `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md` table | 5 rows labelled `NON-EXISTENCE ZONE (Falsified)` | `OUTSIDE $\\mathcal{Z}_{\\text{none}}$ -- root destroyed` |
| `CONSOLIDATED_MASTER_MANIFESTO.md` | "domain of space below $10^{-62}$" — a magnitude, not a set | the set, plus an explicit statement that the two are different objects |
| `msaf_visual.py` stem-plot title | "Zone of Non-Existence Beyond the Critical Line 0.5" over the same five points | "Pixel-shift sweep OUTSIDE the zone" |
| `DEFINISI_OPERASIONAL_MSAF.md` | one correct definition sitting alongside others | declares itself **the definition of record** |

`Skill.md` already carried the correct set and now links to the glossary rather
than restating it as if independent. The DRAF also gained a reading note saying
that no row lies inside the zone and why.

### 2.3 The gate

`znone_check.py` normalises away `|`, `\lvert`, `\rvert`, `x_0` and
`\Delta_{\text{univ}}`, so the three legitimate renderings of the set collapse
to one string. A document that paraphrases instead of reproducing it fails.

| check | condition |
|---|---|
| Z1 | the glossary states `0<|x-x0|<D`, **strictly** on both ends, and declares itself the definition of record |
| Z2 / Z3 | `Skill.md` and the manifesto reproduce the canonical set |
| Z4 | the ambiguous label `NON-EXISTENCE ZONE` is absent from all five documents |
| Z5 | the DRAF carries exactly five sweep rows, `n = 1..5` in order, all labelled OUTSIDE, and none claims membership |
| Z6 | the reading note is present (no-row-inside, the reason, and `n = 1\ldots5`) |
| Z7 | no `plt.title()` calls the sweep the zone; one titles it OUTSIDE |
| Z8 | the actual prohibition sentences survive in both `Skill.md` and the glossary |

Current run: **19 conditions met, exit 0.**

### 2.4 Proof

**Fault injection — one document mutated at a time, restored byte-identical
before the next mutant ran.**

| set | mutants | caught |
|---|---|---|
| Z1 | make the left bound `<=`; make the right bound `<=`; delete the declaration of record | 3 / 3 |
| Z2 / Z3 | drift `Skill.md` to a magnitude paraphrase; drift the manifesto to "anything below 10^-62" | 2 / 2 |
| Z4 | resurrect the ambiguous label in the DRAF, in `msaf_visual.py`, in `Skill.md` | 3 / 3 |
| Z5 | delete sweep row `n = 5`; relabel a row `IN` the zone | 2 / 2 |
| Z6 | delete the whole reading note | 1 / 1 |
| Z7 | restore the old plot title; drop `OUTSIDE` from it | 2 / 2 |
| Z8 | delete the rule in `Skill.md`; delete the prohibition in the glossary | 2 / 2 |
| **total** | | **15 / 15** |

Controls — mutations that must **not** trip the gate:

| control | required | observed |
|---|---|---|
| rewrite `Skill.md`'s set using raw `|` instead of `\lvert` (equivalent) | PASS | exit 0 |
| reword the fix-record comment in `msaf_visual.py` | PASS | exit 0 |
| add a trailing sentence to the manifesto | PASS | exit 0 |
| **total** | | **3 / 3** |

All five documents were byte-identical to their pre-injection bytes after every
mutant, and the gate returned exit 0 at the end.

Reproducible: `harnesses/f2_2_inj.py` — the same 15 mutants and the same 3
controls, re-run 2026-10-06.

### 2.5 Defects found in the gate while building it, and fixed

1. `CANON` still contained `|`, but `normalise()` strips `|` — nothing could
   ever match. Gate reported seven failures on a correct workspace.
2. The strictness probe `\le` matched the substring inside `\left` **and**
   inside an unrelated `\ell_P \le \Delta \le D_obs` bound elsewhere in the
   same glossary. It now tests only the `Z_none` expression.
3. The `Z6` probe required a `}` that the LaTeX does not have.
4. The `Z7` probe demanded exactly one `plt.title()`, but the file has two
   subplots — and separately, the doubled backslashes of a raw matplotlib
   string were not matched.
5. **`Z8` keyed on the word "non-operational", which also sits in `Skill.md`'s
   table row.** Mutant #14 deleted the real rule on line 64 and the gate still
   passed. It now keys on the prohibition sentences themselves. This was a
   genuine false-pass.
6. The `Z5` membership probe was an unreadable comprehension; replaced.

### 2.6 Encoding

Every file touched in F2-2: UTF-8 strict, no BOM, zero CR bytes.

| file | bytes |
|---|---|
| `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md` | 11271 |
| `CONSOLIDATED_MASTER_MANIFESTO.md` | 3142 |
| `Skill.md` | 6671 |
| `DEFINISI_OPERASIONAL_MSAF.md` | 4926 |
| `msaf_zeta_check.py` | (selector updated) |
| `msaf_visual.py` | (title + comment updated) |
| `znone_check.py` | new gate |
| `Brain.MD` | 17963 |
| `F1_REPORT.md` | 36408 |

### 2.7 Change record

| file | change |
|---|---|
| `DEFINISI_OPERASIONAL_MSAF.md` | §1 declared the definition of record |
| `Skill.md` | §3 row links to the glossary instead of restating it |
| `CONSOLIDATED_MASTER_MANIFESTO.md` | magnitude paraphrase replaced by the set |
| `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md` | 5 row labels corrected; reading note added |
| `msaf_visual.py` | plot retitled; fix-record comment explaining why |
| `msaf_zeta_check.py` | C7 now selects on `OUTSIDE`, and fails if the ambiguous label returns |
| `znone_check.py` | new gate, 19 conditions over 5 documents + 1 script |
| `Brain.MD` | `msaf_visual` description corrected; `znone_check.py` entry and pipeline step added |
| `F1_REPORT.md` | F1-L marked FIXED, residual 3 marked CLOSED, 3 retraction rows added, §7 exit amended |

---

## 3. F2-3 — the F1-H numbers now have a producer

### 3.1 The defect

`F1_REPORT.md` §5.1 recorded that `Re = 1.43864420885e-62`,
`Im = 2.2903036742e-63`, `|Delta zeta| = 1.45676081388e-62` reproduce to 7
digits but **no script in this workspace produces them**. `msaf_zeta_check.py`
re-derives the *claim* from the paper and from the identity; recovering the
*computation* is a different thing. The figures were correct and their
provenance file did not exist.

### 3.2 The trap that was avoided

`rho_1` has to be accurate to the working precision. Taken as the usual
14-digit literal `14.13472514173469`, evaluating `zeta(0.5 + rho_1 i)` bottoms
out near `4.7e-16` — that is the error in the root showing up, fifteen orders
of magnitude away from the published `-6.1299e-102`. Only
`mpmath.zetazero(1)` at `dps = 100` reproduces it.

| quantity | produced | published |
|---|---|---|
| `zeta(s_kritis)` | `-6.12985686454756369e-102 + 3.85047904126896917e-101 i` | `-6,1299e-102 + 3,8505e-101 i` |
| `zeta(s_tergeser)` | `1.43864420884960008e-62 + 2.29030367420034391e-63 i` | `1,438644e-62 + 2,290304e-63 i` |
| `\|Delta zeta\|` | `1.45676081388024976e-62` | `1,456761e-62` |
| identity `\|zeta'(rho_1)\| * Delta` vs `\|Delta zeta\|` | rel `3.871e-41` | — |

Relative error against the F1-H eleven-digit targets: `2.78e-13` (Re),
`1.50e-13` (Im), `1.72e-13` (magnitude) — i.e. limited only by the precision
of the published figures themselves.

### 3.3 Two gaps found while proving this stage

**a. Tolerance alone does not detect a misrounded figure.** At 5 sf the
half-unit window is `5e-5`. Editing the paper's `-6,1299` to `-6,1298` is a
*wrong rounding of the true value* — but the relative error is `9.3e-6`, well
inside the window, so both gates passed it. Both now also require the declared
figure to be the correctly **rounded** one:

```
FAIL  zeta_kritis Re  misrounded: computed rounds to -6.1299e-102,
                      document states -6.1298e-102
FAIL  C1 Re rounded to 5 sf: computed -6.1299e-102, document states -6.1298e-102
```

**b. The producer's read-back could never fail.** Step 4 overwrites
`zeta_pixel_results.json` unconditionally, so step 5 was reading what it had
just written — a write-integrity check, not tamper detection. That is now
stated as what it is, and tamper detection is where it belongs: C9 in
`msaf_zeta_check.py` reads the artifact **without rewriting it**.

C9 originally checked only the scalar fields, and a forged `rho_1` passed both
gates. It now requires the artifact to carry this run's own `zetazero(1)`, to
agree with the document, and to be internally consistent component by
component (`dzeta.re = tergeser.re - kritis.re`, and all four complex
components equal to a fresh recomputation).

### 3.4 The gate chain

```
zeta_pixel_producer.py  --produces-->  zeta_pixel_results.json
        |                                      |
        | reads DRAF, recomputes               | read by
        v                                      v
   exit 0/1/2                        msaf_zeta_check.py C9 --exit 0/1/2
```

Neither gate can pass without the other's precondition: the producer refuses
to sign off on a paper it cannot reproduce, and the paper gate refuses to pass
without a producer's artifact.

### 3.5 Proof

**Producer** — exit 0, every published figure reproduced, artifact written and
read back.

**Fault injection — 14 mutants, one file mutated at a time, restored
byte-identical before the next.**

| set | mutants | caught |
|---|---|---|
| paper claims | tamper `\|Delta zeta\|`; tamper `zeta(s_tergeser)` Re; **misround `zeta(s_kritis)` inside the 5 sf window**; delete the `\|Delta zeta\|` claim | 4 / 4 |
| artifact | delete it; tamper `dzeta.abs`; verdict `FAIL`; corrupt the JSON; lie about `dps`; rename the producer; tamper `rho1`; tamper `zeta_kritis.re`; break `dzeta.re`; append a digit to `rho1` | 10 / 10 |
| **total** | | **14 / 14** |

Controls:

| control | required | observed |
|---|---|---|
| add an unused key to the artifact | PASS | both exit 0 |
| re-encode the artifact with different indent | PASS | both exit 0 |
| reword a sentence the gates do not read | PASS | both exit 0 |
| **total** | | **3 / 3** |

Every mutant was applied with the **consumer run before the producer**, because
the producer rewrites the artifact and would otherwise mask the entire
artifact class. Both gates returned exit 0 at the end and both files were
byte-identical to their pre-injection bytes.

Reproducible: `harnesses/f2_3_inj.py` — the same 14 mutants and the same 3
controls, consumer still run before producer, re-run 2026-10-06.

### 3.6 Change record

| file | change |
|---|---|
| `zeta_pixel_producer.py` | new; produces and signs the F1-H figures |
| `zeta_pixel_results.json` | new artifact, 1466 bytes |
| `msaf_zeta_check.py` | `check_scalar()` adds a rounding requirement to C1/C2/C3; new C9 gate over the artifact |
| `Brain.MD` | producer entry, pipeline step, `msaf_zeta_check` entry updated to C1..C9 |
| `F1_REPORT.md` | residual 1 marked **CLOSED by F2-3**; §7 exit amended |

---

## 4. F2-4 — the two bridge copies are now held together by a gate

### 4.1 The defect

F0 residual #6:

> Two registered servers read two copies of `shp_mcp_bridge_v4.py`, kept
> identical only by hand. They are byte-identical as of F0; any future edit
> must be applied to both or routed through a single source, otherwise one
> server silently reverts to the old contract.

"Byte-identical as of F0" is a statement about a moment, not an invariant.
Nothing re-read those bytes. If one copy had been edited since F0 the
workspace would still be reporting a contract it no longer held, and the two
servers would disagree about what a verdict means.

### 4.2 The gate

`bridge_mirror_check.py`, exit 0/1/2 on the Anti-Circularity convention.

| | condition | on failure |
|---|---|---|
| B1 | `opencode.jsonc` parses as JSONC (comments stripped outside string literals) and registers both `shp_asymmetric_wager` and `shp_bridge` | FAIL |
| B2 | both registered scripts exist and are named `shp_mcp_bridge_v4.py` | FAIL |
| B3 | the two scripts are **byte-identical** | FAIL |
| B4 | both carry `v4.2.0-PROOF-ONLY`, `PROOF-ONLY - NOT A SIMULATED`, `"simulated": False`, and both F0-4 regression tests; neither defines the removed `_evaluate_simulated` | FAIL |
| B5 | the canonical registration's write roots all lie inside the workspace, **and** the mirror's declared corpus root exists | FAIL |
| B6 | `--test` exits 0 on **both** copies | FAIL |

As written at F2-4, two lines reported rather than graded — the mirror's
absent corpus root and its undeclared write allowlist — and the live run was
**8 ok, 0 FAIL, 3 SKIP**, exit 0. **F2-5 then repointed that corpus root**, so
two of those three skips became real checks: the gate now reports
**10 ok, 0 FAIL, 1 SKIP**. See §5. What remains is the write allowlist alone,
which is out of scope for F2-4 by stated design.

### 4.3 Why byte-identity is the load-bearing condition

If B3 holds, the mirror **is** the file that just passed `--test`, so one
functional test covers both copies; if B3 fails, the gate already fails. That
argument mattered most while the mirror's own `--test` was skipped. Since F2-5
the mirror runs its suite too, and B3 remains the defence that makes a
*missed* functional difference impossible rather than merely unlikely.

### 4.4 Proof

**Fault injection — 13 mutants at F2-4, one file mutated at a time, restored
byte-identical before the next. (Re-run at **14/14** after F2-5 added a
regression mutant — see §5.6.)**

| set | mutants | caught |
|---|---|---|
| the copies | tamper canonical only; tamper mirror only; reintroduce `def _evaluate_simulated` in both; drop `v4.2.0-PROOF-ONLY` from both; strip the `[TEST 9]` regression from both; delete the mirror; delete the canonical; append non-UTF8 bytes to the canonical | 8 / 8 |
| the registration | rename `shp_bridge`; point the canonical at a missing script; add a write root outside the workspace; delete `SHP_MCP_WRITE_ROOTS`; corrupt the JSONC | 5 / 5 |
| **total** | | **13 / 13** |

Controls: reindent the config through `json`; minify it; reword a comment the
gate does not read; append an identical comment to both copies —
**4 / 4 correct**, all four still exit 0.

Config mutants were injected on **temp copies** of `opencode.jsonc` (the live
registration file is never written); bridge mutants were injected on the real
files and restored. After every mutant and at the end, both bridge copies and
`opencode.jsonc` were byte-identical to their pre-injection snapshots, and the
live gate exited 0.

Reproducible: `harnesses/f2_4_inj.py` — 14/14 mutants and 4/4 controls,
re-run 2026-10-06; the config mutants now run against temp copies of the
registration file and the bridge mutants against temp copies of both scripts,
so the live files are never written (see §8.3.1).

### 4.5 Three defects in the harness, found while building it

None of these were gate defects, and each would have produced a false claim
had it gone unnoticed:

1. **`open(p, "wb").write(fn(rd(p)))` empties the file before reading it.**
   Python evaluates `open(p, "wb")` — which truncates — *before* evaluating
   its argument, so `rd(p)` then reads zero bytes. The mutant wrote nothing
   but its own patch, every required marker vanished, and four different
   mutants produced one identical symptom. Read first, write second.
2. **Config patterns used single backslashes against JSON-escaped `\`.**
   Three mutants silently mutated nothing and the gate passed them. Structural
   config mutants are now built by parsing and re-dumping, not by string
   substitution.
3. **The `v4.2.0-PROOF-ONLY` mutant replaced only the first occurrence**, and
   that marker appears many times — so the mutant was a no-op and the gate
   correctly passed it. A weak mutant is indistinguishable from a weak gate
   until the other direction is tested.

### 4.6 Blind-spot review of F2-4

- **B4 checks markers as substrings.** A marker surviving in a docstring
  while the code behind it is gone would pass B4. B6's functional `--test`
  (TEST 9 and TEST 10 exist precisely for this) covers it on the canonical
  side, and B3 extends that to the mirror. Not closed statically, and not
  claimed to be.
- **`absent` is reported before `present` in B4**, so a mutant doing both at
  once reports only the missing text. It still fails, so this is a reporting
  weakness rather than a false pass.
- **The mirror's write allowlist is not enforced.** `shp_bridge` declares no
  `SHP_MCP_WRITE_ROOTS` and falls back to a built-in list that reaches outside
  its own corpus root. This is a different server with a different corpus, so
  F2-4 does not grade it — recorded here and **not passed**. Scope: editing a
  registered server's allowlist is an operator decision.

### 4.7 Change record

| file | change |
|---|---|
| `bridge_mirror_check.py` | new; B1–B6 over both copies and both registrations |
| `F2_REPORT.md` | this section |
| `Brain.MD` | pipeline step and file entry for the new gate |

---

## 5. F2-5 — the dead corpus root, repointed

### 5.1 The defect

F0 residual #5: `opencode.jsonc` registered `shp_bridge` with
`SHP_MCP_CORPUS_ROOT = D:\Theory_of_Everything_Derivations`, and that directory
does not exist on this machine. The consequence is quiet, not loud —
`list_documents` / `read_document` / `search_corpus` returned **an empty result
set rather than an error**, so a registered server answered "no documents"
forever while `shp_asymmetric_wager` (rooted at the workspace) returned 20.

F0 declined to fix it: *"correcting a registered MCP root changes which corpus
a running server reads, and that is a decision for the operator, not an
audit."* F2-5 asked.

### 5.2 What was actually there

`D:\THE ASYMMETRIC WAGER\Theory_of_Everything_Derivations` **exists**, with
27 files — `NODE_*.pdf.txt`, `kronos.txt`, `gemini-code-*`, the Dream-RSI PDF.
The registration was pointing at a path that never existed here while the
material it names sat inside the workspace, one level down.

### 5.3 The change — one line

```
-        "SHP_MCP_CORPUS_ROOT": "D:\\Theory_of_Everything_Derivations"
+        "SHP_MCP_CORPUS_ROOT": "D:\\THE ASYMMETRIC WAGER\\Theory_of_Everything_Derivations"
```

Validated **before** writing: exactly one occurrence of the old value, the
JSONC still parses, line count unchanged, `CRLF` count `0 → 0`, no BOM, and a
one-line diff. Backup: `opencode.jsonc.bak-f25-20261005_021355`. Nothing else
in the file was touched, and the running session's server still reports the
old root — MCP servers are spawned at session start, so the live effect
arrives on restart.

### 5.4 What the change activated

| | before | after |
|---|---|---|
| `shp_bridge --test` | exit **1** (TEST 6 corpus toolchain failure) | exit **0** |
| `bridge_mirror_check` B5 mirror root | SKIP | **ok** |
| `bridge_mirror_check` B6 mirror `--test` | not run | **runs, exit 0** |
| gate totals | 8 ok / 0 FAIL / **3 SKIP** | **10 ok / 0 FAIL / 1 SKIP** |

### 5.5 A regression is now a failure, not an open question

Before F2-5, an absent mirror corpus root was `SKIP` — correctly, because the
right value had not been decided. **F2-5 decided it.** Leaving the check at
`SKIP` would have handed back the exact hole F2-5 closed: repointing the
registration at the dead path would again pass silently.

B5 now **FAILs** if the mirror's corpus root is missing or undeclared, and a
new mutant **M14** ("repoint the mirror at a nonexistent corpus root") locks
that in. The one surviving SKIP is the mirror's write allowlist, which is a
different question and is recorded rather than graded (§4.6).

### 5.6 Proof

The F2-4 injection suite was **re-run in full after the config change** —
because the suite snapshots `opencode.jsonc` and every config mutant is built
from it, so a config edit invalidates the previous run:

- **14 / 14 mutants caught** (the original 13 plus M14),
- **4 / 4 controls correct**,
- live gate exit **0**,
- both bridge copies and `opencode.jsonc` byte-identical to their snapshots
  after every mutant and at the end.

Reproducible: `harnesses/f2_4_inj.py`, same suite — F2-5 adds no stage of its
own and is proved by re-running F2-4 after the config change (§8.3.1).

### 5.7 Change record

| file | change |
|---|---|
| `C:\Users\usER\.config\opencode\opencode.jsonc` | **one line** — `shp_bridge` corpus root repointed at the workspace subfolder; backup taken |
| `bridge_mirror_check.py` | B5 mirror root SKIP → FAIL (regression guard); the write-allowlist note made **unconditional** (it used to vanish exactly when the server became usable); B6 runs both copies; docstring and summary updated |
| `F0_REPORT.md` | §9 items 5 and 6 marked **CLOSED by F2-5 / F2-4**, recorded not deleted |
| `Brain.MD` | MCP line now names both servers and their roots |

---

## 6. F2-6 — the `p` axis stays, and the panel now earns it

### 6.1 The question and the answer

F1-N left a **design** question open: *"whether the `p` axis should be plotted
at all, given it carries no information over 2000–18000 bits."* Three options:

| | option | verdict |
|---|---|---|
| a | drop the axis and the curve | **rejected** — the axis names the independent variable whose inertness *is* the finding, and a range has to be visible for "flat over 2000–18000" to mean anything |
| b | plot the analytic residual `log10 R_tail(p) − log10 R_tail(p0)` so the dependence shows at its own scale | **rejected** — autoscaling a `1e-58` span draws a confident diagonal and invites the *opposite* reading |
| c | keep axis, curve and markers; make the panel self-contained | **chosen** |

### 6.2 What was actually wrong

The residual's framing ("the axis carries no information") turned out to be
slightly off. The axis carries two real landmarks — the N=400 certificate
operated at 9000 bits and was verified at 18000 bits. The defects were:

1. **Those markers were labelled as curve events.** `Pivot 723 Halt (v2)` and
   `Verified Certificate` sit on a plot of `R_tail` and read as though the
   curve responded to them. This is the *same* defect F1-N already found in
   `Brain.MD`'s prose and corrected there — but the figure itself still had it.
2. **The figure was not self-contained.** The two numbers that make "flat"
   meaningful — `float64 observed span = 0.000e+00` and
   `1 decade would need 1.809e+62 bits` — were printed to stdout only. A reader
   of the image could not distinguish "flat because inert" from "flat because
   the axis is scaled badly".

Both markers now read `certificate: 9000 bits (pivot 723 undetermined)` and
`certificate: 18000 bits (verified)`, the annotation states all three numbers,
and it says outright that the markers are *not features of this curve*.

### 6.3 The gate renders the figure and inspects what was drawn

`visual_check.py` imports `msaf_visual.py` under `MPLBACKEND=Agg` and reads the
**artists** — titles, labels, legend texts, annotation texts, `ydata` — rather
than grepping the source. A grep would be satisfied by a comment; a drawn
artist cannot be.

| | condition |
|---|---|
| V1 | the module renders exactly one figure with two panels |
| V2 | panel 1's x-axis names the precision parameter `p` |
| V3 | panel 1's title declares the curve flat |
| V4 | the annotation carries the analytic span, the float64-observed span, the bits-per-decade figure, and the marker clarification |
| V5 | both vertical markers identify as `certificate: …` operating points |
| V6 | the drawn `ydata` span is **exactly `0.0`** in float64, and the declared float64 span equals what was drawn |
| V7 | `log10_span = -(p_hi - p_lo) · Delta_univ · log10(2)` to 7 sf |
| V8 | `decade_bits = 1 / (Delta_univ · log10(2))` to 7 sf |
| V9 | the legend carries the curve and both markers |

**13 ok, 0 FAIL**, exit 0.

### 6.4 Proof — fault injection, 11 mutants + 3 controls

| mutant | caught by |
|---|---|
| drop the float64-observed span from the figure | V4 |
| drop the bits-per-decade figure | V4 |
| drop the `not features of this curve` clarification | V4 |
| relabel a marker `Pivot 723 Halt (v2)` | V5 |
| title says `exhibits decay` | V3 |
| x-axis renamed to `Iterations` | V2 |
| make the curve visibly non-flat | V6 |
| lie about bits-per-decade by ×1.5 | V8 |
| break the analytic span formula | V7 |
| delete one certificate marker | V5 |
| strip the curve's legend label | V9 |
| **total** | **11 / 11** |

Controls — change the figure size, change a marker colour, reflow a comment:
**3 / 3** still exit 0.

The non-flat mutant is the one worth reading: V6 reports `span = 4.816…` and
states the consequence rather than just the mismatch — *"the title and every
document describing this sweep would now be wrong."*

Every mutation was restored byte-identical before the next, and the live gate
exited 0 at the end.

Reproducible: `harnesses/f2_6_inj.py` — the same 11 mutants and the same 3
controls, re-run 2026-10-06.

### 6.5 Change record

| file | change |
|---|---|
| `msaf_visual.py` | F2-6 decision comment (options a/b/c with reasons); markers relabelled `certificate: …`; annotation extended to four lines |
| `visual_check.py` | new; V1–V9 over the rendered artists |
| `F1_REPORT.md` | residual 4 marked **CLOSED by F2-6** |
| `Brain.MD` | pipeline step, `visual_check.py` entry, `msaf_visual.py` row |

---


## 7. F2-7 -- machine-gating lambda_min at N = 400

### 7.1 The defect, restated from F1-D

`omega_core_v2_results.json` was written by run 2 and holds the N = 800
record (1774 bytes, sha256 `20ff0378bf72065c75ee8af2e873350d0dcd6801e6384db86eb14d7594119cbc`).
The 1971-byte N = 400 record it replaced (sha256
`5aaab0cfbf26f7fc5a3306bcd6a6e82e5482dad54a0a08d55ed4ebdcf22aa4f2`)
survives in three written records and nowhere machine-readable:

| record | line | precision | value |
|---|---|---:|---|
| `omega_core_v2_run.log` | 51 | 25 sf | `6.747092398972142917175307e-509` |
| `PROVENANCE.txt` 6.2 | 164 | 30 sf | `6.74709239897214291717530665950e-509` |
| `OMEGA_CORE_CERTIFICATE.md` 4 | 276 | 30 sf | `6.74709239897214291717530665950e-509` |

F1 recorded the consequence precisely: **three documentary records, zero
machine-readable artefacts** -- the object could not be re-read or re-gated.

### 7.2 The decision, and why the default output name was the hazard

Asked whether to overwrite the shipped N = 800 record or write a separate
file, the operator chose a separate file. The run therefore pins `--out`:

```
python -u gw_omega_core_v2.py --c 100 --dims 400 --prec 9000
    --escalations 3
    --out    omega_core_v2_results_N400.json
    --log    omega_core_v2_run_N400.log
    --heartbeat omega_core_v2_heartbeat_N400.json
    --ckpt   ckpt_N400
```

Launched 2026-10-05 02:27:39 (PID 15252). Two facts were verified from the
live process rather than assumed: the command line actually carries that
`--out` (read back through `Win32_Process`), and the shipped N = 800 artefact
still hashes to `20ff0378...119cbc` after launch. The certificate 8
reproduction block already carried the same warning; it now needs the
canonical output name rather than the placeholder `n400_rerun.json`.

### 7.3 The gate

`gw_verify_production.py` was extended in place (8234 -> 15279 bytes, sha256
`e1c3e0caacb43bfb823abf3c8d00e2c4199dbb11fce34e3de70edd4d041da03c`):

1. The per-row invariants that F1 inlined for N = 800 were extracted into
   `certified_row_checks(r, tag)` and are now applied to **both** rows, so
   the two production records are held to one standard rather than two.
2. The N = 400 row additionally must carry `c == 100`, `N == 400`,
   `dim == 801`.
3. The three documentary records are re-read **from their files at check
   time** -- none is quoted into the source -- and each is compared against
   the freshly computed bound at that record's own significant-digit count
   (25 for the log, 30 for the other two). This removes the magic tolerance
   entirely: `mp.nstr(value, n)` on both sides, string equality.
4. A missing result file, an unreadable one, a non-list, or a wrong row count
   all produce a `FAILURES` line and exit 1 -- never a traceback.

`argv[1]` and `argv[2]` override the two production paths, which is what makes
fault injection possible without ever creating the real artefact.

### 7.4 Proof so far

| what | result |
|---|---|
| fault injection, 24 mutants + 2 controls | **26 / 26**, harness exit 0 |
| missing-documentary-file path (rename -> run -> restore -> hash) | **4 / 4**, every restore byte-identical |
| workspace suite after the edit | **7 / 7** exit 0 |
| `gw_verify_results.py` after the edit | exit 0 |
| `gw_verify_production.py` after the edit | exit 1, one failure only: `[production N=400] result file is missing` |

That last row is the residual being held open by the gate itself. It is the
expected state until the run writes its artefact.

Mutants covered: absent file; non-list JSON; empty list; two rows; missing
required key; wrong `N`; wrong `dim`; `n_neg != 0`; non-hex `sha256`;
`symmetry_dev` "0.0"; non-empty caveats; `anomaly` true; `non_result` true;
non-null `undetermined_pivot`; empty `attempts`; `non_result_reason` present;
bound set to `1`; bound negative; `min_abs_pivot` corrupt; `pivot_sign` "-";
`max_entry_radius` above `1e-50`; a bound internally consistent with its own
`bound_detail` but disagreeing with all three documents; the same at one
digit past the log's precision; `null` document; unparsable document.

Reproducible: `harnesses/f2_7_inj.py` — the same 24 mutants, the same 2
controls and the same 4 missing-document cases, re-run 2026-10-06; §8.3.1
records how the case list was reconstructed from this section.

### 7.5 Defects found while building it, and fixed

**In the gate.** `documentary_records()` used plain `io.open`, so a missing
or unreadable `PROVENANCE.txt` / certificate / run log raised `OSError` and
produced a traceback instead of a `FAILURES` verdict. That is the F1 hardening
rule 5 (a corrupt input must yield a verdict, not a traceback) and it was
found by a blind-spot pass over the finished gate, not by the injection run --
the injection never deletes a source document. Fixed with a `first()` helper
that maps `OSError` to `None`, proven by the rename/restore harness in 7.4.

**In the harness.** Four defects, all mine, all found by reading the output
rather than the summary line:

1. `case()` always wrote a file, so the "missing file" control was in fact a
   valid file and the gate correctly passed it -- the harness reported FAIL.
2. Two mutants were declared with no mutation applied at all, so they were
   controls dressed as mutants.
3. `n_rows` was not honoured, so `M3_tworows` wrote one row.
4. The recovery assertion expected exit 1 while `argv[2]` was a passing
   control row; exit 0 was the correct answer.

None of these is a property of the gate. They are recorded because a harness
that reports its own mistakes as product failures is how a real regression
gets waved through.

### 7.6 Blind-spot review of the F2-7 gate

1. **Positional, not semantic, record selection.** The first numeric
   `lambda_min >=` match in `PROVENANCE.txt` and in `omega_core_v2_run.log` is
   the N = 400 record only because that run was appended first. Reordering the
   log would swap in the N = 800 value. The failure mode is a false FAIL, not
   a false pass, unless an injected line happens to carry the right value.
   Deliberately not hardened: line numbers are more brittle than ordering.
2. **`errors="replace"`** on the log read means a corrupted surrounding byte
   becomes U+FFFD and the regex still fires. A mangled *number* is caught by
   the comparison; mangling elsewhere in the log is outside this gate.
3. **`prec` is deliberately not asserted.** A run that succeeded at 9000 bits
   without escalation would still be a valid positive-definiteness
   certificate. The gate asserts the bound, not the escalation narrative; the
   narrative lives in certificate 3.1.
4. **The new run's own log is not cross-checked.** Only the three original
   records are -- those are the ones F1 found un-gated. The new log and
   heartbeat are covered by `CHECKSUM.sha256` instead.
5. **`mp.mp.dps = 60` is a module global.** A documentary record longer than
   60 significant digits would be rounded by `nstr` before comparison. Current
   records are 25 and 30 digits, so the rounding never reaches them.
6. **Path resolution is `HERE`-relative.** A copy of the gate run outside the
   repo cannot find the records; this is tested to be a clean FAILURES, not a
   bypass.
7. **The final print cannot reach a null row.** `load_row()` records a failure
   before returning `None`, so `r["n_pos"]` is only evaluated when `failures`
   is still empty.

### 7.7 Encoding

Every edit in this stage went through Python
`io.open(..., encoding="utf-8", newline="\n")` or an ASCII payload. Verified
afterwards: no `CR`, no BOM, UTF-8 strict, LF only.

### 7.8 Change record so far

| file | change |
|---|---|
| `gw_verify_production.py` | extended: shared `certified_row_checks()`, N = 400 row, documentary cross-check at native precision, clean verdicts on missing/unreadable inputs |
| `F2_REPORT.md` | this section; Residual and Exit renumbered to 8 and 9; header status/gates refreshed; section 6 subsection headings corrected from 5.x |

### 7.9 Closure checklist -- completed 2026-10-05

- [x] gate run against the real artefact, exit 0
- [x] the artefact's `lambda_min_lower_bound`, sha256 and row shape recorded
      in 7.10 below
- [x] `CHECKSUM.sha256` regenerated once (113 -> 116 rows: three new run
      outputs, plus the refreshed `gw_verify_production.py` entry and a header
      note); the certificate's byte-hash inventory row and its superseded-hash
      note updated
- [x] `Brain.MD`, `REPO_STRUCTURE.md`, `README.md`, `PROVENANCE.txt` §6.2 and
      the certificate updated from "log-recorded only" to "machine-gated"
      (`Skill.md` §3 carries the run status; the certificate edit records the
      superseded `80f6fbf73c45…` hash rather than erasing it)
- [x] `F1_REPORT.md` residual 2 marked CLOSED by F2-7; `F2_REPORT.md` 8 and 9
      rewritten
- [x] Anti-Circularity Gate as the last action, after every file above is final

The box was left until the gate had actually been run -- ticking it first
would be exactly the comment-only-claim failure the gate exists to detect.
Run 2026-10-05 against `OMEGATrackC.lean` and `track_c_side_conditions.smt2`,
output reproduced rather than paraphrased:

```
gate self-test: 13 cases, 0 failed

SMT CIRCULARITY AUDITOR -- z3 5.0.0
files scanned: 1
GENUINE           asserts=1   ctx=sat   script=unsat   core=[0]
                  track_c_side_conditions.smt2
summary: GENUINE=1
ANTI-CIRCULARITY GATE [check]   result: FAIL=0 NOT_RUN=0 SKIP=0   verdict: PASS
ANTI-CIRCULARITY GATE [lean]    result: FAIL=0 NOT_RUN=0 SKIP=0   verdict: PASS
ANTI-CIRCULARITY GATE [claim]   result: FAIL=0 NOT_RUN=0 SKIP=0   verdict: PASS
```

### 7.10 The N = 400 artefact, recorded

Run 2026-10-05 02:27:39 → 10:55:54 (8 h 28 m), PID 15252, final heartbeat
`sweep:complete`.

| field | value |
|---|---|
| file | `omega_core_v2_results_N400.json` |
| bytes / file sha256 | 2223 / `bab3e5f366b3c7e7c2fdcd894520bcdffa30966d66cbfef53fa6efe774eda521` |
| inner `sha256` | `f9735e697c30941a8311ec511634958163ad07bc75432d470555814c77d856d6` |
| `c`, `N`, `dim`, `prec` | 100, 400, 801, 18000 |
| `n_pos` / `n_neg` / `undetermined_pivot` | 801 / 0 / null |
| `anomaly` / `non_result` / `caveats` | false / false / empty |
| `symmetry_dev` / `symmetry_exact` | `"0"` / true |
| `peak_mb` | 4572.721152 |
| `lambda_min_lower_bound` | `6.74709239897214291717530665950e-509` |
| `bound_detail.min_abs_pivot` | `2.014657282505926679349953e-112` (sign `+`) |
| `bound_detail.norm_Linv_F_upper` | `1.727994119336448038542856e+198` |

Attempt 1 at 9000 bits: build 6700.1 s, LDL^T 1162.2 s, `n_pos=723`,
`n_neg=0`, `undetermined_pivot=723`, max entry radius
`2.1547598290585434360e-2577`. Attempt 2 at 18000 bits: build 16132.3 s,
LDL^T 3547.3 s, all 801 pivots certified, max entry radius
`1.398551439204522661230545e-5266`, max pivot radius
`1.135790614274549474670140e-2384`. The escalation point (index 723) and both
precision levels match the certificate's account of the 2026-09-29 run.

The bound reproduces **all three** documentary records: log line 51
(`6.747092398972142917175307e-509`, 25 sf), `PROVENANCE.txt` §6.2 and
certificate §4 (both 30 sf), each compared at its own digit count with a
1e-20 relative tolerance.

Shipped alongside: `omega_core_v2_run_N400.log` (4114 bytes) and
`omega_core_v2_heartbeat_N400.json` (99 bytes). `ckpt_N400/` — 1,362,311,376
bytes of resume state — is excluded from `CHECKSUM.sha256` by the same policy
that excludes `D:\gw_ckpt`: a checkpoint is machine-local resume state, not
evidence.

## 8. Residual — recorded, not closed

Carried into F2-2 … F2-7, exactly as table 0 above.

### 8.1 Open at this point in the phase

| item | source | state |
|---|---|---|
| F2-7 -- machine-gate $\lambda_{\min}$ at $N=400$ | F1 5.2 (F1-D) | **CLOSED 2026-10-05**: run completed, artefact shipped, gate exit 0 against it, 26/26 mutants + 4/4 missing-file proven, `CHECKSUM.sha256` 113 -> 116, checklist 7.9 all ticked, record in 7.10 |
| the `GW_STATUS` "stayed in HEAD" sentence | F1 5.2, second half | not closable: this tree has no `.git`, and creating a repository inside an operator's tree is an operator decision |

### 8.2 New finding -- text encodings across the tree (recorded, not touched)

A sweep of all 145 text files (`.md .py .json .jsonc .txt .smt2 .cff .lean
.ps1`) found 33 carrying CR, a BOM, or bytes that are not valid UTF-8. **None
of them is a file F2 edited, and none is a regression of this phase:**

* **16 are pinned by `CHECKSUM.sha256`.** They are engine-produced run
  outputs written in Windows text mode (`omega_core_v2_results.json`, the
  `smoke_*` JSON and heartbeats, `omega_v2_stdout.txt`, ...), the shipped
  working paper (CRLF), and `ladder_bn.txt` / `ladder_fix.txt`, which are
  **UTF-16 LE with a BOM** -- the PowerShell `Out-File` default, which is the
  same defect the manifest header already records for `CHECKSUM.sha256` itself.
* **1 is this phase's own run output**: `omega_core_v2_heartbeat_N400.json`
  (CRLF, written by the engine). It will be added to the manifest with the
  bytes it actually has.
* **16 are third-party corpus files** under `Theory_of_Everything_Derivations`
  -- external clippings, outside `CHECKSUM.sha256` and outside this phase.

Normalising the first group would change bytes that
`OMEGA_CORE_CERTIFICATE.md` section 6 quotes and that the manifest pins, so it
is **recorded, not fixed**. Every file this phase actually edited was verified
UTF-8-strict / no BOM / LF-only after each edit (7.7, and the equivalent
subsection in sections 1 through 6).

### 8.3 New finding, 2026-10-05 (Fase H) -- the F2 injection harnesses were never preserved

**Superseded on 2026-10-06 by §8.3.1.** The finding below is kept verbatim as
it stood when it was made — every word of it was true on 2026-10-05, including
the counts — and §8.3.1 records what was done about it. Read the two together:
this section is the defect, §8.3.1 is the fix.

D1 of Fase H asked which harness proves each fault-injection count this phase
reports. **There is none.**

* `harnesses/` holds 14 harnesses covering F1, F3, F4, F5 and A1 — `f1_mut`,
  `f3_inj`, `f3_vacuity`, `f3_a1`, `f4_inj`, `f4_brittleness`,
  `f4_build_register`, `f5_1_stagea/b/c`, `f5_2_inj`, `f5_3_inj`,
  `f5_4_inj`, `p09_inj` (added 2026-10-06 by A1; 13 at the time this
  section was written). There is no `f2_*`.
* This report names no harness file anywhere; every `.py` path cited below
  (`landauer_check.py`, `znone_check.py`, `zeta_pixel_producer.py`,
  `bridge_mirror_check.py`, `visual_check.py`, `gw_verify_results.py`) is a
  **gate**, not the script that mutated it.
* A filename sweep for `*f2*` across three levels of the workspace returns
  `F2_REPORT.md` and nothing else.

So the six results this phase publishes were produced by ad-hoc scripts
executed from a scratch folder and not written down:

| stage | claim as published | where it is cited |
|---|---|---|
| F2-1 | 28/28 claim mutants, 6/6 controls | 1.6, `F1_REPORT.md` §5 item 5 |
| F2-2 | 15/15 mutants, 3/3 controls | 2.4, `F1_REPORT.md` §5 item 3 |
| F2-3 | 14/14 mutants, 3/3 controls | 3.5, `F1_REPORT.md` §5 item 1 |
| F2-4 | 13 mutants at F2-4, re-run 14/14 after F2-5 | 4.4, 5.6 |
| F2-6 | 11/11 mutants, 3/3 controls | 6.4, `F1_REPORT.md` §5 item 4 |
| F2-7 | 26/26 mutants, 4/4 missing-document | 7.4, `F1_REPORT.md` §5 item 2 |

`Brain.MD`'s `harnesses/` entry claims the F1/F3/F4/F5 harnesses were copied
byte-identical and sha256-verified "so the results cited in
`F1`/`F3`/`F4`/`F5_REPORT.md` still reproduce from a path the report can
name". **F2 is the phase missing from that sentence**, and the omission was
not noticed because the counts were quoted forward into `F1_REPORT.md` §5,
where they read as inherited fact.

State when opened: **OPEN**. Two honest options, neither taken at the time:

1. rebuild the six harnesses — roughly 110 mutants across six gates, each
   requiring byte-identical restore and a control; or
2. downgrade the six counts at every citation site from *proven* to
   *observed once, not re-runnable*, which is a weaker claim but a true one.

Until one is chosen, the six numbers above were **recorded, not reproducible**
— the distinction `F1_REPORT.md` §5 already applies to the `GW_STATUS`
"stayed in HEAD" sentence.

### 8.3.1 CLOSED 2026-10-06 — option 1 taken, all six harnesses rebuilt

Option 1 was chosen and executed. `harnesses/` now holds one harness per
stage, each asserting its own published table rather than a paraphrase of it:
the expected exit code per case, a needle that must be present before a
mutation is applied (so a no-op cannot be counted as a catch), the original
bytes restored and re-hashed before the next case, a green baseline, and a
green restored baseline.

| stage | harness | claim as published | reproduced | wall time |
|---|---|---|---|---|
| F2-1 | `harnesses/f2_1_inj.py` | 28/28 mutants, 6/6 controls | **28/28, 6/6** | 7 s |
| F2-2 | `harnesses/f2_2_inj.py` | 15/15 mutants, 3/3 controls | **15/15, 3/3** | 2 s |
| F2-3 | `harnesses/f2_3_inj.py` | 14/14 mutants, 3/3 controls | **14/14, 3/3** | 15 s |
| F2-4 | `harnesses/f2_4_inj.py` | 14/14 mutants, 4/4 controls | **14/14, 4/4** | 79 s |
| F2-6 | `harnesses/f2_6_inj.py` | 11/11 mutants, 3/3 controls | **11/11, 3/3** | 29 s |
| F2-7 | `harnesses/f2_7_inj.py` | 26/26 fault injection + 4/4 missing document | **26/26 (24 mutants + 2 controls), 4/4** | 6 s |

Every number published by this phase reproduced on the first complete run of
its rebuilt harness. Two things about the rebuild are recorded rather than
quietly absorbed, because they differ from the ad-hoc scripts the counts came
from and the difference has to be visible:

* **F2-4 never writes the live registration or the live bridge copies.** The
  original run injected bridge mutants into the real files; `f2_4_inj.py`
  injects them into temp copies and reaches them through the gate's own
  `--config` / `--bridge-a` / `--bridge-b` flags. B1–B6 are exercised
  identically; the live servers are never mutated. The one ordering rule that
  this costs and that had to be kept explicitly: a *config* mutant must be
  passed **without** `--bridge-a`, or the override bypasses the registration
  the mutant is supposed to break (that mistake produced one false FAIL before
  it was fixed).
* **F2-7's case set was reconstructed from §7.4, not recovered.** Its
  "Mutants covered" list holds 25 items; the first of them, "absent file", is
  the missing-document row printed immediately above it, so the 24 JSON
  mutants are items 2..25 and the 4/4 row is the rename → run → restore → hash
  path over `PROVENANCE.txt`, `OMEGA_CORE_CERTIFICATE.md`,
  `omega_core_v2_run.log` and `omega_core_v2_results_N400.json`. The two
  controls named in §7.4 were never enumerated there; the rebuilt pair is
  "add an unused key" and "re-indent", both of which must still exit 0.

`harness_check.py` runs all twenty harnesses — the fourteen that already
existed plus these six — sequentially, snapshots the workspace before and
after each, and exits 0 only if every marker appeared and no byte moved:

```
passed=20  failed=0  not_run=0  of 20  |  workspace byte-identical
HARNESS: PASS -- 20/20 behaved as expected, workspace byte-identical
```

`Brain.MD`'s `harnesses/` entry now names F2, and every citation site in
§1.6, §2.4, §3.5, §4.4/§5.6, §6.4, §7.4 and `F1_REPORT.md` §5 refers to a
file that can be run.

---

## 9. Exit

F2-1 … F2-7 exit **complete**. Each
stage was closed the same way — built, blind-spot-audited, then re-proven
after the fix — and the defects were found by reading the deliverables back
once they already appeared to pass:

* F2-1 found two defects in its own gate, one of them (hard-coded `T`) a real
  false-pass in the gate rather than in the document (§1.7);
* F2-4 found three defects in its harness (§4.5);
* F2-7 found one in the gate and four in its harness (§7.5), and after the
  run finished it found a fifth — in its own closure harness, which asserted
  that the result file was *absent* and so failed every case the moment the
  artefact appeared (an expectation written from an assumption rather than
  compared against observation, the same defect §7.5 warned about);
* the 2026-10-06 harness rebuild (§8.3.1) found two defects while building,
  both in its own scripts rather than in the gates: a config mutant passed
  through `--bridge-a` never reached the registration it was meant to break,
  and `os.rename` cannot cross drives, so the F2-7 missing-document path had
  to be moved inside the sub-repository. Neither changed a published number;
  both changed what the harness had to do to prove it.

The Anti-Circularity Gate was run as the last action of F2, after every file
above was final: self-test `13/13`, `gate lean` and `gate claim` PASS,
`gate check` PASS with the auditor returning `GENUINE` and `core=[0]`. The
gated artifacts -- `OMEGATrackC.lean` and `track_c_side_conditions.smt2` --
were not edited during F2; the phase touched gates, reports, `Skill.md`,
`Brain.MD` and the sub-repository's documents, none of which carries a
provenance claim of the form this gate tests. The F2-7 closure harness
defect (a fifth, found after the run finished) is recorded in 7.9/7.10 and in
the exit list above.

§8.3.1 was itself a content edit to this file, so the Anti-Circularity Gate
was re-run after it — as the last action of the rebuild, exactly as §8.3.1's
own rule requires of every claim-bearing phase.
