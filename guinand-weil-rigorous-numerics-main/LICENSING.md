# Licensing — Hybrid Scheme

**Project:** OMEGA Framework: Certified Enclosure of Guinand–Weil Matrices at Extreme Scale
**Author:** Muhammad Aidil Amry · ORCID 0009-0002-9718-9710
**Affiliation:** Independent Researcher | South Sulawesi, Indonesia

This repository uses a **hybrid licence**, settled on 27 September 2026.

## The split

| material | licence | file | rationale |
|---|---|---|---|
| **Source code** — `src/`, `scripts/`, all `*.py` at the root | **MIT** | `LICENSE` | maximise scientific reproducibility; other groups must be able to run, test and extend the verification pipeline without friction |
| **Scholarly documents** — `WORKING_PAPER.md`, `README.md`, `REPO_STRUCTURE.md`, `CITATION.cff`, `docs/*.md` | **CC-BY-4.0** | `LICENSE-DOCS.md` | these are works of scholarship, not software; attribution must travel with them |
| **Computational logs** — `logs/*.md`, `logs/*.txt` | **CC-BY-4.0** | `LICENSE-DOCS.md` | evidence record; citable and quotable with attribution |
| **Saved matrices / data** — `data/*.json` | **CC-BY-4.0** | `LICENSE-DOCS.md` | numerical results derived from the scholarly work |
| **Third-party: the mathematical statement of $Q$** | attributed to the primary source | see below | not ours to relicense |

## GitHub's `LICENSE` file

GitHub's repository inspector reads the file named `LICENSE` and shows one
licence badge. That file is therefore **MIT**, because `src/` is the substance
a visitor would want to reuse. The scholarly-document licence is carried in
`LICENSE-DOCS.md` and is restated in the scope block at the foot of
`LICENSE`, so neither file can be read without a pointer to the other.

A visitor who reads only `LICENSE` still learns, in its final block, that
scholarly documents fall under CC-BY-4.0.

## Third-party attribution

The mathematical definition of the Guinand–Weil test matrix $Q$ is **not**
originated here. It is adopted verbatim from the primary source:

> `https://arxiv.org/html/2607.02828v3`

Our licence grants rights over *our* code and *our* text. It does not
relicense that definition, and it does not imply endorsement by the source
authors.

## Citation

Whichever licence applies to you, please cite via `CITATION.cff`. The
scholarly-document licence additionally *requires* attribution, which is the
point of choosing CC-BY-4.0 for the written record.
