# Rigorous Ball Arithmetic and Bandwidth-Calibrated Spectral Analysis of the Guinand-Weil Operator Framework

## OMEGA Framework — Certified Enclosure of Guinand–Weil Matrices at Extreme Scale

<p align="center">
<strong>Muhammad Aidil Amry</strong><br>
ORCID <a href="https://orcid.org/0009-0002-9718-9710">0009-0002-9718-9710</a><br>
Independent Researcher | South Sulawesi, Indonesia<br><br>
<strong>Project:</strong> OMEGA Framework: Certified Enclosure of Guinand–Weil Matrices at Extreme Scale
</p>

---

## 1. Executive Summary

This repository reports a **certified enclosure** of the smallest eigenvalue of
the Guinand–Weil test matrix $Q_{100,40}$, together with the full diagnostic
record that produced it.

**Principal result.**

$$
\lambda_{\min}(Q_{100,40}) = +1.32105051975174632728899314595 \times 10^{-102}
$$

Two independent ball-arithmetic routes to this number were executed:

| route | tool | outcome |
|---|---|---|
| **A1** — `arb` enclosure + Weyl propagation | `flint.arb`, prec 1024 bits | **CERTIFIED**, margin **74.446 orders** over the required entry-error tolerance |
| **A2** — interval eigen-solver | `flint.arb_mat.eig` (`rump`, `vdhoeven_mourrain`) | **ENCLOSED STRICTLY POSITIVE**, 81/81 eigenvalues isolated, $\operatorname{Im} = 0$ |

Route A1 certifies positivity provided every matrix entry carries absolute
error below

$$
\rho^* = 1.63092656759474834688247443633\times 10^{-104},
$$

while the measured entry error at `dps 180` is

$$
\rho_{\text{actual}} = 5.83986112334288261\times 10^{-179},
\qquad \frac{\rho_{\text{actual}}}{\rho^*} = 3.5807014\times10^{-75}.
$$

> **Precision note that must travel with the number.** $\rho_{\text{actual}}$
> comes from dps-doubling. It is an **estimate**, not a proof: `mpmath` is not
> interval arithmetic, so an error stable across both precisions would not
> appear in the difference. The two links *above* it — the `arb` enclosure of
> the handed matrix and the Weyl inequality — are rigorous. The complete chain
> is therefore **certified conditional on one measured estimate**, and is
> described that way throughout this repository.

Route A2 is rigorous over the matrix as handed to `flint`. It agrees with the
`mpmath` eigenvalue to **79 significant decimal digits**.

**Scope.** This is a result about a *matrix constraint*. It is **not** a proof
of the Riemann Hypothesis, not a proof of Weil positivity, and not a
prime-counting or factorisation result. The source preprint disclaims all four,
and this repository disclaims them with it.

---

## 2. Epistemic Architecture (Zero-Fudging)

The system is designed so that a desired number cannot be produced by
relaxing a criterion. The rules below were fixed **before** the numbers were
read, and every deviation was declared **both before and after** the result.

### 2.1 The primary gate: cross-precision agreement ($dy$)

A quantity $y = -\log_{10}|\lambda|$ is evaluated at two independent
precisions. The claim is `RESOLVED` only if

$$
|y_2 - y_1| < 10^{-4}.
$$

A single-precision reading is never accepted. For $\lambda_{\min}(Q_{100,40})$
the corrected build gives:

| transition | $dy$ | verdict |
|---|---:|---|
| 180 → 260 | $2.11343\times10^{-79}$ | `RESOLVED` |
| 260 → 340 | $2.41909\times10^{-159}$ | `RESOLVED` |

### 2.2 The rejected gate: the precision floor test

A test of the form $\lambda > \lambda_{\max}\cdot 10^{-(dps-10)}$ was run and
found **self-referential**: it compares the *reported value* against the floor,
so noise that happens to fall above the floor passes. Concretely, the true
value $1.32\times10^{-102}$ sits 12 orders *below* the `dps 100` floor
($5.98\times10^{-90}$) while the test still reported "✅ 19 orders". The floor
test is retained in the logs as a **rejected** criterion; it is not used.

### 2.3 The declared deviation on the identity residual

The identity gate compares the defining integral against the closed form.

| precision | $\lvert\psi\rvert$ | $\lvert\psi'\rvert$ |
|---:|---:|---:|
| 140 | $9.381409\times10^{-140}$ | $4.807480089477698\times10^{-138}$ |
| 160 | — | $3.912055399093736\times10^{-159}$ |

Read literally, the $dy$ rule **fails** here: $y(140)=137.318084$,
$y(160)=158.407694$, so $dy = 21.08961 \not< 10^{-4}$. The residual sits at the
precision floor and tracks `dps`.

This deviation was **not** silently absorbed. It was declared before the
number was read, decided by an explicit recorded instruction, and declared
again afterwards. The accepted criterion was:

> *the residual must lie below $\lambda_{\min}$ at two consecutive precisions*

which holds with margins of **35.44 orders** (dps 140) and **56.53 orders**
(dps 160).

We do not describe this as "penetrating the precision floor" or as *absolutely
safe*. It is a **measurement at a stated precision with a stated margin**,
governed by a criterion that replaced the literal rule by explicit decision —
on the record.

### 2.4 Self-correction record

The strongest evidence that the pipeline does not force results is that it
**retracted its own claims eight times**. Each retraction is kept in
`GW_STATUS_2026-09-26.md`; none was deleted.

| # | retracted claim | how it was caught |
|---|---|---|
| 1 | `TENSION — UNRESOLVED` against a source scale of $10^{-59}$ (§7a) | re-read the source verbatim |
| 2 | "outlier" eigenvalue $-4.183251\times10^{-71}$ at `dps 100` | contaminated reading; withdrawn |
| 3 | floor test reported "19 orders" of safety | shown self-referential |
| 4 | Weyl "shift" of $1.746\times10^{-114}$ | came from a 12-digit literal, inside its own rounding |
| 5 | `NOT CERTIFIED, margin −63.41 orders` | JSON parsed at `dps 40`; measured the reader, not the matrix |
| 6 | "only a factor 2.6 more quadrature order is needed" | head already identical to 40 digits |
| 7 | panel subset difference $0.0078009845039928$ | invalid comparison; withdrawn |
| 8 | first `gw_tail_deep` run *worse* than baseline | missing $-\log\pi$ term; fixed and re-tested against `mp.diff` |

---

## 3. Retraction of §7a — Academic Clarification

On 26 September this repository recorded a `TENSION — UNRESOLVED` claim: the
source preprint appeared to state a spectral scale of $10^{-59}$ at
$(c,N)=(100,200)$, which our $\lambda_{\min}(Q_{100,40}) = 1.32\times10^{-102}$
exceeds by 43 orders.

**The tension did not exist. It was our own misreading of the source.**
It was retracted on 27 September after the source was read verbatim:

> *"driving $B_T$ below a spectral scale of $10^{-59}$ at $(c,N)=(100,200)$
> would require $T\approx8\cdot10^{62}$"* — preprint §1 / §$T=800$,
> `arXiv:2607.02828v3`

Three independent checks settle it:

| check | finding |
|---|---|
| source script field `certification_floor_solve` | `{target:"1e-59", T_required:7.98e62}` — a **$B_T$ certification target**, not a spectrum |
| full-text scan | `$\lambda_{\min}$` appears **exactly once**, in the Fig. 2 caption at $c=13,N=4$ |
| the published $(100,200)$ certificate | **inertia only**: $n_+=401$, $n_-=0$ — no $\lambda_{\min}$ value |

**What this demonstrates, precisely.** A correct number ($8\times10^{62}$,
independently verified) generated a *false* tension because the object it
described was misidentified. The system detected the error by re-reading the
primary source rather than by defending the claim. That is the behaviour we
mean by resistance to result-forcing: **the correction ran against our own
conclusion.**

We do **not** claim §7a proves the pipeline infallible. It documents one
specific misreading, caught and reversed.

---

## 4. Methodology

| component | version / choice |
|---|---|
| Python | 3.14 |
| arbitrary precision | `mpmath` (decimal `dps` 30 → 384) |
| ball arithmetic | `python-flint 0.9.0` (`flint.arb`, `flint.arb_mat`) |
| interval eigen-solver | `acb_mat.eig` via `arb_mat.eig`, `algorithm="rump"` |
| quadrature | Gauss–Legendre per panel (GL48 → GL400), adaptive IBP tail |

**Tooling status (stated per layer, not in one line):**

```
numerics   python 3.14 + mpmath + python-flint 0.9.0     RUN
Track C    lean 4.33.1 + Mathlib                         RUN
Track C    z3 4.16.0 (CLI) / z3 5.0.0 (Python binding)  RUN
not run    coqc / isabelle / dkcheck / gcc               NOT RUN
```

Every eigenvalue, enclosure and bound reported here is produced by **ball
arithmetic**, not by a proof assistant: the numerics are certified, they are
not kernel-checked. What `lean` and `z3` run on is Track C, section 4.1 --
the inference from those numbers and their exact-rational arithmetic.

### 4.1 Track C — Lean 4 / Z3 integration: **SHIPPED 2026-10-02**

This section read **NOT STARTED** in every earlier revision, and the
`proofs/TRACK_C.md` plan file that `REPO_STRUCTURE.md` reserved was never
written (that directory never existed either). What ships instead is the
module itself, flat in the root:

| file | role |
|---|---|
| `OMEGATrackC.lean` | 10 theorems: the Rayleigh/Weyl perturbation inference plus 7 side conditions as exact `ℚ` arithmetic |
| `track_c_make_smt.py` | reads the constants out of this README **and** out of the Lean file (no hand copy), then drives `z3` |
| `track_c_side_conditions.smt2` | generated `QF_NRA` file: one assertion, the conjunction of the 7 negations |
| `track_c_smt_z3.log` | every `z3` answer — the conjunction and each negation separately |
| `track_c_lean_verify.log` | `lean` build exit code + `#print axioms` for all 10 theorems |

**What ran on 2026-10-02 (evidence in the two logs above):**

* `lean` 4.33.1 compiled `OMEGATrackC.lean` with `exit=0`; `#print axioms`
  on all ten theorems returns `[propext, Classical.choice, Quot.sound]` and
  **no `sorryAx`**.
* `z3` 4.16.0 answered `unsat` to the conjunction of the seven negations and
  to each negation on its own (`7/7`); the literal cross-check found all
  three constants in this README **and** in the Lean file, `MATCH` on both.
* a circularity audit of `track_c_side_conditions.smt2` reports `GENUINE`:
  the file carries a single assertion whose contradiction needs the claim
  itself (`ctx=sat`, `script=unsat`, unsat core `[0]`), so no negated claim is
  being proved from a context that already hides one.

**What is deliberately out of scope.** `μ`, `ρ_actual` and `ρ*` are outputs
of the FLINT/Arb stage and enter the Lean module as *literals*;
`track_c_make_smt.py` proves that those literals are the ones printed in this
README, **not** that they are the correct values. Ball arithmetic is an
automatic numerics tool, not a proof assistant; describing it as one would be
a category error. `coqc`, `isabelle` and `dkcheck` are not installed on the
machine that produced this file, and `gcc` was not run.

**No claim of kernel verification is made for the numerics themselves.**

### 4.2 Known hazards recorded in the source

* `gw_qinf.py:47` sets `mp.mp.dps = 40` **at module level**. Any import of
  `gw_qinf` — directly or transitively — silently resets precision. Rule:
  **import first, set `mp.mp.dps` afterwards.** This landmine bit three times
  during the project; retraction #5 is a direct consequence.
* `gw_qinf.py:94` calls `mp.lerchphi`, which is **wrong** (see §5).

---

## 5. Principal Diagnostic Finding

The `mp.lerchphi` defect described in §7b of the status report does **not**
stop at the identity gate — it reaches the matrix itself, through the diagonal:

$$
M_{\text{shipped}} = M_{\text{corrected}} + \operatorname{diag}(\delta).
$$

Measured (`gw_entry_audit.py`, `dps 140`):

* $\delta(\pm40) = +3.39110921707750871\times10^{-102}$, $\delta(0)=0$
* $\max\lvert\delta\rvert = 1.4618493934897842764\times10^{-93}$ at $n=-27$,
  which is $1.10658099114\times10^{9}\times\lambda_{\min}$

**Yet the eigenvalue moves by only $7.36383130627605620505628284192\times10^{-118}$
(relative $5.57422384396\times10^{-16}$), sign unchanged.** The reason is
*measured*, not assumed: $\delta \equiv 0$ exactly for $\lvert n\rvert \le 10$
and the $\lambda_{\min}$ eigenvector is concentrated there. Chapter 4 of the
working paper develops this.

A useful side effect: replacing `mp.lerchphi` with the defining series cut the
build from **602.3 s to 2.6 s — a factor of 231.7** — while removing the defect.

---

## 6. Results at a Glance

| quantity | value | status |
|---|---|---|
| $\lambda_{\min}(Q_{100,40})$ | $+1.32105051975174632728899314595\times10^{-102}$ | `FINAL`, $dy=0$ across 140/180/260/340 |
| shipped vs corrected difference | $7.363831306276056\times10^{-118}$ | sign unchanged |
| determinant route vs `eigsy` | agree 25 digits, ratio 1.0 | cross-checked |
| FLINT `rump` enclosure | $\pm\,8.410\times10^{-309}$ | `ENCLOSED STRICTLY POSITIVE` |
| FLINT `vdhoeven_mourrain` | $\pm\,3.79\times10^{-279}$ | `ENCLOSED STRICTLY POSITIVE` |
| A1 margin | 74.446 orders | `CERTIFIED` *(one estimated link)* |
| $\psi'$ identity at $(100,40)$ | $4.807\times10^{-138}$ (140), $3.912\times10^{-159}$ (160) | `PASS`, 35.4 / 56.5 orders |
| $\lambda_{\min}(Q_{100,20})$ | $+3.0256658\times10^{-62}$ | `RESOLVED POSITIF`, dps 70 & 100 |
| c = 13 ladder, rung $N=64$ | $\lambda_{\min}=6.32135140948\times10^{-59}$ | identity valid 19 orders below |
| source-anchored point | $(13,4)$: $9.67926186051\times10^{-15}$ | only source-anchored value |
| Montgomery S2 Unfolding ($\sigma_u = 1.0$) | Power 94.4% ($N=401$), 92.7% ($N=801$), sep = 3.96 $\to$ 5.85 | `VALID OPERATIONAL DOMAIN` |
| S2 Undersmoothing Bias ($\sigma_u \le 0.5$) | sep < 1 (empty decision window), invariant/worse at $N=801$ | `ESTIMATOR PROPERTY` (not $N$-ceiling) |
| $\lambda_{\min}(Q_{100,400})$ lower bound | $+6.74709239897214291717530665950\times10^{-509}$ | `VERIFIED POSITIVE DEFINITE`, $n_+=801$, $n_-=0$ |
| max entry radius at $(100,400)$ | $1.398551439204522661230545\times10^{-5266}$ | `PASS` (gate $10^{-50}$), `symmetry_exact = true` |

### 6.1 The OMEGA-CORE chain (appended 2026-09-29)

The table above is the OPSI (d) chain of 27 September. A second, independent
chain was run after it and is now archived in this repository.

`gw_omega_core_v2.py` builds every entry **natively in Arb** -- there is no
`mpmath` decimal hand-off anywhere in the route -- and certifies inertia by
**interval $LDL^T$ (Sylvester)** rather than by sampling an eigensolver. At
$(c,N)=(100,400)$, $\dim = 801$:

* attempt 1 (9000 bits) stopped at **pivot index 723** because that pivot ball
  straddled zero. It was reported as **undetermined** and the precision was
  doubled -- it was *not* rounded to a sign. This is zero-fudging visible in the
  data.
* attempt 2 (18000 bits) certified all 801 pivots: $n_+ = 801$, $n_- = 0$, so
  the matrix is **positive definite**, with
  $\lambda_{\min} \ge 6.74709239897214291717530665950\times10^{-509}$.

The same engine closed $(c,N)=(100,800)$, $\dim = 1601$, on 2026-10-01:

* the earlier 9000-bit launch terminated as a **measured non-result**
  (undetermined at pivot 1087/1601) and was **not** rounded to a sign either;
  after the 03:15 power cut of 2026-09-30 the restart parameters were locked
  by the operator (`--prec 18000 --escalations 0`, see `gw_launch_v2.ps1`);
* attempt 1 (18000 bits) certified **all 1601 pivots**: $n_+ = 1601$,
  $n_- = 0$, undetermined = none, symmetry exact (mutual-containment
  deviation $= 0$, so the spectrum is provably real) -- the matrix is
  **positive definite**, with
  $\lambda_{\min} \ge 8.67526098867855342892890992571\times10^{-2877}$
  ($\min|d_i| = 2.3175889389605092798\times10^{-120}$ divided by
  $\|L^{-1}\|_F^2$ with $\|L^{-1}\|_F \le 1.6344699115298598798\times10^{1378}$);
* wall time: build 85,213.3 s + certified $LDL^T$ 38,024.0 s + bound
  10,354.0 s (attempt 1, no escalation, peak 8,251.7 MB). Result record
  `omega_core_v2_results.json` (sha256 `20ff0378...119cbc`, internal record
  `e42dad4b...2babb7`), verdict line in `omega_v2_stdout.txt`; invariant gates
  `gw_verify_results.py` (fixtures) and `gw_verify_production.py` (production
  row) both PASS, exit 0.

Full derivation (matrix definition $A_{ij}=W_{02}-W_R-W_p$, the closed forms,
the bound $\lambda_{\min}\ge \min|d_i|/\|L^{-1}\|_F^2$, the telemetry schema,
the five defects found by execution, and the byte-hash inventory) is in
**[`OMEGA_CORE_CERTIFICATE.md`](OMEGA_CORE_CERTIFICATE.md)**.

**Status:** $(100,400)$ `CERTIFIED`. $(100,800)$ `CERTIFIED` (2026-10-01,
1601/1601 certified, verdict **VERIFIED POSITIVE DEFINITE**, bound above).
Both targets carry results and verdicts and are counted toward the claims in
this document.

---

## 7. Reproducibility

```bash
# corrected build + phases 1..6 (incl. ball-arithmetic phase 6)
python gw_corrected_eig.py 100 40 180

# shipped vs corrected, same code path
python gw_compare_builds.py 100 40 140

# precision ladder for lambda_min
python gw_lam_dps.py 100 40 180 260 340

# A1: certified tolerance + measured entry error
python gw_arb_sweep.py gw_matrix_100_200_dps400.json

# entry-error dps-doubling: loads a saved matrix at dps_lo, rebuilds it at dps_hi.
# The dps-180 / dps-260 input matrices of record are NOT shipped in this repo --
# only gw_matrix_100_200_dps400.json is -- so the line below documents the
# invocation and is not runnable from the shipped data alone (see the
# entry-error retraction in GW_STATUS_2026-09-26.md).
python gw_entry_error.py 100 40 180 260 <matrix_dps180.json>

# A2: interval eigen-solver
python gw_corrected_eig.py 100 40 180      # phase 6

# identity gate
python gw_final_gate.py 100 40 160 1000 224
```

**OMEGA-CORE chain (added 2026-09-29).** Both gates below are mandatory
*before* any large sweep, and the invariant check is mandatory *before*
reporting any result:

```bash
# static reference gate
python gw_check_refs.py

# smoke: certified path (N=20 @ 9000 bits)
python gw_omega_core_v2.py --c 100 --dims 20 --prec 9000 --out smoke_results.json

# smoke: escalation-exhausted path (N=20 @ 200 -> 400 bits)
python gw_omega_core_v2.py --c 100 --dims 20 --prec 200 --escalations 1 --out smoke_escalate.json

# JSON invariant gate (no argument: fixtures come from GW_FIXTURE_DIR,
# default the fixtures next to the script -- see the gate overrides below)
python gw_verify_results.py

# the certified target (allow escalation; expect ~11 h on a 4-core laptop)
python gw_omega_core_v2.py --c 100 --dims 400 --prec 9000 --escalations 3 \
    --out omega_core_v2_results.json
```

`source_arb_ldlt_certify.py` must be importable from its own directory. Note
that `gw_qinf.py` line 47 sets `mp.mp.dps = 40` at module import time while
`python-flint` uses `flint.ctx.prec` -- the two are not interchangeable.

**Track C (added 2026-10-02).** Two commands, both exit 0 on the shipped
files; neither needs any of the numerics above:

```bash
# 1. literal cross-check (README <-> Lean) + the seven side conditions via z3
#    (regenerates track_c_side_conditions.smt2 and track_c_smt_z3.log)
python track_c_make_smt.py

# 2. type-check the module and print the axiom footprint of its 10 theorems
#    (needs Lean 4.33.1 + Mathlib on LEAN_PATH; see track_c_lean_verify.log)
lean OMEGATrackC.lean
```

### 7.1 Tested environment and what reproduces identically

Measured on the machine that produced the shipped results:

| component | version |
|---|---|
| CPython | 3.14.4 (`C:\Python314\python.exe`) |
| python-flint | 0.9.0 (`flint.arb` / `flint.arb_mat`, ball arithmetic) |
| mpmath | 1.3.0 (arbitrary-precision decimals, gate parsing only) |
| Lean (Track C) | 4.33.1 (`x86_64-w64-windows-gnu`, commit `819816b2e0`) + Mathlib |
| z3 (Track C) | 4.16.0 CLI, 5.0.0 Python binding |
| OS | Windows 10, PowerShell 5.1, 2C/4T laptop, ~13 GB RAM |

**Reproduces identically** on any machine with that toolchain:

* every verdict and certificate number -- `n_pos`, `n_neg`, `undetermined`,
  `symmetry_dev = "0"`, the anomaly/caveat lists, and the bound string
  `8.67526098867855342892890992571e-2877` -- is a function of the Arb
  interval enclosures, which contain the truth by construction;
* all three gates exit 0 on the shipped fixtures and the shipped production
  row: `python gw_check_refs.py`, `python gw_verify_results.py`,
  `python gw_verify_production.py` (seconds; run from any directory -- paths
  resolve relative to each script file, since 2026-10-01);
* Track C regenerates the same way: `python track_c_make_smt.py` re-reads the
  three constants from this README *and* from `OMEGATrackC.lean`, rewrites
  `track_c_side_conditions.smt2`, and must return `unsat` for the conjunction
  and for each of the seven negations (`exit 0`);
  `lean OMEGATrackC.lean` returns `exit 0` with the axiom footprint recorded
  in `track_c_lean_verify.log`.

**May differ across environments:**

* a different python-flint / Arb release can widen an enclosure, changing the
  last printed digits of a bound. The verdict and the order of magnitude
  cannot change -- an enclosure either contains a sign or it does not;
* wall-clock times are machine-specific. The N=800 target consumed
  133,591.3 s of phase time here (build 85,213.3 s + certified LDL^T
  38,024.0 s + bound 10,354.0 s; peak 8,251.7 MB);
* `gw_launch_v2.ps1`, `gw_sysmon.ps1` and `gw_watchdog.py` are Windows-only
  operational telemetry scripts with machine-local paths; they are not needed
  to reproduce any result. Gate overrides: `gw_verify_production.py` takes
  the N=800 result as `argv[1]` and the N=400 result as `argv[2]` (defaults:
  the two files next to the script); `gw_check_refs.py` accepts an explicit
  file as `argv[1]`; `gw_verify_results.py` reads `GW_FIXTURE_DIR` (default:
  the fixtures next to the script).

Fastest independent check after `git clone`: the three gates above, then the
N=20 smoke runs in section 7. The shipped N=400 artefact
(`omega_core_v2_results_N400.json`) is cross-checked against all three
written records of its bound in seconds by `gw_verify_production.py`; rerunning
the N=400 target itself is hours of runtime, and the full N=800 target is a
~37 h rerun.

---

## 8. Primary Source

The mathematical statement of the Guinand–Weil matrix is taken from the
primary source and never reconstructed from memory:

> `https://arxiv.org/html/2607.02828v3`

---

## 9. Citation

```bibtex
@misc{amry2026omega,
  author       = {Amry, Muhammad Aidil},
  title        = {OMEGA Framework: Certified Enclosure of {G}uinand--{W}eil
                  Matrices at Extreme Scale},
  year         = {2026},
  orcid        = {0009-0002-9718-9710},
  affiliation  = {Independent Researcher, South Sulawesi, Indonesia},
  note         = {Matrix-constraint verification. Not a proof of the Riemann
                  Hypothesis.}
}
```

---

## 10. License & Status

**Hybrid licence** (settled 27 September 2026) — see `LICENSING.md`:

| material | licence |
|---|---|
| **source code** (all `*.py`) | **MIT** — `LICENSE` |
| **scholarly documents** (`*.md`, `*.txt`, `*.json`, `*.log`, `*.cff`, `*.sha256`) | **CC-BY-4.0** — `LICENSE-DOCS.md` |

* Mathematical statement of $Q$: attributed to the primary source above — **not**
  relicensed by us.
* Status: **working repository accompanying `GW_STATUS_2026-09-26.md`.**
  Open items are listed in §8 of that file and are **not** started without
  explicit instruction.

**Disclaimer.** No claim in this repository establishes the Riemann
Hypothesis, Weil positivity, a prime-counting result, or a factorisation
method.
