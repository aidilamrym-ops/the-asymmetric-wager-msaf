# F5_REPORT — Hardening and Re-Proof of the F3/F4 Boundary Gates

**Workspace:** `D:\THE ASYMMETRIC WAGER` (MSAF corpus, DOI `10.5281/zenodo.22791556`)
**Date:** 2026-10-05
**Status:** F5-1, F5-2, F5-3, F5-4, F5-5 executed and proven.
**Language rule:** this document is English; $P_{\text{narrative}} = 0$.

---

## 0. Why F5 exists

F4 closed with an honest register: four residuals, and a `F3` residual table
carrying R3, R4, R6 and R7. None of them were *wrong* — they were **known
gaps**. The purpose of F5 was not to add claims but to close those gaps and
then **prove each closure**, because a residual marked CLOSED without a
harness that fails when the closure is undone is not closed, it is decorated.

The five sub-tasks were chosen by the operator as a set: the test rig (F5-5),
the pending remediation (F5-1), the archive honesty problem (F5-2), the marker
phase (F5-3), and the tolerance defect (F5-4).

---

## 1. Method

Everything in F5 followed the same order, and no step was reported before the
step that proves it:

1. **Map before edit.** Needle lines, anchors and readers were enumerated
   *before* a single byte moved.
2. **Assert the premise before writing.** Every edit script refuses to run
   when its expected pattern is absent or present the wrong number of times.
   An edit that "usually works" is not an edit.
3. **Fail first, then pass.** Each new gate condition was run against the
   un-fixed corpus and had to fail with the exact count the defect predicts.
   Only then was the corpus fixed.
4. **One file per iteration.** Documents were edited one at a time with the
   affected gates re-run after each, so a broken anchor is attributed to the
   edit that broke it.
5. **Injection proves detection.** No condition is claimed as enforced unless
   a mutant was written for it, caught by it, and restored byte-identically.
6. **Anti-Circularity Gate last.** Run after the last edit, never before.

---

## 2. F5-5 — the rig itself (`suite_check.py`)

Eleven root gates were runnable individually but there was no single command
that runs them in order and reports honestly when one was skipped.

| property | value |
|---|---|
| file | `suite_check.py`, 8139 bytes, sha256 `06566635f9e09a08…` |
| gates | 11 at F5-5, fixed order, sequential (never parallel); 12 since 2026-10-05 — see the note below |
| switches | `--list`, `--only NAME`, `--fast`, `--selftest` |
| exit codes | 0 = all ran and passed, 1 = at least one failed, 2 = at least one not run |
| `--fast` | skips `gw_final_gate.py` (~22 min) and reports it `NOTRUN` |

`--fast` prints `SUITE: INCOMPLETE` and returns **2**. It is therefore
impossible to cite `--fast` as a full pass: the exit code refuses it. This is
the same shape as every other gate here — the honest answer is encoded in the
return value, not in a comment.

**Proof:** `selftest` green; `--list` enumerates all 11.

> **Amendment, 2026-10-05 (A2).** The eleven gates above are what F5-5
> built and what F5 proved; that record is left unchanged. `checksum_check.py`
> was added afterwards as a twelfth gate, registered to close
> F0 residual 4 and F5-R6. Running it last turns `CHECKSUM.sha256` from a
> baseline snapshot into a mutation detector across the whole run: any gate
> that had written a tracked file would surface there instead of being
> silently absorbed. `--with-harness` therefore folds the harness runner in
> as a thirteenth entry (2026-10-05, A2).
>
> **Amendment, 2026-10-06 (A1).** `protocol_09_check.py` — the gate that
> machine-proves the encoding of $\Phi$ — was registered ahead of the manifest
> gate, so `checksum_check.py` keeps its place as the **last** entry while the
> suite itself grew. Current state: `--list` enumerates 13, and
> `--with-harness` folds in a fourteenth.

---

## 3. F5-1 — the Planck-length site (F3-R4)

`01_PARADOX_AND_SCALE.md` carried `1.63 \times 10^{-35}` where the register's
authoritative value rounds to `1.62`. F3 declared this and left it open.

* Both sites corrected; register site moved from `declared_variance` to
  `source_agree` with `doc_value 1.62e-35`.
* `REFERENCES.md` and `F3_REPORT.md` R4 → **CLOSED 2026-10-05 (F5-1)**.
* Probe `f5_1_stageb.py`, stages B1–B4:

```
ok    B4 BOTH reverted (exact pre-F5-1 state)   exit=1, reported by P4
       FAIL  P4  SITE_VALUE: PLANCK_LENGTH#1 doc_value 1.63e-35 disagrees
                 with the authoritative value 1.616255e-35 at 3 s.f.
ok    baseline after restore exit=0
STAGE B: PASS -- every revert is caught, baseline intact, files byte-identical
```

Reverting **either** side fails P3/P4. The fix is therefore not cosmetic: the
document and the register are now bound to each other.

---

## 4. F5-2 — layered evidence (F3-R3 and the archive's blind spot)

### 4.1 The blind spot

`theorem_provenance_check.py` P4 validates that an identifier **looks** like
an arXiv id, a DOI or a URL. It never asks whether the thing is *reachable*,
and never asks what licence permits keeping a copy. Two independent probes
showed how far that is from the truth:

| identifier | as registered | reality |
|---|---|---|
| T001 SEP | `.../entries/zeno-paradox/` | **HTTP 404** — correct path is `/entries/paradox-zeno/` |
| `10.1007/s40993-024-00556-x` | "Springer, open" | **HTTP 404** — the real DOI is `10.1007/s40993-023-00498-y` (CC BY 4.0) |
| `.../ENTRiES/goedel-incompleteness` | typo | alive only by accident; normalised |
| `.../jdnorton/.../measure.html` | cited as source | **TLS chain incomplete** — cannot be fetched here |
| `doi:10.1098/rspa.1970.0021` (Royal Society) | cited as source | **HTTP 403** |
| `10.1051/0004-6361/201833910` (EDP) | cited as source | **HTTP 403** |

A citation that 404s is worse than no citation: it looks verified.

### 4.2 Three layers, decided by evidence

Licence was **read**, never assumed. Every record's layer follows from a
string actually found in the retrieved document:

* **Layer A** — content archived here, licence found permitting retention.
  NIST: public domain under 17 U.S.C. 105, per
  `https://www.nist.gov/nist-research-library/library-faqs`.
* **Layer B** — authority identified, licence **not** confirmed, no content
  kept (SEP is copyrighted with no general redistribution grant).
* **Layer C** — the canonical target is unreachable from this machine
  (HTTP 403 or TLS failure). Recorded as inaccessible rather than implied.

Final archive, 22 records: **A = 8, B = 11, C = 3**
(`theorem_provenance.json` 15 → A4/B9/C2; `external_constants.json` 7 →
A4/B2/C1).

### 4.3 What was stored

Eight Layer-A files in `provenance/evidence/`:

| file | bytes | sha256 (head) |
|---|---:|---|
| `arxiv_1807_06209_abs.html` | 78846 | `a8f46f86ddaea582…` |
| `arxiv_2004_09765_abs.html` | 39398 | `c137519d02a5cbf7…` |
| `arxiv_2410_17036_abs.html` | 80834 | `3cfd55774be0d393…` |
| `nist_allascii_2022.txt` | 40801 | `77fb90e66c40db3e…` |
| `springer_mty2024_open_access.html` | 508435 | `9e02c1c934e3e382…` |
| `wikipedia_countably_additive_measure.html` | 650480 | `ee981b8ab51d0b24…` |
| `wikipedia_ihara_zeta_function.html` | 118173 | `8b133039b9dca0a5…` |
| `wikipedia_ultraviolet_catastrophe.html` | 133784 | `763d430caeaee225…` |

### 4.4 F3-R3 closed by a reachable mirror

The canonical Planck 2018 VI DOI is **HTTP 403** here. Rather than pretend,
`PLANCK_2018_VI` is now layer **C** with
`observed: "HTTP 403 from the publisher host"`, and a new layer-A entry
`PLANCK_2018_VI_ARXIV` stores `arXiv:1807.06209` — the same article — which
`OBSERVABLE_UNIVERSE_DIAMETER.snapshot_evidence_id` points at. **F3-R3: CLOSED
2026-10-05 (F5-2).**

### 4.5 New checks

* `theorem_provenance_check.py` **P9 `ARCHIVE_CONSISTENCY`**: legal layers,
  layer↔access agreement, non-empty `licence_basis`, `retrieved_utc` shape,
  layer A ⇒ file exists with matching size and sha256, layer B/C ⇒ no
  `local_copy`, and two-way identifier binding (cited ↔ archived).
* `provenance_check.py` **P9 `LAYER_CONSISTENCY`**: the same for the F3
  register, plus snapshot resolution (a snapshot must be layer A) and
  `reference_facts[].source_id` resolution.

**Proof:** `f5_2_inj.py` — **20/20**. Cases: deleted snapshot, one flipped
byte, layer A relabelled to B and to C with access unchanged, illegal layer
value, licence-basis key removed, pointer to an unknown id, pointer to a
layer-C source, a layer B record claiming content, a quantity losing its
evidence pointer, an archived identifier no longer matching any citation, an
uncited record added, and the archive list deleted — each caught by its own
gate while the other gate stayed green, registers restored byte-identical.

---

## 5. F5-3 — Phase B markers (F3-R6)

### 5.1 Decision

R6 named a marker phase but **defined nothing**: no format, no binding, no
location. Rather than invent silently, the gap was reported and a design was
chosen on the record.

Markers bind to **`external_constants.json` evidence ids**, not to
`theorem_provenance.json` entries, because (a) the planned injections
(phantom / wrong id / missing entry) only have a register to be *wrong about*
on that side, (b) F4's `P3 COVERAGE` already owns borrowed-authority *lines*,
so a second marker there would duplicate it, and (c) the blast radius is three
documents, not fifteen.

### 5.2 Form and location

Eleven markers over **8 lines in 3 documents** — exactly the documents the
register's `sites[]` point at:

| document | marked lines | markers |
|---|---:|---|
| `Skill.md` | 3 (L35, L36, L37) | 4 |
| `01_PARADOX_AND_SCALE.md` | 3 (L18, L25, L29) | 6 |
| `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md` | 1 (L25) | 1 |

Each marker sits **inside an HTML comment at the end of its own line**, so the
rendered document is textually unchanged while the raw file carries the
binding. L29 of `01_PARADOX_AND_SCALE.md` carries both needles and therefore
all three markers.

### 5.3 Before editing: the two things that could have broken

1. **`P3 COVERAGE` is per-line and semantic.** Appending text can only *add*
   tags, never remove one — so the only danger was a marker matching an
   `EXTERNAL` rule. All three marker strings were compiled against all 21
   rules: **`NONE` match**. P3-safe by measurement, not by hope.
2. **Anchored readers.** `msaf_zeta_check` uses `re.match` from line start;
   `znone_check` splits on tab and indexes `[3]`; both tolerate an end-of-line
   append. Confirmed empirically after each of the three edits.

### 5.4 `P10 REF_MARKERS`

Three directions, plus a sweep:

* **RESOLVES** — a marker names an evidence id that exists.
* **REQUIRED** — every line carrying a site needle also carries its
  quantity's marker (and its snapshot's, when a snapshot is declared).
* **PLACED** — a marker sits on a line that really is such a site line.
* **stray sweep** — any marker in a root `.md` that no site points at fails.

**Fail first:** run against the un-marked corpus →
`FAIL P10 REF_MARKERS delta: 11 (markers seen: 0)`, `GATE: FAIL -- 11
condition(s) not met`, while **P1–P9 stayed green**. The "missing marker"
direction was therefore proven before any marker existed.

### 5.5 Proof

Insertion order was smallest file first, with the four reading gates re-run
after each edit — failures went **11 → 10 → 4 → 0** and no anchor ever moved.
The inserter is idempotent: re-running it on a marked file changes **0 bytes**.

`f5_3_inj.py` — **7/7**:

| case | mutant | caught by |
|---|---|---|
| C0, C1 | controls, no edit | both gates green |
| R1 | marker naming a non-existent evidence id | `P10 RESOLVES` |
| R2 | right id pasted onto the wrong line (ℓ_P row marked as $D_{\text{obs}}$) | `P10 PLACED` + `REQUIRED` |
| R3 | every marker stripped from one document | `P10 REQUIRED` |
| R4 | marker moved off its needle line | `P10 PLACED` |
| R5 | marker pasted into a document no site points at | `P10 stray` |

Every failing case was additionally required to fail **at P10 itself**
(`FAIL   P10  REF_MARKERS` in the output), not at some unrelated condition —
a gate that fails for the wrong reason is not a detection.

---

## 6. F5-4 — the P8 tolerance defect (F3-R7)

P8 required the evidence spelling to appear as a token, so `5.5590` failed
against `5.559` although they are equal, and any decimal-shifted spelling of a
large integer could slip past a substring test.

`provenance_check.py` now decodes both sides with `Decimal` and accepts an
**exact numerical equality fallback only after the exact-spelling test
fails**. Decimal never re-introduces the substring defect: `5.5590` passes,
`1038007883590` still fails against `103800788.359`.

**Proof:** `f5_4_inj.py` — **14/14** (3 acceptance cases A1–A3 that must pass,
9 regression cases F1–F9 of unequal values that must still fail, 2 controls),
restore byte-identical, both gates green at the end. Regression:
`f3_inj` 27/27, `f3_vacuity` 11/11 — H2a/H2b/H2c still caught. **F3-R7:
CLOSED 2026-10-05 (F5-4).**

Note the asymmetry: acceptance cases are asserted by *exit 0*, rejection cases
by *exit 1 plus the printed condition*. A test that only checks "it didn't
crash" proves nothing about a gate.

---

## 7. What the blind spots taught

These are the findings that were not in any plan and were found by trying to
prove things.

1. **A gate can be green forever against a dead URL.** P4 validated
   *syntax*. Both the SEP path and the Springer DOI were syntactically perfect
   and returned 404. Syntax validation and existence validation are different
   claims and were being conflated.
2. **"Open access" is not a licence.** The Springer DOI that 404'd was
   replaced by the real one; only there did `CC BY 4.0` actually appear in the
   retrieved document. Layer assignment had to wait for retrieval, never be
   written from a belief.
3. **HTTP 403 is not "gone".** The Planck DOI answers with 403 — reachable,
   blocked. Recording it as layer C *with the observed status* is a stronger
   claim than either archiving nothing or archiving a page we cannot fetch.
4. **Two registers, two vocabularies.** `theorem_provenance.json` round-trips
   safely through `json.load`/`dump` (verified byte-identical);
   `external_constants.json` does **not** — an inline array collapses.
   `internal_constants`-style edits must be textual or they will silently
   reformat someone else's file.
5. **Harness bugs are the real defect class.** Twelve distinct harness faults
   were hit and fixed while building F5; each one produced a *false* verdict,
   never a false alarm:

   | # | fault | wrong verdict it produced |
   |---|---|---|
   | 1 | wrote a file before reading it | destroyed the baseline under test |
   | 2 | JSON backslash patterns double-escaped | mutant never applied, "gate passed" |
   | 3 | `replace(old, new, 1)` on a repeated pattern | mutated the wrong occurrence |
   | 4 | `write()` returns an int, not a string | crashed inside `subprocess` |
   | 5 | assertion count combined with an idempotent re-run | doubled count, "mismatch" |
   | 6 | wrote the expected output from a guess | the expectation matched the bug |
   | 7 | dictionary lookup by id prefix | compared the wrong record |
   | 8 | no `try/finally` restore | one failed case poisoned the next |
   | 9 | tolerance `5e-7` instead of `5 * 10**-sf` | a vacuous comparison passed |
   | 10 | two file-writing harnesses run in parallel | both saw a half-written register |
   | 11 | forgot `+ "\n"` when testing a JSON round-trip | byte-compare failed on the newline, not the content |
   | 12 | `f4_build_register.py` still held the pre-F5-2 identifiers and knew nothing of `archive` | rebuild exited 0 with `uncovered=0` and **deleted all 15 archive records** — reported success while destroying the evidence layer |

   Rules 1, 6, 11 and 12 are the expensive ones: they do not fail loudly, they
   report **success**.
6. **`M11` had retired with the register.** `f3_inj.py` still carried a
   mutant keyed to `declared_variance`, which F5-1 removed. A harness that
   silently stops applying its mutants reports a perfect score over an empty
   set. The mutant was rewritten against the live field and the replacement
   is documented in the code.
7. **The runner's expectations are a second corpus to maintain.** Fase G
   added mutants M29 and M30 to `harnesses\f3_inj.py`, growing its reported
   total from `27/27` to `29/29`, but `harness_check.py` still pinned the
   string `HARNESS: PASS -- 27/27 mutants caught`. The harness was correct;
   the runner would have failed it. That is a **false alarm**, the opposite
   failure mode from the twelve above, and it is just as fatal to the claim
   *"exit 0 means every harness behaved"*, because a runner that cries wolf
   on a correct harness gets edited until it stops — which is how a stale
   expectation turns into a silent one. Caught by running
   `harness_check.py --only f3_inj.py` before quoting any harness total.
   The lesson generalises, and it bit twice in the same phase. A3 added the
   $k_B$ site marker, which moved P10's own `markers seen: 11` to `12`, and
   `harnesses\f5_3_inj.py` asserts that exact string as the precondition for
   running at all — so a *correct* growth in the register broke a harness
   that was testing something else entirely, and reported it as
   `BLOCKED: baseline not green or marker count wrong`. A count encoded
   anywhere, whether in a runner's expectation string or in a harness's
   baseline assertion, is a second place that must be updated when the
   register grows. Both of these failed loudly, which is the good outcome;
   the failure mode to fear is the loud one being edited until it stops
   complaining, and the quiet one never being noticed at all.
8. **Report prose is inside the parser's reach.** `F3_REPORT.md` and
   `F5_REPORT.md` closed their $k_B$ rows by quoting the Phase B marker
   *together with the square brackets that delimit it*. P10's stray sweep
   reads every root-level `.md` that is not a site, so the quotation was
   indistinguishable from a marker pasted into the wrong document and the
   gate reported `markers seen: 14, stray: 2`. The guard behaved exactly as
   designed on a real violation; the fix was in the prose (drop the
   brackets), not in the rule. A syntax reserved for placements cannot be
   used decoratively anywhere the parser can see — which is why this
   paragraph describes the brackets instead of containing any.

---

## 8. Residual

| # | item | state |
|---|---|---|
| F5-R1 | $k_B$ in the register (was F3-R5) | **CLOSED 2026-10-05 (A3)** — `BOLTZMANN_CONSTANT` is now a register entry: site `SOLVABLE_FINITE_PARADOX.md` L83 with the `REF-NIST_CODATA_2022_TABLE` marker, probe against NIST L62, heading in `REFERENCES.md`. `landauer_check.py` remains the gate of record for the Landauer arithmetic; the register covers a different question — where $k_B$ is quoted and whether that matches the archive |
| F5-R2 | independent authority check for a measured `value` at declared precision (was F3-R8) | **CLOSED 2026-10-05 (B1-a)** — P6 makes the tie mandatory instead of opt-in: a non-derived quantity citing archived evidence must declare `evidence_probe` and pass it, one citing unarchived evidence must state a non-empty `probe_waived` reason, and silence is now a FAIL. `harnesses\f3_inj.py` M29 (probe removed from `PLANCK_LENGTH`) and M30 (waiver removed from `OBSERVABLE_UNIVERSE_DIAMETER`) both trip P6; 29/29 mutants, 3/3 controls |
| F5-R3 | F4-R2 (borrowed-authority marker coverage across the F4 scope) | **open — decided 2026-10-05 (B2-b): status quo retained.** The gap is bounded by measurement rather than closed by a pattern list: `harnesses\f4_brittleness.py` reports 0/60 tested paraphrases escaping (25/60 escaped before F4-I; the audit itself read 35/60 caught). A citation-key convention would close the class but requires editing all 15 scope documents and re-verifying the P2 anchors, P3 counts, the F4 markers and the full suite; rejected for now on that radius |
| F5-R4 | encoding sweep of `guinand-weil-rigorous-numerics-main/` | deferred — the sub-repo is outside F5's scope |
| F5-R5 | `.git` "stayed in HEAD" | not attempted — the workspace is not a repository |
| F5-R6 | `CHECKSUM.sha256` covers the sub-repo only (116 rows) and does not track root-level files | **CLOSED 2026-10-05 (A2)** — `checksum_check.py` writes and verifies a workspace-root `CHECKSUM.sha256` over the root files plus `provenance/` (8) and `harnesses/` — 61 rows at A2, **65 since A1** (43 root + 8 + 14) — manifest excluded from its own hash, sub-repositories excluded on purpose because they are third-party or already self-pinned. Verified **65/65** as of 2026-10-06 (61/61 at A2); a tampered file and an unlisted `.bak` are both reported. **71 since the A2 F2 harness rebuild** (43 root + 8 + 20), verified 71/71 — the row count moves only when a listed file is added, which is the point of the manifest. Registered as the twelfth gate of `suite_check.py` and, since A1 inserted `protocol_09_check.py` ahead of it, as the **thirteenth and last**, so it re-hashes after every other gate has run and turns the manifest into a mutation detector rather than a snapshot. A missing manifest exits 2, never 0 |

---

## 9. Verification matrix

| check | command | result |
|---|---|---|
| **suite, full** | `python suite_check.py` | `passed=11 failed=0 not_run=0 of 11` as of F5 (2026-10-05), `SUITE: PASS -- every listed gate returned 0`, **exit 0**, 1607 s — includes `gw_final_gate.py` (1211 s) and `gw_mont_pipeline_check.py` (387 s) |
| rig, partial | `python suite_check.py --fast` | `passed=10 failed=0 not_run=1 of 11` as of F5 (2026-10-05), **exit 2** (never 0 — `--fast` cannot be quoted as a pass) |
| snapshots | sha256 + size vs both registers | **8 of 8** Layer-A files match (4 in `external_constants.json`, 4 in `theorem_provenance.json`), 0 problems |
| F3 gate | `python provenance_check.py` | exit **0**, `GATE: PASS -- 4 quantities, 7 evidence snapshots, 5 reference facts, 10 conditions` |
| F4 gate | `python theorem_provenance_check.py` | exit **0**, P1…P9 including `ARCHIVE_CONSISTENCY` |
| F5-1 probe | `harnesses\f5_1_stageb.py` | `STAGE B: PASS`, B1–B4 all caught, baseline exit 0 |
| F5-2 injection | `harnesses\f5_2_inj.py` | **20/20**, registers byte-identical, both gates green |
| F5-3 injection | `harnesses\f5_3_inj.py` | **7/7**, documents byte-identical, both gates green, every failure at `P10` |
| F5-4 injection | `harnesses\f5_4_inj.py` | **14/14**, restore byte-identical |
| F3 mutants | `harnesses\f3_inj.py` | **27/27** + 3 controls |
| F3 vacuity | `harnesses\f3_vacuity.py` | **11/11**, 0 FALSE-PASS, 0 CRASH |
| F3 schema | `harnesses\f3_a1.py` | **5/5** caught |
| F4 mutants | `harnesses\f4_inj.py` | **31** mutants + 4 controls |
| F4 paraphrase | `harnesses\f4_brittleness.py` | 21 patterns × 60 variants, **clean** |
| markers | byte inspection | `markers seen: 11, stray: 0`, 8 lines, 3 documents, `CR = 0`, no BOM; idempotent re-run = 0 bytes |
| encoding | byte inspection on every file written in F5 | `CR = 0`, `BOM = False`, UTF-8 strict |
| **harness suite, full** | `python harness_check.py` | `passed=13 failed=0 not_run=0 of 13` as of F5 (2026-10-05), `HARNESS: PASS -- 13/13 behaved as expected, workspace byte-identical`, **exit 0** |
| harness rig, partial | `python harness_check.py --fast` | 5 multi-second suites reported `NOT RUN`, **exit 2** (never 0) |
| harness rig, self-test | `python harness_check.py --selftest` | **13/13**, exit 0 — a silent harness, a wrong exit code, a file left behind and a missing file all still fail |
| builder rebuild | `python harnesses\f4_build_register.py` | register rebuilt **byte-identical** (39750 B, `sha256 7dc524cf…`), `archive=kept 15`, `uncovered=0` |
| harness location | sha256 of source vs copy | **13/13 byte-identical**, 112977 B, `CR = 0`, `BOM = False` |
| suite + harnesses | `python suite_check.py --with-harness` | 12 entries as of F5 (2026-10-05), `--fast` forwarded to the harness runner |

> **Amendment, 2026-10-06 (A1).** The rows above are F5's own record and are
> left as they stood. Two things grew afterwards: `protocol_09_check.py`
> joined the suite as the twelfth gate (2026-10-06, A1) and
> `harnesses\p09_inj.py` joined the harness rig as the fourteenth proof
> harness, taking `harness_check.py` to `passed=14` as of 2026-10-06 (A1).
>
> **Amendment, 2026-10-06 (A3).** `report_claim_check.py` joined the suite as
> the fourteenth gate, so `--with-harness` now enumerates 15 entries, and
> `harnesses\a3_report_inj.py` took `harness_check.py` to `passed=21`.

---

## 10. Definition of done

| requirement | state |
|---|---|
| suite 11/11 exit 0 | **yes** — `passed=11 failed=0 not_run=0 of 11` as of F5 (2026-10-05), exit 0, run as the final act of F5 |
| F3 and F4 gates exit 0 | yes — 10 conditions, P1…P9 |
| every sub-task has an injection that **fails** | F5-1 B1–B4, F5-2 20/20, F5-3 7/7, F5-4 14/14, F5-5 `--fast` exit 2 |
| encoding 0 problems | yes |
| report + `Brain.MD` in sync | `Brain.MD` at v1.7 |
| harnesses citable from the workspace | yes — `harnesses\` holds all 13 byte-identical to the files the reports cited, and `harness_check.py` runs them from there |
| Anti-Circularity Gate last | run after the final edit, before this file was declared complete |

F5 introduces no `.lean` or `.smt2` claim; the gate is run to confirm that no
placeholder or comment-only claim entered the corpus while these files were
being written.

---

## 11. Addendum — harnesses moved into the workspace

The F5 reports cited the injection harnesses by a path outside the workspace
(`TEMP\opencode\…`), which meant the evidence could not be re-run from
anything the corpus itself owns: a reviewer with the workspace had the results
but not the instrument. The harnesses are now checked in.

**What moved.** Thirteen files to `harnesses\`, copied byte-identical and
verified `sha256` 13/13 (112977 B): `f1_mut`, `f3_inj`, `f3_vacuity`,
`f3_a1`, `f4_inj`, `f4_brittleness`, `f4_build_register`,
`f5_1_stagea`/`stageb`/`stagec`, `f5_2_inj`, `f5_3_inj`, `f5_4_inj`. Not one
byte of harness code was edited in the move — every one of them resolves the
workspace by an absolute path rather than by `__file__`, so the results the
reports cite travel with the file. Nineteen citations across `F3_REPORT`,
`F4_REPORT`, `F5_REPORT` and `Brain.MD` were rewritten to match; `F4_REPORT`
and `Brain.MD` had to be reworded rather than substituted, because their
commands used `$env:TEMP\opencode\…` and a blind replace would have produced
`$env:harnesses\…`.

Three of the thirteen (`f1_mut`, `f3_vacuity`, `f3_a1`) arrived carrying a
UTF-8 BOM and a single CRLF on their final line — everything else was already
LF. That violates the encoding invariant the corpus enforces on every write,
so both sides were normalized together: source and copy remain byte-identical
to each other, the *code* is untouched (the rewrite was proved equal to the
original minus the BOM and CR bytes), and all three were re-run afterwards
with unchanged output — `f1_mut` 19/19, `f3_vacuity` 11 probes with 0
FALSE-PASS, `f3_a1` `rc=0 restored=True`. The folder now reads `CR = 0`,
`BOM = False` throughout.

**What runs them.** `harness_check.py` executes the thirteen sequentially —
never parallel, per fault 10 — and requires two things of each: the exit code
it is expected to produce, and the sentence it is expected to print. Exit 0
alone is not a pass. It hashes the workspace before and after every harness,
so a byte that does not come back, a file that disappears, or a file that
appears is a failure regardless of what the harness printed. `--selftest`
exercises all of those paths against fixtures; `suite_check.py
--with-harness` folds the runner in as a fifteenth entry, off by default
because the fourteen gates are read-only and the harnesses are not.

Two of the twenty-one are **one-shot migrations**, not verifiers.
`f5_1_stagea.py` and `f5_1_stagec.py` assert the *pre*-F5-1 text still exists
and rewrite it; since F5-1 already applied them, they must now refuse, exit 1,
and change nothing. Encoding that as the expected outcome turns them into a
revert detector: roll the corpus back and they start succeeding, which the
runner reports as a difference.

**What the move found.** Running `f4_build_register.py` to time it destroyed
`theorem_provenance.json` — it exited 0 with `uncovered=0` while deleting all
15 `archive` records, because it still held the four SEP identifiers that F5-2
corrected and had never heard of the archive section. This is fault 12 in
§7: a harness reporting success while corrupting the thing under test. The
builder now carries `archive` over from the register it rebuilds and carries
the corrected identifiers, so a rebuild is byte-identical to the committed
file — which is what F4 §10 step 1 claims and what had silently stopped being
true. The register was restored from a byte-identical copy and the damage was
confirmed to be exactly one file before any of this was re-proven.
