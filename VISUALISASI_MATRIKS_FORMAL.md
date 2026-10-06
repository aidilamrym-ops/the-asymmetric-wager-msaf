# FORMAL MATRIX VISUALIZATION: MODULAR WALL BOUNDARY OPERATOR ($\hat{\mathcal{M}}_N$)

This document contains the formal matrix representation of order $(2N+1) \times (2N+1)$ for the implementation of the **Modular Scale Arithmetic Framework (MSAF)** based on empirical data from the *OMEGA-CORE Falsification Engine v2*.

---

## 1. GLOBAL STRUCTURE OF THE ARB BALL MATRIX $\hat{\mathcal{M}}_N(A)$

The Guinand-Weil truncation matrix is *Real Symmetric* ($A_{nm} = A_{mn}$) with zero-centered coordinate indices ($n, m \in \{-N, \dots, N\}$). The total matrix dimension is $2N+1$ (at $N=400$, dimension = $801 \times 801$; at $N=800$, dimension = $1601 \times 1601$).

$$\hat{\mathcal{M}}_N(A) = \begin{pmatrix} 
A_{-N, -N} & A_{-N, -N+1} & \cdots & A_{-N, 0} & \cdots & A_{-N, N} \\ 
A_{-N+1, -N} & A_{-N+1, -N+1} & \cdots & A_{-N+1, 0} & \cdots & A_{-N+1, N} \\ 
\vdots & \vdots & \ddots & \vdots & \ddots & \vdots \\ 
A_{0, -N} & A_{0, -N+1} & \cdots & A_{0, 0} & \cdots & A_{0, N} \\ 
\vdots & \vdots & \ddots & \vdots & \ddots & \vdots \\ 
A_{N, -N} & A_{N, -N+1} & \cdots & A_{N, 0} & \cdots & A_{N, N} 
\end{pmatrix} \pm \begin{bmatrix} \mathcal{R}_{\text{tail}}(N, c) \end{bmatrix}$$

---

## 2. MATHEMATICAL FORMULATION OF INTERNAL ELEMENTS ($A_{nm}$)

Each internal element cell coordinate is built from the difference of three discrete information space components:
$$A_{nm} = W_{02}(n,m) - W_{R}(n,m) - W_{p}(n,m)$$

With fundamental scale parameters: $L = \ln c$, $U = e^{L/2}$.

### 2.1 Core Geometry Component ($W_{02}$)
Maps the upper bound of information space curvature against the scale truncation parameter $c$:
$$W_{02}(n,m) = \frac{32 \cdot L \cdot \sinh^2(L/4) \cdot \bigl(L^2 - 16\pi^2 mn\bigr)}{\bigl(L^2 + 16\pi^2 m^2\bigr)\bigl(L^2 + 16\pi^2 n^2\bigr)}$$

### 2.2 Local Continuous Component ($W_{R}$)
Operates based on closed-form *digamma/trigamma* series calculations ($\psi, \psi_1$) at the absolute position of the critical coordinate $z = \frac{1}{4} + i\frac{\pi n}{L}$:

*   **For Diagonal Elements ($n = m$):**
    $$W_{R}(n,n) = \kappa(L) + 2 \cdot CC(|n|) + J(L) - \frac{2}{L} \cdot XC(|n|)$$
    *Space Constants:*
    $$\kappa(L) = \ln\Bigl(4\pi\,\frac{e^{L}-1}{e^{L}+1}\Bigr) + \gamma$$
    $$J(L) = -2\ln(U+1) + \ln(U^2+1) + 2\arctan U + \ln 2 - \frac{\pi}{2}$$
    *Analytic Continuation Series:*
    $$CC[n] = -\frac{1}{2}\Bigl(\Re\,\psi\Bigl(\tfrac{1}{4} + i\tfrac{\pi n}{L}\Bigr) - \psi\bigl(\tfrac{1}{4}\bigr)\Bigr) + g_{CC}, \qquad CC[0] = 0$$
    $$XC[n] = \frac{1}{4}\,\Re\,\psi_1\Bigl(\tfrac{1}{4} + i\tfrac{\pi n}{L}\Bigr) - L \cdot g_{X1} - g_{X2}$$

*   **For Non-Diagonal Elements ($n \neq m$):**
    $$W_{R}(n,m) = \frac{S(m) - S(n)}{\pi \cdot (n-m)}$$
    $$S[n] = \frac{1}{2}\,\Im\,\psi\Bigl(\tfrac{1}{4} + i\frac{\pi n}{L}\Bigr) - \frac{2\pi n}{L} \cdot g_S, \qquad S[0] = 0$$

### 2.3 Discrete Prime Number Fluctuation Component ($W_{p}$)
One-directional modular frequency peaks that extract the quantum prime number density contribution ($q = p^a$) below the observation bound $c$:

*   **For Diagonal Elements ($n = m$):**
    $$W_{p}(n,n) = \sum_{q \le c} (\ln p) \cdot q^{-1/2} \cdot \left[ 2\Bigl(1 - \frac{\ln q}{L}\Bigr)\cos\Bigl(\dfrac{2\pi n \ln q}{L}\Bigr) \right]$$

*   **For Non-Diagonal Elements ($n \neq m$):**
    $$W_{p}(n,m) = \sum_{q \le c} (\ln p) \cdot q^{-1/2} \cdot \left[ \frac{\sin\bigl(\frac{2\pi m \ln q}{L}\bigr) - \sin\bigl(\frac{2\pi n \ln q}{L}\bigr)}{\pi \cdot (n-m)} \right]$$

---

## 3. MODULAR WALL BOUNDARY RADIUS ($\mathcal{R}_{\text{tail}}$)

This homogeneous error radius is tasked with compressing the infinite series remainder from the axis functions ($g_S, g_{CC}, g_{X1}, g_{X2}$) and wrapping it into the thickness bound of the arithmetic ball without shifting the midpoint value (*midpoint*):

$$\mathcal{R}_{\text{tail}}(N, c) = 4 \cdot \frac{e^{-\left(2(N+1)+\frac{1}{2}\right)L}}{1 - e^{-2L}} \cdot 2^{-p \cdot \Delta_{\text{univ}}}$$

Where $p$ is the active computation bit precision ($9000 \to 18000\text{ bit}$), and $\Delta_{\text{univ}}$ denotes the physical information pixel constant of the observed universe:
$$\Delta_{\text{univ}} = \frac{\ell_P}{D_{\text{obs}}} \approx 1{,}836653 \times 10^{-62}$$

> **Significant-figure note (F1-A).** $D_{\text{obs}} = 8{,}8 \times 10^{26}$ carries only two significant figures, so only $1{,}8 \times 10^{-62}$ is observationally justified. The digits beyond the second reproduce the defined quotient $\ell_P/D_{\text{obs}}$; they are kept for reproducibility, not as measured precision.

> **Precision-inertness note (F1-N).** The factor $2^{-p\,\Delta_{\text{univ}}}$ is numerically inert over $p \in [2000, 18000]$: the whole range changes $\log_{10}\mathcal{R}_{\text{tail}}$ by only $8{,}85 \times 10^{-59}$, i.e. the curve is horizontal to 58 decimal places. A one-decade shift would need $p \approx 1{,}8 \times 10^{62}$ bits. The $p$ axis therefore records the *certified precision* at which the ball was closed; it does not depict a decay.

---

## 4. ACADEMIC VALIDATION GATES REQUIREMENTS

1.  **Symmetry Exact Side-Condition:** The mutual containment procedure guarantees a provably real matrix spectrum:
    $$\forall_{i,j}, \quad A_{ij}.\texttt{contains}(A_{ji}) \ \wedge \ A_{ji}.\texttt{contains}(A_{ij})$$
2.  **Interval $LDL^T$ Certification:** Pivot ball classification must pass the strict sign test without decimal rounding tolerance intervention:
    $$d_i = A_{ii} - \sum_{k<i} L_{ik}^2\, d_k > 0 \quad \Longrightarrow \quad \text{VERIFIED POSITIVE DEFINITE}$$

---
*This document is designed as a structural technical visual supplement to MSAF for academic examiners.*
