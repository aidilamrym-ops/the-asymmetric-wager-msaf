# F8_REPORT.md — Liveness and pattern-closure (Fase A9)

**Date:** 2026-10-06
**Closes:** `F7-R3`, `F6-R5`
**New tool:** `url_liveness_check.py` + `provenance/url_liveness.json`
**New gate condition:** `provenance_check.py` `P11 LIVENESS_RECORD`
**Extended gate:** `report_claim_check.py` (seven prose-pattern classes)
**New harness:** `harnesses/a9_drift_inj.py` (21 cases)
**Suite gates:** still **14** — `url_liveness_check.py` is a companion, not a gate.

---

## 1. Mandate

Fase A7 left two residuals open and asked this phase to close them, with two
constraints.

`F7-R3` — *re-fetching is manual.* `F7_REPORT.md` §3 re-fetched every URL in
`REFERENCES.md` by hand on 2026-10-06; nothing in the workspace holds that
ability, so the next phase would either repeat the handwork or silently trust
a record nobody re-probes.

`F6-R5` — *the sweep-1 pattern set covers cardinal + ordinal + digit forms of
gates / harnesses / rows / entries / versions.* `report_claim_check.py` already
reads those forms, but several legal spellings slip past it and no harness had
ever shown the gap.

The method is **blind-spot hunt, then fix at the cause — never patch the
symptom**. Every closure below names a class of defect the gate used to read
past, proves the class with an injection, and records what the hunt of this
phase itself turned up.

---

## 2. Method

1. Inventory every URL the workspace already knows: `external_constants.json`
   `evidence[].url`, `theorem_provenance.json` `archive[].url` and non-empty
   `license_basis_url`, the `* URL:` lines of `REFERENCES.md`.
2. Write `url_liveness_check.py`: probe each URL, compare against the register,
   write `provenance/url_liveness.json`.
3. Add `P11 LIVENESS_RECORD` to `provenance_check.py` so the suite holds that
   record to the register **offline**.
4. Extend `report_claim_check.py` to read the prose forms it used to skip.
5. Prove both additions with `harnesses/a9_drift_inj.py`.
6. Hunt this phase's own blind spots; fix what is found at the cause.
7. Re-run every gate; Anti-Circularity Gate last, after the last edit.

---

## 3. The probe (`F7-R3`)

`url_liveness_check.py` re-fetches **24 unique URLs** (8 evidence + 15 archive
+ 1 `license_basis_url`; `REFERENCES.md` reuses the same ids and is not counted
a second time). Each probe records `status`, `final_url`, `body_sha256` and
`error` when there is one.

### 3.1 Verdicts

| Verdict | Meaning | Exit |
|---|---|---|
| `OK` | live `status` equals register `observed_status` | 0 |
| `CHANGED` | register records one status, source answers with another | 1 |
| `UNREACHABLE` | no answer at all | 1 |
| `DIVERGED` | status unchanged, layer-A body no longer hashes to the archived snapshot | **0** (measured, never failed) |

All URLs unreachable → exit **2**, never 0. `DIVERGED` is the fourth verdict
and deliberately **does not fail**.

### 3.2 Why DIVERGED does not fail

The `sha256` in the register pins an **archived local snapshot**, already
verified by `P2` of `theorem_provenance_check.py`. It is not a claim that the
live URL currently serves identical bytes.

The probe of 2026-10-06 falsified the rule that made `DIVERGED` fail:

| URL | status then | status now | bytes | sha |
|---|---|---|---|---|
| `Countably_additive_measure` | 200 | 200 | 650480 → 650737 B | changed |
| `Ihara_zeta_function` | 200 | 200 | 118173 B | changed (same size) |
| `Ultraviolet_catastrophe` | 200 | 200 | 133784 → 134101 B | changed |

Wikipedia re-renders constantly while our snapshot stays intact. Failing on
those three would report a defect in this corpus that exists only in the
outside world. `final_url` is recorded (`final_url_changed`) and never gated —
the 403 on `doi.org/10.1098/rspa.1970.0021` stores `final_url` equal to the
request URL, so there is no redirect to claim.

### 3.3 Result

```
probed 24 URL(s): OK=21 CHANGED=0 UNREACHABLE=0 DIVERGED=3
EXIT=0
```

11/11 status expectations matched (including the 403s still 403). Record:
`provenance/url_liveness.json`, schema `msaf-url-liveness/v1`.

### 3.4 Why this is not a suite gate

`url_liveness_check.py` depends on publishers' uptime. The suite is the
**offline** contract: it must give the same answer with no network. A gate
whose pass depends on a third party is not a gate. The companion is written
down; `P11` holds the record to the register; the suite still runs offline.
`--fixture FILE` / `URL_LIVENESS_FIXTURE` replaces the network for
deterministic tests.

---

## 4. `P11 LIVENESS_RECORD`

`provenance_check.py` now carries **11** conditions. Conditions are named by
their **P-number**, not by a running "number of conditions" count — the
convention is recorded in `F3_REPORT.md` ("the 9th is `P9 LAYER_CONSISTENCY`,
the 10th is `P10 REF_MARKERS`"), so P11 makes the summary print
`%d conditions` = 11. Hardcoded literals are replaced by `len(CONDITIONS)`.

P11 checks, offline, from the record alone:

1. the file exists (message: `run python url_liveness_check.py and commit the
   record`);
2. schema `msaf-url-liveness/v1`, `generated_utc`, `tool`, `probe`;
3. every record parses;
4. the verdict vocabulary is exactly the four above;
5. the URL set equals the register's own set (imported live from
   `url_liveness_check.expectations()`, not re-typed);
6. each record restates `expected_status`, `layer`, `archived_sha256`,
   `retrieved_utc` from the register;
7. no `CHANGED` / `UNREACHABLE` is left standing in the record;
8. `DIVERGED` is reported but not failed;
9. freshness is **not** checked — the gate must not fail because a clock moved.

Four negative directions were proven: record deleted; one URL dropped from the
record; a pin invented that the register never recorded; a `CHANGED` left in
place. Every one exits 1 with a needle that names the defect. After restore the
record is byte-identical and P11 is green again.

---

## 5. `report_claim_check.py` pattern hardening (`F6-R5`)

Seven classes this gate used to read past. Each is injection-proven by
`harnesses/a9_drift_inj.py`; numbers are read from the live rig (`GATES`,
`HARNESSES`) so the harness cannot rot when a gate or a harness is added.

| # | Class | Defect the gate used to read past | Fix |
|---|---|---|---|
| 1 | keyed header | `suite=14 harnesses=21` was mis-read as bare counts (the `=` glued digits to the word); `brain=v…` was never compared | `KEYED` map; `BARE_NUM` now rejects `=` and alphanumeric prefixes |
| 2 | `tally_object` mis-binds | `suite_check.py --with-harness` was counted as harnesses because the ±3-line window hit the wrong line | classify from the claim's **own** line first; window is fallback only |
| 3 | `entries` spelled out | a written-out manifest row count was skipped | `SPOKEN_ENTRIES`, gated on `with-harness\|enumerat` |
| 4 | ordinals past `twentieth` | `twenty-second` passed unread (`ORD_*` was case-sensitive; lists stopped at 20th) | `re.I`; lists generated 0…99 |
| 5 | compounds | `N-gate` / `N-harness` never read | `COMPOUND_GATE`, `COMPOUND_HARNESS` |
| 6 | `x of y` pairs | **then** a pair such as `` `nine of twenty-two harnesses` `` was never read | `OF_GATES`, `OF_HARNESSES` |
| 7 | spelled manifest count without a determiner | `manifest rows listed eighty-one` skipped | `SPOKEN_ROWS_BARE` |

Plus two guards that are not pattern gaps but blind spots:

- **word-list corruption.** If the generated cardinal/ordinal lists are not
  what the code believes, the gate used to compare prose against wrong numbers
  and call it a pass. `vocabulary_problem()` runs at the head of
  `live_values()` and exits 2 after printing a `FAIL` that names the
  corruption, rather than answering.
- **spurious matches.** `SPOKEN_*` forms are gated so ordinary words like
  `ninety-nine` do not fire inside `ninety-nine-year-old`; the generator bug
  that produced `fifty-one` for 81 is recorded in §6.

Injection probes were run on **temp copies**, never on the corpus, and the
final corpus state was required to produce the same verdicts the live rig
produces. Injected defects were caught with the expected needle
(`history` when anchored to a phase record, `FAIL` otherwise). Cases written
**without** an anchor correctly fail; a case that stays green when it should
have failed is a harness bug, not a gate pass, and was fixed.

The 13-case A8 probe family remains valid; A8 itself was **deferred** — see
`Brain.MD` (the `Tugas tambahan.md` Kamus Pemetaan is absent and three of its
six proposed names collide with existing symbols). No `protocol_09.*` byte was
touched.

---

## 6. Blind-spot hunt of this phase's own work

The hunt is mandatory. What it turned up:

### 6.1 Generator spelled 81 as "fifty-one"

`_CARD_ONES[1:]` produced 180 entries and `spelled(81)` returned `fifty-one`
because the tens stem and ones stem concatenated without a hyphen. Fixed at
the generator: `_CARD_ONES[1:10]`, `len == 100`, `spelled(81) == "eighty-one"`.
A harness case that would have silently exercised the wrong string was
retargeted.

### 6.2 An A8 edit had overwritten a historical `brain=v…` record

`F7_REPORT.md` §6 is a **phase record**. It stated `brain=v1.14` because A8
edits had overwritten the version string the F7 verification actually read.
A phase record must not be rewritten to match a later tree; the string was
restored to `v1.13`, the value F7 verified, and the surrounding sentence was
anchored `as of 2026-10-06` instead of being left to drift.

### 6.3 `F5_REPORT.md` said "10 conditions" without a date

Same class. The line now reads `10 conditions, P1…P9, as of F5 (2026-10-05)`.
`F7_REPORT.md` `10 conditions` keeps the value with an `as of 2026-10-06`
anchor. **Historical numbers stay; they get a date or a scope, not a silent
rewrite.**

### 6.4 `checksum_check.py` docstring claimed counts it does not check

"39 root artefacts" and "thirteen fault-injection harnesses" were stale prose.
The sub-repo header `TOTAL FILES : 116` was **verified correct**, not 124 —
that claim is now written down so a later reader does not "fix" it to a wrong
number. The 39 malformed-encoding files in the sub-repo remain **pinned,
recorded, not fixed**; normalization is out of A9 scope on purpose.

### 6.5 Condition counting was a named-convention problem, not a bug

`report_claim_check` and `provenance_check` both print `%d conditions`.
`F3_REPORT.md:372` establishes the convention that a condition *is* a P-number.
P11 therefore prints 11, and the 9th/10th names are `P9`/`P10`. The
hardcoded `10` literals that would have gone stale were replaced by
`len(CONDITIONS)`.

### 6.6 Root-file inventory

`report_claim_check` P8 counts **every regular file at the workspace root**,
including `CHECKSUM.sha256`. At A8 that was 52; with `url_liveness_check.py`
and `F8_REPORT.md` it is **54**. The `Brain.MD` map was updated to name both
new files, plus `harnesses/a9_drift_inj.py`.

### 6.7 The harness's own first run (five defects, all fixed at the cause)

`harnesses/a9_drift_inj.py` was written to prove the A9 additions can fail.
Its first execution did not prove that — it exposed five defects in the
harness and in the tools it judges. None was patched around; each was fixed
where it lived.

1. **Injections were disarmed by the gate's own escape hatch.** P1–P12 wrote
   lines like `` `suite=15 harnesses=22 …`, as of 2026-10-06 ``. P5 permits a
   numeric claim that carries a date within one line, so the gate correctly
   reported `history, not current` and exited 0. An injection that carries
   the gate's own excuse is not a defect the gate is required to catch. The
   harness now injects **without** a date, phase tag or `then`.
2. **Control-case logic was inverted.** `want_rc == 0` entered the
   `if rc == 0: fail("the defect was NOT caught")` branch, so the two controls
   that must stay green were reported as failures. Controls are now judged
   first, and a defect case is only a failure when the tool exits 0.
3. **`url_liveness_check.py` crashed on a cross-drive `--out`.**
   `os.path.relpath(out_path, HERE)` raises `ValueError` when the output is on
   `C:` and the workspace is on `D:` — exactly what a temp-dir `--out` does.
   The FAIL message therefore never printed, L5 lost its needle and L6 exited
   1 instead of 2. The path is now shown as given when `relpath` cannot
   compute one.
4. **All-unreachable with a fixture did not return exit 2.** The TOOL NOT RUN
   branch was gated on `not fixture`, so a fixture that reached nothing fell
   through to the contradict-register path. `reached == 0` now returns 2
   whether the emptiness came from the network or from the fixture — the tool
   has established nothing either way.
5. **Corruption reason was greppable only as `SKIP`.** `report_claim_check`
   printed `SKIP  live values unavailable: …` on vocabulary corruption; the
   harness (and any other gate) greps `FAIL`. It now prints `FAIL  live values
   unavailable: …` then `report_claim_check: SKIP`, the same shape
   `url_liveness_check` already used for an unusable fixture.

After those five fixes the harness reports
`HARNESS: PASS -- 21/21 cases behaved as expected, every tool green before
and after, every target byte-identical`, and `harness_check.py` re-runs it as
the twenty-second harness in the folder.

### 6.8 `f5_2_inj.py` still demanded `f3=0` for mutations P11 now restates

The first full `suite_check.py --with-harness` run after A9 failed on
`f5_2_inj.py` G3/G4/G9. Those three cases mutate the `archive` section of
`theorem_provenance.json` and were written when `provenance_check.py` had ten
conditions, none of which read that section — so the harness demanded
`f4=1` (P9 ARCHIVE_CONSISTENCY, the property under test) **and** `f3=0`
(nothing else may break sideways).

`P11 LIVENESS_RECORD` re-derives its URL expectations from that same
`archive` section. A layer relabelled, an illegal layer, or the archive list
removed therefore now fails **both** gates: f4 via P9, f3 via P11 naming the
exact URL and the layer disagreement. That is a second detector over the same
register, not a sideways break. Silencing P11 for these mutations would have
been the cover-up; the harness contract was the stale artefact.

Fixed at the cause: G3/G4/G9 now expect `both` gates to fail, the docstring
records why, and the FAIL detail printer also surfaces `P11` lines. Every
other case keeps the original "other gate stays green" clause, which still
holds for mutations P11 does not restate (G5 licence key, G6 local_copy
claim, G7 renamed identifier, G8 uncited record — all still `f4=1, f3=0`).

This is the same class as §6.2: a harness or a report that encodes the gate
surface *as it was* goes stale the moment a new condition is added, and the
stale artefact — not the new gate — is what must change.

---

## 7. Verification matrix

| Artefact | Command | Result |
|---|---|---|
| encoding | `CR=0 BOM=False endLF=True` on every new/edited file | pass |
| probe syntax | `url_liveness_check.py --help` | exit 0 |
| probe live | `python url_liveness_check.py` | `OK=21 CHANGED=0 UNREACHABLE=0 DIVERGED=3`, exit 0 |
| P11 positive | `python provenance_check.py` | `ok   P11  LIVENESS_RECORD … urls: 24, ok: 21, diverged: 3`, exit 0 |
| P11 negative ×4 | delete record / drop URL / invent pin / leave CHANGED | exit 1 each, needle named |
| patterns | temp-copy injections (keyed, compound, of-y, ordinal, spelled entries, spelled manifest, control) | every injected defect caught; controls stay green |
| vocabulary guard | corrupt `_CARD_ONES` in a copy | gate exits 2, not 0 |
| harness | `python harnesses/a9_drift_inj.py` | `HARNESS: PASS -- 21/21 cases behaved as expected, every tool green before and after, every target byte-identical` |
| manifest | `python checksum_check.py` then `--update` then verify | header `TOTAL FILES` equals scope; both directions green |
| gate | `python provenance_check.py` (11 conditions) | exit 0 |
| gate | `python theorem_provenance_check.py` | exit 0 |
| gate | `python report_claim_check.py` | `report_claim_check: PASS` |
| gate | `python harness_check.py` | 22 harnesses, PASS |
| suite | `python suite_check.py --with-harness` | 15/15 |
| AC Gate | last, after the last edit | see §9 |

---

## 8. Residuals

| Id | Statement | Status |
|---|---|---|
| `F7-R3` | re-fetching is manual | **CLOSED 2026-10-06 (A9).** `url_liveness_check.py` + `P11 LIVENESS_RECORD`. |
| `F6-R5` | pattern set covers the spelled forms | **CLOSED 2026-10-06 (A9).** Seven classes + vocabulary guard + generator fix, injection-proven 21/21. |

New, recorded, **not** closed in A9:

| Id | Statement |
|---|---|
| `F8-R1` | `report_claim_check` still does not parse the **string** `10 conditions` as a claim about the condition count. The P-number convention makes the number true by definition, but a prose sentence that says "nine conditions" while `len(CONDITIONS)` is 11 would pass unread. Candidate rule: any root `.md` sentence matching `\b(nine|ten|eleven|twelve|\d+)\s+conditions\b` must equal `len(CONDITIONS)`. |
| `F8-R2` | `provenance/url_liveness.json` freshness is not gated. A record that is weeks old still passes P11. Policy question for a later phase: age limit, or re-run on a schedule. |
| `F8-R3` | Sub-repo encoding remains pinned-not-fixed (39 files, `CHECKSUM.sha256` header `TOTAL FILES : 116`). Out of A9 scope on purpose. |
| `F8-R4` | A8 (`protocol_09` / `Tugas tambahan.md`) remains deferred. |

---

## 9. How to re-run this phase

```bash
# 1. the probe (network; writes the record)
python url_liveness_check.py

# 2. the registers, offline
python provenance_check.py
python theorem_provenance_check.py

# 3. prose and manifest
python report_claim_check.py
python checksum_check.py

# 4. the harness (mutates, then restores byte-identically)
python harnesses/a9_drift_inj.py
python harness_check.py
python suite_check.py --with-harness

# 5. Anti-Circularity Gate, last, after the last edit
python "C:\Users\usER\.config\opencode\skills\anti-circularity\scripts\gate.py"
```

`--fixture` on `url_liveness_check.py` makes step 1 deterministic; without
network, P11 still holds the committed record to the register.

---

*F8_REPORT.md v1 — written 2026-10-06 (Fase A9).*
