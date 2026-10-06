import numpy as np
import matplotlib.pyplot as plt

# 1. UNIVERSE SCALE CONSTANT PARAMETER DEFINITIONS (MSAF)
L_p = 1.616255e-35       # Planck scale (meters)
D_obs = 8.8e26           # Observable Universe diameter (meters)
Delta_univ = L_p / D_obs # Universe Pixel Constant (~1.836e-62)

print(f"=== INITIALIZATION MSAF FRAMEWORK ===")
# Delta_univ is the exact quotient of the two declared inputs, but D_obs is
# stated to 2 significant figures, so only ~2 sf of the quotient are
# physically justified (relative half-width 0.568%).  The full double is kept
# for the arithmetic below; the printout states what is actually known.
print(f"Universe Pixel Constant (Delta_univ): {Delta_univ:.7e}")
print(f"  as justified by D_obs = 8.8e26 (2 sf): {Delta_univ:.1e}  (+-0.568%)\n")

# 2. MODULAR WALL RADIUS (R_tail) VS BIT PRECISION SIMULATION (OMEGA-CORE v2)
# Faithful to the documented formula:
#   rem = 4 * exp(-(2(N+1)+0.5)*L) / (1 - exp(-2L)),  L = ln(c)
#   R_tail = rem * 2**(-p * Delta_univ)
# Evaluated in the log10 domain to avoid float64 underflow.
def calculate_r_tail_log10(N, c, prec_bits):
    L = np.log(c)
    log10_rem = (np.log10(4.0)
                 - (2 * (N + 1) + 0.5) * L * np.log10(np.e)
                 - np.log10(1.0 - np.exp(-2.0 * L)))
    log10_attenuation = -prec_bits * Delta_univ * np.log10(2.0)
    return log10_rem + log10_attenuation

precisions = np.array([2000, 4000, 6000, 9000, 12000, 15000, 18000])
r_tail_log10 = [calculate_r_tail_log10(N=400, c=100, prec_bits=p) for p in precisions]

# F1-N: the factor 2**(-p * Delta_univ) is numerically inert over this range.
# Evaluated analytically: in float64 the term is lost entirely under the
# accumulated log10_rem (~-1604), so differencing the sampled curve gives 0.
# F2-6: DECISION ON THE p AXIS (residual F1-N #4)
#
# The question was whether to plot the p axis at all, "given it carries no
# information over 2000-18000 bits".  Three options were weighed:
#
#   (a) drop the axis and the curve -- nothing to see;
#   (b) plot the analytic residual log10 R_tail(p) - log10 R_tail(p0) so the
#       p-dependence shows at its own (~1e-58) scale;
#   (c) keep axis, curve and markers, and make the panel self-contained.
#
# (a) is wrong: the axis names the independent variable whose inertness IS the
# finding, and the range examined has to be visible for the finding to mean
# anything.  (b) is worse than it looks: autoscaling a 1e-58 span draws a
# confident diagonal that invites the opposite reading.  (c) is chosen.
#
# What F2-6 actually fixes is that the panel was NOT self-contained.  The two
# numbers that make "flat" meaningful -- the float64-observed span and the
# bits needed for a single decade -- were printed to stdout only, and the two
# axvlines were labelled as if the curve moved through them (the same defect
# F1-N found in Brain.MD's prose).  Both are corrected below.
p_lo, p_hi = int(precisions[0]), int(precisions[-1])
log10_span = -(p_hi - p_lo) * Delta_univ * np.log10(2.0)
log10_span_f64 = float(r_tail_log10[-1] - r_tail_log10[0])
decade_bits = 1.0 / (Delta_univ * np.log10(2.0))
print(f"R_tail precision factor 2^(-p*Delta_univ):")
print(f"  analytic log10 span, p={p_lo}..{p_hi} : {log10_span:.3e}  -> curve is flat")
print(f"  float64 observed span              : {log10_span_f64:.3e}  (term below resolution)")
print(f"  bits needed for a 1-decade shift   : {decade_bits:.3e} bits\n")

# 3. PLOT 1: DOCUMENTED R_tail BEHAVIOR VS BIT PRECISION
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(precisions, r_tail_log10, 'r-o', linewidth=2, label=r'$\log_{10}\mathcal{R}_{\text{tail}}$')
plt.xlabel('Computational Bit Precision ($p$)', fontsize=10)
plt.ylabel(r'$\log_{10}\mathcal{R}_{\text{tail}}$', fontsize=10)
plt.title('Documented $\\mathcal{R}_{\\text{tail}}$ vs Precision (OMEGA-CORE v2) -- numerically flat', fontsize=11, fontweight='bold')
plt.grid(True, which="both", ls="--")
# F2-6: these mark where the N=400 certificate operated, not events on this
# curve.  The labels say so; the annotation repeats it.
plt.axvline(x=9000, color='blue', linestyle=':', label='certificate: 9000 bits (pivot 723 undetermined)')
plt.axvline(x=18000, color='green', linestyle='--', label='certificate: 18000 bits (verified)')
plt.annotate(rf'flat: $\Delta\log_{{10}}$ over {p_lo}$\to${p_hi} bits = {log10_span:.1e}'
             + "\n"
             + rf'float64 observed span = {log10_span_f64:.1e}'
             + "\n"
             + rf'1 decade would need {decade_bits:.3e} bits'
             + "\n"
             + 'vertical markers = certificate operating points,',
             xy=(0.02, 0.04), xycoords='axes fraction', fontsize=8, color='#555555', va='bottom')
plt.annotate('                 not features of this curve',
             xy=(0.02, 0.02), xycoords='axes fraction', fontsize=8, color='#555555', va='bottom')
plt.legend()

# 4. PLOT 2: PIXEL-SHIFT SWEEP OUTSIDE Z_none
# F2-2: the plotted points are n = 1..5 universe pixels from the anchor, i.e.
# distance >= Delta_univ.  Z_none is 0 < |x - x0| < Delta_univ, so NONE of these
# points is inside it -- the zone itself is never evaluated at all.  The old
# title called this sweep "Zone of Non-Existence", which is the same ambiguity
# F1-L found in the DRAF table.
# Visualizes the absolute Zeta function response when shifted per universe pixel
pixels = np.array([0, 1, 2, 3, 4, 5])
# Per-pixel deviation |Delta zeta| = |zeta'(rho_1)| * Delta_univ = 1.456761e-62
# (7 sf).  This is a constant recorded from the 100-DPS recomputation, NOT a
# value this file evaluates: msaf_visual.py contains no zeta call.  It is
# recomputed and gated by msaf_zeta_check.py (checks C3/C6/C7).
zeta_deviation = pixels * (1.456761e-62)

plt.subplot(1, 2, 2)
plt.stem(pixels, zeta_deviation, linefmt='b-', markerfmt='bo', basefmt='r-')
plt.xlabel('Horizontal Shift (Universe Pixel Units $\\Delta_{\\text{univ}}$)', fontsize=10)
plt.ylabel('Functional Deviation Magnitude $|\\Delta\\zeta|$', fontsize=10)
plt.title('Pixel-shift sweep OUTSIDE $\\mathcal{Z}_{\\text{none}}$ -- $|\\Delta\\zeta| \\propto \\Delta_{\\text{univ}}$',
          fontsize=11, fontweight='bold')
plt.xticks(pixels, ['0.5\n(Anchor)', '+1 px', '+2 px', '+3 px', '+4 px', '+5 px'])
plt.grid(True, ls=":")

for i, txt in enumerate(zeta_deviation):
    if i > 0:
        plt.annotate(f"{txt:.2e}", (pixels[i], zeta_deviation[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)

plt.tight_layout()
print("Generating visualization vectors... [SUCCESS]")
print("R_tail log10 values:", [f"{v:.4f}" for v in r_tail_log10])
print("Displaying MSAF simulation plot.")
plt.show()
