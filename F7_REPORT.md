# F7_REPORT.md — Archive policy and upstream history (Fase A7)

**Date:** 2026-10-06
**Phase:** A7
**Inherits:** `F6_REPORT.md` §9 — *What F7 (A7) inherits*
**Closes:** `F6-R1`, `F6-R2`, `F5-R5`, `F4_REPORT.md` §9 R1 (remainder)

---

## 1. Mandate

Fase A5 ended with two residuals explicitly handed to A7, and one older residual
that only A7 could touch:

| id | item | why it needed this phase |
|---|---|---|
| `F6-R1` | the upstream `GW_STATUS` history needed to close `F5-R5` | closing it needs the history of a repository that is not this one |
| `F6-R2` | `F4_REPORT.md` §9 R1 remainder: where the archive lives and under what licence | closing it is a decision, and a decision nobody wrote down does not stay closed |
| `F5-R5` | the `GW_STATUS` sentence: *"$N=400$ certificate stayed in HEAD"* | unverifiable while this tree had no `.git` |

Two working principles governed the phase, both of them the kind of thing that
goes wrong quietly:

1. **Observe the status, do not assume it.** Every fetch in §3 was performed
   twice — once while probing, once while re-verifying for this report — and the
   status written into the register is the status that came back.
2. **Read the licence out of the document, not out of the domain.** `arxiv.org`
   does not make an arXiv page redistributable; the page's own licence link does.
   `plato.stanford.edu` does not make a Stanford page open access; `info.html`
   does not.

---

## 2. Method

1. Re-fetch every URL the two registers can still reach and record the observed
   status, final URL and byte count (§3).
2. For each source, read the licence text out of the retrieved document and
   assign or confirm the layer: **A** body kept, **B** record only, **C**
   failure recorded (§4).
3. Locate the upstream repository, clone it in full, and check every clause of
   `GW_STATUS_2026-09-26.md` L1682 against the real history (§5).
4. Diff this workspace's sub-repository against upstream HEAD, file by file and
   byte by byte (§5.4).
5. Rewrite every prose statement that steps 3 and 4 falsify, rather than leaving
   them to be found by a later reader (§7).
6. Re-run the register gates, the archive harness, the manifest, the harness rig
   and the full suite; run the Anti-Circularity Gate last (§6).

---

## 3. What was re-fetched on 2026-10-06

Status and byte counts below were observed **twice**, on the initial probe and
again on the re-verification pass for this report.

| source | URL | status | bytes | licence read out of the document | action |
|---|---|---|---|---|---|
| Mossinghoff–Trudgian preprint | `https://arxiv.org/abs/1410.3926` | **200** | 39360 | `<div class="abs-license"><a href="http://arxiv.org/licenses/nonexclusive-distrib/1.0/" …>view license</a></div>` | **layer A, snapshot added** |
| SEP copyright policy | `https://plato.stanford.edu/info.html` | **200** | 30116 | *"All rights are reserved … other than for purposes of fair use, without written permission from the copyright holder"* — no Creative Commons grant anywhere on the page | layer **B confirmed**, `license_basis_url` recorded |
| SEP Zeno entry | `https://plato.stanford.edu/entries/paradox-zeno/` | **200** | 97054 | governed by `info.html` above | layer **B confirmed** |
| Pitt, *Measure and probability* | `https://sites.pitt.edu/~jdnorton/teaching/paradox/chapters/measure/measure.html` | **200** | 47086 | `<span …>Copyright, John D. Norton</span>` — nothing else | **layer C → B** |
| Hawking–Penrose 1970 | `https://doi.org/10.1098/rspa.1970.0021` | **403** | — | not reached; `royalsocietypublishing.org` answers a Cloudflare challenge | layer **C confirmed** |
| Planck 2018 VI | `https://doi.org/10.1051/0004-6361/201833910` | **403** | — | not reached; `aanda.org` answers a DataDome challenge | layer **C confirmed** |
| Mossinghoff–Trudgian–Yang 2024 | `https://doi.org/10.1007/s40993-023-00498-y` | **200** | — | CC BY 4.0, already recorded by F5-2 | layer **A confirmed** |
| Platt 2017 author manuscript | `https://research-information.bris.ac.uk/…/78836669/platt_zeta_submitted.pdf` | **200** | 497822 | licence field reads *Unspecified* | layer **B confirmed**, copy discarded |

Two of these results are *corrections of earlier records* and two are
*confirmations of records already correct*; §4 says which is which, because a
phase that only reports its successes hides the ones it checked and did not
change.

**The Pitt record was the one genuinely wrong entry.** It had been filed as
layer C on 2026-10-05 because the fetch failed on an incomplete TLS chain. A
failure to connect is not a property of the source: the page answers HTTP 200
today. It is now layer B, with both dates and both observations written into
`theorem_provenance.json` — the old failure is recorded in the `observed` field
rather than deleted, so the history of the record survives the correction.

---

## 4. The storage and licensing decision (`F6-R2`, `F4_REPORT.md` §9 R1)

### 4.1 What was undecided

`F4_REPORT.md` §9 R1 closed *partially* at F5-2 and left this sentence standing:

> "…archiving the remainder in full is a storage and licensing decision rather
> than a code change."

A residual phrased as a decision is a residual nobody is obliged to pick up. A7
took it, and wrote it where a later reader cannot miss it — `REFERENCES.md` §1,
heading **Archive policy decision (A7, 2026-10-06)**:

* **Archive** a source only when a redistribution permission was actually read
  out of the retrieved document (public domain, CC BY / CC BY-SA /
  CC BY-NC-SA, or the arXiv distribution licence). That is the whole of layer
  **A**, and every layer-A file is hash-verified by `provenance_check.py` P2 or
  `theorem_provenance_check.py` P9 on each run.
* **Do not archive** a source whose landing page states no redistribution
  permission. The bibliographic record, the retrieval date and the observed
  status are kept and the body is discarded. That is layer **B**, and after A7
  it is a recorded decision rather than an unfinished task.
* **Record** a source that cannot be retrieved at all, with the failure that was
  observed, instead of implying it was read. That is layer **C**.

### 4.2 What was executed

| change | evidence |
|---|---|
| **one snapshot added** | `provenance/evidence/arxiv_1410_3926_abs.html`, 39360 bytes, SHA-256 `dff8840502d028d597f1ab9ab2c59f12cd5609eaba4601e8c968e599a6522419`, `CR = 0`, no BOM, last byte `>` — registered in `external_constants.json` as `MOSSINGHOFF_TRUDGIAN_2015_ARXIV`, layer A, `mirror_of: MOSSINGHOFF_TRUDGIAN_2015` |
| **one record moved C → B** | Pitt `measure.html`: `access_class` `inaccessible` → `publisher_landing_page`, `observed_status` → 200, `retrieved_utc` → 2026-10-06, `license_basis` → *"no redistribution licence identified; body not archived"* |
| **three records re-read, unchanged** | SEP `goedel`, `intuitionism`, `zeno`: `license_basis_url` → `https://plato.stanford.edu/info.html` (the page that actually carries the terms) |
| **two records re-tried, unchanged** | Planck DOI and `doi:10.1098/rspa.1970.0021` re-fetched with a browser user agent, both HTTP 403, both still layer C; the retry is written into the `note` field, the original `observed` string is left alone |
| **one record re-checked, unchanged** | `PLATT_2017`: a Bristol author manuscript exists but its licence field is *Unspecified*, which is not a permission |
| **one harness retargeted** | `harnesses/f5_2_inj.py` mutants G4 and G6 pointed at the Pitt record; that record is now layer B with a non-empty `license_basis`, so they were re-pointed at `doi:10.1098/rspa.1970.0021`, the record whose properties they test. Result unchanged: `HARNESS: PASS -- 20/20 cases behaved as expected, registers byte-identical, both gates green at the end` |

### 4.3 Tally

| | at F5-2 (2026-10-05) | at A7 (2026-10-06) |
|---|---|---|
| records | 22 | **23** |
| layer A | 8 | **9** |
| layer B | 11 | **12** |
| layer C | 3 | **2** |

### 4.4 Two counts that are both right and are not the same count

This is the sort of near-collision that produces a false correction later, so it
is stated once, here.

* `provenance_check.py` prints **`N evidence snapshots`**, and `N` is
  `len(evidence)` in `external_constants.json` — a count of *register records*,
  layer A, B and C together. It read 7 before A7 and reads 8 now.
* The count of **hashed layer-A files actually on disk** under
  `provenance/evidence/` is a different quantity: 4 from `external_constants.json`
  plus 4 from `theorem_provenance.json` made 8 at F5-2, and the ninth was added
  by A7.

Both numbers are live, both are correct, and neither is a restatement of the
other. `F5_REPORT.md` §9 and `F3_REPORT.md` §9 quote the gate's own output and
are therefore about the first quantity.

---

## 5. Upstream history (`F5-R5`, `F6-R1`)

### 5.1 Finding the repository

The URL was in the workspace's own sub-repository all along:
`guinand-weil-rigorous-numerics-main/CITATION.cff` line 16.

```
https://github.com/aidilamrym-ops/guinand-weil-rigorous-numerics
```

Two independent clones were taken into a temp directory: a `blob:none` partial
clone used for `git show` / `git diff`, and a full clone used for the tree
comparison in §5.4. Both report the same history.

* `origin/HEAD` = `6082dcd67d9bcd932780176b02a4ec806dc01fec` *"fix: source-hash
  gate pins both copies of the vendored source + full rerun evidence"*
* annotated tag `v1.0.0-certified` = `784520f…`, peeling to `a928d0f…`

### 5.2 The sentence under test

`GW_STATUS_2026-09-26.md` **L1682**, quoted verbatim from upstream HEAD:

> | 2026-09-30 ~09:00 | Snapshot pushed as commit `bfa40dc` (12 files, 102
> tracked). Before committing, `omega_core_v2_results.json` was merged so the
> **$N=400$ certificate stayed in HEAD** instead of being overwritten by the
> in-flight $N=800$ attempt. Pre-commit secret scan: **0 hard hits** (1
> declared local path, recorded in `PROVENANCE.txt` 6.9). | session log
> 2026-09-30 |

F5 could not test this sentence. A6 gave this workspace a repository, but the
local history begins at the A6 commit and the sub-repository carries no `.git`
of its own, so the merge was still not inspectable here. A7 fetched the history
that actually contains it.

### 5.3 Clause-by-clause result

| clause | check | result |
|---|---|---|
| *"commit `bfa40dc`"* | `git log -1 bfa40dc` | exists: `bfa40dcb1769a7820e413f7d2702a30c463b8fef`, 2026-09-30 09:12:19 +0800, *"Add power-cut checkpointing to the OMEGA-CORE sweep (option C)"* |
| *"(12 files, 102 tracked)"* | `git diff --name-status e65319d bfa40dc` → 12 lines; `git ls-tree -r bfa40dc \| Measure-Object -Line` → 102 | **both exact** |
| *"was merged"* | `git log -1 --format=%P bfa40dc` | one parent, `e65319d3e148697a9c7f3a626f0a56f91252f34f` — so *merged* describes the **content** merge of the JSON, not a git merge; no parent side was discarded |
| *"`omega_core_v2_results.json` was merged"* | `git diff --numstat e65319d bfa40dc -- omega_core_v2_results.json` | **16 added, 1 deleted** |
| *"so the $N=400$ certificate stayed in HEAD"* | `git diff e65319d bfa40dc -- omega_core_v2_results.json` | the diff is a pure **append**: the `+` block opens a new array element *after* the existing `}`, and the only `-` line is `]` (the old missing newline). The $N=400$ record is context, not removal. `git show bfa40dc:omega_core_v2_results.json` contains **both** `"N": 400` and `"N": 800` |
| *"$N=400$ certificate" is the one the certificate pins* | blob ids | `index 30ca146..dbdd52d` — the pre-image blob is `30ca1467b757952da97a299985463f245b4d376b`, the prefix `OMEGA_CORE_CERTIFICATE.md` L505 records |

**Verdict: ESTABLISHED, scoped to `bfa40dc`.** The sentence was true on the
date it was written.

### 5.4 The scope the sentence does not carry

A claim that is true at one commit and superseded later must say so, or the
next reader will find the counterexample and dismiss the whole record.

* At `e65319d` (the parent), `omega_core_v2_results.json` is 1971 bytes,
  SHA-256 `5aaab0cfbf26f7fc5a3306bcd6a6e82e5482dad54a0a08d55ed4ebdcf22aa4f2`
  — exactly what `REPO_STRUCTURE.md` L214 and `OMEGA_CORE_CERTIFICATE.md` L767
  record.
* At `bfa40dc` it is 2413 bytes, SHA-256
  `b1160cd8e093887446c500b4936c8ce588a6dbf23941e78f1a4621d32add2675`.
* At `d70f6fa` (2026-10-01) the file is **replaced** by the single $N=800$
  record: 1774 bytes, SHA-256
  `20ff0378bf72065c75ee8af2e873350d0dcd6801e6384db86eb14d7594119cbc`.

So "stayed in HEAD" holds at `bfa40dc` and stops holding at `d70f6fa`. Both
halves are now written down: `F5-R5`, `F1_REPORT.md` §1/§5, `Brain.MD` and
§7 of this report all carry the scope.

### 5.5 Fidelity of this workspace against upstream

| file | workspace | upstream | verdict |
|---|---|---|---|
| `omega_core_v2_results.json` | 1774 B, `20ff0378…` | `20ff0378…` at `d70f6fa`, `8a86d7e`, `0fc9d5d` and `6082dcd` | **byte-identical** |
| `GW_STATUS_2026-09-26.md` | 108404 B, `4d0769f9…` | `4d0769f9…` at `6082dcd` (HEAD) | **byte-identical** |

### 5.6 Tree diff — workspace sub-repository vs upstream HEAD

```
workspace files (excl .git/__pycache__) : 121
upstream tracked files at HEAD          : 113
only in workspace : 8
   + ckpt_N400/build.ckpt
   + ckpt_N400/build.ckpt.time
   + ckpt_N400/ldlt.ckpt
   + ckpt_N400/ldlt.ckpt.time
   + gw_final_gate_run.log
   + omega_core_v2_heartbeat_N400.json
   + omega_core_v2_results_N400.json
   + omega_core_v2_run_N400.log
only in upstream  : 0
content differs   : 14
   ~ CHECKSUM.sha256
   ~ OMEGATrackC.lean
   ~ OMEGA_CORE_CERTIFICATE.md
   ~ PROVENANCE.txt
   ~ README.md
   ~ REPO_STRUCTURE.md
   ~ gw_final_gate.py
   ~ gw_mont_pipeline_check.py
   ~ gw_verify_production.py
   ~ gw_verify_results.py
   ~ track_c_lean_verify.log
   ~ track_c_make_smt.py
   ~ track_c_side_conditions.smt2
   ~ track_c_smt_z3.log
```

Reading: this workspace is a **superset** of upstream — nothing upstream has is
missing — and the eight extra files are exactly the `N = 400` rerun evidence
that F2-7 shipped on 2026-10-05 plus its checkpoint scratch, which upstream has
never had. The fourteen differences are the workspace's own audit trail: the
gates F1/F2 hardened, the logs of the runs that produced them, and the manifests
that pin them. Nothing here suggests the two trees are copies of each other,
and §5.5 says precisely which two files are.

---

## 6. Verification matrix

| check | command | result |
|---|---|---|
| external provenance gate | `python provenance_check.py` | exit **0**, `GATE: PASS -- 5 quantities, 8 evidence snapshots, 5 reference facts, 10 conditions` |
| borrowed-authority gate | `python theorem_provenance_check.py` | exit **0**, `P9 ARCHIVE_CONSISTENCY 15 archived sources, layers agree with access, every layer-A snapshot hash-verifies, no uncited record`, `THEOREM PROVENANCE CHECK: every borrowed authority is registered, evidenced and closed.` |
| layered-archive injection | `harnesses/f5_2_inj.py` | exit **0**, `HARNESS: PASS -- 20/20 cases behaved as expected, registers byte-identical, both gates green at the end`, `registers restored byte-identical: True`, `final: f3=0 f4=0` |
| report/prose gate | `python report_claim_check.py` | exit **0** as of 2026-10-06, `report_claim_check: PASS` — header `suite=14`, `harnesses=21`, `manifest=81`, `brain=v1.13`, `P8 Brain.MD names every one of the 52 files at the workspace root` |
| manifest | `python checksum_check.py` | exit **0** as of 2026-10-06, `ok   CHECKSUM  matched 81/81 listed, 81 on disk`, `CHECKSUM: PASS -- 81 files match CHECKSUM.sha256` |
| harness rig | `python harness_check.py` | exit **0** as of 2026-10-06, `passed=21  failed=0  not_run=0  of 21  |  workspace byte-identical`, `HARNESS: PASS -- 21/21 behaved as expected, workspace byte-identical` |
| full suite | `python suite_check.py --with-harness` | exit **0** as of 2026-10-06, `passed=15  failed=0  not_run=0  of 15`, `SUITE: PASS -- every listed gate returned 0` |
| Anti-Circularity Gate | `gate.py` over the final artefacts | run **last**, after the last edit |

Encoding of every file this phase wrote or edited: UTF-8 strict, no BOM,
`CR = 0`, last byte LF.

---

## 7. Stale statements found and fixed

Every one of these was a sentence that had been true when written and was not
true when A7 read it. They are listed because the finding, not the edit, is the
deliverable.

| file | statement | why it was false | now |
|---|---|---|---|
| `F4_REPORT.md` §9 R1 | *"the SEP Zeno path and the Springer DOI both returned **HTTP 404** and were never retrievable, so those are recorded as layer C"* | already false when F5-2 finished — F5-2 corrected both identifiers inside the same phase (`F5_REPORT.md` §4.1) | rewritten with an explicit *Correction by A7* note; the row's real residual (the storage decision) is closed |
| `F4_REPORT.md` §9 R1 | *"8 hashed snapshots"* and *"archiving the remainder … is a … decision"* | eight became nine; the decision was never taken | both replaced |
| `F5_REPORT.md` F5-R5 | *"NOT ESTABLISHED"* | unverifiable only for lack of the upstream history | **ESTABLISHED**, scoped to `bfa40dc`, with `d70f6fa` named as the superseding commit |
| `F5_REPORT.md` §4.2 / §4.3 | *"Final archive, 22 records: A = 8, B = 11, C = 3"*; *"Eight Layer-A files"* | true at F5-2, stale after A7 | anchored to F5-2 (2026-10-05) with the A7 tally beside it — rewritten as history, not as a current claim |
| `F5_REPORT.md` §9 | two rows quoting `4 quantities, 7 evidence snapshots` | stale twice over (A3 added a quantity, A7 a record) | anchored *as of F5 (2026-10-05)* |
| `F3_REPORT.md` §9 | gate-of-record row quoting `4 quantities, 7 evidence snapshots` | stale | live output restored, with the growth spelled out in the same cell |
| `F1_REPORT.md` §1, §5, §6 | *"remains **NOT ESTABLISHED**"*; *"no phase can close, because this tree has no `.git`"* | A6 created the repository, A7 fetched the history | rewritten: NOT ESTABLISHED at F1's date, **ESTABLISHED** since A7 |
| `F6_REPORT.md` §8 / §9 | F6-R1 and F6-R2 *"open — A7 scope"* | A7 is no longer a scope, it has happened | **CLOSED** with pointers into §4 and §5 |
| `REFERENCES.md` `### OBSERVABLE_UNIVERSE_DIAMETER` | *"Evidence: none locally archived"* | imprecise — the authority is layer C, but an arXiv snapshot *is* archived; it simply does not contain the number | states exactly that, and that `probe_waived` is the honest consequence |
| `Brain.MD` | five places asserting no `.git`, a stale `78 files`, and a version still at v1.12 | falsified by A6, by this phase's new files, and by the edits above | all corrected; version **v1.13** |

`F2_REPORT.md` was checked and already carried A6's annotation, so it was left
alone: a phase record that has been annotated once does not need a second edit.

### 7.1 A root file that arrived during this phase

At 2026-10-06 15:17, after the first draft of this report and before the
verification run, `Tugas tambahan.md` appeared at the workspace root. It is an
instruction to rename the private component names of the Protocol 09 artefacts
to universal symbols. **A7 did not act on it** — it belongs to whatever phase
picks it up, and folding someone else's task into a provenance phase is exactly
how a report starts claiming things it did not do.

It was registered, because the gates require that: `report_claim_check.py` P8
demands that `Brain.MD` name every root file, and P3 demands that the manifest
list every file in scope. So the manifest moved from 80 to 81 rows and the map
gained a row that says, in as many words, that the file is a queued task and not
a corpus artefact.

---

## 8. Residual

| id | item | state |
|---|---|---|
| `F7-R1` | the $N=400$ evidence exists only in this workspace, never upstream | **recorded, not closed** — §5.6 names the eight files and says why. Publishing them upstream is an operator decision about someone else's repository, not a correction of this one |
| `F7-R2` | the Planck parameter table is still not archived | **unchanged from F3** — the authority is layer C and the arXiv snapshot carries no occurrence of `diameter` or `comoving`, so `D_obs` still rests on a declared `probe_waived` reason. A snapshot of the table remains the candidate follow-up |
| `F7-R3` | re-fetching is manual | the register records a date, not a liveness guarantee; no URL monitor runs in this workspace. `provenance_check.py` P2 verifies *bytes*, which is the property a gate can actually hold |

---

## 9. How to re-run this phase

```text
# 1. the two register gates
python provenance_check.py
python theorem_provenance_check.py

# 2. the archive harness (mutates, then restores byte-identically)
python harnesses\f5_2_inj.py

# 3. prose and manifest
python report_claim_check.py
python checksum_check.py --update
python checksum_check.py

# 4. the rig
python harness_check.py
python suite_check.py --with-harness

# 5. upstream comparison (needs a clone of the repository named in §5.1)
git clone https://github.com/aidilamrym-ops/guinand-weil-rigorous-numerics upstream
git -C upstream log -1 --format=%H%n%P bfa40dc
git -C upstream diff --numstat e65319d bfa40dc -- omega_core_v2_results.json
git -C upstream show 6082dcd:GW_STATUS_2026-09-26.md | findstr "stayed in HEAD"

# 6. Anti-Circularity Gate, last, after the last edit
gate.py <workspace targets>
```
