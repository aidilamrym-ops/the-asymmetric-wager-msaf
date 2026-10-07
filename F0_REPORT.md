# F0_REPORT — Anti-Circularity Audit of the `verified` / `unsat` Claims

**Date:** 2026-10-04
**Phase:** F0 (blind-spot closure, pre-F1)
**Scope:** every assertion in `D:\THE ASYMMETRIC WAGER` that a machine has
checked a proof or that a solver returned `UNSAT` / `SATISFIABLE`.
**Language:** English (project artefact).
**Standing:** this report supersedes nothing by silent edit. Every change it
introduced is listed in §7 with the old value recorded.

---

## 1. Method

1. Enumerate all claims of the form *verified*, *checked*, `unsat`, `sat`,
   `UNSATISFIABLE`, `SATISFIABLE` across the workspace.
2. For each, require an artefact pair: a source that the tool ran **on**, and a
   log that the tool **produced**. No artefact ⇒ `TOOL NOT RUN`, which is never
   a success.
3. Re-run the tooling from the shipped artefacts only (no cached outputs).
4. Re-derive every numeric verdict with exact rational arithmetic in Python
   `fractions.Fraction`, i.e. without the solver that produced the claim.
5. Record residual and unverifiable items rather than dropping them.

Tools used (versions as reported by the binaries themselves):

| tool | version / path |
|---|---|
| Anti-Circularity Gate | `C:\Users\usER\.config\opencode\skills\anti-circularity\scripts\gate.py` |
| Lean | 4.33.1, commit `819816b2e0a3bf405af45ae5c7af2491d8f5bee6` |
| Z3 | 4.16.0 (runner), auditor self-reports 5.0.0 |
| Python | 3.14 (`C:\Python314\python.exe`) |

---

## 2. Gate results

```
gate self-test: 13 cases, 0 failed          (exit 0)
gate check OMEGATrackC.lean track_c_side_conditions.smt2
  SMT CIRCULARITY AUDITOR -- z3 5.0.0
  GENUINE   asserts=1  ctx=sat  script=unsat  core=[0]
            the contradiction needs 0 axioms plus the claim,
            and no axiom is the claim's negation
  ANTI-CIRCULARITY GATE [check]  result: FAIL=0 NOT_RUN=0 SKIP=0  verdict: PASS
  exit 0
```

`core=[0]` is the load-bearing line: the single asserted clause is the
negation of the conjunction of the seven side conditions, and the unsat core
contains no axiom. The contradiction is not fed back in from outside.

---

## 3. Independent re-derivation (exact rational, no solver)

The three constants were parsed out of the shipped `OMEGATrackC.lean`
rather than copied from the README:

```
lambdaMin  = 132105051975174632728899314595 / 10^131
rhoActual  = 583986112334288261            / 10^196
rhoStar    = 163092656759474834688247443633 / 10^133
```

The generator's own three-way literal cross-check against `README.md`
reported `MATCH` on all 3 constants on regeneration.

Exact evaluation of the seven side conditions — each one evaluated as a
statement over `Fraction`, i.e. with no rounding at any step:

| # | condition | exact value | verdict |
|---|---|---|---|
| 1 | `rhoActual <= rhoStar` | true, by 74.4460318880 decades | True |
| 2 | `rhoActual * 10^74 <= rhoStar` | true, by 0.446 decades | True |
| 3 | `rhoActual * 401 < lambdaMin` | `5.84e-179 * 401 = 2.34e-176 < 1.32e-102` | True |
| 4 | `not (rhoStar * 401 < lambdaMin)` | `rhoStar*401/lambdaMin = 4.950617283950617` | True |
| 5 | `rhoStar * 81 <= lambdaMin` | `rhoStar*81/lambdaMin = 0.9999999999999999` | True |
| 6 | `lambdaMin < rhoStar * 82` | `rhoStar*82/lambdaMin = 1.012345679012346` | True |
| 7 | `0 < rhoStar` | `rhoStar > 0` | True |

Conjunction of all seven: **True**, with no solver involved.

---

## 4. Reproducibility from shipped bytes

| step | result |
|---|---|
| `track_c_make_smt.py` re-run in a clean copy | `wrote track_c_side_conditions.smt2 (1532 bytes, 7 claims)`, `RESULT: PASS -- 7/7 negations UNSAT`, exit 0 |
| generated `.smt2` vs shipped | byte-identical (regenerated, now hash `99d485c4…`) |
| `lean -o OMEGATrackC.olean OMEGATrackC.lean` on a byte-identical stage | exit 0, 11.5 s, `olean=361560` bytes |
| `source == stage` | `IDENTICAL` |
| `#print axioms` on all 10 theorems | 10/10 return `[propext, Classical.choice, Quot.sound]` |
| `sorryAx` / error lines | 0 |

---

## 5. Blind spots found

### F0-1 — `nDim` was mislabelled, and a docstring stated a falsehood

`nDim := 401` was documented as *"Dimension of the Guinand-Weil test matrix
(N = 401)"*. It is not a dimension of any matrix in this workspace. `401` is
the `N` of `Q_{100,200}`; the constants that `nDim` multiplies —
`lambdaMin`, `rhoActual`, `rhoStar` — belong to `Q_{100,40}`, which is
`81 x 81`. The number 401 is a *conservative enlargement* of the true
dimension, not the dimension.

Second, `tolerance_fails_the_coarse_bound` was documented as

> *The report's `ρ*` therefore cannot be the crude entrywise bound `n · max|E|`;
> it must come from a tighter norm step.*

This is **refuted by the code that produces `ρ*`**. `gw_arb_sweep.py` line 172
computes `rho_star = lam_lo / nrm` with `n = 81`, and `gw_opt_b_arb.py` lines
313/320 compute `rho_star = mp.mpf(lam_float) / n`. `ρ*` *is* the crude
entrywise bound at the true dimension `n = 81`. `GW_STATUS_2026-09-26.md`
§7c.4 says the same. The theorem statement itself (`¬(ρ* · 401 < λ_min)`) is
correct and unchanged; only its prose conclusion was false.

**Not changed:** `nDim := 401`. Its value is a legitimate stronger hypothesis
and every verdict that uses it still holds (condition 3 passes by ~76 orders at
401). Changing the value would move the artefact for no gain.

### F0-2 — `ρ*` is a binary64 quotient, and `implied_constant_gt_81` was true only by rounding

The strict inequality `ρ* · 81 < λ_min` holds, but only by
**relative 1.259e-16** (absolute gap `1.6631e-118`). That gap is exactly the
rounding error of the binary64 division used to produce the literal:

```
float(lambdaMin) = 1.3210505197517463e-102
float(lambdaMin)/81 = 1.6309265675947483e-104
rhoStar as printed  = 1.6309265675947483e-104
bit-identical: True
```

The exact quotient `λ_min / 81` differs from `ρ*` by relative `1.90e-16`, so
the two are indistinguishable past 16 digits. The verdict the theorem gates is
decided by 74 orders of margin and is unaffected either way — but a *strict*
inequality that is true only because of a rounding artefact of the constant's
own provenance is not a property of the matrix, so it must not be claimed.

Compounding it, `implied_constant_lt_82` was documented as evidence that the
report's Weyl step used a spectral norm (`√n ≈ 20`) plus a structural factor,
"and *not* with the crude constant `n = 401`". The bracket `[81, 82)` contains
`81`, which **is** the crude constant. The speculation is withdrawn.

**Changed:** `implied_constant_gt_81` → `implied_constant_ge_81`, formula
`rhoStar * 81 < lambdaMin` → `rhoStar * 81 <= lambdaMin`. Non-strict `≤` is
true at full precision regardless of rounding direction, so the theorem no
longer depends on how the literal was produced. `rhoStar`'s docstring now
records its provenance and states that no digit past the 16th may be read as a
measurement.

### F0-3 — `SOLVABLE_FINITE_PARADOX.md` claimed a solver result that was never run

Two independent defects:

**(a) Unsupported claim.** §1.B displayed `Z3(Φ) → [UNSATISFIABLE]` as an
executed outcome. A scan of the entire workspace on 2026-10-04 found **exactly
one `.smt2` file** — `guinand-weil-rigorous-numerics-main/track_c_side_conditions.smt2`
— and exactly one Z3 log, both belonging to the Track C gate and neither about
Protocol 09. There is no encoding of `Φ` and no run log — as of 2026-10-04;
both now exist and are gated (A1, see the closing paragraph of this section).
The correct status *then* was
`TOOL NOT RUN`. `Brain.MD` line 33 was propagating the claim into the
knowledge map.

**(b) Internal contradiction.** §1.B asserted `UNSATISFIABLE` while §3's
metrics table recorded `STATUS: SATISFIABLE` for the same case — two opposite
verdicts for one problem, in one file, both presented as results.

A third defect followed from the first: §4 ordered agents to *"run this
Gödelian loop simulation"*, and no such simulation exists anywhere in the
workspace. That directive was an instruction to fabricate a run.

**Not claimed in the other direction either.** Writing an `.smt2` for `Φ` and
handing it to Z3 would not automatically yield a `GENUINE` result: as the
problem is stated, the conclusion follows from the two definitions alone, so a
literal encoding would be discharged from its own axioms and the auditor would
report `VACUOUS` or `SINGLE_AXIOM`. A `GENUINE` encoding needs a concrete
finite state machine for Protocol 09 — transition relation, self-reference
operator, step counter — which the document does not specify. That gap is
recorded in §1.B of the document itself as the work required.

**The gap is now filled — A1, 2026-10-06.** `protocol_09.smt2` is that
finite state machine, and `protocol_09_check.py` proves that the two defects
this section predicted do *not* occur: the context alone is `sat`, so the
script is not `VACUOUS`, and each of the three core axioms `[11]` `b >= i`,
`12` `HALT => i >= M`, `[13]` `M > N` is load-bearing when dropped, so the
verdict is not `SINGLE_AXIOM`; the auditor returns `GENUINE`. What A1 does
**not** discharge is the second half of the warning: the encoding carries an
obstruction it can state but not remove — under A3 (`P09 < M`) the branch
`SCAN, i > P09` is unreachable, so the machine halts without ever exercising
self-reference. That is declared in the script's header rather than papered
over, and it is the honest limit of this closure: the encoding proves the
halting claim it encodes, not the unboundedness of the loop that motivated
it. §1.B of the document has been re-pointed at the gate.

> **Amendment, 2026-10-07 (A12).** The A1 artefacts were renamed by Fase A12:
> `protocol_09.smt2` → `bounded_loop.smt2`, `protocol_09.log` →
> `bounded_loop.log`, `protocol_09_check.py` → `bounded_loop_gate.py`.
> Token mapping (own Kamus, `KAMUS_PEMETAAN.md`): `P09→p09_op`,
> `SCAN→q_scan`, `SELFCHECK→q_check`, `HALT→q_halt`, `M→m_budget`,
> `N→n_budget`. Gate still 8/8; auditor still `GENUINE`.

### F0-4 — `shp_mcp_bridge_v4.py` would return verdicts no solver produced

When `z3py` was absent, `SMTTribunal._evaluate_simulated()` ran a regex over
the SMT script and returned `SATISFIABLE` or `UNSATISFIABLE` as verdicts,
marked `"simulated": True` and labelled `[SIMULATED-ONLY - NOT A PROOF]`.

Two defects followed.

**(a) The label disclaimed the proof but did not remove the verdict.** The
strings `SATISFIABLE` / `UNSATISFIABLE` survive independent of their label:
every consumer in the file compares `verdict_report["verdict"] == "UNSATISFIABLE"`
and none of them inspects `simulated`. A downstream reader — or a later edit
that drops the flag — sees a verdict, not a disclaimer. In a corpus about pure
physics and pure mathematics, a guessed verdict is indistinguishable from a
fabricated one at the point of use.

**(b) The suite's own verdict contradicted its exit code.**
`run_integrated_test_suite()` printed
`>> TRIBUNAL STATE: CONTRADICTION [UNSAT]. FIX SYSTEM COHERENCE.` and then
returned normally, so `--test` exited **0**. An exit code of 0 is a
machine-checkable claim that every check passed. The suite was not evidence.

Relabelling alone would have made it worse: renaming `[SIMULATED-ONLY - NOT A
PROOF]` to `[PROOF-ONLY - NOT A SIMULATED]` while leaving the regex branch
reachable would label a heuristic as a proof — a strictly stronger false
claim. The label was therefore made **true by removing the branch**:

* `_evaluate_simulated` is gone. With `z3py` absent the tribunal returns
  verdict `TOOL NOT RUN` with `[PROOF-ONLY - NOT A SIMULATED]`, never a
  SAT/UNSAT answer. The refusal is fail-closed: `handle_call_tool` already
  requires exactly `SATISFIABLE` to write a file or execute a command, so
  `TOOL NOT RUN` blocks the action (line 905/955: *write/execution refused
  (fail-closed)*).
* The test suite now returns `success` and `--test` exits `0` only if every
  check passed.
* Two new tests pin the contract: **TEST 9** forces `z3_active = False` and
  requires `TOOL NOT RUN` for both a satisfiable and an unsatisfiable script;
  **TEST 10** places a write *inside* the allowlist with the solver disabled
  and requires refusal — so the only possible cause of refusal is the missing
  proof.

A third, pre-existing test defect surfaced while verifying: **TEST 4**
hardcoded its "safe" path to `%TEMP%`, which is legitimately outside
`SHP_MCP_WRITE_ROOTS` when the opencode registration restricts the roots. The
test therefore reported `CONTRADICTION` while enforcement was working
correctly. It now derives the path from `_default_write_roots()[0]`.

The bridge exists in two registered copies and both must comply:

| registration | file | corpus root |
|---|---|---|
| `shp_asymmetric_wager` | `D:\THE ASYMMETRIC WAGER\mcp\shp_mcp_bridge_v4.py` | `D:\THE ASYMMETRIC WAGER` |
| `shp_bridge` | `C:\Users\usER\oracle-toe\GUINAND_WEIL\shp_mcp_bridge_v4.py` | `D:\Theory_of_Everything_Derivations` |

Both are now byte-identical, sha-256
`9755469673e5e55bea841ea201f5a70c3243cd9f4c2ccc27d5b254ba66c2a4d2` (55781 bytes).

---

## 6. What was *not* affected

| claim | status |
|---|---|
| Track C's 7 side conditions, `unsat` verdict, `GENUINE` audit | **intact** — same verdicts before and after the edits |
| `nDim := 401`, all three numeric literals | **unchanged byte-for-byte** |
| `margin_satisfies_master_theorem`, `tolerance_fails_the_coarse_bound`, `implied_constant_lt_82`, `tolerance_positive` statements | **unchanged** (prose only) |
| `mcp/shp_mcp_bridge_v4.py` verdict strings | **changed by F0-4** — see §5. The earlier reading of them as harmless was wrong: the label disclaimed the proof but the verdict string survived to every consumer |
| `Theory_of_Everything_Derivations\…pdf.txt` `UNSATISFIABLE` | **not a result claim** — a prompt instruction ("output `[UNSATISFIABLE]` and halt") |

---

## 7. Change record

| file | change |
|---|---|
| `guinand-weil-rigorous-numerics-main\OMEGATrackC.lean` | 4 docstrings corrected (`nDim`, `margin_satisfies_master_theorem`, `tolerance_fails_the_coarse_bound`, `implied_constant_lt_82`), `rhoStar` provenance added, `implied_constant_gt_81` → `implied_constant_ge_81` with `≤` |
| `guinand-weil-rigorous-numerics-main\track_c_make_smt.py` | `CLAIMS` entry renamed and formula changed to `rhoStar * 81 <= lambdaMin` |
| `…\track_c_side_conditions.smt2`, `…\track_c_smt_z3.log` | regenerated |
| `…\track_c_lean_verify.log` | rewritten from a fresh build; old sha/elapsed/olean recorded in an AMENDMENT block |
| `…\OMEGA_CORE_CERTIFICATE.md` | §6.7 hash table updated; superseded hashes recorded; §6.7 Lean bullet re-measured |
| `…\CHECKSUM.sha256` | 6 entries refreshed (5 Track C + the certificate); regeneration note added |
| `SOLVABLE_FINITE_PARADOX.md` | §1.B claim → `TOOL NOT RUN` + encoding gap; §2 script no longer asserts an unobserved verdict; §3 table contradiction withdrawn; §4 rewritten as a directive that forbids inventing the run |
| `Brain.MD` | line 33 rewritten to carry the corrected status; new row added for `F0_REPORT.md` |
| `mcp\shp_mcp_bridge_v4.py` | F0-4: simulation branch removed, verdict `TOOL NOT RUN` under `[PROOF-ONLY - NOT A SIMULATED]`, `--test` exit code made honest, TEST 9/10 added, TEST 4 path derived from the live allowlist |
| `C:\Users\usER\oracle-toe\GUINAND_WEIL\shp_mcp_bridge_v4.py` | replaced byte-for-byte with the workspace copy, so the `shp_bridge` registration is PROOF-ONLY too |
| `F0_REPORT.md` | this file |

The first six rows are inside the sub-repository and are covered by
`guinand-weil-rigorous-numerics-main\CHECKSUM.sha256`. At the time of this
phase the workspace root had no manifest, so `SOLVABLE_FINITE_PARADOX.md`,
`Brain.MD`, `F0_REPORT.md` and `mcp\shp_mcp_bridge_v4.py` were hashed by
nothing; their sizes were recorded in §8 instead. **Closed by A2 on
2026-10-05**: `checksum_check.py` now writes and verifies a root-level
`CHECKSUM.sha256` covering those files and every other root file, plus
`provenance/` and `harnesses/`, and runs as the last gate of the suite. The
canonical bridge file lives outside the workspace by design —
it is the registered source of `shp_bridge`, and Brain.MD documents the
source → workspace copy relationship.

### Superseded, not erased

```
OMEGATrackC.lean                8894d24bee7107dee42ea2bcf3a6034323d1188872d41e43126b4326589fea95  13837
track_c_make_smt.py             42ac3122ac81c5505d65bf7239fa21554227136fde4c3476ae18bebd6f000933  12714
track_c_side_conditions.smt2    77456c1652559ce84d246ad250244cf5bb35cf5d8c66dc6915daf6bafd43ee40   1533
track_c_lean_verify.log         46d4b109dd5ccc5d75a42607bcb8ca61b1da1d0ddb366dfbdc527659888f3b79   1810
track_c_smt_z3.log              366c16b17fe85841a248da5fdd4ec828e9b81b8d1665c8d27c7b819606e777da   1383
shp_mcp_bridge_v4.py            fd37e072f32a00d012b83ac1c103a44cb3011c5dda57e9995a0e23812f717c3f  54004
```

The 2026-10-02 build of `OMEGATrackC.lean` was sound: `exit=0`, 12.6 s,
`olean=358736`, same axiom footprint. It is superseded because four of its
docstrings stated things that are false, not because it failed to build.

The pre-F0 `shp_mcp_bridge_v4.py` was likewise sound code — it labelled its
simulated path honestly. It is superseded because the label did not travel
with the verdict string to its consumers, and because `--test` exited 0 while
printing `CONTRADICTION`.

---

## 8. Verification after the change

```
gate self-test                 13 cases, 0 failed            exit 0
gate check                     GENUINE / verdict PASS        exit 0
Z3 on regenerated .smt2        7/7 negations UNSAT, combined conjunction UNSAT
exact-rational re-evaluation   7/7 True, conjunction True (no solver)
CHECKSUM.sha256                112/112 entries match, 0 missing, 0 unlisted
Lean rebuild                   exit 0, 11.5 s, olean=361560
#print axioms                  10/10 = [propext, Classical.choice, Quot.sound]
sorryAx / error lines          0
shp_mcp_bridge_v4.py --test    10/10 PASS, LOCKED [SATISFIABLE]   exit 0
  TEST 9  z3py disabled        both scripts -> TOOL NOT RUN
  TEST 10 write, no proof      refused, file not created
workspace/canonical bridge     byte-identical, sha 97554696…c2a4d2
old label in workspace         0 occurrences of SIMULATED-ONLY - NOT A PROOF
OMEGATrackC.lean encoding      UTF-8 strict, no BOM, 16382 bytes
SOLVABLE_FINITE_PARADOX.md     UTF-8 strict, no BOM, 6931 bytes
Brain.MD                       UTF-8 strict, no BOM, 11255 bytes
mcp\shp_mcp_bridge_v4.py       UTF-8 strict, no BOM, 55781 bytes
```

### Honest failures still standing

```
shp_bridge --test (its own configured env)    9/10, exit 1
  TEST 6 FAIL: Corpus Root D:\Theory_of_Everything_Derivations does not exist
```

This is not a regression and is not papered over: the path named in
`opencode.jsonc` for the `shp_bridge` registration is absent from this
machine, so `list_documents` / `read_document` / `search` index nothing for
that server. The exit code now reports it instead of hiding it (see F0-4).

### Current hashes

```
OMEGATrackC.lean                a5773617d02dc257844dbe1ffac6af08a2ed9c01c8f1968afefe8ef33940a646  16382
track_c_make_smt.py             33b4f22e4a09f04c595907ae3c1a2a39245bd6b210a5701b89ad1c406c96775c  12714
track_c_side_conditions.smt2    99d485c42feeb6b33e77fbab4fb3b55a1208379dd9f6e52246cf5a412b85aa96   1532
track_c_lean_verify.log         68f56e01ba0861cebaaa37a4f2e690124f7f818df9168ea72eb16c385426268a   2380
track_c_smt_z3.log              454b49faf30c0aace06b1266992a7eb7ab2e0398d64533cb2fc408d2e6036038   1383
shp_mcp_bridge_v4.py            9755469673e5e55bea841ea201f5a70c3243cd9f4c2ccc27d5b254ba66c2a4d2  55781
```

---

## 9. Residual items handed to F1

1. **`Φ` has no encoding — CLOSED by A1, 2026-10-06.** A `GENUINE`
   machine-check of Protocol 09 required the finite-state specification named
   in §5 F0-3, and that specification did not exist. It does now:
   `protocol_09.smt2` writes Protocol 09 as a finite-state machine over
   `QF_LIA` (configurations `(q0,i0,b0)` → `(q1,i1,b1)`, five transition
   rules, the self-reference operator `P09`, a step counter, axioms A0..A6),
   with the halting claim as the **last** assertion so the circularity auditor
   audits the sentence this report documents. `protocol_09.log` records the
   run and is bound to the script by `sha256`, so a stale log cannot vouch for
   edited bytes. `protocol_09_check.py` — the twelfth gate (2026-10-06, A1),
   inserted immediately ahead of the manifest gate — recomputes all eight
   conditions
   rather than trusting any of them: script unsat, context alone **sat** (not
   `VACUOUS`), context + negated claim **sat** (the context refutes the claim
   rather than everything), each of the three core axioms load-bearing when
   dropped (not `SINGLE_AXIOM`), auditor **`GENUINE`**. Fault injection
   confirmed the gate fails on all four, and is reproducible rather than
   anecdotal: `harnesses\p09_inj.py` applies a forced-inconsistent context, a
   clobbered log hash, a removed axiom and a removed marker, requires exit 1
   with the matching condition each time, and requires the gate to pass again
   on the restored bytes — `6/6`, with both artefacts byte-identical
   afterwards. It is registered as the fourteenth harness (2026-10-06, A1) in
   `harness_check.py`. The two obstructions
   recorded in §5 F0-3 are carried in the script's header rather than dropped:
   the `SCAN, i > P09` branch is unreachable under A3 and is proved so, so
   only one of the two is discharged by the encoding. The defensible statement
   is no longer solely the tool-free bound — the encoding is checked — but the
   bound itself is unchanged.
2. **`ρ*` digits past 16 are not measurements — POLICY NOTE; the current
   chain already satisfies it (B3-a, decided 2026-10-05).** The shipped digits
   were not read off a binary64 literal: they originate in the `flint.arb`
   enclosure at `prec = 1024 bits`, all seven Track C side conditions were
   evaluated here as statements over `Fraction` with no rounding at any step,
   and the generator's three-way literal cross-check against `README.md`
   reported `MATCH` on all three constants. If a future claim needs
   `λ_min / 81` to more than 16 significant digits, compute it at elevated
   precision and record the method; do not read it off the binary64 literal.
3. **The `n = 401` / `n = 81` distinction — CONDITIONAL POLICY NOTE; no edit
   made (A4, decided 2026-10-05).** The distinction now appears in four
   docstrings but not in `README.md` §4.1 or `WORKING_PAPER.md`; both are
   pinned in `guinand-weil-rigorous-numerics-main\CHECKSUM.sha256`, and both
   still describe Track C at a level where the distinction does not bite, so
   editing them would break a pin with no failing check to justify it. For
   whoever does edit one: `n = 401` is the matrix dimension
   (`dim(full) = 2N+1 = 401`, `gw_opt_b.py`), while `n = 81` is the divisor in
   `ρ* = λ_min / n` and the factor in `λ_min^true ≥ λ_min^parse − nρ`;
   `WORKING_PAPER.md` states only "With $n=81$" without saying what the 81
   counts, which is the whole reason the two are easy to conflate. If either
   file is ever edited to state a dimension-specific margin, it must say which
   `n` it means.
4. **`CHECKSUM.sha256` records this report's predecessor hashes only — CLOSED
   by A2, 2026-10-05.** The maintenance obligation was real and entirely
   manual: any later edit to a listed file required refreshing its entry, and
   nothing checked whether that had been done, so a stale manifest and a fresh
   one were indistinguishable. The manifest still does not hash itself, and
   that property is unchanged. What is new is that the refresh is now
   *verified* rather than hoped for: `checksum_check.py` re-hashes **65
   files** — 43 at the workspace root, 8 under `provenance/`, 14 under
   `harnesses/` (61 at A2; the three `protocol_09.*` artefacts and
   `harnesses\p09_inj.py` joined with A1) — against the root
   `CHECKSUM.sha256`, reports a listed file that is
   absent, a size that moved, a digest that differs and a file present but
   never listed, and is registered as the thirteenth and last gate (A2,
   2026-10-05) of `suite_check.py`
   so that it runs *after* every other gate. A manifest that is missing exits
   2 rather than 0: integrity cannot be claimed without a baseline. The
   sub-repository manifest is deliberately out of scope — it pins its own 116
   entries and two authorities over one set of bytes is worse than one.
5. **`shp_bridge`'s corpus root does not exist — CLOSED by F2-5.**
   `opencode.jsonc` set `SHP_MCP_CORPUS_ROOT` to
   `D:\Theory_of_Everything_Derivations`, absent from this machine. F2-5 found
   the real tree at `D:\THE ASYMMETRIC WAGER\Theory_of_Everything_Derivations`
   (27 files) and, on the operator's decision, repointed the registration
   there. Exactly one line of the config changed; `shp_bridge --test` now exits
   0 and `bridge_mirror_check` B6 runs the mirror's suite instead of skipping
   it. Recorded rather than deleted, as with every other closure.
6. **The bridge is duplicated — CLOSED by F2-4.** Two registered servers read
   two copies of `shp_mcp_bridge_v4.py`, "kept identical only by hand".
   `bridge_mirror_check.py` now machine-checks that byte-identity (B3), the
   v4.2.0-PROOF-ONLY contract in both (B4), and both registrations (B1/B2/B5),
   with each copy's own `--test` run in B6. Fault injection: **14/14 mutants
   caught, 4/4 controls correct**. The hand-maintained property is still
   hand-maintained — what is new is that a failure is now detected rather than
   discovered.
7. **PROOF-ONLY is not a proof of anything.** The change makes the bridge
   refuse to answer when no solver ran. It does not make any claim in the
   corpus true. The seven Track C side conditions remain the only
   machine-checked results in this workspace.

---

## N. Addendum 2026-10-07 (phase A15) -- `rho_actual` re-anchored from estimate to bound

Sections 1-5 above record this workspace at F0 time and are left as written.
One of the three constants changed after that, so this addendum states the
change rather than letting the older table stand unqualified.

| constant | at F0 time (section 3) | since 2026-10-07 |
|---|---|---|
| `lambdaMin` | `132105051975174632728899314595 / 10^131` | unchanged |
| `rhoActual` | `583986112334288261 / 10^196` | `58287013697174734848 / 10^198` |
| `rhoStar` | `163092656759474834688247443633 / 10^133` | unchanged |
| margin `rho* / rho_actual` | 74.4460318880 decades | 74.4468626023 decades |

`rhoActual` was a **dps-doubling estimate**; it is now the ball-arithmetic
upper bound `max_ij (|M_ref_ij - center_ij| + rad_ij)` measured by the new
`gw_rho_formal.py`, which re-evaluates the same corrected-build formulas in
`flint.arb` / `flint.acb` at 1200 working bits and gives the Lerch series of
`beta_L` a proved geometric tail bound. The new value is *smaller* than the
estimate it replaces, which is what an upper bound should be relative to a
two-builds difference.

The seven side conditions of section 3 were re-evaluated with the new literal
and still hold; `rho_actual * 10^74 <= rhoStar` now has 0.4468 decades of slack
and `rho_actual * 401 = 2.34e-176 < lambda_min` is unchanged in verdict.

What was verified after the edit, and what was not:

* `track_c_make_smt.py`: three-way literal match against `README.md` **MATCH**,
  7/7 negations UNSAT, exit 0; `track_c_side_conditions.smt2` regenerated.
* `z3` on the regenerated script: UNSAT, via the anti-circularity gate, which
  reports `GENUINE=2`.
* `lean -o OMEGATrackC.olean OMEGATrackC.lean` (the row in section 4) was
  **NOT RUN** for the new literal: the machine that made the change has no
  Mathlib. No theorem statement changed, so that row still describes the
  proofs, but it no longer covers the current bytes of the file.
* The dps-180 reference matrix `gw_matrix_100_40_dps180.json`, absent when this
  report was written, was rebuilt on 2026-10-07 with `gw_corrected_eig.py`; its
  `lambda_min` reproduces `lambdaMin` to all 30 published digits. That matrix and
  `gw_rho_formal_100_40.json` are megabyte-scale generated data and are not
  tracked in git; the commands that regenerate both are in the sub-repository
  `README.md` (A1 section).