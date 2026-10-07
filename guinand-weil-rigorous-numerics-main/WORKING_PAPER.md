---
title: "Certified Enclosure of the Smallest Eigenvalue of a Guinand–Weil Test Matrix at Extreme Scale"
subtitle: "OMEGA Framework: Ball-Arithmetic Verification of $Q_{100,40}$ with a 74-Order Positivity Margin"
author:
  - name: Muhammad Aidil Amry
    orcid: 0009-0002-9718-9710
    affiliation: Independent Researcher, South Sulawesi, Indonesia
date: 27 September 2026
status: Working paper — not yet submitted
lang: en
geometry: margin=1in
fontsize: 11pt
---

# Abstract

We report a certified enclosure of the smallest eigenvalue of the Guinand–Weil
test matrix $Q_{100,40}$ constructed from the primary source
(`arXiv:2607.02828v3`), and give the full diagnostic record behind it.

$$
\lambda_{\min}(Q_{100,40}) = +1.32105051975174632728899314595\times10^{-102}.
$$

Two ball-arithmetic routes were executed with `python-flint 0.9.0` at 1024
working bits. **Route A1** combines an `arb` enclosure of the matrix as handed
with Weyl propagation of an enclosed per-entry error bound, certifying positivity
with a margin of **74.4468 orders** above the required tolerance
$\rho^*=1.63092656759474834688247443633\times10^{-104}$. **Route A2**, the
validated interval eigen-solver `acb_mat.eig`, isolates all 81 eigenvalues under
both the `rump` and `vdhoeven_mourrain` algorithms and returns an enclosure
strictly positive with zero imaginary part; it agrees with the arbitrary-precision
`mpmath` value to **79 significant decimal digits**.

The entry-error link of the chain was, until 2026-10-07, a dps-doubling
*estimate*: `mpmath` is not interval arithmetic, so an error invariant under
dps-doubling would not have appeared. It is now a ball-arithmetic upper bound
(§3.2), so the chain no longer rests on an estimate — but the bound is a
Python/FLINT output consumed as a literal in the Lean module, not a
kernel-checked quantity, and we state that rather than claiming otherwise.

We further document a defect in `mp.lerchphi` that propagates into the matrix
diagonal, producing a maximal entry perturbation of
$1.4618493934897842764\times10^{-93}$ — $1.1\times10^{9}$ times the eigenvalue
itself — while shifting $\lambda_{\min}$ by only
$7.363831306276056\times10^{-118}$, a relative change of
$5.57422384396\times10^{-16}$. The insensitivity is *measured*: the perturbation
vanishes identically for $|n|\le 10$, and the corresponding eigenvector is
localised there. We record eight self-retracted claims, including two produced
by our own instrumentation.

**Keywords:** Guinand–Weil matrix, smallest eigenvalue, ball arithmetic, interval
eigen-solver, verified numerics, eigenvalue localisation

**Scope statement.** This is a result about a *matrix constraint*. It is not a
proof of the Riemann Hypothesis, of Weil positivity, of a prime-counting
statement, or of a factorisation method. The source preprint disclaims all four.

---

# Chapter 1 — Introduction to Guinand–Weil Spectral Analysis

## 1.1 The object

The Guinand–Weil test matrix $Q(m,n;c)$ is defined in the primary source. We
adopt its statement verbatim and never reconstruct it from memory; the complete
definition, including the archimedean block and the pole term, is held in
`src/core/gw_qinf.py` and cross-checked against the source at every revision.

The matrix depends on the parameters $c>1$ and the half-size $N$, with
$L=\log c$ and index range $m,n\in\{-N,\dots,N\}$. Two structural properties
will matter throughout:

1. **Dependence on $N$ is only through the index range.** Every entry of
   $Q_{\text{full}}(m,n)$ depends on $(m,n,c)$ via $L$ and not on $N$. Hence
   $Q_{40}$ is a *principal submatrix* of $Q_{200}$, and Cauchy interlacing gives
   $$
   \lambda_{\min}(Q_{100,200}) \le \lambda_{\min}(Q_{100,40}).
   $$
   This inequality is used only as a structural remark, never as a measurement.

2. **The archimedean block enters through two closed forms.** Writing
   $\psi_{\text{arch}} = \alpha_L$ and
   $\psi'_{\text{arch}} = -2(\gamma_L - \beta_L)$, the diagonal reads
   $$
   P_0[n] = -2(\gamma_L-\beta_L) + \psi'_{\text{prime}}(n),
   \qquad
   Q(m,n) = \frac{P_0[m]-P_0[n]}{m-n} + \text{pole}.
   $$
   A single defective scalar function therefore contaminates $Q$ **purely
   through the diagonal**, since $Q$ depends on the archimedean block only via
   differences of $P_0$.

## 1.2 What is being claimed

The object of this paper is the *positivity of one finite symmetric matrix at
one parameter pair*, established to a stated margin. The literature context —
and the reason such a matrix is of interest at all — is the spectral
interpretation developed in the source. We do not extend that interpretation.

## 1.3 Evidentiary rules

Three rules were fixed before any number in this paper was read.

**R1 — Cross-precision agreement.** With $y=-\log_{10}|\lambda|$, a value is
`RESOLVED` only if $|y_2-y_1| < 10^{-4}$ at two independently set precisions.

**R2 — The floor test is rejected.** A test of the form
$\lambda > \lambda_{\max}\cdot10^{-(dps-10)}$ compares the *reported* value
against the floor and is therefore self-referential: noise falling above the
floor passes. We show this concretely — the true
$\lambda_{\min}=1.32\times10^{-102}$ lies 12 orders below the `dps 100` floor
($5.98\times10^{-90}$) while the test still reported "19 orders" of margin. The
test is retained in the logs as rejected and is not used.

**R3 — Deviations are declared twice.** Any departure from R1 is announced
before the number is read and again after it, with the replacement criterion
stated in advance. §1.4 is the one instance.

## 1.4 The declared deviation

For the identity residual $\psi'$ at $(100,40)$ the literal R1 fails:
$y(140)=137.318084$, $y(160)=158.407694$, so $dy=21.08961\not<10^{-4}$. The
residual tracks `dps` because it sits at the precision floor.

The replacement criterion, stated before the second precision was run, was:

> the residual must lie below $\lambda_{\min}$ at two consecutive precisions.

Measured margins: **35.44 orders** at `dps 140`
($\psi' = 4.807480089477698\times10^{-138}$) and **56.53 orders** at `dps 160`
($\psi' = 3.912055399093736\times10^{-159}$).

We present these as measurements with stated margins. We do not describe them
as absolute safety, and the deviation is not folded into R1.

## 1.5 Tooling

Python 3.14, `mpmath` ($dps$ 30–384), `python-flint 0.9.0`. Every eigenvalue,
enclosure and bound reported in this paper is produced by ball arithmetic;
**the numerics are not kernel-checked by a proof assistant**, and we do not
present them as if they were. Ball arithmetic is an automatic numerics tool.

Added after this text was first written (2026-10-02, repository root, README
§4.1): a Lean 4 module `OMEGATrackC.lean` covering the certified-tolerance
perturbation inference that underpins Route A1 (Chapter 3) -- the Rayleigh /
Weyl step, the constants $81 < C < 82$, and the measured margin -- over the
literals this paper prints, cross-checked against `z3` for its seven
exact-rational side conditions. `lean` and `z3` **have been run**
on that module (logs: `track_c_lean_verify.log`, `track_c_smt_z3.log`). The
module takes $\mu$, $\rho_{\text{actual}}$ and $\rho^*$ as *literals* -- it
checks that they are the numbers this paper states, not that they are correct
numbers. `coqc`, `isabelle`, `dkcheck` and `gcc` were **not run**.

---

# Chapter 2 — Panel-Resolution Diagnostics at the Critical Panel $\{39,40\}$

This chapter answers a narrow question: *is the discrepancy between the
defining integral and the closed form a defect of the closed form, or an
artefact of the quadrature?* The answer determines whether any eigenvalue
computed downstream can be trusted at all.

## 2.1 The singularity lies on the panel boundary

The integration domain is partitioned into panels of width
$T = 2\pi/L$, with Gauss–Legendre nodes on each. The cut-off structure of the
integrand is **not generic**: the singular scale satisfies
$$
d = \rho n = nT \quad\text{exactly},
$$
so every critical point falls on a panel *edge*, for all $n$. A quadrature rule
applied across such a boundary loses its convergence order in a way that
cannot be repaired by increasing the node count alone.

This structural fact is the reason the diagnostics below localise so sharply
onto the first panel rather than distributing over the domain.

## 2.2 Per-panel localisation of the quadrature discrepancy

Measuring the GL48→GL64 difference panel by panel:

| panel | share of total difference |
|---:|---:|
| 0 | **94.74 %** |
| 1 | 1.316 % |
| 4–8 | $7.7037198\times10^{-33}$ — the `dps 30` noise floor |

Order-escalation of panel 0 alone, at two independent precisions (`dps 70` and
`dps 120`, bit-identical):

| escalation | residual |
|---|---:|
| 48 → 64 | $2.31859\times10^{-30}$ |
| 64 → 96 | $1.83102\times10^{-37}$ |
| 96 → 128 | $6.83785\times10^{-56}$ |

The sequence decreases monotonically and identically at both precisions:
**the head is quadrature-limited and converging**, not closed-form-deficient.

## 2.3 The critical panel $\{39,40\}$

Panel $\{39,40\}$ is the one where the two candidate explanations — rounding
at a critical panel versus an incorrect closed form — are directly separable.

| comparison | value |
|---|---:|
| `mp.quad` vs GL224 at $\{39,40\}$ | $-6.915533833\times10^{-74}$ |
| … at *both* quadrature orders | **identical** |

The difference does not move when the quadrature order changes. That is the
signature of **`mp.quad`'s own precision floor**, not of an unresolved
integral: a genuine truncation error would respond to order escalation, a
precision floor does not.

Supporting convergence data for the head:

| comparison | value | reading |
|---|---:|---|
| GL96 vs GL224 | $3.3522821109408\times10^{-79}$ | panel 0 = **100 %** of the movement |
| GL400 vs GL224 | $\le 1.5314658188969\times10^{-137}$ | converged |
| `mp.quad` vs GL224, panel 0 | $4.100266179\times10^{-143}$ | converged |

## 2.4 The exact null space of the pole block

The pole term contributes a block $Q_{\text{pole}}$ possessing an **exact
$N$-dimensional kernel**. This is a *structural*, provable degeneracy of the
block in isolation — the eigenvalue zero occurs there exactly, not numerically.

It is essential to state what this does and does not establish.

* It **does** explain why zero-eigenvalue phenomena must be excluded from any
  numerical spectrum claim: a solver reporting a zero eigenvalue inherited from
  the pole block has said nothing about $Q$.
* It **does not** transfer to the full matrix. In $Q_{100,40}$ the archimedean
  block lifts the kernel, and the measured smallest eigenvalue is
  $1.32\times10^{-102} \neq 0$.

## 2.5 Diagnostic retraction

One claim in this chapter was retracted. A panel-subset comparison initially
reported a difference of $0.0078009845039928$ between panels $\{0..60\}$ and a
50-panel subset. The comparison was invalid — the two panel sets are not
commensurate — and the number was withdrawn rather than reinterpreted.

## 2.6 Conclusion of Chapter 2

The discrepancy is **quadrature/truncation-limited, not a defect of the closed
form**. After treatment (adaptive exact tail, $R$ promoted to a free parameter,
critical panels raised to GL128/GL160), the identity depths in §1.4 are reached
and the downstream eigenvalue computation is placed on a validated footing.

---

# Chapter 3 — OMEGA A1/A2: Certified Enclosure with `flint.arb`

## 3.1 Capabilities established before use

An API audit was executed before any claim was made about `flint`. Findings,
all measured against `python-flint 0.9.0`:

| question | finding |
|---|---|
| does `arb_mat.eig` return enclosures? | **yes** — `acb` objects carrying a radius |
| is `arb_mat.eig` independent of `acb_mat.eig`? | **no** — it is a *wrapper*. Routes A1 and A2 are therefore **not independent of each other**; both are independent only of `mpmath` |
| which algorithm is certified? | `"rump"` (validated intervals). `"approx"` explicitly provides **no** error bounds and was excluded |
| can the archimedean block be computed inside `arb`? | **no** — `dir(flint)` contains **zero** `psi`, `digamma`, `polygamma`, `hyp2f1` or `lerchphi` functions |
| `ldlt` / `cholesky` / `svd` on `arb_mat`? | absent; only `charpoly, det, eig, inv, solve, exp, trace` |

The fourth row is load-bearing: because the archimedean block cannot be
evaluated inside `arb`, the entries arrive as decimal text. The radius that
`arb` assigns on parsing covers **FLINT's binary rounding only** — it does not
cover the `mpmath` origin of the digits. Any statement of the form "certified
to 308 digits" would be false, and the certificate below is constructed to
avoid that error.

## 3.2 Route A1 — enclosure plus Weyl propagation

Parsing the corrected 81×81 matrix at 1024 bits and running `rump` with no
inflation:

$$
\lambda_{\min} = 1.321050519751746327288993145948\ldots\times10^{-102}
\;\pm\; 8.410\times10^{-309},
\qquad \operatorname{Im} = 0,
$$

with all 81 eigenvalues isolated. Since the metric is
$\lvert\Delta M_{ij}\rvert\le\rho$,

$$
\lVert\Delta M\rVert_2 \le \sqrt{\lVert\Delta M\rVert_1\lVert\Delta M\rVert_\infty}
= n\rho,
\qquad
\lambda_{\min}^{\text{true}} \ge \lambda_{\min}^{\text{parse}} - n\rho .
$$

With $n=81$ the certified tolerance is

$$
\rho^* = \frac{\lambda_{\min}^{\text{parse}}-8.410\times10^{-309}}{81}
= 1.63092656759474834688247443633\times10^{-104}.
$$

### The entry error, enclosed

Since 2026-10-07 the per-entry error is not measured by dps-doubling but
*enclosed*. `gw_rho_formal.py` re-evaluates the same corrected-build formulas of
`gw_corrected_eig.build_blocks_corrected` in `flint.arb`/`flint.acb` at 1200
working bits — `acb.hypgeom_2f1`, `arb.digamma` and `acb.polygamma` are ball
primitives — and evaluates the one term with no primitive, the Lerch series in
`beta_L`, as a ball series carrying a proved geometric tail bound. Against the
dps-180 reference matrix this gives

$$
\rho_{\text{actual}} = 5.8287013697174734848\times10^{-179},
\qquad
\frac{\rho_{\text{actual}}}{\rho^*} = 3.5738589\times10^{-75}.
$$

**Certified margin: 74.4468 orders.**

> **Epistemic status.** $\rho^*$ and the Weyl step are rigorous, and so is the
> entry-error bound: it is `max_ij (|M_ref_ij − center_ij| + rad_ij)`, an upper
> bound by construction rather than a sample of a difference. The dps-doubling
> estimate it replaces was $5.83986112334288261\times10^{-179}$ — larger, as
> expected, since an estimate measures the gap between two dps builds. What is
> still outside the kernel: this bound is a Python/FLINT output that
> `OMEGATrackC.lean` consumes as a literal, and that module could not be
> recompiled after the literal changed because the measuring machine has no
> Mathlib. The literal is checked by `track_c_make_smt.py` (three-way match
> against the README, seven side conditions as exact rationals), by the
> regenerated SMT-LIB2 conjunction under `z3`, and by the anti-circularity
> audit.

### Negative result: the solver with radii

Inflating the entry radii — uniformly at $\rho\ge10^{-180}$, or with measured
per-entry radii — makes `rump` and `vdhoeven_mourrain` **fail to isolate** the
spectrum. This was reproduced at **both** 1024 and 4096 working bits.

This is a **limitation of the algorithm**, not evidence about
$\lambda_{\min}$: it says the solver cannot separate this spectrum once the
entries carry any radius, even one 75 orders below $\rho^*$. It is recorded as a
negative result. Route A1's certificate comes from Weyl propagation on the
parse-only enclosure, not from the perturbed solve.

## 3.3 Route A2 — the interval eigen-solver

| algorithm | wall time | isolation | enclosure |
|---|---:|---:|---|
| `rump` | 33.8 s | 81 / 81 | **ENCLOSED STRICTLY POSITIVE** |
| `vdhoeven_mourrain` | 5.7 s | 81 / 81 | **ENCLOSED STRICTLY POSITIVE** |

Both return $\operatorname{Im} = 0.0$, as required for a real symmetric matrix.
Agreement with the `mpmath` value: **79 significant decimal digits**, against a
`dps 180` error budget of roughly 69 digits.

## 3.4 The precision ladder

| transition | $\lvert\Delta\lambda_{\min}\rvert$ | $dy$ | verdict |
|---|---:|---:|---|
| 180 → 260 | $6.42868363925\times10^{-181}$ | $2.11343\times10^{-79}$ | `RESOLVED` |
| 260 → 340 | $7.3584542294\times10^{-261}$ | $2.41909\times10^{-159}$ | `RESOLVED` |

Over the same range the **entries** move by $5.4\times10^{-179}$ while the
**eigenvalue** moves by $10^{-181}$ — at the `dps 180` floor. The eigenvalue is
therefore insensitive to the entry error by a factor of order $10^{140}$. That
is a measurement, and it is what licenses Chapter 4.

## 3.5 Two retracted readings

**(i)** The Weyl "shift" $1.746\times10^{-114}$ first reported against the
shipped value was compared against a hard-coded 12-digit literal whose own
uncertainty is $\sim10^{-114}$. The shift was *inside* the rounding of the
reference. It is not a measurement and is retracted.

**(ii)** An initial reading of `gw_entry_error.py` reported
`max |M(180) − M(260)| = 4.19986259663e-41`, hence
`NOT CERTIFIED, margin −63.41 orders`. The JSON was parsed **before**
`mp.mp.dps` was set, so the 180-digit strings were read at `dps 40` — the
module-level landmine at `gw_qinf.py:47`. The number measured the reader, not
the matrix. Corrected value: $5.83986112334288261\times10^{-179}$, and the
verdict inverted by **138 orders** to $+74.446$ — that was the dps-doubling
tool's own margin; the rigorous bound of §3.2 gives $+74.4468$.

---

# Chapter 4 — Eigenvector Localisation and Defect Immunity at $n=-27$

## 4.1 The defect reaches the matrix

`gw_qinf.py:94` evaluates $\beta_L$ with `mp.lerchphi`, a function shown to be
wrong by the identity gate. Because it enters through $P_0$ and $Q$ depends on
$P_0$ only through differences, the contamination is *exactly diagonal*:

$$
M_{\text{shipped}} = M_{\text{corrected}} + \operatorname{diag}(\delta).
$$

Measured profile of $\delta$ at `dps 140`:

| $n$ | $\delta(n)$ |
|---:|---:|
| $0$ | $0$ |
| $\lvert n\rvert\le 10$ | $\equiv 0$ |
| $\pm15$ | $1.9453394\times10^{-113}$ |
| $\pm20$ | $3.767\times10^{-99}$ |
| $\pm25$ | $2.310\times10^{-94}$ |
| $\pm30$ | $4.438\times10^{-94}$ |
| $\pm35$ | $3.795\times10^{-97}$ |
| $\pm40$ | $3.39110921707750871\times10^{-102}$ |
| $\mathbf{-27}$ | $\mathbf{1.4618493934897842764\times10^{-93}}$ — **the maximum** |

The maximal entry perturbation is
$$
\frac{\max\lvert\delta\rvert}{\lambda_{\min}}
= 1.10658099114\times10^{9}.
$$

Read alone, this figure says the shipped matrix is corrupted by roughly nine
orders of magnitude more than the quantity being reported from it.

## 4.2 What actually happens

Both builds were re-run through an **identical code path**, differing at a
single call site:

| build | $\lambda_{\min}$ | build time |
|---|---|---:|
| shipped (`mp.lerchphi`) | $1.32105051975174706367212377355\times10^{-102}$ | **602.3 s** |
| corrected (defining series) | $1.32105051975174632728899314595\times10^{-102}$ | **2.6 s** |

$$
\Delta = -7.36383130627605620505628284192\times10^{-118},
\qquad
\frac{\lvert\Delta\rvert}{\lambda_{\min}} = 5.57422384396\times10^{-16}.
$$

**The sign is unchanged**, and the corrected build is **231.7× faster**.

## 4.3 Why — and why this is measurement rather than argument

First-order perturbation theory gives
$$
\Delta\lambda_{\min} = \sum_i v_i^2\,\delta_i,
$$
where $v$ is the $\lambda_{\min}$ eigenvector. Two measurements pin this down:

1. $\delta_i \equiv 0$ **exactly** for $\lvert i\rvert\le 10$;
2. the eigenvector of $\lambda_{\min}$ is concentrated in that same window.

Combining them, $\Delta\lambda_{\min}$ inherits only second-order contributions
outside the window — consistent with the observed
$7.36\times10^{-118}$ against a $\max\lvert\delta\rvert$ nine orders *larger*.

The converse check in §3.4 makes this independently verifiable: across
`dps 180 → 260 → 340` the entries move by $5.4\times10^{-179}$ while
$\lambda_{\min}$ moves by $10^{-181}$. A perturbation concentrated away from
the eigenvector cannot move its eigenvalue, and here we see both halves of that
statement measured on the same matrix.

A Weyl bound applied naively would have predicted a possible sign change. It
over-estimated the effect by a factor of order $10^{9}$. Weyl is a worst-case
inequality; its failure here is *informative* and is the reason Route A1 uses
it only as a tolerance criterion rather than as a prediction.

## 4.4 Consequences for the other parameter pairs

The `mp.lerchphi` defect is not constant across `dps`; it is **stable within
regimes** (identical digits within a regime):

| pair | `dps 40–70` | `dps 90–120` | `dps 140–280` | `dps 300–384` |
|---|---|---|---|---|
| $(100,40)$ | at floor | $3.5887864\times10^{-86}$ | $8.4283129\times10^{-100}$ | $1.6990117\times10^{-127}$ |
| $(13,64)$ | at floor | at floor | at floor | $1.7202763\times10^{-220}$ |

Consequences:

* **The $c=13$ ladder is unaffected.** At `dps 100` (the precision used for
  $N=64$) the defect lies *at the floor* ($5.23\times10^{-105}$ against a
  $10^{-100}$ floor) and is undetectable; the identity gate independently
  bounds it 19 orders below $\lambda_{\min}(13,64)=6.32135140948\times10^{-59}$.
* **$(100,20)$ is unaffected.** Built at `dps 70` and `100`, with worst-case
  defect $3.59\times10^{-86}$ reaching the diagonal through the measured chain
  factor $0.0108573620475813$, giving $\delta\sim3.9\times10^{-88}$ against
  $\lambda_{\min}=3.0256658\times10^{-62}$ — a margin of **26 orders**.
* The corrected build evaluates the defining series directly, so the defect no
  longer enters any newly computed matrix.

---

# Conclusion

**Formal statement.** For the Guinand–Weil test matrix $Q_{100,40}$ constructed
from the primary source, the smallest eigenvalue satisfies

$$
\boxed{\;\lambda_{\min}(Q_{100,40}) = +1.32105051975174632728899314595\times10^{-102}
\;>\; 0\;}
$$

and the matrix constraint is

> **[CERTIFIED STRICTLY POSITIVE]**

on the following basis:

1. **Route A2** — `flint.arb_mat.eig` isolates all 81 eigenvalues under two
   validated algorithms and returns an enclosure strictly positive with zero
   imaginary part. *Rigorous over the matrix as handed.*
2. **Route A1** — `arb` enclosure combined with Weyl propagation certifies
   positivity with a margin of **74.4468 orders** over the required entry-error
   tolerance. *Conditional on $\rho_{\text{actual}}$, which since 2026-10-07 is
   a ball-arithmetic upper bound consumed as a literal rather than a
   dps-doubling estimate; the bound itself is rigorous (§3.2).*
3. **Precision ladder** — $dy = 2.11\times10^{-79}$ (180→260) and
   $2.42\times10^{-159}$ (260→340), both far below the $10^{-4}$ threshold.
4. **Cross-checks** — determinant route agrees with `eigsy` to 25 digits at
   ratio 1.0; the identity gate passes with 35.44 and 56.53 orders of margin.

### What this does not establish

This result concerns **a matrix constraint only**. It does **not** establish:

* the Riemann Hypothesis;
* Weil positivity;
* any prime-counting statement;
* any factorisation method.

The source preprint disclaims all four, and we disclaim them with it. For the
numerics of this paper **no proof assistant has been run**: `coqc`, `isabelle`,
`dkcheck` and `gcc` are `NOT RUN`. Since 2026-10-02 the repository additionally
ships `OMEGATrackC.lean`, type-checked by `lean` 4.33.1 with `z3` 4.16.0 on its
seven side conditions -- that module checks the inference and the arithmetic
*over* the numbers printed here, not the origin of the numbers (§1.5).

### Limitations

* The certificate in Route A1 rests on one quantity produced outside the Lean
  kernel: $\rho_{\text{actual}}$. Since 2026-10-07 it is an interval-arithmetic
  upper bound rather than an estimate (§3.2), so the earlier limitation no
  longer applies — but it is still a Python/FLINT output consumed as a literal.
* The belief that blocked this earlier — that `python-flint 0.9.0` cannot
  evaluate the archimedean block in interval arithmetic because it "exposes no
  psi/digamma/polygamma/hyp2f1/lerchphi" — was **partly false**. Verified on
  0.9.0: `arb.digamma`, `acb.polygamma` and `acb.hypgeom_2f1` are all
  ball-valued primitives. Only `lerchphi` is genuinely absent, and it needed
  only a ball series with a proved tail bound. That false capability claim is
  what kept the chain on dps-doubling for as long as it did.
* Routes A1 and A2 are **not independent of one another**: `arb_mat.eig`
  wraps `acb_mat.eig`. Both are independent only of `mpmath`.
* The eigenvalue result is a measurement at finite precision. It is not a proof
  in the proof-assistant sense, and nothing here should be cited as one.
* The $N\to\infty$ limit of $\lambda_{\min}$ is **open**. Positive values are
  measured at $4\le N\le 64$ ($c=13$) and at $(100,20)$, $(100,40)$; no
  measurement or argument in this paper decides the limit.

### Open items (updated 2026-10-02)

This section previously listed three items as **not started**. All three were
carried out on 27 Sep 2026 and are recorded in `GW_STATUS_2026-09-26.md`:

* (a) entry-wise diff against the released source package -- §7g, 398 decimal
  digits of agreement with `arb_ldlt_certify.py` (gate G3 `LULUS`);
* (b) the $(100,200)$ 401×401 matrix with even/odd split -- §7d, the two
  sectors agree with the full spectrum, $\max|\Delta| =
  5.4615478\times10^{-399}$;
* (d) the conditional status of Montgomery pair correlation -- §7h, run 2
  (2000 samples, seed `20260927`) returns S2
  `INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION`, reported as a
  resolution-limited operational measurement and explicitly **not** as
  Montgomery's theorem.

No item from that list is open any more; the list is retained in this updated
form rather than deleted, so the correction is visible on the page.

---

## References

1. Primary source for the Guinand–Weil matrix statement:
   `https://arxiv.org/html/2607.02828v3`.
2. `python-flint 0.9.0` — Ball arithmetic (`flint.arb`, `flint.arb_mat`,
   `acb_mat.eig`).
3. `mpmath` — arbitrary-precision decimal arithmetic.
4. Repository record: `GW_STATUS_2026-09-26.md`, §7, §7a (retracted),
   §7b, §7c; operational record for 2026-09-30 → 2026-10-01 in §10.

---

## Supplementary material

| file | contents |
|---|---|
| `GW_STATUS_2026-09-26.md` | canonical status report, all diagnostics (§2.4 retraction table, §7a–§7h, §10 operational record) |
| `OMEGA_CORE_CERTIFICATE.md` | interval $LDL^T$ chain, $N=400$ and $N=800$ certificates |
| `gw_arb_sweep.py`, `gw_arb_measured.py` | A1 and A2 scripts as executed (flat root) |
| `REPO_STRUCTURE.md` | directory schema and inventory |

The supplementary documents `RETRACTIONS.md`, `EPISTEMIC_RULES.md` and
`API_AUDIT.md` named in earlier drafts of this table **were never produced**;
their material lives in `GW_STATUS_2026-09-26.md` and `OMEGA_CORE_CERTIFICATE.md`
5.1. The table above lists only files that exist.

---

*Correspondence: Muhammad Aidil Amry, ORCID 0009-0002-9718-9710,
Independent Researcher, South Sulawesi, Indonesia.*
