# FILE: KAMUS_PEMETAAN.md
# Kamus Pemetaan — mapping dictionary for the Protocol 09 / bounded-loop
# formal artefacts.  Written by Fase A12 (2026-10-07) because the dictionary
# `Tugas tambahan.md` defers to did not exist in this workspace (A8 search,
# Brain.MD row for that file).  Language: English.
# Status: authoritative for the A12 rename; historical aliases listed below.

---

## 1. Scope

`Tugas tambahan.md` (2026-10-06) asked for the private component names of the
formal logic artefacts to be replaced by universal symbols, with the gate
retargeted and the Z3 log regenerated.  A8 deferred the task: no *Kamus
Pemetaan* could be read, and three of the six proposed names collide with
symbols this corpus already defines.  A12 writes the missing dictionary and
executes the rename with collision-free names.  The mathematical object is
unchanged: the same Gödelian Compliance Loop, the same eight gate conditions,
the same `unsat` verdict.

## 2. Token mapping

| Private name (A1) | Proposed in `Tugas tambahan.md` | **Kamus A12 (used)** | Why the proposed name is not used |
|---|---|---|---|
| `P09` | `q_self` | `p09_op` | In this corpus `q` means *control state* (`q0`/`q1` in the encoding).  `P09` is the self-reference **index**, not a state. |
| `SCAN` | `q_scan` | `q_scan` | Unambiguous.  Control state "examining protocol *i*". |
| `SELFCHECK` | `q_check` | `q_check` | Unambiguous.  Control state at the loop's own specification. |
| `HALT` | `q_halt` | `q_halt` | Unambiguous.  Absorbing completion state. |
| `M` | `M_inf` | `m_budget` | `M_inf` already names a matrix in `guinand-weil-rigorous-numerics-main/gw_band.py`, and `_inf` reads as the actual infinity AGENTS.md forbids.  `M` is how many protocols must be examined — a finite budget. |
| `N` | `N_steps` | `n_budget` | `N_steps` is already the evolution step count `5.444685399e61` in `external_constants.json`.  `N` here is the step budget of the encoded loop, a different quantity. |

## 3. File mapping

| Private name (A1) | **Kamus A12 (used)** |
|---|---|
| `protocol_09.smt2` | `bounded_loop.smt2` |
| `protocol_09.log` | `bounded_loop.log` |
| `protocol_09_check.py` | `bounded_loop_gate.py` |

The fault-injection harness keeps its A1 historical filename
`harnesses/p09_inj.py`; only its internal paths and mutation needles were
retargeted by A12.

## 4. Collision evidence (measured, not assumed)

* `N_steps` — `external_constants.json` and F1_REPORT.md F1-B:
  `N_steps = 5.444685399e61`.  Register value, not a budget symbol.
* `M_inf` — `guinand-weil-rigorous-numerics-main/gw_band.py` lines 204–206:
  `M_inf = G.even_matrix(...)`; the name also violates the no-actual-infinity
  rule.
* `q_self` — `protocol_09.smt2` already uses `q0`/`q1` for control state;
  joining that namespace with an index operator would be ambiguous.

## 5. Historical aliases

* Before 2026-10-07 (A12), the encoding lived at `protocol_09.smt2` with
  tokens `P09`/`SCAN`/`SELFCHECK`/`HALT`/`M`/`N` and the gate was
  `protocol_09_check.py`.  Phase reports F0, F5, F8, A11 and TAHU_A10 record
  that history and keep those names as history; each carries an amendment
  pointing here.
* The mathematical claim is unchanged: the halting claim is the last
  `(assert ...)`, the three core axioms are load-bearing, and the circularity
  auditor must return `GENUINE`.

## 6. Further renames (instruction step 5)

The instruction asked for a recommendation of further renames after the gate
passes.  A12 recommendation: **stop here**.  The remaining private-looking
names in the encoding (`q0`, `q1`, `i0`, `i1`, `b0`, `b1`) are already the
standard configuration of a finite-state machine — control state, protocol
index, step counter — and are documented in `bounded_loop.smt2` header.  No
further token in this encoding is ambiguous or colliding.  A future rename
should be proposed only when a new collision is *measured*, not because a
name looks informal.
