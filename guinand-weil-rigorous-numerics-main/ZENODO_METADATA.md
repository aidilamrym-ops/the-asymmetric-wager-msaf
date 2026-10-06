# ZENODO_METADATA.md

Ready-to-paste metadata for the manual Zenodo upload form.
Companion file: [`.zenodo.json`](.zenodo.json) (machine-readable, Zenodo metadata format).

---

## 1. Title

```
Rigorous Ball Arithmetic and Bandwidth-Calibrated Spectral Analysis of the Guinand-Weil Operator Framework
```

## 2. Authors / Creators

```
Amry, Muhammad Aidil
```

| field | value |
|---|---|
| Affiliation | Independent Researcher \| South Sulawesi, Indonesia |
| ORCID | `0009-0002-9718-9710` |

Zenodo parses `name` as `Family, Given`. This was corrected from the earlier
draft `Dahlia, Muhammad Aidil Amry`, which made *Dahlia* the family name, to match
the public ORCID record `0009-0002-9718-9710` (`family-name: Amry`,
`given-names: Muhammad Aidil`) that `CITATION.cff` already followed. Architect's
decision, 2026-09-27 — recorded here rather than changed silently.

## 3. Upload type / Access / License

| field | value |
|---|---|
| Resource type | **Software** |
| Access right | **Open** |
| License | **MIT** |
| Version | `v1.0.0-certified` |

## 4. Abstract (copy-paste block)

```
This repository provides a fully reproducible, deterministic, and rigorously
verified numerical framework for the Guinand-Weil explicit formula matrix
operators. Utilizing high-precision ball arithmetic (arbitrary precision via
FLINT/Arb) on consumer-grade hardware, this codebase verifies positive
definiteness and inertia constraints (201+200=401) up to precision bounds of
10^-398 to 10^-1170.

It also ships a bandwidth-calibrated spectral-correlation instrument (S1/S2)
whose unfolding bandwidth is swept at sigma_u = 0.3, 0.5, 1.0: power is >= 90%
at sigma_u = 1.0 and 0% at sigma_u <= 0.5, so the bandwidth, not the sample
size N, is the binding constraint. On the real spectrum at this resolution the
instrument returns S1 = INCONCLUSIVE and S2 = INCONSISTENT WITH MONTGOMERY;
neither is a confirmation of Montgomery's conjecture.

Includes complete forensic audit trails and cryptographic provenance manifests,
together with an explicit register of known residual defects (cacat 18, cacat
19, and the unexplained K5 row of the pipeline report). No claim is made about
the Riemann Hypothesis, Weil positivity, prime counting, or integer
factorisation.
```

## 5. Keywords (paste as a comma-separated list)

```
Guinand-Weil Formula, Ball Arithmetic, Arbitrary Precision, Spectral Analysis, Random Matrix Theory, FLINT/Arb, Rigorous Numerics
```

## 6. Provenance and integrity files to upload alongside the code

| file | purpose |
|---|---|
| `GUINAND_WEIL/PROVENANCE.txt` | SHA-256 of the 4 verification scripts, 8 run logs, and 1 input file |
| `GUINAND_WEIL/THIRD_PARTY_SOURCES.md` | licence of the single vendored file (MIT, byte-identical to upstream) + runtime dependency versions |
| `GUINAND_WEIL/CHECKSUM.sha256` | per-file SHA-256 manifest |
| `GUINAND_WEIL/GW_STATUS_2026-09-26.md` | full audit report, including the open defects |
| `state/STATE.md` | session log with the pre-registered rules and their amendments |

---

## 7. NOTE ON CLAIM EDITING (recorded openly, not done silently)

The abstract above differs from the originally drafted text in **one** place
(entry 7a below), and this file was additionally realigned with `.zenodo.json`
in one place (entry 7b). Both are recorded here rather than changed silently.

### 7a. Spectral-correlation wording

The draft listed *spectral correlation* among the things the codebase
**"verifies"**. That wording is not supported by the audited verdicts:

| statistic | audited verdict on the real spectrum |
|---|---|
| S1 (gap ratio) | `INCONCLUSIVE` (chart-dependent: T and L disagree) |
| S2 (pair correlation) | `INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION`, all 6 grid points |

Both numbers come from `gw_montgomery_100_200_run2.log` and are reported in
`GW_STATUS_2026-09-26.md`. The correction states the instrument's *measured
power* (`>= 90%` at `sigma_u = 1.0`, `0%` at `sigma_u <= 0.5`) instead of
implying a positive RMT confirmation that was not obtained.

Everything else in the draft — `201+200=401`, `10^-398`, `10^-1170`,
`sigma_u = 1.0` — was checked against the repository and matches:

- `GW_STATUS_2026-09-26.md:669,1081` — inertia `n+ = 201+200 = 401`, `n- = 0`
- `GW_STATUS_2026-09-26.md:316,342` — `delta_Linf = 4.1137004583661995868e-398`
- `GW_STATUS_2026-09-26.md:1015` — enclosure radius `1.8120487388668704061e-1170`
- `gw_s2_ceiling_run3.log` — power `94.4%` (N=401) / `92.7%` (N=801) at `sigma_u = 1.0`

### 7b. Paste block realigned with `.zenodo.json` (Architect's decision, 2026-09-27)

Section 4 of this file and the `description` field of `.zenodo.json` differed by
exactly one sentence — 1085 vs 1157 characters, everything else byte-equal after
whitespace normalisation:

| source | end of the final paragraph |
|---|---|
| `.zenodo.json` | "...an explicit register of known residual defects **(cacat 18, cacat 19, and the unexplained K5 row of the pipeline report)**." |
| this file (before) | "...an explicit register of known residual defects." |

The shorter form was the omission. The Architect chose to **publish the explicit
list**, so section 4 now carries the parenthetical naming all three residuals.
This only names defects that are already registered openly in
`GW_STATUS_2026-09-26.md` (§7a, §7h.6–§7h.8) — it adds no new claim and retracts
nothing. The cross-check `zenodo_xcheck.py` asserts the two strings are equal
after whitespace normalisation, so they cannot drift apart again silently.
