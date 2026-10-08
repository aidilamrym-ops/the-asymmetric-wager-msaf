import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.LinearAlgebra.Matrix.Symmetric
import Mathlib.LinearAlgebra.Matrix.Hermitian
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.NormNum

open Matrix

/-!
# Track C of the OMEGA / Guinand-Weil certification chain

`README.md` §4.1 recorded this track as **NOT STARTED** while this module
existed outside the repository.  On 2026-10-02 the module was shipped here and
§4.1 was rewritten to state the actual tool status: `lean` **RAN** (this file,
`exit=0`, axiom footprint of all ten theorems
`[propext, Classical.choice, Quot.sound]`), `z3` **RAN** (the seven side
conditions below), `coqc` / `isabelle` / `dkcheck` not installed on the machine
that produced this file, `gcc` **NOT RUN**.

On 2026-10-07 (phase A15) the `rhoActual` literal below was re-anchored from a
dps-doubling **estimate** to a rigorous ball-arithmetic upper bound produced by
`gw_rho_formal.py`.  That machine had no Mathlib, so the file could not be
recompiled there; the re-anchored literal rested on `track_c_make_smt.py`
(three-way literal match against `README.md`, plus the seven side conditions
evaluated as exact rationals), the regenerated `track_c_side_conditions.smt2`
under `z3`, and the anti-circularity audit.  That gap was registered as residual
`A15-R1`.

On 2026-10-07 (phase A17) it was closed.  Mathlib was installed (release
`v4.33.1`, commit `0df444a360eaa60ab8c11dca51a86af692955474`, matching the Lean
4.33.1 toolchain this corpus pins) and **this file was recompiled**: the kernel
compiled the byte-for-byte copy of this module with **no diagnostics of any
kind**, the code carries no `sorry` token outside comments and no
`axiom`/`constant` declaration, and the axiom footprint of all ten theorems is
`[propext, Classical.choice, Quot.sound]` again -- identical to the 2026-10-02
run, which is the expected result since no theorem statement changed.  The seven
numerical theorems (`measured_within_tolerance`, `margin_at_least_74_orders`,
`margin_satisfies_master_theorem`, `tolerance_fails_the_coarse_bound`,
`implied_constant_ge_81`, `implied_constant_lt_82`, `tolerance_positive`) are
`by norm_num` over the literal *below*, so the kernel has now evaluated the new
bound itself and not merely agreed that the file parses.

Note on method: `lake build` was **not** the evidence, because a lakefile target
builds the library module named in it, not this file.  The evidence is
`lake env lean` run on the byte-for-byte copy, with its diagnostics read: an
earlier attempt reported a green `lake build` while the module it had built was
a one-line `import Mathlib`.  Reproduce with `trackc_recompile.py`, which fails
if the kernel reports a hole, if the footprint drifts, or if any of the ten
theorems is missing.  (A file cannot record its own sha256, so the digest of the
verified copy is in `track_c_lean_verify.log` and in `A17_REPORT.md` instead.)

This module closes the *logical* half of that gap.  It proves, in Lean 4 with
Mathlib:

1. **Certified positivity from an entrywise enclosure.**  If a reference matrix
   has a strictly positive Rayleigh margin `μ` and the true matrix differs
   entrywise by at most `ρ` with `ρ·n < μ`, then the true matrix is positive
   definite.  This is a Rayleigh-quotient form of Weyl perturbation.

2. **The numerical side conditions, as exact rational arithmetic.**  The
   report's headline margin ("74.446 orders over the required entry-error
   tolerance") is restated as `ρ_actual · 10^74 ≤ ρ*`, a decidable inequality on
   `ℚ` that the kernel normalises itself.

**Honest scope statement.**  What is machine-checked here is the *inference*
("these numbers imply positive definiteness") and the *arithmetic* ("the reported
numbers satisfy these inequalities").  What is **not** machine-checked is the
origin of the numbers themselves: `μ`, `ρ_actual` and `ρ*` are outputs of the
FLINT/Arb ball-arithmetic stage, and this module consumes them as literals.
No claim of kernel verification is made for the numerics.

Since 2026-10-07 that includes one change in kind: `ρ_actual` used to be a
dps-doubling estimate and is now an *upper bound produced by interval
arithmetic* (`gw_rho_formal.py`), so the entry-error link of the chain is no
longer an estimate — but it is still a Python/FLINT output consumed here as a
literal, not a Lean-checked quantity.  `μ` and `ρ*` are likewise literals.
-/

namespace OMEGA

/-! ## 1. The enclosure predicates -/

/-- `Q` lies entrywise within `ρ` of the reference matrix `Qhat`. -/
abbrev EntrywiseEnclosure {n : ℕ} (Qhat Q : Matrix (Fin n) (Fin n) ℝ) (ρ : ℝ) : Prop :=
  ∀ i j, |Q i j - Qhat i j| ≤ ρ

/-- The reference matrix has Rayleigh quotient at least `μ` on every nonzero
vector: this is `λ_min(Qhat) ≥ μ` stated without invoking the spectral
theorem, which is exactly the hypothesis the ball-arithmetic stage supplies. -/
abbrev RayleighMargin {n : ℕ} (Qhat : Matrix (Fin n) (Fin n) ℝ) (μ : ℝ) : Prop :=
  ∀ x : Fin n → ℝ, x ≠ 0 → μ * ∑ i, x i ^ 2 ≤ x ⬝ᵥ (Qhat *ᵥ x)

/-! ## 2. Elementary inequalities -/

/-- Blunt two-variable AM-GM: `2·|a|·|b| ≤ a² + b²`. -/
theorem two_abs_mul_le_add_sq (a b : ℝ) : 2 * (|a| * |b|) ≤ a ^ 2 + b ^ 2 := by
  have h := two_mul_le_add_sq (|a|) (|b|)
  rw [sq_abs, sq_abs] at h
  rw [mul_assoc] at h
  simpa [mul_comm] using h

/-- **Enclosure bound on the Rayleigh quotient.**

An entrywise-`ρ` perturbation `E` moves `x ⬝ᵥ (E *ᵥ x)` by at most
`ρ · n · ∑ x i²`.  The constant is `n` (the sharp one), obtained by expanding
`|∑_i ∑_j x_i E_ij x_j|`, applying `|E_ij| ≤ ρ`, and bounding
`(∑ |x_i|)² ≤ n · ∑ x_i²` through the double-sum AM-GM. -/
theorem enclosure_quad_bound {n : ℕ} (E : Matrix (Fin n) (Fin n) ℝ) (ρ : ℝ)
    (hρ : 0 ≤ ρ) (hE : ∀ i j, |E i j| ≤ ρ) (x : Fin n → ℝ) :
    |x ⬝ᵥ (E *ᵥ x)| ≤ ρ * n * ∑ i, x i ^ 2 := by
  classical
  have hexpand : x ⬝ᵥ (E *ᵥ x)
      = ∑ i : Fin n, x i * ∑ j : Fin n, E i j * x j := by
    simp only [dotProduct, mulVec]
  rw [hexpand]
  -- (b) termwise bound.  Stated as a named fact *before* it is used: with the
  --      upper bound left as a metavariable, Lean cannot infer the implicit
  --      `g` of `Finset.sum_le_sum` nor the `b` of `le_trans`, and the whole
  --      step is rejected with "don't know how to synthesize implicit argument".
  have hterm : ∀ i : Fin n, |x i * ∑ j : Fin n, E i j * x j|
      ≤ |x i| * ∑ j : Fin n, ρ * |x j| := by
    intro i
    calc
      |x i * ∑ j : Fin n, E i j * x j|
          = |x i| * |∑ j : Fin n, E i j * x j| := abs_mul ..
      _ ≤ |x i| * ∑ j : Fin n, |E i j * x j| :=
          mul_le_mul_of_nonneg_left (Finset.abs_sum_le_sum_abs _ _) (abs_nonneg _)
      _ = |x i| * ∑ j : Fin n, |E i j| * |x j| := by simp only [abs_mul]
      _ ≤ |x i| * ∑ j : Fin n, ρ * |x j| :=
          mul_le_mul_of_nonneg_left
            (Finset.sum_le_sum fun j _ =>
              mul_le_mul_of_nonneg_right (hE i j) (abs_nonneg (x j)))
            (abs_nonneg _)
  -- (a) triangle inequality over the outer index
  refine le_trans (Finset.abs_sum_le_sum_abs (fun i : Fin n =>
      x i * ∑ j : Fin n, E i j * x j) _) ?_
  refine le_trans (Finset.sum_le_sum fun i _ => hterm i) ?_
  -- (c) factor ρ out of both sums
  rw [← Finset.mul_sum]
  rw [← Finset.sum_mul]
  -- (d) bound (∑|x_i|)² by n·∑x_i²
  have hAB : ∀ a b : ℝ, 2 * (|a| * |b|) ≤ a ^ 2 + b ^ 2 := two_abs_mul_le_add_sq
  have hpair : 2 * ((∑ i : Fin n, |x i|) * ∑ j : Fin n, |x j|)
      ≤ ∑ i : Fin n, ∑ j : Fin n, (x i ^ 2 + x j ^ 2) := by
    rw [Finset.sum_mul_sum]
    simp only [Finset.mul_sum]
    exact Finset.sum_le_sum fun i _ =>
      Finset.sum_le_sum fun j _ => hAB (x i) (x j)
  have hCalc : (∑ i : Fin n, ∑ j : Fin n, (x i ^ 2 + x j ^ 2))
      = 2 * n * ∑ i : Fin n, x i ^ 2 := by
    simp only [Finset.sum_add_distrib]
    have hA : (∑ i : Fin n, ∑ j : Fin n, x i ^ 2)
        = n * ∑ i : Fin n, x i ^ 2 := by
      have inner : ∀ i : Fin n, (∑ j : Fin n, x i ^ 2)
          = (n : ℝ) * x i ^ 2 := fun i => by
        rw [Finset.sum_const, nsmul_eq_mul, Finset.card_univ, Fintype.card_fin]
      simp only [inner]
      rw [← Finset.mul_sum]
    have hB : (∑ i : Fin n, ∑ j : Fin n, x j ^ 2)
        = n * ∑ i : Fin n, x i ^ 2 := by
      have inner : (∑ j : Fin n, x j ^ 2) = ∑ k : Fin n, x k ^ 2 := rfl
      rw [inner]
      rw [Finset.sum_const, nsmul_eq_mul, Finset.card_univ, Fintype.card_fin]
    rw [hA, hB]
    ring
  have hle : (∑ i : Fin n, |x i|) * ∑ j : Fin n, |x j|
      ≤ n * ∑ i : Fin n, x i ^ 2 := by
    -- `rw [hCalc]` alone already discharges the side goal (the right-hand side
    -- is still a metavariable, so the closing `rfl` assigns it), which left
    -- `exact le_refl _` with nothing to do.  Stated with `le_of_eq` instead.
    have h := le_trans hpair (le_of_eq hCalc)
    rw [mul_assoc] at h
    exact le_of_mul_le_mul_left h (by norm_num : (0 : ℝ) < 2)
  have hprod : (∑ i : Fin n, |x i|) * (ρ * ∑ j : Fin n, |x j|)
      = ρ * ((∑ i : Fin n, |x i|) * ∑ j : Fin n, |x j|) := by ring
  -- `(ρ * ↑n) * s` and `ρ * (↑n * s)` are propositionally equal but *not*
  -- definitionally equal for `ℝ`, so plain `exact` cannot bridge them; the
  -- association of the right-hand side has to be rewritten explicitly.
  have hassoc : ρ * ↑n * ∑ i : Fin n, x i ^ 2
      = ρ * (↑n * ∑ i : Fin n, x i ^ 2) := by ring
  rw [hprod, hassoc]
  exact mul_le_mul_of_nonneg_left hle hρ

/-! ## 3. The master theorem: enclosure + margin  ⇒  positive definite -/

/-- **Certified positivity.**

A real symmetric reference matrix whose Rayleigh quotient is bounded below by
`μ > 0` stays positive definite under any entrywise perturbation of size
`ρ < μ / n`.

This is the inference rule the OMEGA report calls "arb enclosure + Weyl
propagation"; the proof is a Rayleigh-quotient version of Weyl's inequality. -/
theorem certified_positivity {n : ℕ}
    (Qhat Q : Matrix (Fin n) (Fin n) ℝ)
    (hQ : Q.IsSymm)
    -- `0 < μ` is derivable from `hρ`, `hmargin : ρ * n < μ` and `n ≥ 0`, so it
    -- is carried for documentation only; `_` marks it as intentionally unused.
    (μ ρ : ℝ) (_hμpos : 0 < μ) (hρ : 0 ≤ ρ)
    (hmargin : ρ * n < μ)
    (hRay : RayleighMargin Qhat μ)
    (hE : EntrywiseEnclosure Qhat Q ρ) :
    Q.PosDef := by
  classical
  apply Matrix.PosDef.of_dotProduct_mulVec_pos
  · -- symmetry of Q gives Hermiticity
    exact Matrix.isHermitian_iff_isSymm.mpr hQ
  · intro x hx
    have hRay' := hRay x hx
    have hquad := enclosure_quad_bound (Q - Qhat) ρ hρ
      (fun i j => by simpa using hE i j) x
    have hident : Q = Qhat + (Q - Qhat) := by
      rw [add_comm Qhat (Q - Qhat)]
      exact (sub_add_cancel Q Qhat).symm
    -- `PosDef` is stated over `star x`; for real matrices `star x = x`.
    have hstar : star x = x := by simp
    rw [hstar]
    -- Split the quadratic form across the reference and the perturbation.
    -- `hident` must be applied to the left-hand side only: rewriting the whole
    -- goal would also rewrite the `Q` inside `Q - Qhat` on the right-hand side
    -- into `(Qhat + (Q - Qhat)) - Qhat`, and the two sides never meet again.
    -- Quantifying over `A` makes that scoping restriction explicit.
    have hsplit : x ⬝ᵥ (Q *ᵥ x)
        = x ⬝ᵥ (Qhat *ᵥ x) + x ⬝ᵥ ((Q - Qhat) *ᵥ x) := by
      have hk : ∀ A : Matrix (Fin n) (Fin n) ℝ,
          A = Qhat + (Q - Qhat) →
            x ⬝ᵥ (A *ᵥ x) = x ⬝ᵥ (Qhat *ᵥ x) + x ⬝ᵥ ((Q - Qhat) *ᵥ x) := by
        intro A hA
        rw [hA, Matrix.add_mulVec]
        simp only [dotProduct, Pi.add_apply, mul_add, Finset.sum_add_distrib]
      exact hk Q hident
    rw [hsplit]
    -- ∑ x i² is strictly positive because x ≠ 0
    have hposT : 0 < ∑ i : Fin n, x i ^ 2 := by
      -- `push_neg` is deprecated in this Mathlib; `by_contra` twice is the
      -- direct equivalent and keeps the file warning-free.
      by_contra hle0
      have hz : ∀ i : Fin n, x i = 0 := by
        intro i
        by_contra hne
        have h1 : 0 < x i ^ 2 := sq_pos_of_ne_zero hne
        have h2 : x i ^ 2 ≤ ∑ j : Fin n, x j ^ 2 :=
          Finset.single_le_sum (fun _ _ => sq_nonneg _) (Finset.mem_univ i)
        linarith
      exact hx (funext hz)
    -- the perturbation term is bounded below
    have hlow : -(ρ * n * ∑ i : Fin n, x i ^ 2)
        ≤ x ⬝ᵥ ((Q - Qhat) *ᵥ x) := (abs_le.mp hquad).1
    have hge : μ * ∑ i : Fin n, x i ^ 2 - ρ * n * ∑ i : Fin n, x i ^ 2
        ≤ x ⬝ᵥ (Qhat *ᵥ x) + x ⬝ᵥ ((Q - Qhat) *ᵥ x) := by linarith
    have hgt : 0 < μ * ∑ i : Fin n, x i ^ 2 - ρ * n * ∑ i : Fin n, x i ^ 2 := by
      have hm : 0 < μ - ρ * n := by linarith
      have hfact : μ * ∑ i : Fin n, x i ^ 2 - ρ * n * ∑ i : Fin n, x i ^ 2
          = (μ - ρ * n) * ∑ i : Fin n, x i ^ 2 := by ring
      rw [hfact]
      exact mul_pos hm hposT
    linarith

/-! ## 4. The numerical side conditions, as exact `ℚ` arithmetic

The constants below are transcribed verbatim from this repository's
`README.md` §1 (checked mechanically by `track_c_make_smt.py`, which reads
the same literals out of the file instead of trusting a copy).
Each is written as an exact rational (decimal numerator over a power of ten), so
the kernel — not a floating-point unit — decides the inequalities.
-/

/-- Coarse max-norm constant `n` used by every side condition below.

`401 = 2 * 200 + 1` is the dimension of `Q_{100,200}`.  It is **not** the
dimension of the matrix the three literals below describe: `lambdaMin`,
`rhoStar` and `rhoActual` are those of `Q_{100,40}`, whose dimension is
`2 * 40 + 1 = 81`.  The larger number is used on purpose.  A bound proved
with `n = 401` also holds at `n = 81`, so each condition below is strictly
stronger than the one the `Q_{100,40}` certificate actually needs; this is a
stand-in chosen for conservatism, not a property of any single matrix. -/
abbrev nDim : ℕ := 401

/-- `λ_min(Q̂) = +1.32105051975174632728899314595 × 10⁻¹⁰²` (README §1). -/
abbrev lambdaMin : ℚ := 132105051975174632728899314595 / 10 ^ 131

/-- Rigorous upper bound on the entry error:
    `ρ_actual ≤ 5.8287013697174734848 × 10⁻¹⁷⁹`.

    Measured by `gw_rho_formal.py`, which re-evaluates the same corrected-build
    formulas of `gw_corrected_eig.build_blocks_corrected` in FLINT ball
    arithmetic (prec 1200 bits) and reports
    `max_ij (|M_ref_ij − center_ij| + rad_ij)` against the dps-180 reference
    matrix `gw_matrix_100_40_dps180.json` (81 × 81, verified symmetric).  This
    is an upper bound by construction, not a sample of a difference.

    It replaces the dps-doubling estimate `5.83986112334288261 × 10⁻¹⁷⁹` this
    literal carried until 2026-10-07, and it is *smaller* than that estimate —
    as it should be, since the estimate measures the gap between two dps builds
    while this measures the distance to the true value.

    The one transcendental the corrected build has no FLINT primitive for, the
    Lerch series inside `beta_L`, is evaluated there as a ball series with a
    proved geometric tail bound; `λ_min` is untouched, and the dps-180 rebuild
    reproduces `lambdaMin` to all 30 published digits. -/
abbrev rhoActual : ℚ := 58287013697174734848 / 10 ^ 198

/-- Certified tolerance `ρ* = 1.63092656759474834688247443633 × 10⁻¹⁰⁴`
(`README.md` line 37).  A 30-digit numerator over `10^133`
gives `10^(29-133) = 10^-104`; `10^132` would silently shift `ρ*` up by one
order of magnitude and move `λ_min / ρ*` from `81` down to `8.1`.

Which of its digits are significant: the published value is **bit-identical**
to `float(λ_min) / 81`, which is what `gw_opt_b_arb.py` computes
(`lam_float = float(lam_parse)`; `rho_star = mp.mpf(lam_float) / n`), so it is
a binary64 quotient printed out in full.  Its first 16 digits agree with the
exact `λ_min / 81`; the exact quotient differs from it by `1.90e-16`
relative.  The verdict this tolerance gates is decided by 74 orders of margin
and is unaffected, but no digit past the 16th may be read as a measurement. -/
abbrev rhoStar : ℚ := 163092656759474834688247443633 / 10 ^ 133

/-- **The gate the report actually runs:** measured error under certified
tolerance. -/
theorem measured_within_tolerance : rhoActual ≤ rhoStar := by norm_num

/-- **74 orders of margin, kernel-checked.**  The README reports 74.4468 orders;
this establishes the integer part `≥ 74` as an exact rational inequality. -/
theorem margin_at_least_74_orders : rhoActual * 10 ^ 74 ≤ rhoStar := by norm_num

/-- The side condition of `certified_positivity` on the **measured** error,
evaluated at the enlarged constant `nDim = 401`:
`ρ_actual · nDim ≈ 2.34 × 10⁻¹⁷⁶ ≪ 1.32 × 10⁻¹⁰²`, so the theorem applies
with an enormous reserve.  At the true dimension `81` of `Q_{100,40}` the
  product is `≈ 5.8 × 10⁻¹⁷⁸` and the reserve is 74.4468 orders -- the figure
  the certificate reports.  Both readings satisfy the same side condition;
  this one is the stronger of the two. -/
theorem margin_satisfies_master_theorem :
    rhoActual * nDim < lambdaMin := by norm_num

/-- The certified tolerance carries **no slack under dimension enlargement**:
at `nDim = 401`, `nDim · ρ* ≈ 6.54 × 10⁻¹⁰²` exceeds
`λ_min ≈ 1.32 × 10⁻¹⁰²`.

This establishes nothing about which norm the report used, and an earlier
comment here claimed exactly that.  `ρ*` *is* the crude entrywise bound
`λ_min / n` with `n = 81`, the dimension of `Q_{100,40}`: that is how both
`gw_arb_sweep.py` and `gw_opt_b_arb.py` compute it.  At the true dimension the
two sides therefore meet at equality -- `81 · ρ* = λ_min` by construction --
so the tolerance clears the side condition only by equality
(`implied_constant_ge_81`).  It is the enlargement to `n = 401` that makes it
fail here.  What clears even the enlarged bound is the measured error
`ρ_actual`, by 74 orders (`margin_satisfies_master_theorem`). -/
theorem tolerance_fails_the_coarse_bound : ¬ (rhoStar * nDim < lambdaMin) := by
  simp only [not_lt]
  norm_num

/-- The reported literals pin the effective perturbation constant from below:
`λ_min / ρ* ≥ 81`, i.e. `ρ*` clears the master theorem's side condition at the
true dimension `n = 81` of `Q_{100,40}`.

The bound is tight at its left end and is stated with `≤` for that reason.
`ρ*` was *defined* as `λ_min / 81` (`gw_arb_sweep.py`, `gw_opt_b_arb.py`), so
the ratio is 81 by construction; only `≥` survives at full precision.  The
strict form this theorem previously took, `ρ* * 81 < λ_min`, was true of the
transcribed literal but by `1.26e-16` relative only, which is the binary64
rounding of `rhoStar` and nothing else -- an artefact of how the literal was
produced, not a property of the matrix, so it is not claimed. -/
theorem implied_constant_ge_81 : rhoStar * 81 ≤ lambdaMin := by norm_num

/-- …and from above: it is below `82`.  Together with
`implied_constant_ge_81` this brackets the constant in `[81, 82)`.

The bracket is tight at its left end and says nothing beyond that.  `ρ*` is
*defined* as `λ_min / 81`, so `λ_min / ρ* = 81` -- the crude max-norm constant
for the `81 × 81` matrix -- and `81` is what sits at the left end of the
interval.  The two inequalities together therefore identify the crude
constant; an earlier comment here read them instead as evidence of a
spectral-norm step (`√n ≈ 20`) combined with a structural factor, and that
reading is withdrawn. -/
theorem implied_constant_lt_82 : lambdaMin < rhoStar * 82 := by norm_num

/-- The certified tolerance really is a tolerance: it is positive. -/
theorem tolerance_positive : (0 : ℚ) < rhoStar := by norm_num

end OMEGA
