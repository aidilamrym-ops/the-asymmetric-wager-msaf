# Repository Directory Schema

**Project:** OMEGA Framework — Certified Enclosure of Guinand–Weil Matrices at Extreme Scale
**Author:** Muhammad Aidil Amry · ORCID 0009-0002-9718-9710
**Affiliation:** Independent Researcher | South Sulawesi, Indonesia

Target repository: `aidilamrym-ops/guinand-weil-rigorous-numerics` (public).
`omega-guinand-weil` was the working title used when this schema was drafted;
the repository was published under the name above.

Every path below maps to a file that **exists on disk today**. Nothing is
listed that has not been produced by an executed run.

```
omega-guinand-weil/
│
├── README.md                       # repository front page (generated)
├── WORKING_PAPER.md                # preprint draft (generated)
├── REPO_STRUCTURE.md               # this file
├── CITATION.cff                    # machine-readable citation metadata
├── LICENSE                         # MIT — source code
├── LICENSE-DOCS.md                 # CC-BY-4.0 — scholarly documents
├── LICENSING.md                    # the hybrid split, rationale, attribution
│
├── src/                            # 30 gw_*.py + 2 probe_*.py — ENGLISH, as executed
│   │
│   ├── core/                       # construction of Q_inf and its closed forms
│   │   ├── gw_qinf.py                # build_blocks. LINE 47 sets mp.mp.dps=40 at module
│   │   │                             #   level (LANDMINE). LINE 94 calls mp.lerchphi (defect).
│   │   ├── gw_full_vs_even.py        # full_matrix() — full vs even-sector assembly
│   │   ├── gw_v0_exact.py            # exact V0 / leading term
│   │   ├── gw_deep_v2.py             # closed_dpsi, closed_psi — the SHIPPED closed forms
│   │   └── gw_deep_v3.py             # lerchphi_series() — the CORRECTION
│   │
│   ├── gates/                      # identity validation: integral vs closed form
│   │   ├── gw_final_gate.py          # the psi / psi' gate; `python gw_final_gate.py c N dps R GL`
│   │   │                             #   (F1: provenance-locked to the certified
│   │   │                             #    c=100, N=400 -- other c/N exit 2 before
│   │   │                             #    any quadrature; exit 0 pass / 1 fail)

│   │   ├── gw_closed_third.py        # third closed-form cross-check
│   │   ├── gw_arch_check.py          # archimedean baseline sweep in R
│   │   ├── gw_arch_diag.py           # asymptotic diagnostics
│   │   ├── gw_head_diag.py           # head-region diagnostics
│   │   ├── gw_tail_deep.py           # tail via adaptive IBP
│   │   └── gw_panel_diag.py          # per-panel quadrature localisation
│   │
│   ├── eigenspectrum/              # eigenvalue routes and cross-checks
│   │   ├── gw_corrected_eig.py       # corrected build + phases 1-6 (incl. phase_arb)
│   │   ├── gw_compare_builds.py      # SHIPPED vs CORRECTED, same code path
│   │   ├── gw_lam_dps.py             # lambda_min vs dps precision ladder
│   │   ├── gw_det_check.py           # determinant route vs eigensy route
│   │   ├── gw_degeneracy.py          # exact zero eigenspace of the pole block
│   │   ├── gw_spectrum_detail.py     # full eigenvalue listing
│   │   ├── gw_c100_probe.py          # c=100 behaviour probe
│   │   └── gw_cfree_head.py          # c-free head formulation
│   │
│   ├── certified/                  # OMEGA A1 / A2 — ball arithmetic
│   │   ├── probe_flint_eig.py        # API audit: what flint 0.9.0 actually exposes
│   │   ├── probe_arb_rad.py          # API audit: attaching an explicit radius to an arb
│   │   ├── gw_arb_sweep.py           # uniform-radius sweep -> rho* via Weyl
│   │   ├── gw_arb_measured.py        # measured per-entry radii -> FLINT eigen-solver
│   │   ├── gw_entry_error.py         # dps-doubling entry-error measurement
│   │   ├── gw_entry_audit.py         # delta-versus-matrix audit, full -N..N scan
│   │   └── gw_lerchphi_regime.py     # defect regime map over dps
│   │
│   ├── ladder/                     # goal C — the c=13 ladder, fit-only
│   │   ├── gw_ladder_analysis.py
│   │   ├── gw_ladder_ext.py
│   │   └── gw_model_final.py
│   │
│   └── goals/                      # goals A, B, D, E
│       ├── gw_band.py                # goal D — B_T and the band [-B_T, 0)
│       ├── gw_worked_example.py      # goal E — second external anchor
│       └── gw_model_final.py         # (shared with ladder/)
│
├── data/                           # saved intermediate artefacts
│   ├── gw_matrix_100_40_dps180.json   # corrected 81x81 matrix, dps 180, 180-digit strings
│   └── README.md                     # provenance of every JSON: command that produced it
│
├── logs/
│   ├── GW_STATUS_2026-09-26.md       # CANONICAL status report
│   │                                   #   §7  eigen FINAL
│   │                                   #   §7a RETRACTED
│   │                                   #   §7b root-cause log
│   │                                   #   §7c OMEGA A1/A2 execution
│   ├── ladder_bn.txt                 # ladder raw output
│   ├── ladder_fix.txt                # ladder raw output
│   └── run/                          # captured stdout of every command cited in the paper
│
├── proofs/                         # INTENTIONALLY EMPTY — see TRACK_C.md
│   └── TRACK_C.md                    # Lean 4 / Z3 integration plan; STATUS: NOT STARTED
│
├── docs/
│   ├── EPISTEMIC_RULES.md            # the dy gate, the override, the floor test rejection
│   ├── RETRACTIONS.md                # all 8 retracted claims, kept not deleted
│   ├── API_AUDIT.md                  # flint 0.9.0 capability matrix
│   └── IDENTITY_DEPTHS.md            # psi / psi' residuals at every precision run
│
└── scripts/
    └── update_registry.py
```

> **Tree superseded as of 2026-09-29 / 2026-10-02** (details in the
> postscript below): the repository is flat-root, and the `proofs/` entry with
> `TRACK_C.md STATUS: NOT STARTED` was never produced as drawn -- Track C
> instead shipped in the root on 2026-10-02 (`OMEGATrackC.lean` and friends).
> The tree is left unedited as the original proposal record.

## Inventory as executed

| category | count |
|---|---:|
| `gw_*.py` (canonical) | **30** |
| `probe_*.py` (API audits) | 2 |
| `ladder_*.txt` (raw logs) | 2 |
| status reports | 1 (`GW_STATUS_2026-09-26.md`, 37 kB) |
| JSON matrices in `data/` | 1 (`gw_matrix_100_40_dps180.json`) |

All 30 `gw_*.py` plus both probes pass `py_compile`. SHA256 of the working
copies matches the canonical copies byte-for-byte.

> **Superseded by the current inventory in the postscript below (2026-10-02).**
> This table is the 2026-09-29 proposal state and is deliberately left
> unedited; the counts, the file sizes and the `data/` layout it states no
> longer describe the published repository.

## What goes in `proofs/` -- reserved, never created

The proposal reserved a `proofs/` directory whose only content would have
been `TRACK_C.md`, the Lean 4 / Z3 integration plan. **That directory was
never created and `TRACK_C.md` was never written.** As of the 2026-09-29
proposal, **no proof assistant had been run on any claim in this
repository** -- which is exactly why the directory was left empty rather than
filled with a placeholder. The reasoning behind an empty
directory -- that an empty folder must not be mistakable for a completed one
-- is honoured by saying this outright instead of shipping a placeholder.

> **Superseded 2026-10-02.** Track C was later shipped *flat in the root*
> (`OMEGATrackC.lean`, `track_c_make_smt.py`, `track_c_side_conditions.smt2`
> and the two logs), not under `proofs/`; `lean` and `z3` have since been run
> on the seven side conditions. The `proofs/` directory and `TRACK_C.md` were
> still never created. See *Files added 2026-10-02* below and README §4.1.


---

## Postscript (2026-09-29) -- layout as actually published

The tree above was written against the original *nested* proposal. The
repository as published is **flat-root**: every file sits directly in the
repository root, with no `src/`, `data/`, `logs/`, `proofs/`, `docs/` or
`scripts/` directories. README path references were flattened to match
(commit `8ec0745`); this file is corrected here rather than rewritten, so the
original proposal stays auditable.

Consequently the sentence "Every path below maps to a file that exists on disk
today" no longer holds for the **directories** it names. It also no longer
holds for **six files** the tree above lists, none of which was ever produced:

| promised in the tree | status |
|---|---|
| `docs/EPISTEMIC_RULES.md`, `docs/RETRACTIONS.md`, `docs/API_AUDIT.md`, `docs/IDENTITY_DEPTHS.md` | **never written** -- the material they would hold is inside `GW_STATUS_2026-09-26.md` (§2 rules, §7c/§7h retraction and defect tables, the `flint` 0.9.0 API facts) and `OMEGA_CORE_CERTIFICATE.md` 5.1 |
| `data/README.md`, `logs/run/` | **never created** -- captured stdout is shipped flat, under its own file names |
| `data/gw_matrix_100_40_dps180.json` | **never shipped** -- README §7 states the dps-180/260 inputs of record are not in this repository; the shipped matrix is `gw_matrix_100_200_dps400.json` in the root |

They are recorded here as *promised and not produced* rather than silently
dropped, so a reader can tell the difference between a missing document and a
forgotten one. `proofs/` never existed as a directory at all, and `TRACK_C.md`
was never written -- that part still holds. What no longer holds is the
companion claim that no proof assistant has been run: Track C was shipped into
the repository root on 2026-10-02, where `lean` compiled `OMEGATrackC.lean`
and `z3` discharged the seven side conditions (README §4.1, and
`track_c_lean_verify.log` / `track_c_smt_z3.log`).

### Files added 2026-09-29 (OMEGA-CORE chain)

| file | role |
|---|---|
| `OMEGA_CORE_CERTIFICATE.md` | matrix definition, zero-fudging architecture, the $N=400$ certificate, telemetry schema, byte-hash inventory |
| `gw_omega_core_v2.py` | the engine: interval $LDL^T$, auto-escalation, three anomaly gates |
| `gw_sysmon.ps1` | 60 s system telemetry + ALERT taxonomy (log-and-continue) |
| `gw_watchdog.py` | 60 s liveness watcher against the JSON heartbeat |
| `gw_launch_v2.ps1` | detached launcher |
| `gw_check_refs.py` | static reference gate (pre-run) |
| `gw_verify_results.py` | JSON invariant gate (post-run) |
| `omega_core_v2_results.json` | the $N=400$ certificate |
| `omega_core_v2_run.log` | forensic run log, VERDICT lines |
| `omega_v2_sysmon.log`, `omega_core_v2_watchdog.log`, `omega_core_v2_heartbeat.json` | telemetry snapshot |
| `*_FAILED_absbug_*` (5 files) | the failed run, kept as audit trail |
| `smoke*` (6 files) | both smoke gates, green |

`omega_v2_sysmon.log` and `omega_core_v2_watchdog.log` were **live logs**
snapshotted while the $N=800$ target was still running; at the 2026-09-29 cut
their hashes described that instant. The sweep has since completed and both
logs are final (superseded entries below; authoritative bytes: certificate
sections 6.3 and 6.6).

### Files added 2026-09-30 / 2026-10-01 (checkpointing + the N=800 certificate)

| file | role |
|---|---|
| `gw_ckpt.py` | build / $LDL^T$ checkpoint serializer used by `--ckpt` |
| `gw_verify_production.py` | production-row invariant gate: applies the same invariants to **both** shipped result rows, and (F2-7) cross-checks the $N=400$ bound against `PROVENANCE.txt` 6.2, `OMEGA_CORE_CERTIFICATE.md` 4 and `omega_core_v2_run.log` 51, each at that record's own significant-digit count; parses with `mpmath` because float64 underflows a $10^{-2877}$ bound |
| `gw_ldlt_probe.py`, `ldlt_probe_100_100.json` | pivot-ball probe used to size the $N=800$ precision |
| `omega_v2_stdout.txt` | captured verdict stream of the certified $N=800$ run |
| `wd_selftest.log` | watchdog self-test record |
| `Rigorous Ball Arithmetic and Bandwidth-Calibrated Spectral Analysis of the Guinand-Weil Operator Framework.md` | the working-paper manuscript |

Supersessions inside existing files (authoritative detail: `OMEGA_CORE_CERTIFICATE.md` 6.1/6.6, `PROVENANCE.txt` 6.8/6.9):

* `omega_core_v2_results.json` now holds the **$N=800$** record (1601/1601
  certified, VERIFIED POSITIVE DEFINITE). The $N=400$ bytes of 2026-09-29
  remain in this repository's git history (commit `e65319d`, file sha256
  `5aaab0cf...`) -- the line above that calls the file "the $N=400$
  certificate" describes the 2026-09-29 state.
* `omega_core_v2_run.log`, `omega_core_v2_heartbeat.json` and the two
  telemetry logs are the **final** state of the completed sweep
  (2026-10-01 21:06), not the mid-run snapshot; final sizes and hashes:
  certificate 6.3 / 6.6.
* `gw_check_refs.py`, `gw_verify_results.py` and `gw_verify_production.py`
  resolve paths relative to their own file since 2026-10-01 (clone-portable;
  `argv[1]` / `GW_FIXTURE_DIR` overrides), and the `gw_launch_v2.ps1`
  comment's archive reference was corrected to the verifiable commit
  `e65319d`. Argument lists and executed runs are unchanged -- certificate
  6.1, PROVENANCE 6.9.

### Files added 2026-10-05 (F2-7 -- the $N=400$ artefact ships)

| file | role |
|---|---|
| `omega_core_v2_results_N400.json` | the regenerated $N=400$ certificate (801/801 certified, VERIFIED POSITIVE DEFINITE), shipped for the first time |
| `omega_core_v2_run_N400.log` | forensic log of the 2026-10-05 $N=400$ run |
| `omega_core_v2_heartbeat_N400.json` | heartbeat of that run (final state `sweep:complete`) |

`omega_core_v2_results.json` still holds the $N=800$ record. The $N=400$
row is now read from its own file by `gw_verify_production.py` (`argv[2]`),
which also cross-checks it against `PROVENANCE.txt` 6.2, certificate 4 and
`omega_core_v2_run.log` line 51. The 2026-09-29 $N=400$ bytes remain in the
supersessions list above.

Deliberately **not** shipped from this repository: `ckpt_N400/`
(`build.ckpt`, `ldlt.ckpt` and their two `.time` files,
1,362,311,376 bytes) -- the resume state the 2026-10-05 $N=400$ run
left behind after reaching `sweep:complete`. It is excluded from
`CHECKSUM.sha256` for the same reason `D:\gw_ckpt` is excluded from
the $N=800$ certificate: a checkpoint is machine-local resume state,
not evidence. The evidence is `omega_core_v2_results_N400.json`.

Deliberately **not** shipped from the working folder: `gw_omega_core.py` (v1
engine, superseded by `gw_omega_core_v2.py` and referenced nowhere in this
repository), `*.bak_*` CTP backups, and `task_backup_*.xml` (machine-local
scheduled-task export).

### Files added 2026-10-02 (Track C)

| file | role |
|---|---|
| `OMEGATrackC.lean` | 10 theorems: the Rayleigh/Weyl perturbation inference plus 7 side conditions as exact `ℚ` arithmetic |
| `track_c_make_smt.py` | cross-checks the constants README ↔ Lean, emits `track_c_side_conditions.smt2`, drives `z3` |
| `track_c_side_conditions.smt2` | generated `QF_NRA` file: one assertion, the conjunction of the 7 negations |
| `track_c_smt_z3.log` | `z3` answers, per negation and for the conjunction |
| `track_c_lean_verify.log` | `lean` build exit code + `#print axioms` for all 10 theorems |

These sit in the **root**, not in a `proofs/` directory -- the repository keeps
its flat layout, and the promised `proofs/TRACK_C.md` plan file remains
unwritten (recorded as such, not silently replaced). The two logs are shipped
as evidence of runs that actually happened on 2026-10-02; what the module does
*not* cover is stated in README §4.1 (the literals come from the FLINT/Arb
stage and are not re-derived inside Lean).

### Files added 2026-10-02 (source-hash gate rerun)

| file | role |
|---|---|
| `gw_even_vs_src_100_200_rerun_20261002.log` | full rerun (exit 0, 339 s) of `gw_even_vs_src.py 100 200 400 2000` after that script was taught to pin **both** copies of the vendored source; reproduces $\delta$, $\delta_{\rm rel}$, the median ratio and the `V1` verdict **identically** to `gw_even_vs_src_100_200.log` |

The original `gw_even_vs_src_100_200.log` is kept unedited -- it records the
2026-09-27 state, when the working copy was still byte-identical to upstream.
Which copy exists where, and why both logs are honest:
`THIRD_PARTY_SOURCES.md` §1, `PROVENANCE.txt` §6.10, certificate §1/§6.1.

### Current inventory (measured 2026-10-02)

Counted from `git ls-files` on the published tree; supersedes the proposal
table above, which is left untouched as the 2026-09-29 record.

| category | count |
|---|---:|
| tracked files (manifest covers 112 + `CHECKSUM.sha256` itself) | **113** |
| `*.py` -- all pass `py_compile`, 0 failures | **52** |
| `gw_*.py` | 47 |
| `probe_*.py` | 2 |
| other `*.py` (`source_arb_ldlt_certify.py`, `update_registry.py`, `track_c_make_smt.py`) | 3 |
| `*.md` | 10 |
| `*.log` (forensic run logs, shipped on purpose) | 22 |
| `*.json` | 12 |
| `*.ps1` | 2 |
| `*.lean` (Track C) | 1 |
| `*.smt2` (Track C, generated) | 1 |
| working-tree size | 64.64 MB (67776166 bytes) |

Verification re-run on this date: `python gw_check_refs.py`,
`python gw_verify_results.py`, `python gw_verify_production.py` -- **all exit
0**; `python track_c_make_smt.py` -- **exit 0** (`unsat` 7/7 + combined,
literal cross-check `MATCH` 3/3); `lean OMEGATrackC.lean` -- **exit 0** with
axiom footprint `[propext, Classical.choice, Quot.sound]` on all 10 theorems;
`python gw_even_vs_src.py 100 200 400 2000` -- **exit 0**, verdict `V1`, log
`gw_even_vs_src_100_200_rerun_20261002.log`; `CHECKSUM.sha256` re-verified
against every listed file -- **0 hash or size mismatches**.