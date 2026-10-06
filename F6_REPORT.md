# F6_REPORT — Blind-Spot Audit of the Corpus and Cross-Report Consistency

**Workspace:** `D:\THE ASYMMETRIC WAGER` (MSAF corpus, DOI `10.5281/zenodo.22791556`)
**Date:** 2026-10-06 (Fase A5)
**Status:** three sweeps executed, four defects closed, three gate rules added, every rule injection-proven.
**Language rule:** this document is English; $P_{\text{narrative}} = 0$.

---

## 0. Why F6 exists

Every previous phase hardened a *gate*. A5 was pointed at the thing no gate
reads: the prose. The reports, the knowledge map and the residual registers
between them carry thousands of statements about the rig, and until this phase
only the digit-shaped ones were ever compared with anything live.

Three questions, in the order they were asked:

1. Does a number written as a **word** get read? (Sweep 1)
2. Do the reports still agree with **each other**, after A6 changed the
   workspace underneath them? (Sweep 2)
3. Does anything **exist** that a document says exists, and does the knowledge
   map still describe the tree it claims to map? (Sweep 3)

---

## 1. Method

Same order as F5, because that order is what made F5 auditable:

1. **Recon before edit.** Every residual register (`F4_REPORT.md` §9,
   `F5_REPORT.md` §8, `F2_REPORT.md` §8, `F1_REPORT.md` §5) read in full before
   a byte moved.
2. **Dry-run the sweep first.** The written-numeral pattern set was run as a
   throwaway script and its matches triaged *before* any of it was promoted
   into a gate, so the gate was written against a list of known results rather
   than invented.
3. **Fail first.** Each new gate condition was run against the unfixed corpus
   and had to fail with the defect's own name printed before the corpus was
   fixed.
4. **Injection proves detection.** No new condition is claimed as enforced
   unless a mutant was written for it, caught by it, and restored
   byte-identically.
5. **Anti-Circularity Gate last.** Run after the last edit, never before.

---

## 2. Sweep 1 — a number written as a word is a number

### 2.1 The gap

`report_claim_check.py` read `\d+` and ordinals. It did not read "thirteen".
A sentence that says *the thirteen gates are a read-only contract* makes exactly
the claim that *13 gates* makes; both were the wording found at A5, and a corpus
whose author writes figures in prose is a corpus whose figures were not gated.

### 2.2 Dry run

The pattern `(all|the) <cardinal> (root )?gates|harnesses|rows` was run over the
root Markdown corpus unfiltered. Ten matches: **nine disagreed with the live
value, one agreed.**

| # | site | printed | live | verdict at A5 |
|---|---|---|---|---|
| 1 | `Brain.MD` §1.1 preamble | all six harnesses | 21 | subset phrase, ambiguous (A5) |
| 2 | `Brain.MD` flag paragraph | **the thirteen gates** | 14 | **defect** (A5) |
| 3 | `F1_REPORT.md` §4 | all ten rows | — | not a manifest claim at A5, see 2.4 |
| 4 | `F2_REPORT.md` §8.3 | the six harnesses | 21 | subset phrase, ambiguous (A5) |
| 5 | `F2_REPORT.md` §8.3.1 | all six harnesses | 21 | subset, already dated (A5) |
| 6 | `F2_REPORT.md` §9 | **all twenty harnesses** | 21 | **defect, unanchored** (A5) |
| 7 | `F4_REPORT.md` §1 table | the eleven gates | 14 | **defect, chain incomplete** (A5) |
| 8 | `F5_REPORT.md` §1 | Eleven root gates | 14 | **defect, unanchored** (A5) |
| 9 | `F5_REPORT.md` §1 | The eleven gates above | 14 | history, dated on the line (A5) |
| 10 | `F5_REPORT.md` §7 | the fourteen gates | 14 | correct (A5) |

### 2.3 What was fixed

**A5-1 — `Brain.MD`, current-tense constitution.**
*"the flag is off by default because the thirteen gates are a read-only
contract"*. Present tense, no date, in the file `Skill.md` tells every agent to
read first. Corrected to *fourteen*. This is the sentence the new C1 spelled
rule now holds permanently.

**A5-2 — `F2_REPORT.md` §9, unanchored.**
*"`harness_check.py` runs all twenty harnesses"* sat three lines above a date,
outside the one-line anchor window. Rewritten so the count and its date share a
line: the method sentence became timeless (*runs every harness in
`harnesses\`*) and the historical figure moved into its own dated sentence
(*At A2 (2026-10-06) it ran all twenty harnesses*).

**A5-3 — `F4_REPORT.md` §1, incomplete chain.**
The suite-regression row recorded `11/11 → 12/12 (A2) → 13/13 (A1)` and then
stopped, because it was last written before A3. Appended `14/14 since
2026-10-06, A3`.

**A5-4 — `F5_REPORT.md` §1, unanchored past tense.**
*"Eleven root gates were runnable individually"* reads as a statement about the
rig today. Prefixed with *At F5's start*, which is what was meant.

**A5-5 — three subset phrases, disambiguated.**
`Brain.MD` and `F2_REPORT.md` said "the six harnesses" / "all six harnesses"
about F2's six, in a workspace that has twenty-one. Each now reads "the six F2
harnesses". They were not wrong; they were only decidable from context, and
context is what a sweep does not have.

### 2.4 The one false positive, and why it is a rule

Match 3, `F1_REPORT.md`: *"all ten rows"* — about `PROVENANCE.txt`, not about
`CHECKSUM.sha256`. The digit-shaped rule had already solved this by requiring
`CHECKSUM|manifest` on the same line; the spelled rule now applies the identical
gate. A `rows` claim that does not name the manifest is not a claim about the
manifest.

---

## 3. Sweep 2 — the reports against each other

A6 made the workspace a Git repository. Five statements across three documents
still said it was not, and none of them carried a date that would let a reader
discover that.

| site | printed | state after A6 |
|---|---|---|
| `F1_REPORT.md` §3 findings | "the workspace contains **zero** `.git` directories" | restated, dated |
| `F1_REPORT.md` §5 item 2 | "NOT ESTABLISHED … because there is no `.git`" | restated, reason split from verdict |
| `F2_REPORT.md` §2 stage table | "requires a `.git`, which this tree does not have" | superseded note added |
| `F2_REPORT.md` §8.1 | "not closable: this tree has no `.git`" | superseded note added |
| `F5_REPORT.md` §8 F5-R5 | "not attempted — the workspace is not a repository" | **re-stated in full** |

**A5-6 — F5-R5 restated.** The premise is now false, so the row no longer
reads as a live assessment. The *verdict does not move*: the repository's
history begins at the A6 commit and the sub-repository carries no `.git` of its
own, so the `N = 400` merge recorded in `GW_STATUS_2026-09-26.md` still cannot
be inspected here. Closing it needs the upstream history, which is A7 scope.
The three older sites were annotated rather than rewritten — they are phase
records and rewriting them would falsify the record of what each phase knew.

---

## 4. Sweep 3 — does anything exist that the corpus says exists

A throwaway audit (kept out of the workspace, so it could not perturb the
manifest it was auditing) checked three things over the root Markdown corpus:
relative links, backtick-quoted filenames, and the coverage of `Brain.MD`'s
file map.

- **Relative links:** 3 present, **0 dead**.
- **Root files never named in any document:** 0 before the fixes.
- **Backtick filenames with no file behind them:** 31 raw hits, of which the
  large majority are command lines (`python suite_check.py`), filenames that
  deliberately describe an absence (`Framework.md`, `opencode.jsonc`), external
  paths (`shp_mcp_bridge_v4.py`), or headings inside other files
  (`CMB_INFORMATION_ANALYSIS.md`, correctly reported by `F2_REPORT.md` §1 as
  not existing). **One was a genuine defect.**

**A5-7 — three artefacts that were never there.**
`F4_REPORT.md` §3 *Artefacts* carried the row
*"`f4_survey1.py`, `f4_survey2.py`, `f4_coverage_dry.py` | corpus survey
(harnesses/)"*. None of the three exists anywhere in the workspace — not in
`harnesses\`, not at the root, not in a sub-repository. They were one-off
survey tools run during F4 and never committed.

The row has been **removed rather than annotated**, because a table headed
*Artefacts* is a claim about what is on disk, and a claim about what is on disk
cannot be satisfied by a note. An `A5 correction` note records what the row
used to say, what the scripts were, and that the corpus counts they produced
appear exactly once, in the §2 transcript, as a scan summary no gate reads.

The same note covers `f4_hits.json`, named in that transcript: a console dump,
not a shipped file.

**A5-8 — the knowledge map had fallen behind the tree.**
`Brain.MD` is described, in `AGENTS.md`, as the knowledge map of every file in
the workspace. The four files A6 added — `LICENSING.md`, `LICENSE`,
`.gitignore`, `.gitattributes` — were in none of its sections. Nothing failed.
Four rows were added to §1, each stating what the file is *for* rather than
that it exists.

---

## 5. What the audit did **not** find

Recorded because a clean result is only evidence if the search is described:

- **Encoding:** 216 files report CR/BOM/invalid-UTF-8. Every one of them is
  inside `BootLoops-ai/`, which `.gitignore` excludes and `checksum_check.py`
  therefore never scans. Out of scope, unchanged.
- **Orphan root files:** none.
- **Dead relative links:** none.
- **`F5-R4`, `F2` §8.2, `F1` §5 residual:** recorded-not-closed before this
  phase and still recorded-not-closed; A5 did not close them and does not
  claim to.
- **`F4_REPORT.md` §9 R1:** *partially answered by F5-2* remains accurate. The
  remainder — where the archive lives and under what licence — is **A7 scope**,
  not A5.

---

## 6. Gate changes, and the proof of each

All three additions are inside `report_claim_check.py`; no gate was added to or
removed from `suite_check.py`, so the suite count is unchanged.

| rule | what it now reads | defect that revealed the gap |
|---|---|---|
| **C1 spelled** | cardinal words in `Skill.md`/`Brain.MD` must equal the live value, **with no date allowed** | A5-1 |
| **P5 spelled** | cardinal words in any root `.md` must equal the live value unless a date, phase tag or "then" sits within one line | A5-2, A5-4 |
| **P6 row** | a backtick `.py` on a line whose column says `harnesses/` must resolve to a file | A5-7 |
| **P8 map** | every file at the workspace root must be named in `Brain.MD` | A5-8 |

Two design points worth stating, because both were chosen after the first
attempt failed:

- **Cardinal, not just any number-word.** `(all|the) <word> gates` is the
  claim form. *"pass three gates"*, *"of two gates"* and *"across six gates"*
  count something else, and the determiner is what separates them. Ordinals
  stay with the ordinal rule, which already knows the difference between *the
  twelfth gate* and *a second harness*.
- **C1 has no anchor; P5 does.** The constitution states today's numbers. A
  report may carry dated history. Giving `Brain.MD` the same escape hatch as a
  phase report would have let A5-1 pass.

### 6.1 Proof

`harnesses/a3_report_inj.py` grew from six cases to **ten**, two for each rule
added in this phase:

| case | defect applied | must print |
|---|---|---|
| `SKILL_GATES` | suite count raised by one | `SKILL_GATES` |
| `BRAIN_FOLDER` | harness count raised by one | `BRAIN_FOLDER` |
| `SKILL_ENTRY` | entry ordinal raised by one | `SKILL_ENTRY` |
| `P5` | unanchored stale digit tally in `F4_REPORT.md` | `P5 F4_REPORT.md` |
| `P6` | citation of a harness that does not exist | `P6 reports name harnesses` |
| `P4` | a second `Brain.MD` version string | `P4 Brain.MD declares` |
| `SPOKEN_BRAIN_GATES` | *fourteen* rewritten to *fifteen* in the constitution | `SPOKEN_BRAIN_GATES` |
| `P5 spoken` | an unanchored stale cardinal appended to `F4_REPORT.md` | `harness count=` |
| `P6 row` | a ghost `.py` behind a `(harnesses/)` column | `P6 F4_REPORT.md` |
| `P8` | a root file's only mention in `Brain.MD` renamed away | `P8 Brain.MD does not name` |

Every count in the harness is derived from `suite_check.GATES` and
`harness_check.HARNESSES` at run time rather than written into the file, so the
harness does not rot when the rig grows. Result: **10/10 cases caught, baseline
and restored baseline both exit 0, every target byte-identical.**

---

## 7. Verification matrix

| check | command | result |
|---|---|---|
| report-claim gate | `python report_claim_check.py` | PASS, exit 0 — 50 numeric claims across 19 documents, C1/P3/P4/P5/P6/P7/P8 green |
| injection proof | `python harnesses\a3_report_inj.py` | **10/10** caught, both baselines exit 0 |
| harness rig | `python harness_check.py` | **21/21** behaved as expected, workspace byte-identical |
| manifest | `python checksum_check.py` | rows updated and re-verified at the count printed in `Brain.MD` |
| encoding | byte inspection of every edited file | `CR = 0`, `BOM = False`, `endLF = True` |
| full suite | `python suite_check.py --with-harness` | every gate returned 0 |
| anti-circularity | `gate.py` over the final artefacts | run last, after the last edit |

---

## 8. Residuals

| id | item | state |
|---|---|---|
| F6-R1 | the upstream `GW_STATUS` history needed to close F5-R5 | **CLOSED 2026-10-06 (A7).** The upstream repository was located from `guinand-weil-rigorous-numerics-main/CITATION.cff` L16 and cloned; every clause of `GW_STATUS_2026-09-26.md` L1682 was checked against the real history and holds at `bfa40dc`. `F5-R5` moved from NOT ESTABLISHED to ESTABLISHED, with the scope that `d70f6fa` later superseded the file. See `F7_REPORT.md` §5 |
| F6-R2 | `F4_REPORT.md` §9 R1 remainder: where the archive lives and under what licence | **CLOSED 2026-10-06 (A7).** The storage and licensing decision is taken and written down in `REFERENCES.md` §1 "Archive policy decision (A7, 2026-10-06)": archive what a redistribution permission allows, keep record-only for the rest, record failures as failures. `F4_REPORT.md` §9 R1 rewritten accordingly (its old "two identifiers returned 404, so those are layer C" sentence was already false when F5-2 finished); one snapshot added, one layer-C record re-fetched and moved to layer B, two re-tried and unchanged. Tally now 23 records, A = 9, B = 12, C = 2. See `F7_REPORT.md` §4 |
| F6-R3 | 216 encoding findings inside `BootLoops-ai/` | recorded, out of scope: the folder is gitignored and never scanned |
| F6-R4 | `F5-R4` (sub-repository encoding sweep), `F2` §8.2, `F1` §5 | still recorded-not-closed; unchanged by A5 |
| F6-R5 | sweep 1 pattern set covers cardinal + ordinal + digit forms of *gates / harnesses / rows / entries / versions* | **CLOSED 2026-10-06 (A9).** Seven classes that this gate used to read past are now read and injection-proven: the keyed header (`suite= / harnesses= / manifest= / brain=`), `=`-glued digits no longer mis-bind as bare counts, `tally_object` classifies from the claim's own line before the ±3 window (so `suite_check.py --with-harness` is an entry count, not a harness count), spelled `entries`, ordinals past `twentieth` (generated to `ninetieth`), `N-gate` / `N-harness` compounds and `x of y` pairs, and spelled manifest rows without a determiner. See `harnesses/a9_drift_inj.py` and `F8_REPORT.md` |

---

## 9. What F7 (A7) inherits

*Status after A7 (2026-10-06): both items below were received open and are now
closed in `F7_REPORT.md`; the rest of this list is unchanged.*

- F6-R1 and F6-R2, both about **where things are kept and under what terms** —
  received open, **closed by A7** (upstream history fetched; archive policy
  written into `REFERENCES.md` §1).
- The `REFERENCES.md` URL layer, which A5 deliberately did not disturb — A7
  re-checked every URL it could re-fetch and recorded the outcomes without
  changing a single identifier.
