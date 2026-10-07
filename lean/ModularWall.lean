/-!
# ModularWall.lean

FILE: lean/ModularWall.lean
PURPOSE: Honest formal sheet for the MSAF Modular Wall.  Two carriers:

        1. `TailRadius` -- the structural contract of R_tail: a nonnegative
           rational radius.  The closed-form exponential value of R_tail
           is computed numerically by OMEGA-CORE v2 / msaf_visual.py over
           the infinite product; it is NOT evaluated here (Lean 4 core
           has no `Real.exp`).
        2. `modularWall` (M_hat_N) -- the Modular Wall Boundary Operator,
           wrapping a value `x` with a tail radius.  Zero-fudging is by
           construction: the midpoint of the result is `x` itself.

        Theorems (no `sorry`, core-only):

        1. `midpoint_never_shifts` -- structural zero-fudging (`rfl`).
        2. `interval_midpoint` -- arithmetic zero-fudging: the midpoint of
           `[x - r, x + r]` recomputed as `((x - r) + (x + r)) / 2` is `x`.
        3. `wall_contains_midpoint` -- every wall contains its midpoint.
        4. `interval_nonempty` -- for `r >= 0` the wall interval is
           non-degenerate: `x - r <= x + r`.

WHAT THIS IS NOT
        - Not a proof that R_tail is small, flat (F1-N), or bounded by any
          explicit constant.  Numerical flatness lives in OMEGA-CORE /
          visual_check, not here.
        - Not a claim about RH, the Critical Line, or the continuum.
        - Not an evaluation inside Z_none (Z_none stays non-operational).
        - Not a refutation of anything; not a proof about physical space.

BUILD
        Lean 4.33.1 core only (no Mathlib, no Batteries, no imports).
        This file is standalone: it does not import DiscreteCoordinates.
        AC Gate `lean` must see zero `sorry` tokens.

STATUS
        Fase A14 candidate.  Companion to lean/DiscreteCoordinates.lean.
-/

namespace MSAF
namespace ModularWall

/-! ## Core arithmetic helpers (duplicated locally so this file stays
       standalone; same proofs as the helpers in DiscreteCoordinates.lean) -/

theorem natCast_num (k : Nat) : (((k:Nat):Rat)).num = Int.ofNat k := rfl
theorem natCast_den (k : Nat) : (((k:Nat):Rat)).den = 1 := rfl

theorem natCast_add_num (a b : Nat) :
    (((a:Nat):Rat) + ((b:Nat):Rat)).num = Int.ofNat a + Int.ofNat b := by
  simp only [Rat.add_def, natCast_num, natCast_den, Int.ofNat_one, Int.mul_one, Nat.mul_one]
  simp only [Rat.normalize, Nat.gcd_one_right]
  rfl

theorem natCast_add_den (a b : Nat) :
    (((a:Nat):Rat) + ((b:Nat):Rat)).den = 1 := by
  simp only [Rat.add_def, natCast_num, natCast_den, Int.ofNat_one, Int.mul_one, Nat.mul_one]
  simp only [Rat.normalize, Nat.gcd_one_right]
  rfl

theorem ofNat_add_eq (a b : Nat) : Int.ofNat (a + b) = Int.ofNat a + Int.ofNat b := by
  show ((a + b : Nat) : Int) = _
  exact Int.natCast_add a b

theorem natCast_add (a b : Nat) :
    ((a + b:Nat):Rat) = ((a:Nat):Rat) + ((b:Nat):Rat) := by
  apply Rat.le_antisymm
  · rw [Rat.le_iff]
    rw [natCast_num (a+b), natCast_den (a+b)]
    rw [natCast_add_num a b, natCast_add_den a b]
    simp only [Int.ofNat_one, Int.mul_one]
    rw [ofNat_add_eq a b]
    omega
  · rw [Rat.le_iff]
    rw [natCast_num (a+b), natCast_den (a+b)]
    rw [natCast_add_num a b, natCast_add_den a b]
    simp only [Int.ofNat_one, Int.mul_one]
    rw [ofNat_add_eq a b]
    omega

theorem one_as_natCast : (1:Rat) = ((1:Nat):Rat) := rfl
theorem two_as_natCast : (2:Rat) = ((2:Nat):Rat) := rfl

theorem two_ne_zero : (2:Rat) ≠ 0 := by
  intro h
  have hnum := congrArg Rat.num h
  have h20 : (2:Int) = (0:Int) := hnum
  omega

theorem add_one_one : (1:Rat) + 1 = (2:Rat) := by
  rw [one_as_natCast, ← natCast_add 1 1, two_as_natCast]

theorem x_plus_x (x : Rat) : x + x = x * (2:Rat) := by
  calc x + x = x * 1 + x * 1 := by rw [Rat.mul_one]
    _ = x * (1 + 1) := by rw [← Rat.mul_add]
    _ = x * (2:Rat) := by rw [add_one_one]

theorem half_two (x : Rat) : (x + x) / 2 = x := by
  rw [Rat.div_def]
  rw [x_plus_x]
  rw [Rat.mul_assoc]
  rw [Rat.mul_inv_cancel 2 two_ne_zero]
  rw [Rat.mul_one]

theorem sub_add_zero (x : Rat) : x - 0 = x := by
  rw [Rat.sub_eq_add_neg, Rat.neg_zero, Rat.add_zero]

theorem rat_neg_pos {a : Rat} (h : (0:Rat) < a) : -a < 0 := by
  have h0num : (0:Rat).num = 0 := rfl
  have h0den : (0:Rat).den = 1 := rfl
  rw [Rat.lt_iff]
  rw [h0num, h0den, Rat.neg_num, Rat.neg_den]
  show -a.num * ((1:Nat):Int) < (0:Int) * ((a.den:Nat):Int)
  rw [show ((1:Nat):Int) = (1:Int) from Int.ofNat_one]
  rw [Int.mul_one, Int.zero_mul]
  have hlt := Rat.lt_iff 0 a
  rw [h0num, h0den] at hlt
  have h2 := hlt.mp h
  simp only [show ((1:Nat):Int) = (1:Int) from Int.ofNat_one] at h2
  simp only [Int.zero_mul, Int.mul_one] at h2
  omega

theorem pos_of_nonzero {r : Rat} (hr : 0 ≤ r) (hn : ¬r = 0) : (0:Rat) < r := by
  cases Decidable.em ((0:Rat) < r) with
  | inl h => exact h
  | inr hlt =>
    have hle : r ≤ 0 := Rat.not_lt.mp hlt
    have heq : r = 0 := Rat.le_antisymm hle hr
    exact False.elim (absurd heq hn)

theorem sub_left_le (x r : Rat) (hr : 0 ≤ r) : x - r ≤ x := by
  cases Decidable.em (r = 0) with
  | inl he =>
    rw [he, sub_add_zero]
    exact Rat.le_refl (a := x)
  | inr hn =>
    have hpos := pos_of_nonzero hr hn
    have hneg : -r < 0 := rat_neg_pos hpos
    have hlt2 : x + -r < x + 0 := Rat.add_lt_add_left.mpr hneg
    rw [Rat.add_zero] at hlt2
    rw [Rat.sub_eq_add_neg]
    exact Rat.le_of_lt hlt2

theorem le_add_of_nonneg (x r : Rat) (hr : 0 ≤ r) : x ≤ x + r := by
  cases Decidable.em (r = 0) with
  | inl he =>
    rw [he, Rat.add_zero]
    exact Rat.le_refl (a := x)
  | inr hn =>
    have hpos := pos_of_nonzero hr hn
    have hlt2 : x + 0 < x + r := Rat.add_lt_add_left.mpr hpos
    rw [Rat.add_zero] at hlt2
    exact Rat.le_of_lt hlt2

/-! ## Arithmetic zero-fudging -/

theorem interval_midpoint (x r : Rat) : ((x - r) + (x + r)) / 2 = x := by
  have hsum : (x - r) + (x + r) = x + x := by
    rw [Rat.add_comm x r]
    rw [← Rat.add_assoc]
    rw [Rat.sub_add_cancel]
  rw [hsum]
  exact half_two x

theorem interval_nonempty (x r : Rat) (hr : 0 ≤ r) : x - r ≤ x + r :=
  Rat.le_trans (sub_left_le x r hr) (le_add_of_nonneg x r hr)

/-! ## The Modular Wall (M_hat_N) -/

/-- Structural contract of R_tail: a nonnegative rational radius.  The
    numerical value of R_tail itself is computed outside Lean
    (OMEGA-CORE v2 / msaf_visual.py); here only the contract matters. -/
structure TailRadius where
  value : Rat
  nonneg : 0 ≤ value

/-- The uncertainty ball: midpoint plus radius. -/
structure UncertaintyBall where
  midpoint : Rat
  radius : Rat
  radius_nonneg : 0 ≤ radius

/-- Membership: `y` lies in the closed interval
    `[b.midpoint - b.radius, b.midpoint + b.radius]`. -/
def InBall (b : UncertaintyBall) (y : Rat) : Prop :=
  b.midpoint - b.radius ≤ y ∧ y ≤ b.midpoint + b.radius

/-- **M_hat_N (Modular Wall Boundary Operator).**  Wrap the value `x`
    with the tail radius.  Zero-fudging is by construction: the midpoint
    of the result is `x` itself. -/
def modularWall (x : Rat) (rt : TailRadius) : UncertaintyBall :=
  { midpoint := x, radius := rt.value, radius_nonneg := rt.nonneg }

/-- **Zero-fudging, structural form.**  The wall never moves the
    midpoint: it is `x` by definition (`rfl`). -/
theorem midpoint_never_shifts (x : Rat) (rt : TailRadius) :
    (modularWall x rt).midpoint = x := rfl

/-- **Zero-fudging, arithmetic form.**  The midpoint of the wall
    interval `[x - r, x + r]`, recomputed as `((x - r) + (x + r)) / 2`,
    is `x` itself -- the midpoint never shifts. -/
theorem interval_midpoint_zero_fudging (x r : Rat) :
    ((x - r) + (x + r)) / 2 = x := interval_midpoint x r

/-- **Wall contains its midpoint.**  For any radius the wall interval
    contains its own midpoint (the ball is well-formed at its center). -/
theorem wall_contains_midpoint (x : Rat) (rt : TailRadius) :
    InBall (modularWall x rt) x :=
  ⟨sub_left_le x rt.value rt.nonneg, le_add_of_nonneg x rt.value rt.nonneg⟩

end ModularWall
end MSAF