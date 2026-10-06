# F1 Report — Numeric Canon and Pipeline Claim Audit

**Workspace:** `D:\THE ASYMMETRIC WAGER`
**Date:** 2026-10-04
**Predecessor:** `F0_REPORT.md`
**Status:** F1 complete, findings F1-A through F1-Q. Every finding below is
either reproduced by a script in this workspace or marked NOT ESTABLISHED. Nothing is asserted on narrative
grounds. $P_{\text{narrative}} = 0$.

---

## 1. Scope and method

F1 audits two things and nothing else:

1. **The numeric canon** — every number the framework states, against the
   constants it is derived from.
2. **Pipeline claims** — every sentence of the form "this passed", "this is
   verified", "this is unsat", against an executable that can actually go red.

Method, in order:

- `epistemic_sieve` to strip narrative from each claim;
- direct recomputation with `mpmath` 1.3.0 / `numpy` 2.5.2 / `z3` 4.16.0,
  never a re-statement of the original source;
- fault injection to establish that a gate *can* fail, before reporting that
  it passes;
- Anti-Circularity Gate (`gate.py`) run immediately before any sentence of the
  form "machine-verified".

Where a check could not be completed, the finding is recorded as
**NOT ESTABLISHED** rather than quietly dropped.

---

## 2. Findings

### F1-A — Significant-figure laundering in `Delta_univ`  (CONFIRMED, FIXED)

`Delta_univ = L_p / D_obs` with `D_obs = 8.8e26` — two significant figures.
The corpus nevertheless stated the quotient to seven.

- envelope: `D_obs ∈ [8.75, 8.85]e26` → `Delta_univ ∈ [1.82628, 1.84715]e-62`;
- relative half-width **0.568 %**;
- therefore only **two** significant figures (`1.8e-62`) are observationally
  justified; three are not, because the envelope spans `1.83 … 1.85`.

Fixed in `Skill.md` §3, `Brain.MD`, `msaf_visual.py` (printout now states
`1.8e-62 (+-0.568%)` next to the full quotient) and
`VISUALISASI_MATRIKS_FORMAL.md` (explicit significant-figure note).

### F1-B — `N_steps * Delta_univ` off by 0.82 %  (CONFIRMED, FIXED)

`1.836653e-62 × 5.4e61 = 0.99179262`, i.e. −0.82 % from unity. From the
*definition* the product is exactly 1, because `N_steps` is `1/Delta_univ`.
The actual value is `N_steps = 5.444685399e61`, and the published `5.4e61` was
a two-digit rounding of the same constant being multiplied. Corrected wherever
it appeared; the identity now closes to the precision at which it is quoted.

### F1-C — `gw_final_gate.py` could not fail  (CONFIRMED, FIXED)

The threshold `1.32105051975e-102` was printed twice and compared against
nothing; "FAIL" counters were printed yet `sys.exit(0)` was unconditional.
`Brain.MD` listed the file under *Validation*, so the listing was not backed by
anything that could go red. Fixed in F1-P below, and re-proven (below).

### F1-D — The `N = 400` lambda_min exists only as prose  (CONFIRMED)

`6.74709239897214291717530665950e-509` appears in documentation but in no
result file. Root cause established:

- `omega_core_v2_run.log` contains **two appended runs** — header #1 at line 2
  (`dims=[400,800]`, start_prec 9000) with its VERDICT at line 54, header #2 at
  line 76 (`dims=[800]`, start_prec 18000) with VERDICT at line 116;
- run 2 **overwrote** `omega_core_v2_results.json`, which therefore holds a
  single row, `N = 800`;
- the only `N = 400` JSON in the workspace is
  `omega_core_v2_results_FAILED_absbug_20260929_011342.json`
  (`non_result = true`, `bound = null`);
- there is **no two-row JSON** anywhere in the workspace;
- the workspace contained **zero** `.git` directories at F1's date, so
  `GW_STATUS_2026-09-26.md`'s claim that the `N = 400` row "merged so it stayed
  in HEAD" is **NOT ESTABLISHED** here. *(Restated 2026-10-06: A6 gave the
  workspace a repository. The verdict is unchanged, the reason is not — see
  `F5_REPORT.md` F5-R5.)*

**Consequence:** `N = 400` is not machine-gated. `Skill.md` §3 status was
corrected to say that.

> **Amended 2026-10-04 (during F1-R4).** The original wording here said the
> value was *"log-recorded only"*, and that understates it. The same bound is
> recorded in **three** places, and the three agree:
>
> | record | location | precision |
> |---|---|---|
> | run log | `omega_core_v2_run.log` line 51 | 25 sf — `6.747092398972142917175307e-509` |
> | prose + telemetry | `PROVENANCE.txt` §6.2 | 30 sf + radii, timings, verdict |
> | result object | `OMEGA_CORE_CERTIFICATE.md` §4 JSON block | 30 sf, full object |
>
> What is genuinely gone is the **file**: `omega_core_v2_results.json` at
> 1971 bytes with SHA-256 `5aaab0cf…a4f2` no longer exists anywhere in the
> workspace — run 2 overwrote it, and no 1971-byte JSON remains. Its hash
> survives in three documents, so the overwrite is provable, but nothing can
> re-read or re-gate the object.
>
> So the precise statement is: **three documentary records, zero machine-readable
> artefacts.** Still not machine-gated; no longer "log-recorded only".

### F1-E — Five holes in `gw_verify_production.py`  (CONFIRMED, FIXED)

Established by fault injection against 20 mutation variants:

| # | hole |
|---|---|
| 1 | `bound` checked only for `> 0`, never re-derived |
| 2 | `bound_detail` never cross-checked |
| 3 | `dim == 2N+1` never checked |
| 4 | `sha256` checked only for length, not 64-hex shape |
| 5 | missing keys raised `KeyError` (traceback instead of verdict) |

All five closed: `get()` is KeyError-proof, and `deep_invariants()` enforces
dimension, sha256 shape, re-derivation of `bound` from `bound_detail` at
relative tolerance `1e-20`, and `pivot_sign == '+'`. Applied to fixtures
(`gv.CASES`) **and** the production row.

### F1-F — "gradient ratio ≈ 1,01" is wrong  (CONFIRMED, FIXED)

The DRAF claimed `|Delta zeta| / Delta_univ ≈ 1,01`. The actual coefficient is
`|zeta'(rho_1)| = 0.793160433357`. The figure `1,01` was
`|Delta zeta| / Re(Delta zeta) = 1.01259283214` — a different ratio
entirely. Corrected in `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md` §2.

### F1-G — `zeta(s_kritis)` claim not reproduced  (CONFIRMED, FIXED)

The DRAF stated `zeta(s_kritis) ≈ 3,187e-97 − 2,001e-96 i`. Recomputation at
`dps = 100` gives `|zeta(z0)| = 3.898966568e-101`, relative error **1.0**.
The stated number does not reproduce. Replaced by the recomputed value
`−6.1299e-102 + 3.8505e-101 i`.

### F1-H — Per-pixel zeta deviation  (PASSED, provenance gap recorded)

Reproduced independently:

- `Re = 1.43864420885e-62`, `Im = 2.2903036742e-63`,
  `|Delta zeta| = 1.45676081388e-62` — the published 7-digit figures match;
- the identity `|Delta zeta| = |zeta'(rho_1)| · Delta_univ` holds to relative
  `7.4e-63`.

**Residual:** no script in this workspace produces those digits. The values are
correct but their provenance file is missing. Recorded; see §5.

### F1-I — Hardcoded constant presented as simulation output  (CONFIRMED, FIXED)

`msaf_visual.py` carried the literal `1.836653e-62` under a comment claiming it
came "from real 100 DPS simulation data", while the file performs no `zeta`
evaluation at all. The comment is now true to the code: the constant is
declared as a recorded value, and `msaf_zeta_check.py` recomputes and gates it
(C3/C6/C7).

### F1-J — False K1–K6 alarm from a foreign cwd  (CONFIRMED, FIXED)

`gw_mont_pipeline_check.py` located `gw_montgomery.py` relative to the current
working directory. Invoked from anywhere else it printed
`gw_montgomery.py: No such file or directory`, declared
`PROBLEMS = K1..K6`, stated `do NOT run the real analysis`, and exited 1 — a
clean-looking failure report for a run that never started.

Fixed by anchoring every path to `os.path.dirname(os.path.abspath(__file__))`
and passing `cwd=HERE` to the subprocess. Re-proven: the file now exits 0 when
invoked from the workspace root (§4).

### F1-K — `R_tail` formula fidelity  (PASSED)

`msaf_visual.py`'s implementation is term-for-term identical to `Skill.md` §3:

```
rem = 4 * exp(-(2(N+1)+0.5)*L) / (1 - exp(-2L)),  L = ln(c)
R_tail = rem * 2**(-p * Delta_univ)
```

### F1-L — `Z_none` label ambiguity  (CONFIRMED, FIXED in F2-2)

`Skill.md` defines the zone by `0 < |x - x0| < Delta_univ`, while the DRAF
table labels shifts 1…5 as the "NON-EXISTENCE ZONE". The two are different
objects: one is the open pixel around the anchor, the other is the set of
successive pixel shifts.

Closed by F2-2, and the defect was sharper than "ambiguity": **every table row
falls outside the stated set.** Row *n* sits at `|x - x0| = n * Delta_univ`
with `n >= 1`, and the definition is strict on both ends, so no row satisfies
it. The zone is non-operational and is never evaluated, which is exactly why it
has no rows. Three further sites carried the same conflation:

| site | was | now |
|---|---|---|
| `CONSOLIDATED_MASTER_MANIFESTO.md` | "domain of space below `10^-62`" (a magnitude, not a set) | the set, plus a note that the two are different objects |
| `msaf_visual.py` stem-plot title | "Zone of Non-Existence Beyond the Critical Line 0.5" over points at `n >= 1` | "Pixel-shift sweep OUTSIDE the zone" |
| `DEFINISI_OPERASIONAL_MSAF.md` | one correct definition among several | declares itself **the definition of record** |

`znone_check.py` now gates all five documents (19 conditions), and the DRAF
table carries a reading note stating that no row lies inside the zone.

### F1-M — `Skill.md` §3 decimal typo  (CONFIRMED, FIXED)

`1{,}836{,}653 × 10^-62` renders as `1,836,653 × 10^-62`, wrong by `10^5`.
Corrected to `1{,}836653`.

### F1-N — The precision factor is inert  (CONFIRMED, FIXED)

This was the last blind spot found in F1 and it is the most consequential,
because three documents describe a behaviour that does not occur.

`R_tail = rem · 2^(-p · Delta_univ)` and `Delta_univ ≈ 1.84e-62`. Over the
documented sweep `p ∈ [2000, 18000]`:

| quantity | value |
|---|---|
| attenuation per bit, in `log10` | `log10(2) · Delta_univ = 5.528877678e-63` |
| analytic `Delta log10(R_tail)` over the whole sweep | **`-8.846e-59`** |
| float64 observed span (what the plot actually draws) | **`0.000e+00`** |
| bits required for a **one-decade** shift | **`1.809e+62`** |

The plotted curve is therefore horizontal to 58 decimal places. `msaf_visual.py`
prints all seven sampled points as `-1604.3979`, and in float64 the difference
between the first and last is *exactly zero* — the term is lost entirely under
the accumulated `log10(rem) ≈ -1604.4`.

Consequences, all now corrected:

- `Skill.md` §13 said "visualization of `R_tail` **vs bit precision**";
- `Brain.MD` §1 said "Plot of `R_tail` **decay** vs bit precision" and drew
  `axvline` markers at 9000 and 18000 as if the curve moved through them;
- `VISUALISASI_MATRIKS_FORMAL.md` §3 stated `$p$ is the active computation bit
  precision (9000 → 18000 bit)` with no indication that the factor is inert.

**The formula itself is not wrong** and was not changed: `Skill.md` §3 is the
canon and F1-K passed. What was wrong is the *description* of what the formula
does at these parameters. All three descriptions were rewritten, `msaf_visual.py`
now prints the analytic span, the float64-observed span, and the bits-per-decade
figure, and the plot is annotated `flat`.

Two defects in that fix were themselves caught and corrected:

1. the printout used `{:.2e}`, which renders `1.84e-62` — **three** significant
   figures under a label claiming two (a direct F1-A recurrence);
2. the span was originally computed by differencing two accumulated float64
   logs, which returns exactly `0.000e+00` and hides the very quantity being
   reported. It is now computed analytically.

### F1-O — Control-character corruption in three documents  (CONFIRMED, FIXED)

A workspace-wide scan for control characters found 63 in
`VISUALISASI_MATRIKS_FORMAL.md` and 2 each in `01_PARADOX_AND_SCALE.md` and
`README.md`:

| char | count | should be |
|---|---|---|
| `BS  U+0008` | 14 | `\b` (`\begin`, `\bigl`, `\bigr`) |
| `VT  U+000B` | 8 | `\v` (`\vdots`) |
| `TAB U+0009` | 19 + 4 | `\t` (`\text`, `\tfrac`, `\times`, `\to`) |
| `FF  U+000C` | 20 | `\f` (`\frac`, `\forall`) |
| `BEL U+0007` | 2 | `\a` (`\arctan`, `\approx`) |

Root cause identified, not guessed: **lines 88–101 of
`VISUALISASI_MATRIKS_FORMAL.md` were a leftover LLM generator script**
(`with open("README.md", "w", ...)` … `print("All 4 Markdown files saved…")`).
The document body had been produced by writing Python string literals that were
**not raw**, so `\t`, `\f`, `\b`, `\a`, `\v` were consumed as escapes.

The same mechanism ate three `\r` of `\right` and two `\n` of `\neq`, which
survived only as line breaks (`CR = 0` in the file, because a subsequent
universal-newline read had already converted them). All five were rejoined.

Two further defects surfaced once the LaTeX was legible:

- every `pmatrix` row separator had collapsed from `\\` to `\ ` (the `\\` Python
  escape also collapses), so the matrix would have rendered as a single row —
  5 separators restored;
- `Delta_univ` was stated as `1,836 × 10^-62`, four significant figures, which
  is F1-A recurring in a fourth document.

The 21 tabs in `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md` were checked and are all
table separators (0 escape remainders); the form feeds in
`Theory_of_Everything_Derivations/*.pdf.txt` are PDF page breaks. Neither was
touched.

### F1-P — The final gate had one condition where it needed two  (CONFIRMED, FIXED)

The full run of `gw_final_gate.py 100 40 160 1000 224` reported
`GATE: PASS`, but on inspection:

- the criterion was `min(d_mp, d_sr) < lambda_min`. `d_mp = 3.391e-102` is
  **above** `lambda_min = 1.321e-102`; only `d_sr = 3.912e-159` passes;
- the chain-rule prediction that attributes `d_mp`'s excess to mpmath's
  `lerchphi` defect was **printed next to the observation but never tested**.
  The repository's own docs (`gw_deep_v3.py`, `gw_cfree_head.py`) record the
  `(100,40)` gate as *failed* at `3.391e-102`, so the attribution is load-bearing
  — yet it sat outside the gate;
- the threshold is a property of the matrix at `(c, N) = (100, 40)`, but it was
  compared against runs at **any** `(c, N)` without complaint;
- the `VERDICT` line picked a winner even when neither side was below the gate.

Four changes:

| | change |
|---|---|
| **G1** | some side resolves below `lambda_min` (the old condition) |
| **G2** | *if* the mpmath side is being rejected (`d_mp >= GATE`), then `\|predicted − observed\| / observed <= 1e-6`. Otherwise G2 is reported explicitly as vacuous. |
| **provenance guard** | `(c, N) != (100, 40)` → refuse and return 2 *before* spending 16 minutes computing |
| **VERDICT** | prints `none — does not discriminate at this resolution` when `d_best >= GATE` |

Proof that the strengthened gate is not vacuous — three runs, all reproducible:

| run | purpose | result |
|---|---|---|
| `100 40 160 1000 224` | full certification | **PASS**, exit 0. G1 PASS (`3.912e-159 < 1.321e-102`), G2 PASS (`relative = 8.37662e-59 <= 1e-6`) |
| `100 40 40 100 32` | can it fail? | **FAIL**, exit 1. G1 FAIL, G2 FAIL (`relative = 1.0`), `VERDICT: none` |
| `100 4 50 20 32` | off-provenance | **REFUSED**, exit 2, before any quadrature |

### F1-Q — The reference gate passed 64 non-hex `sha256` characters  (CONFIRMED, FIXED)

`gw_verify_results.py` is documented as the gate to *"run after every engine
edit"*. Its digest test was:

```python
check(r["sha256"] and len(r["sha256"]) == 64,
      "%s sha256 must be a 64-hex digest" % tag)
```

A message promising a **64-hex digest**, backed by a **character count**. A
digest of 64 `z` characters reached `exit 0`. It was caught only by
`gw_verify_production.py` — the F1 add-on — which is exactly why F0's fault
injection did not surface it.

Two sibling defects of the same family, both of which *swallowed their own
failure message*:

- the fixture read was `json.load(open(path))` followed by `rows[0]`. A
  truncated, empty, or malformed fixture died with a stack trace, and every
  failure collected up to that point was **never printed**;
- a missing required key was recorded by `check()` and then immediately
  dereferenced on the next line, raising `KeyError`. The loop had just
  appended the failure; the traceback prevented it from ever being shown.

All three fixed: the read and the row count are guarded and become verdicts,
missing keys are recorded and the case is skipped, and the digest test is
`^[0-9a-fA-F]{64}$`. **No decision on valid data changed** — both baselines
still exit 0.

**Re-proof, isolated:** the fixture is restored and hash-verified *before every
mutant*, so no mutant can inherit another's damage.

| gate | mutants | result |
|---|---|---|
| `gw_verify_results.py` | 14 | **14 / 14 caught**, every one a clean `FAILURES` verdict |
| `gw_verify_production.py` | 14 | **14 / 14 caught**, every one a clean `FAILURES` verdict |

Before the fix the same isolated run read **13 / 14** for
`gw_verify_results.py`, with the 64-non-hex mutant the sole survivor, and
`schema: required key deleted` producing a traceback instead of a verdict on
*both* gates.

> **Methodological note.** A first, non-isolated attempt at this injection
> reported `8/8` for both gates. That figure is withdrawn: the script mutated
> the fixtures without restoring between iterations, so the sha256 row was
> reporting the previous mutant's outcome. The isolated table above is the
> figure of record.

### F1-R1 — The certificate's own hash tables went stale the moment F1 landed  (CONFIRMED, FIXED)

Every `| \`file\` | bytes | \`sha256\` |` row in `OMEGA_CORE_CERTIFICATE.md`
(38 rows) was recomputed against the working tree. Six did not match:

| section | file | recorded | on disk | cause |
|---|---|---:|---:|---|
| 6.1 | `gw_verify_results.py` | 4871 | 6343 | **F1** |
| 6.1 | `gw_verify_production.py` | 3248 | 8234 | **F1** |
| 6.6 | `gw_verify_production.py` | 3248 | 8234 | **F1** |
| 6.2 | `omega_core_v2_results.json` | 1971 | 1774 | snapshot (expected) |
| 6.2 | `omega_core_v2_run.log` | 3337 | 7177 | snapshot (expected) |
| 6.2 | `omega_core_v2_heartbeat.json` | 146 | 98 | snapshot (expected) |

The three F1 rows are the finding. F1 edited the gates, regenerated
`CHECKSUM.sha256` twice and re-ran every script — and never re-read the
certificate, so the one document whose job is to pin the code's bytes was the
one place still describing the pre-F1 bytes. A verifier following the
certificate to `gw_verify_results.py` would have computed a hash that matched
nothing on disk, and a manifest that *did* match would have looked like the
liar.

Two further claims in the same tables had also stopped being true:

* section 6.1's clone-portable bullet still said *"the checks performed are
  unchanged"* — F1-Q had just changed them;
* section 6.2 said the $N=400$ record "remains in this repository's git
  history", which cannot be inspected from a copy with no `.git` (F1-D), and
  described the working-tree `omega_core_v2_run.log` as now holding "the
  $N=800$ record" when it in fact holds **two appended runs**.

**Fixed.** Section 6.1 rows now carry the post-F1 size and SHA-256 with a
provenance bullet that names the change, the superseded hashes and F1-Q.
Section 6.6 keeps the 2026-10-01 bytes on purpose — that is the version that
ran that gate — and now states that it is *expected* not to match the working
tree, so a mismatch there is no longer ambiguous. Section 6.2 now discloses
that its three rows are the $N=400$ snapshot, records the two appended runs
with the line numbers of both headers and both verdicts, and marks the git
sentence as not verifiable here. A re-scan reports `match=34, MISMATCH=4,
missing=0`, and the four are exactly the rows now labelled as expected.

### F1-R2 — The manifest had a dead row and an uncovered file  (CONFIRMED, FIXED)

`CHECKSUM.sha256` listed `Framework.md`. That file exists nowhere under the
repository. Conversely it did **not** list the file that does exist under the
long title `Rigorous Ball Arithmetic and Bandwidth-Calibrated Spectral
Analysis of the Guinand-Weil Operator Framework.md` (11163 bytes), so a walk
of the tree would have found one row pointing at nothing and one file the
manifest never covered. Earlier F1 verification had checked hash/size
mismatch and "listed but missing" only for rows it could resolve — it never
compared the two name *sets*, so both defects were invisible to it.

**Fixed.** The dead row is dropped, the present file is hashed, and
`__pycache__/` is confirmed excluded in agreement with the repository's own
`.gitignore`. Whether the two names are a rename cannot be established from a
copy without `.git`, so **no rename is claimed**. Entry count stays 113.
Round-trip: `bad_format=0, rows=113, match=113, mismatch=0, dead=0,
unlisted=[], TOTAL FILES OK`, manifest `BOM=False, LF, pure ASCII`.

### F1-R3 — Two documented invocations were wrong  (CONFIRMED, FIXED)

* `README.md` §7 ran `python gw_verify_results.py smoke_results.json`, but
  that script takes **no argument** — fixtures come from `GW_FIXTURE_DIR` or
  the script's own directory, as its comment says and as README §8 already
  stated. The argument was silently ignored, so the README contradicted
  itself between §7 and §8.
* `REPO_STRUCTURE.md` advertised `python gw_final_gate.py c N dps R GL` as if
  the gate took free arguments. F1-P's `(c,N)` provenance guard made that
  false: any other `c`/`N` now exits 2 before a single quadrature is done.

Both now match the code.

**Operational note, not a defect.** `msaf_visual.py` ends in `plt.show()`, so
a plain run blocks forever waiting for a plot window. It must be run headless
(`MPLBACKEND=Agg`) for an exit code; that is how it was verified here.

### F1-R4 — `PROVENANCE.txt` had ten rows that no longer resolve  (CONFIRMED, FIXED AT THE SITE)

The same scan that caught F1-R1 was widened from the certificate to every
document in the sub-repo. `PROVENANCE.txt` reported **10** hash rows that do
not match the working tree:

| section | file | recorded → now | cause |
|---|---|---|---|
| 6.1 | `gw_omega_core_v2.py` | 24981 → 34145 | engine grew 2026-09-30 |
| 6.1 | `gw_launch_v2.ps1` | 2300 → 3477 | comment-only edit 10-01 |
| 6.1 | `gw_check_refs.py` | 1729 → 1985 | clone-portable 10-01 |
| 6.1 | `gw_verify_results.py` | 4561 → **6343** | **F1-Q** |
| 1 | `gw_mont_pipeline_check.py` | 11973 → **12706** | **F1-J** |
| 6.2 | `omega_core_v2_results.json` | 1971 → 1774 | overwritten by N=800 |
| 6.2 | `omega_core_v2_run.log` | 3337 → 7177 | two runs appended |
| 6.2 | `omega_core_v2_heartbeat.json` | 146 → 98 | overwritten by N=800 |
| 6.3 | `omega_v2_sysmon.log` | 48685 → 526181 | live log at snapshot |
| 6.3 | `omega_core_v2_watchdog.log` | 145997 → 593637 | live log at snapshot |

Eight of those are honest: the file says `Generated : 2026-09-27` at the top
and `Snapshot : 2026-09-29` before §6, and a snapshot that matched the current
tree would be a snapshot of nothing. **The other two are F1's**, and one of
them carried a claim that F1 itself had already voided: §1 asserted that
`gw_mont_pipeline_check.py`'s defect 18 was *"intentionally LEFT UNCHANGED so
that log and code stay mutually consistent"* — F1-J changed that file.

**Fixed at the site, not by rewriting the snapshot.** Section 8 was added,
dated, listing all ten rows with causes and pointing at where current bytes
live; the `LEFT UNCHANGED` sentence carries a retraction marker where it stands
instead of being struck, so a reader of §1 still sees what was intended on
2026-09-27. Sections 1–5 were not edited.

The widened scan also cleared the rest of the tree: across all sub-repo
documents only **4** hash rows remain unmatched, exactly the four now labelled
as expected in §6.2 and §6.6. Fifteen other 64-hex tokens match no file, and
all are accounted for: the vendored upstream source hash (7×), the superseded
N=400 snapshot hashes (3 documents ×3), two content-address hashes of JSON
objects rather than files, and one 64-*digit* decimal lambda value that is not
a hash at all.

---

## 3. Change record

| file | change |
|---|---|
| `VISUALISASI_MATRIKS_FORMAL.md` | 63 control chars restored; 5 swallowed `\right`/`\neq` rejoined; 14-line generator script removed; 5 pmatrix separators `\ ` → `\\`; `Delta_univ` corrected to `1{,}836653` + significant-figure note; F1-N precision-inertness note added |
| `01_PARADOX_AND_SCALE.md` | 2 TABs → `\to` |
| `README.md` | 2 TABs → `\to` |
| `Skill.md` | §3 `1{,}836{,}653` typo; §3 `Delta_univ` significant figures; §3 `lambda_min` status → *N=800 machine-gated, N=400 log-recorded only*; §1 `msaf_visual.py` description → precision-inert |
| `Brain.MD` | §1 `msaf_visual.py` row → flat-to-58-d.p.; plus the F1-B/F1-D/F1-H/F1-I syncs recorded in F0-line items |
| `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md` | 9 numeric corrections in §2 (`zeta(s_kritis)`, `Im`, `\|Delta zeta\|`, gradient ratio, 5-row table) |
| `msaf_zeta_check.py` | **new** — reads the DRAF §2 claims *from the document* and gates C1–C7; exit 0/1/2 |
| `msaf_visual.py` | constant declared as recorded (not simulated); 2-sf printout; F1-N analytic span / float64 span / bits-per-decade printout; flat-curve annotation; two self-inflicted bugs fixed (`{:.2e}` → `{:.1e}`, float64 differencing → analytic) |
| `gw_verify_results.py` | guarded fixture read + row count; missing required keys recorded and skipped instead of `KeyError`; `sha256` now `^[0-9a-fA-F]{64}$` (its message already claimed 64-hex) |
| `gw_verify_production.py` | `deep_invariants()` on fixtures and production; KeyError-proof `get()`; docstring synced to state that F1 edited the reference gate |
| `gw_final_gate.py` | G1+G2, `(c,N)` provenance guard, resolution-aware `VERDICT` |
| `gw_mont_pipeline_check.py` | anchored to its own directory |
| `guinand-weil-rigorous-numerics-main/gw_final_gate_run.log` | **new** — full PASS run, the F1 proof artifact |
| `guinand-weil-rigorous-numerics-main/CHECKSUM.sha256` | regenerated: 112 → **113** entries, 4 hashes updated, 1 file added, F1 header note appended (the first attempt defined the note but never inserted it — caught on re-inspection) |
| `guinand-weil-rigorous-numerics-main/OMEGA_CORE_CERTIFICATE.md` | 6.1 rows re-pinned to post-F1 bytes + provenance bullet with superseded hashes; 6.6 row labelled as deliberately historical; 6.2 discloses the N=400 snapshot, the two appended runs, and the unverifiable git sentence |
| `guinand-weil-rigorous-numerics-main/README.md` | §7 dropped the silently ignored argument from the `gw_verify_results.py` invocation |
| `guinand-weil-rigorous-numerics-main/REPO_STRUCTURE.md` | `gw_final_gate.py` row records the `(c,N)` provenance lock and the 0/1/2 exit codes |
| `guinand-weil-rigorous-numerics-main/CHECKSUM.sha256` | regenerated again: dead `Framework.md` row removed, the long-titled file added, `__pycache__/` excluded, F1-R1 note appended; 113 → 113, round-trip clean |

No numeric literal certified by any result file was altered. The gate threshold
`lambda_min = 1.32105051975e-102` is unchanged.

---

## 4. Verification matrix

| check | tool | result |
|---|---|---|
| Anti-Circularity self-test | `tests/run_tests.py` | **13 / 13 PASS**, exit 0 |
| Anti-Circularity `check` | `gate.py check` | `GENUINE`, `core=[0]`, FAIL=0 NOT_RUN=0, **PASS**, exit 0 |
| Anti-Circularity `claim` | `gate.py claim` | FAIL=0 NOT_RUN=0, **PASS**, exit 0 |
| SMT side conditions | z3 4.16.0 / z3py 5.0.0 | `script=unsat`, `ctx=sat`, needs 0 axioms |
| `gw_verify_results.py` | mpmath | `ALL JSON INVARIANTS PASS`, exit 0 |
| `gw_verify_production.py` | mpmath | `ALL JSON INVARIANTS PASS (fixtures + production N=800)`, exit 0 |
| `msaf_zeta_check.py` | mpmath `dps=100` | `GATE: PASS — every Section 2 claim reproduced at its stated precision`, exit 0 |
| `msaf_visual.py` | numpy + matplotlib (Agg) | exit 0; 7 identical points; analytic span `-8.846e-59`, float64 `0.000e+00`, `1.809e+62` bits/decade |
| `gw_mont_pipeline_check.py` | subprocess | exit 0 **from a foreign cwd** (F1-J re-proven) |
| `gw_final_gate.py 100 40 160 1000 224` | mpmath | **GATE: PASS**, exit 0; G1 + G2 both satisfied |
| `gw_final_gate.py 100 40 40 100 32` | mpmath | **GATE: FAIL**, exit 1 (can it fail?) |
| `gw_final_gate.py 100 4 50 20 32` | mpmath | **REFUSED**, exit 2 (provenance) |
| fault injection, 20 variants | `harnesses\f1_mut.py` | baseline PASS, **19 / 19 mutations caught**, clean `FAILURES` output, no tracebacks |
| fault injection — `gw_verify_results.py` | 14 isolated mutants | **14 / 14 caught**, clean verdicts, fixture byte-identical after every restore |
| fault injection — `gw_verify_production.py` | 14 isolated mutants | **14 / 14 caught**, clean verdicts, fixture byte-identical after every restore |
| fault injection — `msaf_zeta_check.py` | 5 mutants across 2 rounds | **5 / 5 caught** (wrong value, tampered gradient, tampered table row, tampered imaginary part, *deleted claim*), DRAF byte-identical after every round, baseline + restored exit 0 |
| certificate hash scan (F1-R1) | sha256 recompute over 38 rows | 6 mismatches found: **3 were F1's own stale rows** (fixed), 3 are the N=400 snapshot rows, now labelled expected; re-scan `match=34, MISMATCH=4, missing=0` |
| manifest name-set diff (F1-R2) | disk walk vs manifest | dead `Framework.md` row and one uncovered long-titled file, both **0 / 0** after the fix |
| documented invocations (F1-R3) | read vs. code | `README` §7 argument removed (it was ignored); `REPO_STRUCTURE` records the `(c,N)` lock |
| control-character scan | workspace-wide | 0 remaining in the 3 repaired files; DRAF 21/21 legitimate tabs; PDF form feeds are page breaks |
| `CHECKSUM.sha256` round-trip | sha256 recompute | 113 entries, **0** hash/size mismatches, **0** dead rows, **0** unlisted files, `TOTAL FILES` matches, pure ASCII, no BOM, LF |
| encoding of every touched file | strict UTF-8 | **19 / 19 `utf-8-OK`**, `BOM=False`, `CRLF=0` except the CRLF run log written by Python (as `.gitattributes` documents); DRAF's 21 control chars are its legitimate table tabs |

---

## 5. Residual — recorded, not closed

1. **F1-H provenance — CLOSED by F2-3.** `zeta_pixel_producer.py` now
   produces `Re = 1.43864420885e-62`, `Im = 2.2903036742e-63`,
   `|Delta zeta| = 1.45676081388e-62` from first principles: `rho_1` from
   `mpmath.zetazero(1)` at 100 dps (not a 14-digit literal — that variant leaves
   `zeta(s_kritis)` near 5e-16 instead of 6e-102), `Delta_univ` as the exact
   quotient of the two declared inputs, and every published figure read back out
   of the DRAF and compared at its own significant figures **and** checked for
   correct rounding. The derivation is written to `zeta_pixel_results.json`, and
   `msaf_zeta_check.py` check C9 now makes that artifact a condition of passing:
   it must exist, say PASS, carry this run's `rho_1`, agree with the document,
   and be internally consistent component by component. Fault injection:
   **14/14 mutants caught, 3/3 controls correct** — reproducible from
   `harnesses/f2_3_inj.py` (2026-10-06).
2. **F1-D — `N = 400` — CLOSED by F2-7.** The value is now machine-gated
   rather than merely recorded. The `N = 400` target was re-run on 2026-10-05
   (8 h 28 m; escalation 9000 → 18000 bits stopping at pivot 723 with
   `undetermined_pivot=723`, exactly as the certificate predicts) and ships as
   `omega_core_v2_results_N400.json` (2223 bytes, file sha256 `bab3e5f3…`,
   `n_pos=801`, `n_neg=0`, `undetermined_pivot` null, `anomalies` and `caveats`
   empty, `non_result` false). `gw_verify_production.py` accepts it as
   `argv[2]`, applies the certified-row invariants to it, and on every run
   reproduces all three documentary records from their own files — log line 51
   at 25 sf, `PROVENANCE.txt` §6.2 and certificate §4 at 30 sf — each at its
   own digit count with a 1e-20 relative tolerance: exit 0. Fault injection:
   **26/26 mutants caught and 4/4 missing-document cases reported as FAILURES
   without a traceback**, every case leaving both shipped result files
   byte-identical. Detail: `F2_REPORT.md` §7. Reproducible from
   `harnesses/f2_7_inj.py` (2026-10-06).
    The `GW_STATUS` "stayed in HEAD" sentence remains **NOT ESTABLISHED** in
    this workspace. *(F1's stated reason — "because there is no `.git`" — held
    only until A6, 2026-10-06: the workspace is a repository since then, but its
    history begins at the A6 commit and holds no such merge. See F5-R5.)*
3. **F1-L — `Z_none` labelling — CLOSED by F2-2.** One definition of record
   (`DEFINISI_OPERASIONAL_MSAF.md` §1), the DRAF table re-labelled to read
   `OUTSIDE` with a reading note, the manifesto and the plot title corrected,
   and `znone_check.py` gating all five documents. Fault injection:
   **15/15 mutants caught, 3/3 controls correct**, every file restored
   byte-identical. Reproducible from `harnesses/f2_2_inj.py` (2026-10-06).
   Detail in `F2_REPORT.md` §2.
4. **F1-N — plot semantics — CLOSED by F2-6.** The design question is answered:
   **the `p` axis stays.** The inertness over a *stated range* is the finding, so
   dropping the axis would hide which range was examined; plotting the analytic
   residual instead would autoscale a 1e-58 span into a confident diagonal that
   invites the opposite reading. What F2-6 actually fixed is that the panel was
   **not self-contained** — the float64-observed span and the bits-per-decade
   figure were printed to stdout only, and the two `axvline` markers were
   labelled as if the curve moved through them (the same defect F1-N found in
   `Brain.MD`'s prose). The figure now carries all three numbers and labels both
   markers `certificate: …`, gated by `visual_check.py`, which **renders the
   figure and inspects the drawn artists** rather than grepping the source.
   Fault injection: **11/11 mutants caught, 3/3 controls correct** —
   reproducible from `harnesses/f2_6_inj.py` (2026-10-06).
5. **`SOLVABLE_FINITE_PARADOX.md` Landauer sentence — CLOSED by F2-1.** The
   sentence removed in F0 has been re-derived rather than re-asserted: section 3
   now carries `k_B ln 2 = 9,5699296 × 10^-24 J/K`, floors of
   `2,6078058 × 10^-23 J` at 2,725 K and `2,8709789 × 10^-21 J` at 300 K, and an
   explicit statement that **no energy total is claimed** because no erasure
   count exists. Section 1.B links to it. `landauer_check.py` reads all of that
   out of the document and recomputes it at 100 dps; it also gates the same claim
   in `ANTI_INFINITY_BLINDSPOT.md` and `MSAF_COSMOLOGY_DECONSTRUCTION (2).md`,
   where the premise had been missing and the word *absolutely* had been used.
   Fault injection: **28/28 claim mutants caught, 6/6 controls correct**, every
   file restored byte-identical afterwards — reproducible from
   `harnesses/f2_1_inj.py` (2026-10-06). Scope note for the record: sections
   §2 and §4 of that document never carried a thermodynamic claim, so the
   §1.B/§2/§3/§4 wording above was broader than the defect actually was.

---

## 6. Retractions and corrections

Openly, as required by the workspace protocol:

| what was stated | what is now stated |
|---|---|
| `Delta_univ = 1,836653 × 10^-62` as measured precision | the quotient is exact *given the inputs*; `D_obs` carries 2 sf, so only `1.8 × 10^-62 ± 0.568 %` is observational |
| `N_steps ≈ 5,4 × 10^61`, product `= 0,99` | `N_steps = 5.444685399e61`; the product is 1 by definition |
| `R_tail` "decays vs bit precision" | `R_tail` is **flat** across 2000–18000 bits to 58 decimal places; `1.809e+62` bits are needed for one decade |
| "gradient ratio ≈ 1,01" | `|zeta'(rho_1)| = 0.793160433357` |
| `zeta(s_kritis) ≈ 3,187e-97 − 2,001e-96 i` | `−6.1299e-102 + 3.8505e-101 i` (the original does not reproduce) |
| `gw_final_gate.py` listed under *Validation* without a working exit code | the threshold decides the exit status; two conditions, both gated |
| `lambda_min` at `N = 400` presented as a result | log-recorded only; not machine-gated |
| `msaf_visual.py` stem values "from real 100 DPS simulation data" | recorded constant, no `zeta` call in the file, gated externally by `msaf_zeta_check.py` |
| `1{,}836{,}653 × 10^-62` in `Skill.md` §3 | `1{,}836653` |
| `OMEGA_CORE_CERTIFICATE.md` §6.1 as pinning the shipped bytes | it still pinned the **pre-F1** bytes of two gates after F1 edited them, and its provenance bullet still claimed the checks were unchanged; re-pinned, superseded hashes recorded |
| `CHECKSUM.sha256` as covering every tracked file | it listed a `Framework.md` that does not exist and omitted the file present under its long title;
| `ANTI_INFINITY_BLINDSPOT.md`: "to process every bit ... a minimum energy dissipation is required" | Landauer charges irreversible **erasure**, not processing; the infinite-total conclusion is now labelled a premise, not a measurement |
| DRAF table rows labelled "NON-EXISTENCE ZONE (Falsified)" | those rows are at $n\,\Delta_{\text{univ}}$, $n = 1..5$, i.e. **outside** $\mathcal{Z}_{\text{none}}$; the label now says so, and the zone itself is never evaluated |
| `msaf_visual.py`: "Zone of Non-Existence Beyond the Critical Line 0.5" | the plotted points are the same five outside-zone shifts; retitled as a sweep outside the zone |
| `CONSOLIDATED_MASTER_MANIFESTO.md`: zone = "domain below $10^{-62}$" | a magnitude is not a set; the open-pixel set is stated and the glossary is named the definition of record |
| `MSAF_COSMOLOGY_DECONSTRUCTION (2).md`: the purge "**absolutely** emits a minimal heat dissipation" | the bound is conditional on irreversibility; the floor is evaluated at the document's own T as `2,6078058 × 10^-23 J` per bit, and no total is claimed | both corrected, count still 113 |

Nothing in this report was edited silently; every superseded value above was
replaced at its source and the source re-verified afterwards.

---

## 7. Exit

F1 exits **complete**. All four closable residual items are now closed, each by the phase that closed it and recorded above rather than deleted: items 5 and 3 by F2-1 and F2-2, item 4 by F2-6, and item 2 (`N = 400`) by F2-7. The `GW_STATUS` "stayed in HEAD" sentence remains the one item that no phase can close, because this tree has no `.git`.

F1-R1 was found by re-reading the deliverables after F1 appeared to pass, i.e. by
auditing the audit: every hash table and every documented command the report
itself relied on was recomputed against the working tree. The lesson recorded
for F2 is that **regenerating the manifest is not the same as re-reading the
certificate** — three documents had to agree and only one had been checked.

The Anti-Circularity Gate was run as the last action of F1, after every file
above was final: self-test `13/13`, `gate check` → `GENUINE`, `core=[0]`,
verdict **PASS**.
