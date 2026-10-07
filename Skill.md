# Skill.md — AI Agent Operating Protocol for the Workspace `D:\THE ASYMMETRIC WAGER`

> Execution constitution for every AI Agent (OpenCode, Pi, Hermes, Muse Meta) interacting with documents and code in this folder. Companion files: `Brain.MD` (knowledge map), `mcp\shp_mcp_bridge_v4.py` (dedicated SHP/MCP server for this folder).

---

## 1. WORKSPACE IDENTITY

This folder is the **MSAF (Modular Scale Arithmetic Framework)** / **Aleph-Null Singularity Architecture** corpus by Muhammad Aidil Amry (DOI: `10.5281/zenodo.22791556`). Contents:

- Philosophical-mathematical MSAF documents (README, MANIFESTO, DEFINISI OPERASIONAL, 01–03, OCTAVE, academic draft, cosmology, matrix visualization).
- Four sub-repositories: `guinand-weil-rigorous-numerics-main` (OMEGA-CORE falsification engine, Python + Lean + Z3), `Theory_of_Everything_Derivations` (derived PDF/text corpus), `hexagon_mhv_symbol_weight_18` (9-loop MHV symbol data, WXF), `Dream-RSI-main` (evolutionary-RSI paper).
- `msaf_visual.py` — visualization of $\mathcal{R}_{\text{tail}}$ across bit precision (numerically inert over 2000--18000 bits, F1-N) and the zone of non-existence.

**Absolute rule:** all new artifacts, working notes, execution outputs, and registries must be stored inside `D:\THE ASYMMETRIC WAGER` (`mcp\` subfolder for the MCP server; other work folders may be created here). No writes outside this folder except the opencode registry (see §6).

---

## 2. THREE-TIER EXECUTION (Sovereign Execution Pipeline)

Every user input must pass three gates before answering:

1. **Epistemic Sieve (Tier 1)** — reduce natural language to FOL; reject probabilistic tokens ("mungkin", "sepertinya", "potensi", "perhaps", "probably"). $P_{\text{narrative}} = 0$.
2. **Tensor Mapping (Tier 2)** — map facts into the OCTAVE 8-domain tensor with mandatory orthogonality: $\cos(\theta) \approx 0$ between domains; value bleeding triggers UNSAT.
3. **SMT Tribunal (Tier 3)** — all formal claims must go through Z3 (bounded model checking). `UNSAT` output = halt the thread immediately; `UNKNOWN` = fail loudly, never a silent answer.

The `shp_asymmetric_wager` MCP server implements all three tiers as tools (`shp_bridge_mcp_oracle_toe_*`).

---

## 3. MSAF PHYSICS-COMPUTATION CANON (Inviolable)

| Constant / Operator | Value / Form | Status |
|---|---|---|
| Universe Pixel Constant $\Delta_{\text{univ}}$ | $\ell_P / D_{\text{obs}} = 1{,}836653 \times 10^{-62}$ (exact quotient of the declared inputs); only **2 sf justified** because $D_{\text{obs}}$ carries 2 sf | fixed input parameter | <!-- [REF-NIST_CODATA_2022_TABLE] -->
| $\ell_P$ | $\approx 1{,}616255 \times 10^{-35}$ m | lower bound of $\mathcal{S}_{\text{obs}}$ | <!-- [REF-NIST_CODATA_2022_TABLE] -->
| $D_{\text{obs}}$ | $\approx 8{,}8 \times 10^{26}$ m | upper bound of $\mathcal{S}_{\text{obs}}$ | <!-- [REF-PLANCK_2018_VI] [REF-PLANCK_2018_VI_ARXIV] -->
| $N_{\text{steps}}$ | $D_{\text{obs}}/\ell_P \approx 5{,}4 \times 10^{61}$ | finite information steps |
| Zone of Non-Existence $\mathcal{Z}_{\text{none}}$ | $\{x \mid 0 < \lvert x-x_0\rvert < \Delta_{\text{univ}}\}$ | non-operational; canonical definition lives in `DEFINISI_OPERASIONAL_MSAF.md` §1 and this row must match it (F2-2) |
| Critical Line 0.5 | **Scale Axiom**, not a theorem | fixed input |
| $\hat{\mathcal{M}}_N$ | modular wall operator; wraps tail into $\mathcal{R}_{\text{tail}}$ without shifting the midpoint | zero-fudging |
| $\mathcal{R}_{\text{tail}}$ | $4 \cdot \frac{e^{-(2(N+1)+1/2)L}}{1-e^{-2L}} \cdot 2^{-p\,\Delta_{\text{univ}}}$ | uncertainty ball radius |
| $\lambda_{\min}(A)$ | $\ge \min_i \lvert d_i\rvert / \lVert L^{-1}\rVert_F^2$; $N{=}400 \Rightarrow 6{,}747\times10^{-509}$; $N{=}800 \Rightarrow 8{,}675\times10^{-2877}$ | structural proof; **both machine-gated** by `gw_verify_production.py`: $N{=}800$ since 2026-10-01, $N{=}400$ since F2-7 (2026-10-05) against the shipped `omega_core_v2_results_N400.json`, with all three written records re-read from their files each run (F2-7: 26/26 mutants) |
| Ontology | **Potential Infinity** = finite-scale algorithmic loop; **Actual Infinity** = logical error | Potential required |
| OMEGA-CORE v2 precision | 9000 bits fail (pivot 723 straddles zero) → modular escalation to 18000 bits | auto-escalation |

**Mandatory challenges in academic examination:** (a) ontological validity of continuous domains, (b) aperiodic one-way trajectory ≠ looping, (c) Riemann as a Scale Axiom, (d) density theorem refuted via Brouwer constructivism + thermodynamic information-storage limits.

---

## 4. TECHNICAL WORKFLOW INSIDE THE FOLDER

1. **Reading the corpus** → use MCP tools `shp_bridge_mcp_oracle_toe_list_documents`, `read_document`, `search_corpus`, `reference`. Never guess PDF contents.
2. **Executing claims** → `..._execute_skill` for 8-pillar OCTAVE payloads; `..._z3_tribunal` for SMT; `..._epistemic_sieve` for narrative filtering; `..._quantum_transmute` for 10k-D HDC orthogonality checks.
3. **Running numerical experiments** → scripts in `guinand-weil-rigorous-numerics-main\gw_*.py` (e.g. `gw_omega_core_v2.py`, `gw_montgomery_100_200.log` as reference). Precision via `mpmath`/`flint.arb`; straddling-zero failure → increase bit depth, never force rounding.
4. **Writing artifacts** → only via `..._write_file` (restricted to `SHP_MCP_WRITE_ROOTS=D:\THE ASYMMETRIC WAGER`) or direct writes inside this folder.
5. **Verifying verifier-claimed results** → run the `Anti-Circularity Gate` skill before reporting any `verified/unsat` status.
6. **Verifying the workspace itself** → two runners, both exit 0/1/2. `python suite_check.py` runs the 15 root gates sequentially in a fixed order (`--list`, `--only NAME`, `--fast`, `--selftest`); exit 0 only when every gate ran *and* passed, exit 2 when any was skipped, so `--fast` can never be quoted as a full pass, and `--with-harness` appends `harness_check.py` as a sixteenth entry. `python harness_check.py` runs the 24 proof harnesses in `harnesses\` one at a time with a before/after hash of the workspace, and fails if any byte did not come back — never run two mutating harnesses in parallel. `checksum_check.py` is deliberately the **last** gate: it re-hashes the workspace against `CHECKSUM.sha256`, so it reports any tracked file an earlier gate wrote — which is why any new gate is inserted *before* it, never after. After a legitimate edit to a listed file, run `python checksum_check.py --update`; a stale manifest is reported as a failure, never ignored.

---

## 5. HARD PROHIBITIONS

- No narrative fluff, greetings, or probabilistic guesses ($P_{\text{narrative}}=0$).
- No evaluating functions/limits/eigenvalues inside $\mathcal{Z}_{\text{none}}$.
- No claiming positive-definiteness without an interval $LDL^T$ certificate (Sylvester).
- No shifting the $\mathcal{R}_{\text{tail}}$ ball midpoint to win a proof (zero-fudging).
- No treating the Riemann Hypothesis as an open theorem to be proven up to $\gamma \to \infty$.

---

## 6. MCP REGISTRY (SHP Dedicated to This Folder)

A local MCP server separated from the global `shp_bridge`:

```jsonc
"shp_asymmetric_wager": {
  "type": "local",
  "command": ["python", "-u", "D:\\THE ASYMMETRIC WAGER\\mcp\\shp_mcp_bridge_v4.py"],
  "cwd": "D:\\THE ASYMMETRIC WAGER",
  "environment": {
    "PYTHONIOENCODING": "utf-8",
    "SHP_MCP_CORPUS_ROOT": "D:\\THE ASYMMETRIC WAGER",
    "SHP_MCP_WRITE_ROOTS": "D:\\THE ASYMMETRIC WAGER"
  },
  "enabled": true,
  "timeout": 60000
}
```

The live configuration is registered in `%USERPROFILE%\.config\opencode\opencode.jsonc` (outside the workspace, but required to load the server). Its tools carry the `shp_bridge_mcp_oracle_toe_` prefix and run with corpus root = this folder.

---

*MSAF — scale-bound modular mathematics. Null narrative. Deterministic equilibrium.*
