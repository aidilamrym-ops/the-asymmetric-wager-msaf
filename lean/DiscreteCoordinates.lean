/-!
# DiscreteCoordinates.lean

FILE: lean/DiscreteCoordinates.lean
PURPOSE: Honest formal sheet for the MSAF coordinate lattice.  Scale axiom:
        finite step count `n > 0`, scale `Δ = 1/n` (Potential Infinity /
        finite constructive steps).  Two theorems only:

        1. `min_separation` — distinct valid coordinates are at distance ≥ Δ.
        2. `no_valid_coord_in_open_zone` — no valid coordinate lies in the
           open zone `0 < |x - x0| < Δ`.

WHAT THIS IS NOT
        - Not a refutation of ℝ/ℂ or of classical analysis.
        - Not a proof that physical space is discrete.
        - Not a proof about RH, the Critical Line, Protocol 09, R_tail,
          or M_hat_N (those live elsewhere; R_tail is a later phase).
        - Not an evaluation inside Z_none (Z_none stays non-operational).

BUILD
        Lean 4.33.1 core only (no Mathlib, no Batteries).  AC Gate `lean`
        must see zero `sorry` tokens.

STATUS
        Fase A13 candidate.  Written to strengthen what the corpus already
        claims about finite scale, not to add narrative.
-/

namespace MSAF

/-! ## Scale axiom and valid coordinates -/

/-- Scale axiom object: a finite positive step count `n`. -/
structure PixelScale where
  n : Nat
  n_pos : 0 < n

/-- Absolute value on core `Rat` (core Lean has no `abs` for `Rat`). -/
def absR (x : Rat) : Rat := if x < 0 then -x else x

/-- Scale `Δ = 1/n`.  This is the Scale Axiom made operational: not a
    theorem about the continuum, but a stipulated quantum of coordinates. -/
def PixelScale.Δ (s : PixelScale) : Rat :=
  (1:Rat) / ((s.n:Nat):Rat)

/-- A coordinate is valid when it is a lattice point `k * Δ` with
    `0 ≤ k ≤ n`.  The cap `k ≤ n` records that the scale budget is finite. -/
def IsValidCoordinate (s : PixelScale) (x : Rat) : Prop :=
  ∃ k : Nat, k ≤ s.n ∧ x = ((k:Nat):Rat) * s.Δ

/-! ## Core arithmetic helpers (Lean 4.33.1, no Mathlib) -/

theorem natCast_num (k : Nat) : (((k:Nat):Rat)).num = Int.ofNat k := rfl
theorem natCast_den (k : Nat) : (((k:Nat):Rat)).den = 1 := rfl

theorem int_ofNat_pos {n : Nat} (hn : 0 < n) : (0:Int) < Int.ofNat n := by
  cases n with
  | zero => exact absurd hn (by omega)
  | succ _ => simp

theorem natCast_inj {k m : Nat} (h : ((k:Nat):Rat) = ((m:Nat):Rat)) : k = m := by
  have hn := congrArg Rat.num h
  rw [natCast_num] at hn
  rw [natCast_num] at hn
  exact Int.ofNat.inj hn

theorem natCast_pos {n : Nat} (hn : 0 < n) : (0:Rat) < ((n:Nat):Rat) := by
  have hnum := natCast_num n
  have hden := natCast_den n
  have h0num : (0:Rat).num = 0 := rfl
  have h0den : (0:Rat).den = 1 := rfl
  rw [Rat.lt_iff]
  rw [h0num, h0den, hnum, hden]
  show (0:Int) * ((1:Nat):Int) < Int.ofNat n * ((1:Nat):Int)
  rw [show ((1:Nat):Int) = (1:Int) from Int.ofNat_one]
  rw [Int.zero_mul, Int.mul_one]
  exact Int.ofNat_lt.mpr hn

theorem rat_lt_of_lt_of_le {a b c : Rat} (h1 : a < b) (h2 : b ≤ c) : a < c := by
  apply Classical.byContradiction
  intro h
  have hca : c ≤ a := Rat.not_lt.mp h
  have hba : b ≤ a := Rat.le_trans h2 hca
  exact Rat.not_le.mpr h1 hba

theorem natCast_one_le {k : Nat} (hk : 1 ≤ k) : (1:Rat) ≤ ((k:Nat):Rat) := by
  have hnum := natCast_num k
  have hden := natCast_den k
  have h1num : (1:Rat).num = 1 := rfl
  have h1den : (1:Rat).den = 1 := rfl
  rw [Rat.le_iff]
  rw [h1num, h1den, hnum, hden]
  show ((1:Nat):Int) * ((1:Nat):Int) ≤ Int.ofNat k * ((1:Nat):Int)
  rw [show ((1:Nat):Int) = (1:Int) from Int.ofNat_one]
  rw [Int.one_mul, Int.mul_one]
  exact Int.ofNat_le.mpr hk

theorem Δ_pos (s : PixelScale) : (0:Rat) < s.Δ := by
  show (0:Rat) < (1:Rat) / ((s.n:Nat):Rat)
  rw [Rat.div_def]
  have hnpos := natCast_pos s.n_pos
  have hinv : (0:Rat) < ((s.n:Nat):Rat)⁻¹ := Rat.inv_pos.mpr hnpos
  have hone : (1:Rat) * ((s.n:Nat):Rat)⁻¹ = ((s.n:Nat):Rat)⁻¹ := Rat.one_mul _
  rw [hone]
  exact hinv

theorem Δ_ne_zero (s : PixelScale) : s.Δ ≠ 0 := by
  intro h
  have hpos := Δ_pos s
  rw [h] at hpos
  exact Rat.lt_irrefl hpos

theorem sub_mul_eq (a b c : Rat) : a * c - b * c = (a - b) * c := by
  rw [Rat.sub_eq_add_neg, Rat.sub_eq_add_neg]
  rw [Rat.add_mul]
  rw [Rat.neg_mul]

theorem absR_nonneg (x : Rat) : (0:Rat) ≤ absR x := by
  show (0:Rat) ≤ (if x < 0 then -x else x)
  cases Decidable.em (x < 0) with
  | inl h =>
    rw [if_pos h]
    have hxnum : x.num < 0 := by
      have hlt := Rat.lt_iff x 0
      rw [show (0:Rat).num = 0 from rfl, show (0:Rat).den = 1 from rfl] at hlt
      have h2 := hlt.mp h
      simp only [show ((1:Nat):Int) = (1:Int) from Int.ofNat_one] at h2
      simp only [Int.mul_one, Int.zero_mul] at h2
      exact h2
    have hneg : (0:Rat) ≤ -x := by
      have h0num : (0:Rat).num = 0 := rfl
      have h0den : (0:Rat).den = 1 := rfl
      rw [Rat.le_iff]
      rw [h0num, h0den, Rat.neg_num, Rat.neg_den]
      show (0:Int) * ((x.den:Nat):Int) ≤ -x.num * ((1:Nat):Int)
      rw [show ((1:Nat):Int) = (1:Int) from Int.ofNat_one]
      rw [Int.zero_mul, Int.mul_one]
      omega
    exact hneg
  | inr h =>
    rw [if_neg h]
    exact Rat.not_lt.mp h

theorem absR_neg (x : Rat) (h : x < 0) : absR x = -x := by
  show (if x < 0 then -x else x) = -x
  rw [if_pos h]

theorem absR_of_nonneg {x : Rat} (h : 0 ≤ x) : absR x = x := by
  show (if x < 0 then -x else x) = x
  rw [if_neg]
  intro hlt
  exact Rat.not_le.mpr hlt h

theorem natCast_sub_den (k m : Nat) : (((k:Nat):Rat) - ((m:Nat):Rat)).den = 1 := by
  simp only [Rat.sub_def, natCast_num, natCast_den, Int.ofNat_one, Int.mul_one, Nat.mul_one]
  simp only [Rat.normalize, Nat.gcd_one_right]
  rfl

theorem natCast_sub_num (k m : Nat) :
    (((k:Nat):Rat) - ((m:Nat):Rat)).num = Int.ofNat k - Int.ofNat m := by
  simp only [Rat.sub_def, natCast_num, natCast_den, Int.ofNat_one, Int.mul_one, Nat.mul_one]
  simp only [Rat.normalize, Nat.gcd_one_right]
  rfl

theorem ofNat_sub {m k : Nat} (h : m ≤ k) : Int.ofNat k - Int.ofNat m = Int.ofNat (k - m) :=
  (Int.ofNat_sub h).symm

theorem natCast_sub {k m : Nat} (h : m ≤ k) :
    ((k:Nat):Rat) - ((m:Nat):Rat) = ((k - m:Nat):Rat) := by
  apply Rat.le_antisymm
  · rw [Rat.le_iff]
    rw [natCast_sub_num, natCast_den (k-m)]
    rw [natCast_num (k-m), natCast_sub_den k m]
    simp only [Int.ofNat_one, Int.mul_one]
    rw [ofNat_sub h]
    omega
  · rw [Rat.le_iff]
    rw [natCast_sub_num, natCast_den (k-m)]
    rw [natCast_num (k-m), natCast_sub_den k m]
    simp only [Int.ofNat_one, Int.mul_one]
    rw [ofNat_sub h]
    omega

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

theorem sub_neg_swap (a b : Rat) : a - b = -(b - a) := by
  calc a - b = a + -b := Rat.sub_eq_add_neg ..
    _ = -b + a := Rat.add_comm ..
    _ = -b + -(-a) := by rw [Rat.neg_neg]
    _ = -(b - a) := by rw [← Rat.neg_add, Rat.sub_eq_add_neg]

theorem rat_neg_pos {a : Rat} (h : 0 < a) : -a < 0 := by
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

/-! ## 1. Minimum separation of distinct valid coordinates -/

/-- **Minimum separation.**  Two distinct valid coordinates differ by at
    least one scale unit `Δ`.  This is a theorem about the lattice model,
    not a claim about ℝ. -/
theorem min_separation (s : PixelScale) (x y : Rat)
    (hx : IsValidCoordinate s x) (hy : IsValidCoordinate s y)
    (hxy : x ≠ y) :
    s.Δ ≤ absR (x - y) := by
  obtain ⟨k, hk, hxk⟩ := hx
  obtain ⟨m, hm, hym⟩ := hy
  have hΔpos := Δ_pos s
  have hxy' : x - y = (((k:Nat):Rat) - ((m:Nat):Rat)) * s.Δ := by
    rw [hxk, hym]
    exact sub_mul_eq _ _ _
  have hne : k ≠ m := fun he => hxy (by rw [hxk, hym, he])
  have hkm : k < m ∨ m < k := by
    cases Nat.lt_trichotomy k m with
    | inl h => exact Or.inl h
    | inr h => cases h with
      | inl heq => exact absurd heq hne
      | inr h => exact Or.inr h
  cases hkm with
  | inl hlt =>
    have hmk_pos : 1 ≤ m - k := by omega
    have hsub : ((m:Nat):Rat) - ((k:Nat):Rat) = ((m-k:Nat):Rat) :=
      natCast_sub (Nat.le_of_lt hlt)
    have hmk_one_le : (1:Rat) ≤ ((m-k:Nat):Rat) := natCast_one_le hmk_pos
    have hyx : y - x = (((m:Nat):Rat) - ((k:Nat):Rat)) * s.Δ := by
      rw [hxk, hym]
      exact sub_mul_eq _ _ _
    have hyx' : y - x = ((m-k:Nat):Rat) * s.Δ := by
      rw [hyx, hsub]
    have hge : ((m-k:Nat):Rat) * s.Δ ≥ (1:Rat) * s.Δ :=
      Rat.mul_le_mul_of_nonneg_right hmk_one_le (Rat.le_of_lt hΔpos)
    have hge' : ((m-k:Nat):Rat) * s.Δ ≥ s.Δ := by
      rw [Rat.one_mul] at hge
      exact hge
    have hΔ_le : s.Δ ≤ y - x := by
      rw [hyx']
      exact hge'
    have hpos_yx : (0:Rat) < y - x :=
      rat_lt_of_lt_of_le hΔpos hΔ_le
    have hxy_neg : x - y = -(y - x) := sub_neg_swap x y
    have hx_neg : x - y < 0 := by
      rw [hxy_neg]
      exact rat_neg_pos hpos_yx
    have habs : absR (x - y) = y - x := by
      rw [absR_neg (x - y) hx_neg]
      rw [hxy_neg]
      exact Rat.neg_neg _
    rw [habs]
    exact hΔ_le
  | inr hgt =>
    have hkm_pos : 1 ≤ k - m := by omega
    have hsub : ((k:Nat):Rat) - ((m:Nat):Rat) = ((k-m:Nat):Rat) :=
      natCast_sub (Nat.le_of_lt hgt)
    have hkm_one_le : (1:Rat) ≤ ((k-m:Nat):Rat) := natCast_one_le hkm_pos
    have hge : ((k-m:Nat):Rat) * s.Δ ≥ (1:Rat) * s.Δ :=
      Rat.mul_le_mul_of_nonneg_right hkm_one_le (Rat.le_of_lt hΔpos)
    have hge' : ((k-m:Nat):Rat) * s.Δ ≥ s.Δ := by
      rw [Rat.one_mul] at hge
      exact hge
    have hxy'' : x - y = ((k-m:Nat):Rat) * s.Δ := by
      rw [hxy', hsub]
    have hpos : (0:Rat) < x - y := by
      rw [hxy'']
      exact rat_lt_of_lt_of_le hΔpos hge'
    have habs : absR (x - y) = x - y := absR_of_nonneg (Rat.le_of_lt hpos)
    rw [habs]
    rw [hxy'']
    exact hge'

/-! ## 2. No valid coordinate in the open zone -/

/-- **Open-zone emptiness for lattice points.**  Under the Scale Axiom,
    the open zone `0 < |x - x0| < Δ` contains no *valid* coordinate when
    `x0` is itself valid.  This does **not** say the real interval is
    empty; it says the MSAF lattice has no point there. -/
theorem no_valid_coord_in_open_zone (s : PixelScale) (x x0 : Rat)
    (hx : IsValidCoordinate s x) (hx0 : IsValidCoordinate s x0) :
    ¬ (0 < absR (x - x0) ∧ absR (x - x0) < s.Δ) := by
  intro h
  have hpos := h.1
  have hlt := h.2
  have hne : x ≠ x0 := by
    intro he
    rw [he, Rat.sub_self] at hpos
    have habs0 : absR (0:Rat) = (0:Rat) := by
      show (if (0:Rat) < 0 then -(0:Rat) else (0:Rat)) = (0:Rat)
      rw [if_neg (Rat.lt_irrefl (a := (0:Rat)))]
    rw [habs0] at hpos
    exact absurd hpos (Rat.not_lt.mpr (Rat.le_refl (a := (0:Rat))))
  have hsep := min_separation s x x0 hx hx0 hne
  exact absurd hlt (fun hlt' =>
    Rat.lt_irrefl (rat_lt_of_lt_of_le hlt' hsep))

end MSAF