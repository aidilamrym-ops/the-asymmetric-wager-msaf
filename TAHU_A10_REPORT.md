# FILE: TAHU_A10_REPORT.md
# Fase A10 — honesty rewrite of the two `tahap uji` documents, provenance
# registration, suite gate 15, and injection harness.
# Date: 2026-10-07.  Language: English.

---

## 1. Scope

Fase A10 executed options 1B, 2b/2c, 3ii and 4y of the A10 decision:

1. **1B** — rewrite both documents under
   `Theory_of_Everything_Derivations/tahap uji/` so their claims are true and
   machine-checkable.
2. **2b/2c** — English only; every rewritten claim carries `[F9-x]` / phase
   provenance in this report rather than in the F4 register (the `tahap uji`
   tree is **outside** the 15-document F4 scope, so `[F4-x]` markers were not
   added there).
3. **3ii** — `tahap_uji_audit.py` registered as suite gate **15**.
4. **4y** — `ρ_Λ`, `ħ`, `c`, `ω_P`, `ρ_Planck` and `1/Δ_univ` registered in
   `external_constants.json` with evidence probes, `REFERENCES.md` sections,
   and a new `provenance_check.py` recompute mode.

## 2. Defects found in the previous documents (pre-rewrite)

| ID | Document | Defect | Why it was dishonest |
|---|---|---|---|
| S-1 | Vacuum | Claimed `ρ_MSAF ≡ ρ_observed` with **absolute error 0** and `[STATUS: SATISFIABLE]` | No artefact, log or recomputation in the workspace produced that equality. The Planck-cutoff density is of order `10^111` J/m^3, not `10^-10`. |
| S-2 | Vacuum | Used `1/Δ_univ` (dimensionless) as if it were a physical frequency bound | The reciprocal of a length ratio has no s^-1 unit. The Planck cutoff frequency is a different registered quantity. |
| S-3 | Vacuum | Called renormalisation a "dirty trick" (`renormalisasi kotor`) | Standard EFT procedure; the corpus's own F4-F finding already rejected that framing. |
| S-4 | Vacuum | Claimed the divergent integral "≈ 10^111" as if it evaluated | The integral diverges; any finite number needs a stated cutoff. |
| V-1 | Sieve | Gate 3 described as requiring "purely SATISFIABLE" for all computation | `bounded_loop.log` (A1; historical name `protocol_09.log`) records `script=unsat ctx=sat`. Context sat ≠ every prose claim true. |
| V-2 | Sieve | Landauer sold as proof of computational crash / thermodynamic incineration | Landauer is a per-bit energy floor. `landauer_check.py` gates the floor arithmetic only. |
| V-3 | Sieve | Navier--Stokes "proven smooth deterministically" | Clay open problem. F4-D already recorded this as an open claim. |
| V-4 | Sieve | Gate 2 (quantum censorship) presented as part of a passing triple-gate | No gate script implements it. |
| V-5 | Sieve | Coercion doctrine forbidding negotiation | Rhetoric, not a mathematical argument. |

## 3. Rewrite decisions (1B)

### 3.1 `THE_VACUUM_CATASTROPHE_SOLUTION.md`

* Language: English.
* The divergent integral is stated as divergent; no fake evaluation.
* The honest cutoff chain is: inputs `ħ`, `c`, `ℓ_P` →
  `ω_P = c/ℓ_P` → `ρ_Planck = ħc/(8π²ℓ_P⁴)`.
* Registered numbers (each needle occurs **exactly once**, mode
  `source_agree`):
  * `1{,}054571817 \times 10^{-34}` — `REDUCED_PLANCK_CONSTANT`
  * `2{,}99792458 \times 10^{8}` — `SPEED_OF_LIGHT`
  * `6 \times 10^{-10}` — `DARK_ENERGY_DENSITY`
  * `5{,}867696 \times 10^{111}` — `PLANCK_VACUUM_DENSITY`
  * `1{,}854859 \times 10^{43}` — `PLANCK_FREQUENCY`
  * `5{,}444685 \times 10^{61}` — `RECIPROCAL_UNIVERSE_PIXEL` (dimensionless)
* The former zero-error / SATISFIABLE-as-result claims are **withdrawn** in
  the document itself.
* The residual ratio `ρ_Planck/ρ_Λ ≈ 9.8×10^120` is stated as **open**.

### 3.2 `THE_SOVEREIGN_SIEVE_PROTOCOL.md`

* Language: English.
* Trap diagram labelled **rhetorical framing**, not a proof.
* RH: numerical identity gated; RH itself **not** claimed proven.
* Navier--Stokes: **open** Clay problem.
* Dark matter / bounce: **interpretive**, not gated as established.
* Gate 1: implemented (`landauer_check.py`), Landauer = floor.
* Gate 2: **not implemented** — recorded as open residual.
* Gate 3: implemented for Protocol 09 only; context sat, claim unsat,
  negated claim sat; cross-read of `protocol_09.log`.

> **Amendment, 2026-10-07 (A12).** Gate 3 cross-read file is now
> `bounded_loop.log` (renamed from `protocol_09.log`; A12). Gate 2 remains
> not implemented.
* Coercion doctrine rewritten without negotiation bans.

## 4. Provenance chain (4y)

| Id | Kind | Value | Authority | Evidence |
|---|---|---|---|---|
| `REDUCED_PLANCK_CONSTANT` | measured, exact | 1.054571817e-34 J s | SI 2019 / CODATA 2022 | `NIST_CODATA_2022_TABLE` L304 |
| `SPEED_OF_LIGHT` | measured, exact | 2.99792458e8 m/s | SI 2019 / CODATA 2022 | `NIST_CODATA_2022_TABLE` L330 |
| `DARK_ENERGY_DENSITY` | measured | 6e-10 J/m^3 | Wikipedia *Dark energy* CC BY-SA 4.0 | `WIKIPEDIA_DARK_ENERGY` (layer A, sha256 `20944a6e…67e41`) |
| `PLANCK_FREQUENCY` | derived | 1.854859e43 s^-1 | quotient `c/ℓ_P` | recompute mode `quotient` |
| `PLANCK_VACUUM_DENSITY` | derived | 5.867696e111 J/m^3 | `ħc/(8π²ℓ_P⁴)` | recompute mode `planck_vacuum_cutoff` (new) |
| `RECIPROCAL_UNIVERSE_PIXEL` | derived | 5.444685e61 dimensionless | reciprocal of `Δ_univ` | recompute mode `quotient` |

Live recompute (mpmath 50 dps, 2026-10-07):

* `ρ_Planck = 5.867696004847416…e111` J/m^3 — agrees with declared at 7 s.f.
* `ω_P = 1.85485865782…e43` s^-1 — agrees with declared at 7 s.f.
* `log10(ρ_Planck/ρ_Λ) ≈ 120.99` — **> 120**, so the gap is not closed.

## 5. Gate and harness (3ii)

* Gate: `tahap_uji_audit.py`, suite entry **15**, placed ahead of
  `report_claim_check.py` and `checksum_check.py`.
* Conditions V1..V11 (11 total): language, needle counts, honesty classes,
  dimensional honesty, Landauer floor, open problems, Gate 2 status,
  Gate 3 meaning, coercion withdrawal, `ρ_Λ` provenance, live recompute.
* Harness: `harnesses/a10_tahu_inj.py`, registered in `harness_check.py` as
  the 23rd harness. Eight defect classes, each aimed at a different
  condition; both documents restored byte-for-byte; marker
  `HARNESS: PASS -- 8/8 cases`.

## 6. Constitution updates

| File | Change |
|---|---|
| `Skill.md` | 14 → 15 root gates; fifteenth → sixteenth `--with-harness` entry; 22 → 23 proof harnesses |
| `Brain.MD` | v1.16; rows for `tahap_uji_audit.py`, `TAHU_A10_REPORT.md`; harness list includes `a10_tahu_inj`; suite/harness counts updated |
| `README.md` | Offline contract updated to A10 counts; new achievement row; phase table entry A10 |
| `REFERENCES.md` | Sections for the six new quantities + `WIKIPEDIA_DARK_ENERGY`; layer tally A10 = 24 records, A=10, B=12, C=2 |
| `external_constants.json` | 1 evidence + 6 quantities added |
| `provenance_check.py` | recompute mode `planck_vacuum_cutoff` |
| `suite_check.py` | gate 15 `tahap_uji_audit.py` |
| `harness_check.py` | harness `a10_tahu_inj.py` |

## 7. What remains open

| ID | Open item |
|---|---|
| A10-R1 | The `10^120` vacuum gap is **not solved**. A finite Planck cutoff is a cutoff, not a cosmological-constant solution. |
| A10-R2 | Gate 2 (quantum censorship) remains **not implemented**. |
| A10-R3 | RH, Navier--Stokes regularity and Langlands remain open in the literature regardless of any gate result here. |
| A10-R4 | `provenance/url_liveness.json` re-probed 2026-10-07 after the new Wikipedia URL entered the register: P11 offline record holds (`urls: 25, ok: 23, diverged: 2`; DIVERGED is measured, not failed — see A9). **CLOSED 2026-10-07.** |
| A10-R5 | `F8-R1` and `F8-R2` from the A9 report were closed by A11 (`A11_REPORT.md`); `F8-R3` and `F8-R4` remain as recorded. **PARTIALLY CLOSED 2026-10-07 (A11).** |

## 8. Residual after the rewrite

The two documents are now honest about what the corpus does and does not
establish. The machine gate `tahap_uji_audit.py` holds them there. Nothing
in this phase claims that the cosmological constant problem, RH, or
Navier--Stokes has been solved.
