# Licensing — hybrid scheme for this repository

**Project:** The Asymmetric Wager — Modular Scale Arithmetic Framework (MSAF)
**Author:** Muhammad Aidil Amry · ORCID 0009-0002-9718-9710
**Affiliation:** Independent Researcher | South Sulawesi, Indonesia
**Canonical DOI:** https://doi.org/10.5281/zenodo.22791556

This repository uses a **hybrid licence**. It mirrors the scheme already in
force inside `guinand-weil-rigorous-numerics-main/LICENSING.md`, so the two
trees do not contradict each other.

## The split

| material | licence | file | rationale |
|---|---|---|---|
| **Machine-readable artefacts** — `*.py` at the root, `harnesses/*.py`, `mcp/*.py`, `*.smt2` | **MIT** | `LICENSE` | maximise reproducibility; another group must be able to run the gates, the harnesses and the solver checks without friction |
| **Scholarly documents** — every `*.md` at the root: the corpus, `F0_REPORT.md` … `F5_REPORT.md`, `README.md`, `Brain.MD`, `Skill.md`, `AGENTS.md`, `REFERENCES.md`, `LICENSING.md` | **CC-BY-4.0** | this file | these are works of scholarship, not software; attribution has to travel with them |
| **Numerical registers and data** — `external_constants.json`, `theorem_provenance.json`, `zeta_pixel_results.json`, `CHECKSUM.sha256`, `protocol_09.log` | **CC-BY-4.0** | this file | the evidence record; citable and quotable with attribution |
| **Third-party material** | as recorded at each item | see below | not ours to relicense |

## What neither licence covers

Three classes of file in this repository are **excluded from this licence
grant**, because this repository did not create them and has no standing to
relicense them:

1. **`guinand-weil-rigorous-numerics-main/`** — a self-contained tree with its
   own hybrid licence: MIT for its source code, CC-BY-4.0 for its scholarly
   documents, set out in
   `guinand-weil-rigorous-numerics-main/LICENSING.md`. Its `LICENSE` file is
   the one GitHub reads for that subtree.

2. **`provenance/evidence/`** — verbatim snapshots of external sources,
   retained so that a quoted number can be re-checked against the page it
   came from. Each snapshot keeps the licence basis recorded against it in
   `REFERENCES.md` and in the registers:

   | snapshot | licence basis |
   |---|---|
   | `nist_allascii_2022.txt` | NIST publications are in the public domain and not subject to US copyright (17 U.S.C. 105) |
   | `arxiv_1807_06209_abs.html` | arXiv non-exclusive distribution licence |
   | `arxiv_2004_09765_abs.html` | arXiv non-exclusive distribution licence |
   | `arxiv_2410_17036_abs.html` | CC BY-NC-SA |
   | `springer_mty2024_open_access.html` | CC BY 4.0, as stated on the retrieved page |
   | `wikipedia_countably_additive_measure.html` | CC BY-SA |
   | `wikipedia_ihara_zeta_function.html` | CC BY-SA |
   | `wikipedia_ultraviolet_catastrophe.html` | CC BY-SA |

   The licence in this file grants rights over *our* text. It does not
   relicense those pages, and it does not imply endorsement by their authors
   or publishers.

3. **`source_arb_ldlt_certify.py`**, vendored inside the sub-repository —
   MIT, Copyright (c) 2026 Akiva Groskin, with provenance, both pinned
   SHA-256 values and the licence text reproduced in
   `guinand-weil-rigorous-numerics-main/THIRD_PARTY_SOURCES.md`.

## The CC-BY-4.0 terms

Canonical licence text (governs in full):

    https://creativecommons.org/licenses/by/4.0/legalcode

Human-readable summary:

    https://creativecommons.org/licenses/by/4.0/

**You are free to:**

* **Share** — copy and redistribute the material in any medium or format.
* **Adapt** — remix, transform, and build upon the material for any purpose,
  even commercially.

**Under the following terms:**

* **Attribution** — you must give appropriate credit, provide a link to the
  licence, and indicate if changes were made. You may do so in any reasonable
  manner, but not in any way that suggests the licensor endorses you or your
  use.
* **No additional restrictions** — you may not apply legal terms or
  technological measures that legally restrict others from doing anything the
  licence permits.

**Notices:** no warranties are given. The licensor may not be able to grant
all the permissions necessary for your intended use. Other rights such as
publicity, privacy, or moral rights may limit how you use the material.

## Mandatory attribution

    Muhammad Aidil Amry. "The Asymmetric Wager: Modular Scale Arithmetic
    Framework." ORCID 0009-0002-9718-9710. Independent Researcher, South
    Sulawesi, Indonesia, 2026. Licensed CC-BY-4.0.
    https://doi.org/10.5281/zenodo.22791556
    https://creativecommons.org/licenses/by/4.0/

## Note on substantive claims

Nothing in this repository establishes the Riemann Hypothesis, Weil
positivity, a prime-counting result, or a factorisation method. The Critical
Line at 0.5 is asserted as a Scale Axiom of this framework, not as a theorem
proved to infinity, and no claim here is offered as a proof of any open
problem.
