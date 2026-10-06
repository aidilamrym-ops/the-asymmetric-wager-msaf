# REFERENCES.md — External Provenance Register for the MSAF Corpus

**Workspace:** `D:\THE ASYMMETRIC WAGER`
**Date opened:** 2026-10-05 (F3-1)
**Machine companion:** `external_constants.json` + `provenance_check.py`
**Standing:** every external quantity used by this corpus is listed here with its
authority, edition, uncertainty, retrieval date and a hashable evidence snapshot.
Nothing in this file supersedes an existing artefact by silent edit; the one
documented deviation found by F3-1 is declared openly in `PLANCK_LENGTH`.

> Why this file exists: before 2026-10-05 the corpus cited $\ell_P$, $D_{\text{obs}}$
> and $k_B$ inside its own documents with **no bibliography anywhere in the root
> tree**. The numbers were correct; the provenance was absent. This file closes
> that gap. Gate of record: `provenance_check.py` (exit 0/1/2).

---

## 1. Evidence snapshots

Each entry below is registered in `external_constants.json` with `bytes` and
`sha256`. Entries carrying a `local_copy` are hash-verified offline by the gate.

Since F5-2 every entry also carries a **layer**:

* **A** — the retrieved body is stored locally under `provenance/evidence/`
  because a redistribution permission was found for it (public domain,
  CC BY / CC BY-SA / CC BY-NC-SA, or the arXiv distribution licence).
* **B** — no redistribution permission was identified, so only the
  bibliographic record is kept and the body is discarded.
* **C** — the source could not be retrieved from this machine; the observed
  failure is recorded and no snapshot is claimed.

### Archive policy decision (A7, 2026-10-06)

`F4_REPORT.md` §9 R1 left the remainder of the archive open as *"a storage and
licensing decision rather than a code change"*. The decision has been taken, and
it is written here so that only a change of policy can reopen it:

* **Archive** a source only when a redistribution permission was actually read
  out of the retrieved document (public domain, CC BY / CC BY-SA / CC BY-NC-SA,
  or the arXiv distribution licence). That is the whole of layer **A**, and every
  layer-A file is hash-verified by `provenance_check.py` P2 or
  `theorem_provenance_check.py` P9 on each run.
* **Do not archive** a source whose landing page states no redistribution
  permission. The bibliographic record, the retrieval date and the observed
  status are kept and the body is discarded. That is layer **B**, and after A7 it
  is a recorded decision rather than an unfinished task.
* **Record** a source that cannot be retrieved at all, with the failure that was
  observed, instead of implying it was read. That is layer **C**.

A7 executed the decision. One further source qualified and was added as
`MOSSINGHOFF_TRUDGIAN_2015_ARXIV`; one former layer-C record (the Pitt
`measure.html` page) was re-fetched with HTTP 200 on 2026-10-06 and moved to
layer B because it carries only *"Copyright, John D. Norton"*; two layer-C
records were re-tried the same day and stayed at layer C (the Planck DOI and
`doi:10.1098/rspa.1970.0021`, both HTTP 403 from this machine even with a
browser user agent); the three SEP entries were re-read against
`https://plato.stanford.edu/info.html`, which grants reproduction only for fair
use and so stays at layer B; and an author manuscript of `PLATT_2017` was located
at the Bristol research portal but its licence field reads *Unspecified*, which
is not a redistribution permission, so that record also stays at layer B.

**Tally at A7: 23 records, A = 9, B = 12, C = 2** (22 records, A = 8, B = 11,
C = 3 at F5-2, 2026-10-05).

### NIST_CODATA_2022_TABLE

CODATA Recommended Values of the Fundamental Physical Constants, 2022 adjustment.
Publisher: NIST / CODATA Task Group on Fundamental Constants.
Machine-readable ASCII table.

* URL: `https://physics.nist.gov/cuu/Constants/Table/allascii.txt`
* DOI of the accompanying paper: `10.1063/5.0279860`
  (Mohr, Newell, Taylor, Tiesinga, *J. Phys. Chem. Ref. Data* **54**, 033105 (2025))
* Retrieved (UTC): 2026-10-05
* Bytes: 40801
* SHA-256: `77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67`
* Local copy: `provenance/evidence/nist_allascii_2022.txt`
* Access class: `full_text_local_copy` — layer **A**
* Licence basis: NIST Library FAQ, NIST publications are in the public
  domain and not subject to US copyright (17 U.S.C. 105)

### PLATT_TRUDGIAN_2021

Dave Platt, Tim Trudgian, *The Riemann hypothesis is true up to $3\cdot 10^{12}$*.

* arXiv: `2004.09765`
* URL: `https://arxiv.org/abs/2004.09765`
* Retrieved (UTC): 2026-10-05
* Bytes: 39398
* SHA-256: `c137519d02a5cbf7146fed1499c73e03943ce8cd75f9bf78f4d82d65bcc16bc7`
* Local copy: `provenance/evidence/arxiv_2004_09765_abs.html`
* Access class: `full_text_local_copy` — layer **A**
* Licence basis: arXiv non-exclusive distribution licence, linked from the
  retrieved page

### MOSSINGHOFF_TRUDGIAN_2015

M. J. Mossinghoff, T. S. Trudgian, *Nonnegative trigonometric polynomials and a
zero-free region for the Riemann zeta-function*, J. Number Theory **157**, 329-349 (2015).

* Retrieved (UTC): 2026-10-05 (cited from the reference list of arXiv:2004.09765)
* Access class: `publisher_landing_page` — layer **B** (no redistribution
  licence identified; body not archived)
* Licence check re-run by A7 (2026-10-06): the Elsevier/JNT landing page still
  states no redistribution permission, so this record stays at layer B.
* Snapshot: `MOSSINGHOFF_TRUDGIAN_2015_ARXIV` below, hash-verified locally —
  the open preprint of the same article, whose abstract states the constant
  `5.573412` this register records.

### MOSSINGHOFF_TRUDGIAN_2015_ARXIV

M. J. Mossinghoff, T. S. Trudgian, *Nonnegative trigonometric polynomials and a
zero-free region for the Riemann zeta-function* (arXiv preprint of the article
above).

* arXiv: `1410.3926`
* URL: `https://arxiv.org/abs/1410.3926`
* Retrieved (UTC): 2026-10-06
* Bytes: 39360
* SHA-256: `dff8840502d028d597f1ab9ab2c59f12cd5609eaba4601e8c968e599a6522419`
* Local copy: `provenance/evidence/arxiv_1410_3926_abs.html`
* Access class: `full_text_local_copy` — layer **A**
* Licence basis: arXiv non-exclusive distribution licence, linked from the
  retrieved page
* Role: added by A7 to execute the archive policy above. The submitted abstract
  reads *no zeros in the region $\sigma \ge 1 - 1/(5.573412 \log|t|)$ for
  $|t| \ge 2$*, which is `RF_ZERO_FREE_R_MT2015` read back out of an archived,
  hash-verified page rather than out of a landing page that cannot be retained.

### MOSSINGHOFF_TRUDGIAN_YANG_2024

M. J. Mossinghoff, T. S. Trudgian, A. Yang, *Explicit zero-free regions for the
Riemann zeta-function*, Res. Number Theory **10**, 11 (2024).

* DOI: `10.1007/s40993-023-00498-y` (corrected by F5-2; the register
  previously carried the mistyped `10.1007/s40993-024-00556-x`, which returns
  HTTP 404)
* Retrieved (UTC): 2026-10-05
* Bytes: 508435
* SHA-256: `9e02c1c934e3e38278f72ba0e1aa9e87fe1ab2953b1c6ce4077f04e7665bda45`
* Local copy: `provenance/evidence/springer_mty2024_open_access.html`
* Access class: `full_text_local_copy` — layer **A**
* Licence basis: open access under CC BY 4.0, stated in the retrieved page

### PLANCK_2018_VI

Planck 2018 results. VI. Cosmological parameters. Aghanim, N. et al. (Planck
Collaboration), *Astronomy & Astrophysics* **641**, A6 (2020).

* DOI: `10.1051/0004-6361/201833910`
* arXiv: `1807.06209`
* Retrieved (UTC): 2026-10-05
* Access class: `inaccessible` — layer **C** (HTTP 403 from the publisher
  host; no snapshot is claimed for this DOI)
* Snapshot: `PLANCK_2018_VI_ARXIV` below, hash-verified locally
* Role: provenance for the $\Lambda$CDM cosmology that yields
  $D_{\text{obs}} = 8.8\times10^{26}$ m. The catalogue of derived diameter used
  here is a **2-significant-figure reference value**, not a Planck headline
  number; no uncertainty is claimed for it.

### PLANCK_2018_VI_ARXIV

Planck 2018 results. VI. Cosmological parameters (arXiv preprint of the
article above).

* arXiv: `1807.06209`
* URL: `https://arxiv.org/abs/1807.06209`
* Retrieved (UTC): 2026-10-05
* Bytes: 78846
* SHA-256: `a8f46f86ddaea582f60500ab7708ec801a4e8d86b3be6ca9825ce9ca139e7c4d`
* Local copy: `provenance/evidence/arxiv_1807_06209_abs.html`
* Access class: `full_text_local_copy` — layer **A**
* Licence basis: arXiv non-exclusive distribution licence, linked from the
  retrieved page
* Role: the archived snapshot behind $D_{\text{obs}}$; added by F5-2 to close
  residual R3, since the canonical DOI is layer C.

### PLATT_2017

David J. Platt, *Isolating some non-trivial zeros of zeta*, Math. Comp. **86** (307),
2449-2467 (2017).

* DOI: `10.1090/mcom/3198`
* Retrieved (UTC): 2026-10-05
* Access class: `publisher_landing_page` — layer **B** (no redistribution
  licence identified; body not archived)
* Licence check re-run by A7 (2026-10-06): an author manuscript is retrievable
  from the Bristol research portal, but its licence field reads *Unspecified*,
  which is not a redistribution permission. The record therefore stays at
  layer B and no copy is kept.

---

## 2. Quantities used by the corpus

### PLANCK_LENGTH

Symbol $\ell_P$. Value `1.616255e-35` m, 7 significant figures, **not exact**.
Uncertainty: `1.8e-40` m (CODATA: `0.000 018 e-35`).

* Authority: CODATA 2022
* Evidence: `NIST_CODATA_2022_TABLE`
* Retrieved (UTC): 2026-10-05
* Appears in this corpus at two sites, and **they do not carry the same precision**:

| site | as written | status |
|---|---|---|
| `Skill.md` (canon row) | `1{,}616255 \times 10^{-35}` | agrees with the source at 7 s.f. |
| `01_PARADOX_AND_SCALE.md` L25 and L29 | `1.62 \times 10^{-35}` | agrees with the source at 3 s.f. (corrected by F5-1, 2026-10-05) |

**Variance found by F3-1 and closed by F5-1 (both 2026-10-05).**
F3-1 recorded openly, rather than editing silently, that
`01_PARADOX_AND_SCALE.md` read `1.63e-35` where the correctly rounded
3-significant-figure form of `1.616255e-35` is `1.62e-35` -- a relative
deviation of `8.504e-3` (+0.8504 %). F5-1, the phase permitted to edit that
file, corrected both sites (L25 and L29) and moved the register entry from
`declared_variance` to `source_agree`. Nothing downstream moved: both values
reproduce $N_{\text{steps}} \approx 5{,}4 \times 10^{61}$ at the two
significant figures the corpus declares for $N_{\text{steps}}$. The gate
now rejects the old value -- reverting the document, the register, or both
each produces a P3 or P4 failure (verified by the F5-1 stage-B probes).

### OBSERVABLE_UNIVERSE_DIAMETER

Symbol $D_{\text{obs}}$. Value `8.8e26` m, 2 significant figures, **not exact**.

* Uncertainty: none quoted. The value is **model dependent**: it is the
  $\Lambda$CDM comoving diameter (about 46.5 Gly radius, 93 Gly diameter)
  inferred from Planck cosmological parameters, not a directly measured length.
* The corpus already declares that only 2 significant figures are justified
  (`Skill.md` canon row, `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md`).
* Underlying cosmology: Planck 2018 results VI, Aghanim et al.,
  *A&A* **641**, A6 (2020), DOI `10.1051/0004-6361/201833910`, arXiv `1807.06209`.
* Authority for the quoted decimal: common reference value, cross-checked
  against the comoving-radius identity $2 \times 4.40\times10^{26}$ m.
* Evidence: no local copy of the Planck parameter table. The authority
  `PLANCK_2018_VI` is layer **C** (HTTP 403), and the layer-A snapshot
  `PLANCK_2018_VI_ARXIV` holds only the arXiv **abstract page**, in which
  `diameter` and `comoving` occur zero times — verified 2026-10-05 — so the
  decimal cannot be read back out of any archived text and the quantity carries
  an explicit `probe_waived` reason instead of silence. **This is a known
  provenance weakness and is recorded here rather than hidden**; a snapshot of
  the cosmological parameter table remains the candidate follow-up.
* Retrieved (UTC): 2026-10-05
* Sites: `01_PARADOX_AND_SCALE.md` L18 and L29 (`8.8 \times 10^{26}`),
  `Skill.md` canon row (`8{,}8 \times 10^{26}`).

### UNIVERSE_PIXEL_CONSTANT

$\Delta_{\text{univ}} = \ell_P / D_{\text{obs}}$. Value `1.836653e-62`,
7 significant figures **as a quotient of the declared inputs**; only 2 of those
figures are physically justified because $D_{\text{obs}}$ carries 2.

* Kind: derived. `derived_from = [PLANCK_LENGTH, OBSERVABLE_UNIVERSE_DIAMETER]`
* The gate recomputes this quotient independently at 100 decimal places and
  requires it to round to `1.836653e-62` at 7 significant figures.
* Sites: `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md` (`1,836653 \times 10^{-62}`),
  `Skill.md` canon row (`1{,}836653 \times 10^{-62}`).

### ZETA_DERIVATIVE_FIRST_ZERO

$|\zeta'(\rho_1)|$ where $\rho_1 = \tfrac12 + 14.1347251417346937904572519836 i$.

* Authoritative value (recomputed, `mpmath` 100 dps): `0.793160433356506116013897565274`
* Corpus site value: `0,7931604334` in `DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md`,
  i.e. 10 significant figures, a correct rounding of the authoritative value.
* Authority: recomputation on this machine (independent of any corpus artefact).
* Retrieved (UTC): 2026-10-05
* Note: the gate of record for the surrounding Section 2 claims remains
  `msaf_zeta_check.py`. This register only certifies the provenance chain and
  the rounding of the constant itself.

### BOLTZMANN_CONSTANT

Symbol $k_B$. Value `1.380649e-23` J K^-1, 7 significant figures as written,
**exact**.

* Uncertainty: `exact`. $k_B$ is a defining constant of the SI (2019), fixed at
  exactly `1.380649e-23` J K^-1, so the entry carries `exact: true` and
  `uncertainty: "exact"` rather than an error bar.
* Authority: SI 2019 defining constant, listed in the CODATA 2022 adjustment.
* Evidence: `NIST_CODATA_2022_TABLE`. The probe reads
  `provenance/evidence/nist_allascii_2022.txt` L62, where the
  `Boltzmann constant` line carries both the value `1.380 649 e-23` and the
  `(exact)` marker in the uncertainty column -- so the value and its
  exactness are read out of the archive together, not asserted.
* Retrieved (UTC): 2026-10-05
* Site: `SOLVABLE_FINITE_PARADOX.md` (`1{,}380649\times10^{-23}`).
* Added 2026-10-05 (A3), lifting the deferral recorded as F3-R5 / F5-R1.
  `landauer_check.py` remains the gate of record for the Landauer arithmetic
  that *uses* $k_B$; this entry answers a different question -- where the
  constant itself is quoted in the corpus, and whether that quotation matches
  the archived source.

---

## 3. Reference facts about the external state of the field

These record what the public literature has established, so that this corpus is
never read as contradicting a result it simply never cited.

### RF_RH_HEIGHT_VERIFIED

`3000175332800`

All non-trivial zeros $\rho$ with $0 < \Im(\rho) \le 3{,}000{,}175{,}332{,}800$
(about $3\cdot10^{12}$) have been verified to satisfy $\Re(\rho) = 1/2$, rigorously,
by interval / ball arithmetic.
Source: `PLATT_TRUDGIAN_2021`.

### RF_RH_ZEROS_ON_LINE

`12363153437138`

The count of non-trivial zeros covered by the verification above.
Source: `PLATT_TRUDGIAN_2021`.

### RF_ZERO_FREE_R_MT2015

`5.573412`

Best zero-free region constant $R$ in $\beta \ge 1 - 1/(R \log \gamma)$ for
$\gamma > 3$ at the time of arXiv:2004.09765.
Source: `MOSSINGHOFF_TRUDGIAN_2015` (layer B); the same constant is readable
from the layer-A snapshot `MOSSINGHOFF_TRUDGIAN_2015_ARXIV`.

### RF_ZERO_FREE_R_MTY2024

`5.559`

Improved zero-free region constant published in 2024, superseding the 2015 value.
Source: `MOSSINGHOFF_TRUDGIAN_YANG_2024`.

### RF_PLATT2017_ZERO_COUNT

`103800788359`

Non-trivial zeros isolated rigorously to absolute precision $\pm 2^{-102}$ up to
height $3.0610046 \times 10^{10}$.
Source: `PLATT_2017`.

---

## 4. Scope note

`provenance_check.py` gates the entries above. It does **not** re-derive the
claims of `msaf_zeta_check.py`, `landauer_check.py` or `gw_verify_production.py`;
those remain the gates of record for their own subjects. Every quantity listed
here that is also gated elsewhere is cross-referenced rather than duplicated.
