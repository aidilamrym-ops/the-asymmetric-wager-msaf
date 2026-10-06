# Third-Party Sources

Files in this repository that were not written by the OMEGA authors, together
with the licence under which they are redistributed.

---

## 1. `source_arb_ldlt_certify.py`

| field | value |
|---|---|
| origin | `https://github.com/akivag613/connes-cvs-` |
| path | `papers/2_guinand_weil_dictionary_tail_order/scripts/arb_ldlt_certify.py` |
| retrieved | 2026-09-27 |
| size as shipped | 12863 bytes |
| SHA-256 as shipped | `33617ce64b0e052c07873b196a3744f2f5142a4aaf7b4cfbe9e3de43d17c27bb` |
| size as retrieved (verbatim) | 12256 bytes |
| SHA-256 as retrieved | `b7fee730a83baedc860ca456547d2799ec10894a79edecc6d5612931b41509e3` |
| licence | MIT — `Copyright (c) 2026 Akiva Groskin` |
| used by | `gw_omega_core_v2.py` (imports `build_arb_tau`, the certified matrix entries), `gw_opt_a_diff.py` (Option (a) entrywise matrix diff), `gw_even_vs_src.py` |

### Why the file is stored verbatim -- and how it was then modified

The SHA-256 as retrieved is **byte-identical** to the `script_sha256` field
recorded in the upstream provenance file
`artifacts/c100_N200_arb_ldlt_prec9000_provenance.json`, which also records
`n_pos = 401`, `n_neg = 0`, `dimension = 401`, `prec_bits = 9000`,
`c = 100`, `N = 200`, `package_commit = 8ce0fc791ed9c9ca6f4ba512322720b4be80421b`.

Storing the file byte-for-byte is therefore part of the *evidence*: it makes
reproduction of the diff in `gw_opt_a_diff.py` a check against the exact code
that produced the published certificate, rather than against an approximation
of it. Re-typing the formulas by hand would have destroyed that link.

**That verbatim copy is preserved at git commit `b76be0d` (2026-09-27):**
`git show b76be0d:source_arb_ldlt_certify.py | sha256sum` must print
`b7fee730...1509e3`, and the file at that commit is 12256 bytes.

**The working-tree file is no longer that copy.** On 2026-09-30 09:12:19
(commit `bfa40dc`, "Add power-cut checkpointing to the OMEGA-CORE sweep") the
file was extended with exactly three keyword arguments on `build_arb_tau` --
`start_row`, `row_hook`, `prefill` -- so a multi-hour sweep could resume after
the machine lost power. All three default to the original behaviour and no
arithmetic was changed; the diff is 607 bytes of new parameters and hooks only.
The copy that ran the certified $N=800$ sweep is this 12863-byte file,
SHA-256 `33617ce6...c27bb`. The pre-edit bytes are also on disk outside the
repository as `source_arb_ldlt_certify.py.bak_20260930_062119` (12256 bytes,
`b7fee730...`).

**Consequences an evaluator should know about, recorded rather than hidden:**

* `OMEGA_CORE_CERTIFICATE.md` section 1 reconciles both hashes and says which
  run used which copy; section 6.1 lists the shipped one.
* The engine prints the *original* hash from a hard-coded string
  (`gw_omega_core_v2.py` line 707), so the caveat block inside
  `omega_core_v2_run.log` and `omega_v2_stdout.txt` reports `b7fee730...` even
  for the $N=800$ block, which ran on `33617ce6...`. The logs are never edited.
* `gw_even_vs_src.py` (lines 54-64, 154-172) recomputes the on-disk SHA-256 and
  compares it against **both** pinned copies: `b7fee730...` (verbatim upstream)
  or `33617ce6...` (the documented 2026-09-30 extension). It reports which one
  it found, and it fails on any third value with
  `*** MISMATCH -- do NOT trust this run ***`. Its original log
  `gw_even_vs_src_100_200.log` recorded `MATCH -- byte-identical` on
  2026-09-27, which was true then; the full rerun of 2026-10-02
  (`gw_even_vs_src_100_200_rerun_20261002.log`, exit 0, 339 s) records
  `MATCH -- documented local extension` and reproduces $\delta_{L_\infty}$,
  $\delta_{\rm rel}$, the median ratio and the `V1` verdict **identically** to
  the 2026-09-29 log -- only wall-clock times differ. Both logs are shipped;
  neither was edited.
* `gw_opt_a_diff.py` prints the SHA-256 it actually loaded and which pinned
  copy that is, instead of asserting a single hash in a header comment.

### MIT licence text (as distributed with the source package)

```
MIT License

Copyright (c) 2026 Akiva Groskin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Scope statement

`source_arb_ldlt_certify.py` is used for two different purposes here; they must
not be conflated:

1. **Comparison** (the original purpose). `gw_opt_a_diff.py` and
   `gw_even_vs_src.py` rebuild a reference matrix with it and diff ours against
   it, byte-checking that the vendored file still matches the published
   `script_sha256`.
2. **Construction.** `gw_omega_core_v2.py` executes
   `import source_arb_ldlt_certify as src` and calls `src.build_arb_tau(...)` to
   produce the Arb entries of every OMEGA-CORE target, including both certified
   ones ($N=400$ and $N=800$). The matrix entries quoted in
   `OMEGA_CORE_CERTIFICATE.md` are therefore built by this third-party code;
   that code is MIT-licensed, unmodified in its arithmetic, and pinned by
   SHA-256 in section 1 above.

What is *not* taken from it is its `certified_inertia()` path. No inertia
reported anywhere in this repository comes from that function: OMEGA-CORE
inertias come from the engine's own interval $LDL^T$ (`certified_ldlt`,
Sylvester's criterion), and the inertias in `gw_corrected_eig.py` and
`gw_opt_b_arb.py` come from `flint.arb_mat.eig`.

Nothing in this repository establishes the Riemann Hypothesis, Weil
positivity, a prime-counting result, or a factorisation method. The upstream
preprint disclaims all four.

---

## 2. Runtime third-party dependencies (not vendored, not modified)

These are consumed from the interpreter environment. No file from them is
copied into this repository, and none of their code was edited.

| component | version | role in the verification chain |
|---|---|---|
| CPython | 3.14.4 (`C:\Python314\python.exe`) | interpreter; `py_compile` sweep |
| NumPy | 2.5.2 | `eigvalsh`, the pair-difference histogram in `r2_curve` |
| SciPy | present (`scipy.stats.norm`) | the Gaussian CDF inside `unfold()` |
| mpmath | present | arbitrary-precision path |
| python-flint | 0.9.0 | `arb_mat.eig` certified inertia path |

**Tool status:** `python 3.14` + `numpy` + `scipy` were **RUN**.
`lean` / `coqc` / `isabelle` / `dkcheck` / `z3` / `gcc` were **NOT RUN** in the
session that produced the freeze. Subsequently, on 2026-10-02, `lean` 4.33.1
and `z3` 4.16.0 **were RUN** for Track C only (`OMEGATrackC.lean`,
`track_c_make_smt.py`); `coqc`, `isabelle`, `dkcheck` and `gcc` remain **NOT
RUN**. See `OMEGA_CORE_CERTIFICATE.md` section 6.7 for what that run does and
does not establish.

### Provenance of first-party artifacts

SHA-256 for every verification script, run log and input file — including the
two *failed* diagnostic logs, which are retained so that the bugs behind them
stay auditable — is recorded in [`PROVENANCE.txt`](PROVENANCE.txt). Living
documents (`GW_STATUS_2026-09-26.md`, `state/STATE.md`,
`state/PROJECT_REGISTRY.json`) are deliberately excluded from that file because
they are edited as work proceeds; hash them at the moment of archiving instead.

Known residuals carried into the freeze are listed at the end of
`PROVENANCE.txt` (defect 18, the unexplained K5 row of `GW_STATUS` §h.3,
defect 19, and the repository-wide `py_compile` count of 853/856).
