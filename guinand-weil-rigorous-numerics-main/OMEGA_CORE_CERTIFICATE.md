# OMEGA-CORE Falsification Engine v2 -- Certified Positive Definiteness of the Guinand-Weil Matrices at $N=400$ and $N=800$

**Snapshot:** 2026-09-29 15:19:49 (the $N=400$ certificate; the $N=800$ target completed 2026-10-01 21:06)
**Target (this snapshot):** $(c, N) = (100, 400)$, $\dim = 2N+1 = 801$
**Target (recorded in section 6.6):** $(c, N) = (100, 800)$, $\dim = 2N+1 = 1601$
**Verdict:** `VERIFIED POSITIVE DEFINITE` for both targets -- $n_{+}=801,\ n_{-}=0$ ($N=400$) and $n_{+}=1601,\ n_{-}=0$ ($N=800$)
**Tool status:** python 3.14.4 + python-flint 0.9.0 produced every number below. `coqc` / `isabelle` / `dkcheck` / `gcc` **NOT RUN**. `lean` 4.33.1 and `z3` 4.16.0 were run on 2026-10-02, but only for the separate Track C module (`OMEGATrackC.lean`, section 6.7), which takes the literals printed here as *inputs*. **No number below is kernel-checked**, and ball arithmetic is not a proof assistant.

> **SCOPE LIMIT, read literally.**
> Nothing in this document establishes the Riemann Hypothesis, Weil positivity,
> a prime-counting result, or a factorisation method. What is certified is the
> inertia of two finite, deterministic, real symmetric matrices -- of order 801
> ($N=400$) and of order 1601 ($N=800$) -- together with a rigorous lower bound
> on each smallest eigenvalue. Each matrix is a *finite truncation*, not the
> operator it approximates.

---

## 1. The matrix, as built

`build_arb_tau(c, N, prec)` (in the vendored source package
`source_arb_ldlt_certify.py`, MIT) assembles a $(2N+1)\times(2N+1)$ Arb ball matrix. Indexing is

**Two SHA-256 values exist for that file; both are correct for different
copies, and they are not interchangeable.**

| copy | bytes | SHA-256 | where it is recorded |
|---|---:|---|---|
| original third-party package, stored verbatim | 12256 | `b7fee730a83baedc860ca456547d2799ec10894a79edecc6d5612931b41509e3` | git `b76be0d` (2026-09-27); upstream `script_sha256`; `THIRD_PARTY_SOURCES.md` section 1; `PROVENANCE.txt` line 83 |
| resume-enabled copy that actually ran the $N=800$ sweep | 12863 | `33617ce64b0e052c07873b196a3744f2f5142a4aaf7b4cfbe9e3de43d17c27bb` | working tree and git `bfa40dc` (2026-09-30 09:12:19); section 6.1 of this certificate |

The 2026-09-30 edit added exactly three keyword arguments to `build_arb_tau`
(`start_row`, `row_hook`, `prefill`) so the sweep could resume after the power
cut; all three default to the original behaviour, so no arithmetic changed.
The $N=400$ runs of 2026-09-29 used the original bytes; the $N=800$ sweep used
the extended copy. Caveat: `gw_omega_core_v2.py` line 707 prints the *original*
hash from a hard-coded string, so the caveat block inside
`omega_core_v2_run.log` and `omega_v2_stdout.txt` reports `b7fee730...` for the
$N=800$ block as well. The file that ran is the `33617ce6...` copy. The logs are
never edited (see `PROVENANCE.txt`); this correction is recorded here.

$$i, j \in \{0,\dots,2N\}, \qquad n = i - N, \qquad m = j - N,$$

so $n,m \in \{-N,\dots,N\}$, and with

$$L = \ln c, \qquad \mathrm{sp2} = 16\pi^2, \qquad \ell^2 = L^2,
\qquad \texttt{pref02} = 32\,L\,\sinh^2(L/4),$$

the entry is

$$\boxed{\;A_{ij} \;=\; W_{02}(n,m) \;-\; W_{R}(n,m) \;-\; W_{p}(n,m)\;}
\qquad\text{written to } A[i,j]\text{ and }A[j,i].$$

**Caution on notation.** $W_{02}$, $W_{R}$, $W_{p}$ and the name $\tau$ are the
*source code's own labels* (`W02`, `WR`, `Wp`, `build_arb_tau`). The formulae
below are transcribed from that code, not imported from an external reference;
any renaming for publication must be chosen by the author, not inferred here.

### 1.1 The three terms

$$W_{02}(n,m) \;=\; \frac{32\,L\,\sinh^2(L/4)\,\bigl(L^2 - 16\pi^2 mn\bigr)}
{\bigl(L^2 + 16\pi^2 m^2\bigr)\bigl(L^2 + 16\pi^2 n^2\bigr)}$$

$$W_{R}(n,m) \;=\;
\begin{cases}
\kappa(L) \;+\; 2\,CC(|n|) \;+\; J(L) \;-\; \dfrac{2}{L}\,XC(|n|), & n = m,\\[2.2ex]
\dfrac{S(m) - S(n)}{\pi\,(n-m)}, & n \neq m,
\end{cases}$$

$$W_{p}(n,m) \;=\; \sum_{\substack{q = p^{a} \\ q \le c}} (\ln p)\; q^{-1/2}\; \chi_{q}(n,m),
\qquad
\chi_{q}(n,m)=\begin{cases}
2\Bigl(1 - \dfrac{\ln q}{L}\Bigr)\cos\!\Bigl(\dfrac{2\pi n \ln q}{L}\Bigr), & n = m,\\[2.2ex]
\dfrac{\sin\!\bigl(\frac{2\pi m \ln q}{L}\bigr) - \sin\!\bigl(\frac{2\pi n \ln q}{L}\bigr)}{\pi\,(n-m)}, & n \neq m.
\end{cases}$$

In code the prime-power weights and positions are

```
weights   = [arb(p).log() * (arb(q) ** arb('-0.5')) for (q, p) in prime_powers_up_to(c)]
positions = [arb(q).log()                     for (q, p) in prime_powers_up_to(c)]
```

i.e. weight $=(\ln p)\,q^{-1/2}$ and $y = \ln q$, exactly as written above.

### 1.2 Closed constants

$$\kappa(L) = \ln\!\Bigl(4\pi\,\frac{e^{L}-1}{e^{L}+1}\Bigr) + \gamma,
\qquad U = e^{L/2},$$

$$J(L) = -2\ln(U+1) + \ln(U^2+1) + 2\arctan U + \ln 2 - \frac{\pi}{2}.$$

### 1.3 Closed series (digamma / trigamma at $z = \tfrac14 + i\tfrac{\pi n}{L}$)

With $w = \dfrac{2\pi n}{L}$:

$$S[n] = \tfrac12\,\Im\,\psi\!\Bigl(\tfrac14 + i\tfrac{\pi n}{L}\Bigr) - w\,g_S,
\qquad S[0] = 0,$$

$$CC[n] = -\tfrac12\Bigl(\Re\,\psi\!\Bigl(\tfrac14 + i\tfrac{\pi n}{L}\Bigr) - \psi\!\bigl(\tfrac14\bigr)\Bigr) + g_{CC},
\qquad CC[0] = 0,$$

$$XC[n] = \tfrac14\,\Re\,\psi_1\!\Bigl(\tfrac14 + i\tfrac{\pi n}{L}\Bigr) - L\,g_{X1} - g_{X2}.$$

### 1.4 Geometric sums and the rigorous tail

With $c_k = 2k + \tfrac12$, $e_k = e^{-c_k L}$, $\mathrm{den} = c_k^2 + w^2$:

$$g_S = \sum_k \frac{e_k}{c_k^2 + w^2},\qquad
g_{CC} = \sum_k \frac{e_k\,w^2}{c_k\,(c_k^2+w^2)},\qquad
g_{X1} = \sum_k \frac{e_k\,c_k}{c_k^2 + w^2},\qquad
g_{X2} = \sum_k \frac{e_k\,(c_k^2 - w^2)}{(c_k^2+w^2)^2}.$$

The summation stops when $e_k < 2^{-(\texttt{prec}+24)}$, and the entire
truncation remainder is **wrapped into the radius, never discarded**:

$$\text{rem} \;=\; 4\cdot\frac{e^{-(2(k+1)+\frac12)L}}{1 - e^{-2L}},
\qquad \texttt{widen}(x) \;=\; x + [0 \pm \text{rem}].$$

`widen` adds a ball centred at zero: the tail **widens the enclosure without
moving the midpoint**. This is the first of the zero-fudging properties -- an
unsummable tail can only make the interval larger, never shift it toward a
desired value.

---

## 2. Zero-Fudging architecture

### 2.1 Why v2 and not v1

v1 fed an mpmath-built matrix into `flint.arb` as **decimal text** and called
`arb_mat.eig` for the full spectrum. Both failure modes were *measured*, not
supposed:

1. **Speed.** `arb_mat.eig` on $801\times801$ @ 2851 bits ran 94 minutes without
   finishing and was killed by a shell timeout. A full spectrum is $O(n^3)$ with
   a large constant (deflation iterations).
2. **Rigour.** v1's radius covered FLINT rounding only; the mpmath *origin* of
   the digits was not enclosed. That caveat was real.

v2 therefore builds every entry natively in Arb (no decimal hand-off anywhere)
and answers falsification directly by interval $LDL^T$.

### 2.2 Certification by interval $LDL^T$ (Sylvester)

`certified_ldlt_with_L(A, DIM, ...)` runs the recurrence

$$d_i = A_{ii} - \sum_{k<i} L_{ik}^2\, d_k, \qquad
L_{ji} = \frac{1}{d_i}\Bigl(A_{ji} - \sum_{k<i} L_{jk} L_{ik}\, d_k\Bigr),
\qquad L_{ii} = 1,$$

entirely in Arb ball arithmetic, and classifies **each pivot ball**:

| condition evaluated on the ball $s$ | meaning |
|---|---|
| $s > 0$ (ball strictly positive) | `n_pos += 1`, **proved** |
| $s < 0$ (ball strictly negative) | `n_neg += 1`, **proved -- HALT-level anomaly** |
| **both** comparisons `False` | `undetermined = i`, **escalate, never fudge** |

The third row is the essential point. On an Arb ball, `s > 0` and `s < 0` are
*both* `False` whenever the radius straddles zero. That state is **not** read as
"s $= 0$", and it is **not** rounded away -- it is reported as undetermined and
the precision is doubled.

If every pivot ball is strictly signed, then $(n_{+}, n_{-})$ is **proved, not
observed**, and
$$\text{lambda\_min negative} \iff n_{-} > 0 .$$

### 2.3 The other two anomaly channels

* **$\Im \neq 0$.** For a *real symmetric* matrix the spectrum is real -- a
  theorem, not a numerical reading. v2 therefore verifies symmetry as a
  **side-condition** (mutual containment: $a\texttt{.contains}(b)\ \wedge\
  b\texttt{.contains}(a)$) and reports the anomaly as *structurally excluded*
  rather than pretending an imaginary-part probe is a test. `symmetry_dev = "0"`,
  `symmetry_exact = true` for this target.
* **Radius explosion.** Reported as `max_entry_radius` and `max_pivot_radius`,
  measured, never widened to look good. The gate fires if the maximum entry
  radius exceeds $10^{-50}$.

A *tool* failure is kept distinct from an anomaly: if the symmetry check itself
raises, `sym_ok = None` and the caveat recorded is
`"SYMMETRY NOT VERIFIED -- the Im!=0 question is UNANSWERED for this target,
not exonerated"`. An unanswered question is never printed as a pass.

### 2.4 Auto-escalation

```
attempts = []
cur = prec                                     # default 9000
for attempt in range(1, max_prec_escalations + 2):   # --escalations 3 -> up to 4 attempts
    ctx.prec = cur
    A, DIM = src.build_arb_tau(c, N, cur)
    ...
    res = certified_ldlt_with_L(A, DIM, heartbeat=max(1, DIM // 8))
    ...
    if res["undetermined"] is None:            # certified -> form the bound, return
        ...
    ckpt("  UNDETERMINED pivot at index %d -> escalating precision" % res["undetermined"])
    if attempt > max_prec_escalations:
        break
    cur = int(cur * 2)                         # 9000 -> 18000 -> 36000 -> 72000
```

**Exhausting the escalations yields a non-result, not a verdict.** The branch
records `non_result_reason = "UNDETERMINED after precision escalation to N bits"`
and `non_result = True`. It does **not** hard-code `anomaly: False`; `anomalies`
is re-initialised every attempt and `anomaly` is derived as `bool(anomalies)`,
so a certified negative pivot on any attempt still halts the sweep. This was a
real defect (see §5) and is called out in the source.

### 2.5 The rigorous $\lambda_{\min}$ bound

Independent of the positivity certificate, v2 derives a lower bound from
$A = LDL^{\mathsf T}$:

$$x^{\mathsf T} A x = y^{\mathsf T} D y \;\; (y = L^{\mathsf T}x)
\;\geq\; \min_i(d_i)\,\|y\|^2
\;\geq\; \min_i(d_i)\,\sigma_{\min}(L)^2\,\|x\|^2,$$

$$\sigma_{\min}(L) = \frac{1}{\sigma_{\max}(L^{-1})} \;\geq\; \frac{1}{\|L^{-1}\|_F},
\qquad\Longrightarrow\qquad
\boxed{\;\lambda_{\min}(A) \;\geq\; \frac{\min_i |d_i|}{\|L^{-1}\|_F^{2}}\;}$$

Both factors are enclosed: `min_abs_pivot` uses `abs_lower()` (a *proved* lower
bound on $|d_i|$; on a ball containing 0 it returns 0, so the bound degrades
rather than overclaims), and $\|L^{-1}\|_F$ uses `abs_upper()` on every entry of
`arb_mat.inv()`.

---

## 3. The $N=400$ certificate

Verbatim from `omega_core_v2_results.json` as it stood when this section was
written. **The shipped file now holds the $N=800$ record only** (section 6.6);
the $N=800$ run overwrote it on 2026-10-01, so the block below survives solely
in this certificate and in `omega_core_v2_run.log`:

```json
{
  "c": 100,
  "N": 400,
  "dim": 801,
  "prec": 18000,
  "attempts": [
    {
      "attempt": 1,
      "prec": 9000,
      "build_s": 6191.3,
      "ldlt_s": 1171.8,
      "n_pos": 723,
      "n_neg": 0,
      "undetermined_pivot": 723,
      "max_entry_radius": "2.1547598290585434360e-2577",
      "max_pivot_radius": "6.5054156664262011852e-38"
    },
    {
      "attempt": 2,
      "prec": 18000,
      "build_s": 15939.7,
      "ldlt_s": 3614.3,
      "n_pos": 801,
      "n_neg": 0,
      "undetermined_pivot": null,
      "max_entry_radius": "1.3985514392045226612e-5266",
      "max_pivot_radius": "1.1357906142745494747e-2384"
    }
  ],
  "n_pos": 801,
  "n_neg": 0,
  "undetermined_pivot": null,
  "max_entry_radius": "1.398551439204522661230545e-5266",
  "max_pivot_radius": "1.135790614274549474670140e-2384",
  "symmetry_dev": "0",
  "symmetry_exact": true,
  "lambda_min_lower_bound": "6.74709239897214291717530665950e-509",
  "bound_detail": {
    "min_abs_pivot": "2.014657282505926679349953e-112",
    "pivot_sign": "+",
    "norm_Linv_F_upper": "1.727994119336448038542856e+198"
  },
  "anomalies": [],
  "caveats": [],
  "anomaly": false,
  "non_result": false,
  "peak_mb": 2334.02368,
  "transcript_head": [
    "0 + 4.890674294301233991434966888540561967175 1.398551439e-5266",
    "1 + 4.879171853044798705234270808880393829141 7.057590182e-5267",
    "2 + 0.4001416424901752726827283512353355377121 3.564599480e-5267"
  ],
  "transcript_tail": [
    "798 + 3.292835214788987331069110828543800673987e-29 1.375399638e-2395",
    "799 + 1.327531752515989029937004273896561935248e-26 7.112689651e-2389",
    "800 + 1.638719166685593608248050594068888532525e-26 1.135790614e-2384"
  ],
  "sha256": "a38cb70e53f60ac21a66c23c83ef48fa75e57fbe14a8c9c58251df46856f18bb"
}
```

### 3.1 Reading of the two attempts

| | attempt 1 | attempt 2 |
|---|---:|---:|
| precision | 9000 bits | **18000 bits** |
| `build_arb_tau` | 6191.3 s | 15939.7 s |
| interval $LDL^T$ | 1171.8 s | 3614.3 s |
| $n_+$ | 723 | **801** |
| $n_-$ | 0 | 0 |
| undetermined pivot | **index 723** | none |
| max entry radius | $2.154759\times10^{-2577}$ | $1.398551\times10^{-5266}$ |
| max pivot radius | $6.505415\times10^{-38}$ | $1.135790\times10^{-2384}$ |

Attempt 1 **stopped at pivot 723** because that pivot ball straddled zero. It was
reported as undetermined and escalated; it was *not* rounded to a sign. Attempt 2
at double precision certified all 801 pivots. The $\lambda_{\min}$ bound then took
a further 2425.0 s (`arb_mat.inv()` on $801\times801$).

The escalation is the zero-fudging property made visible in the data: the
engine's first answer was "I do not know", and it cost an extra 15 939.7 s of
build to convert that into knowledge.

### 3.2 Result

$$n_{+} = 801,\quad n_{-} = 0 \quad\Longrightarrow\quad
A \text{ is positive definite, } \lambda_{\min} \;\geq\; 6.74709239897214291717530665950\times10^{-509}$$

`anomalies = []`, `caveats = []`, `symmetry_exact = true`, `non_result = false`,
`peak_mb = 2334.02`.

**Reproducibility anchor.** Attempt 1's `max_entry_radius`
(`2.1547598290585434360e-2577`) is byte-identical to the value recorded by an
earlier, independently terminated run of the same target at the same precision.
The build is deterministic.

---

## 4. Hardware reliability framework (telemetry)

Two independent, **log-and-continue** monitors observe the sweep. Neither can
kill, restart, or modify the process under measurement.

### 4.1 `gw_sysmon.ps1` -- system telemetry, 60 s interval

One line per sample:

```
[<ts>] ram=<MB> commit=<MB> disk=<GB> ac=<0|1> batt=<%> alive=<bool> pid=<n> priv=<MB> cpu=<s> stage=<stage>
```

Emitted as a separate line prefixed `[<ts>] ALERT ` when any of

| ALERT | condition | operator action |
|---|---|---|
| `SWEEP-DEAD` | monitored PID no longer exists | investigate |
| `AC-LOST` | `ACLineStatus != 1` | **highest priority -- restore power** |
| `COMMIT-LOW` | free virtual commit below threshold | let pagefile grow |
| `RAM-LOW` | free physical RAM below threshold | expect thrashing |
| `DISK-LOW` | free disk below threshold | investigate |

The monitor's own counters are *not* alerts: matching on the literal `] ALERT `
(with the leading bracket) is required, or `commitAlert=` self-matches and
produces a false positive.

### 4.2 `gw_watchdog.py` -- liveness, 60 s interval

```
[<ts>] pid=<n> ACTIVE cpu=<s>(+<delta>s) ws=<MB> hb={...}
```

`build_arb_tau` is silent for hours, so **log silence alone cannot distinguish
"still building" from "dead"**. The engine therefore drops a JSON heartbeat on
every stage change:

```json
{ "ts": "...", "pid": 1420, "stage": "build_arb_tau:start", "c": 100, "N": 800, "prec": 9000, "attempt": 1 }
```

A rising `cpu(+delta)` with a frozen `hb.stage` is *healthy*: it means the engine
is deep inside one long call, not wedged. The watchdog reports `ACTIVE` or
`DEAD`; it never acts.

### 4.3 Observed reliability record

**While the sweep ran** (2026-09-29 10:11:49 -> 2026-10-01 21:06): **0 `ALERT`
lines**. `ac=1` (mains present) in all 3329 samples that carry the field, so
`AC-LOST = 0`. At the snapshot moment of 2026-09-29 15:19:49: free physical RAM
9.5 GB, free commit 14.4 GB, CPU delta +52 to +59 s per 60 s sample (one core
saturated, no thrashing), page faults not elevated. Neither
`omega_core_v2_run.log` nor `omega_v2_stdout.txt` contains a single `] ALERT `.

**After it finished**, the log-and-continue monitor kept running and raised
**60 x `ALERT SWEEP-DEAD`**, one per minute, from 2026-10-01 21:07:20 to
22:06:27, every one of them `pid=2356` and every one carrying
`stage=sweep:complete`. That is the expected shape of a monitor that outlives
the process it watches: the engine had already exited cleanly with
`VERIFIED POSITIVE DEFINITE`, and neither monitor may kill or restart anything.
So the honest statement is **0 ALERT during the run, 60 terminal-cycle
`SWEEP-DEAD` after it**, not "0 across the whole log file".

The final telemetry of record:

* `omega_v2_sysmon.log` -- 3332 lines. Three `sysmon start` lines:
  `interval=5s` at 2026-09-29 10:11:49 (three samples 5 s apart), then
  `interval=60s` at 10:13:23, then `interval=60s` again at 2026-09-30 08:37:22
  (the resume after the power cut). Exactly one gap > 120 s exists in the file,
  2026-09-30 03:15:19 -> 08:37:22 = 19 323 s, and it is that power cut. Last
  line 2026-10-01 22:06:27.
* `omega_core_v2_watchdog.log` -- 3929 lines, seven `WATCHDOG start` lines, all
  `interval=60s`, the last two monitoring `pid=2356`. **0 `DEAD`, 0 `ALERT`**
  for its entire life; its final line is
  `last heartbeat: {"stage": "sweep:complete", ...}` at 2026-10-01 21:07:15.
* `omega_v2_pid.txt` = `2356` (the certified run); `omega_v2_stderr.txt` = 0 B
  (no stderr was ever written); `wd_selftest.log` = the 2026-09-28 self-test of
  the watchdog's own polling loop.

Two self-inflicted false alarms are recorded here because they were *our* bugs,
not the system's:

1. `Select-String "ALERT"` matched `commitAlert=` -- the correct pattern is `"\] ALERT "`.
2. A process search matched its own shell -- fixed by excluding the parent
   (harness) PID and accepting `svchost` as a legitimate parent.

### 4.4 Why the engine owns its own log file

`ckpt()` prints **and** appends to a file the Python process itself holds open.
The preceding run wrote only through a PowerShell `Tee-Object` pipe; when the
harness dropped the shell record, the pipe died with it, Python's stdout broke,
and **zero recoverable evidence was left**. A file the process owns cannot be
taken away by the harness.

---

## 5. Defects found and fixed before this certificate was trusted

Five defects were found by executing the engine, not by inspection:

1. **Missing `.abs()`** in a python-flint call -- raised after a completed
   multi-hour build and destroyed it. Fixed; the failed run is archived as
   `*_FAILED_absbug_*` rather than deleted.
2. **Symmetry test mathematically wrong.** It compared `A[i,j] == A[j,i]`, but on
   a ball $x - x = [0 \pm 2r]$ is never empty, so a *perfectly symmetric* matrix
   would have produced a false `ASYMMETRIC` signal. Replaced by mutual
   containment. Had it gone unnoticed it would have manufactured a false
   falsification.
3. **`Lf[i][i]` diagonal** left at zero when materialising $L$, which made
   `arb_mat.inv()` report "matrix is singular" and cost the whole
   $\lambda_{\min}$ bound.
4. **`anomaly` hard-coded `False`** in the escalation-exhausted branch, with
   `anomalies` overwritten by the undetermined message. A certified negative
   pivot preceding an undetermined one would have been **silently swallowed** --
   the worst failure mode a falsification engine can have. Fixed: `anomalies` is
   re-initialised each attempt and `anomaly = bool(anomalies)`; `undetermined`
   is reported separately via `non_result_reason`.
5. **Missing `non_result` key** in the certified branch of the result schema.

Both smoke paths pass after the fixes: the certified path
(`N=20 / 9000 bits`, $n_{+}=41$) and the escalation-exhausted path
(`N=20 / 200 -> 400 bits`). Their logs are shipped in this repository.

### 5.1 API facts measured on python-flint 0.9.0

Established by execution, because they are not obvious from the documentation:

* there is **no** `.abs()` on the ball type used here; `abs_lower()` /
  `abs_upper()` are the rigorous primitives;
* `==` and `!=` both return `False` **even for a ball compared with itself**
  when the radius is nonzero -- hence mutual containment instead of equality;
* `.contains()`, `.upper()`, `.lower()`, `.sqrt()`, `.str(n, radius=False)`,
  `arb_mat.inv()` behave as expected, with `inv()` requiring a unit diagonal.

---

## 6. Ship inventory

Snapshot 2026-09-29 15:19:49 was the original archival cut, taken while the
$N=800$ sweep was still running. The sweep completed on 2026-10-01 21:06;
section 6.6 carries its final bytes, section 6.3 the final telemetry, and the
status table in section 7 is final.

### 6.1 Engine and instrumentation

| file | bytes | SHA-256 |
|---|---:|---|
| `gw_omega_core_v2.py` | 34145 | `823de907bb53c42ae297a06a5f4549c48655e6fec87efea8c7a52eadbd98fb85` |
| `source_arb_ldlt_certify.py` | 12863 | `33617ce64b0e052c07873b196a3744f2f5142a4aaf7b4cfbe9e3de43d17c27bb` |
| `gw_sysmon.ps1` | 5048 | `bd93a6c2f8ecee9ac8f5b630a82cb5b6ae0d0e1f3993e0ae18594cc3779e1f2e` |
| `gw_watchdog.py` | 5398 | `670b582ca18c1673cabd86d8cb4e47e57ce76c7d2aeec7cd697cec689a832d11` |
| `gw_launch_v2.ps1` | 3477 | `c043e6a47e13379bccb95072ba0cfcb506eb3d677404f03b847bf26daf258073` |
| `gw_ckpt.py` | 8629 | `07fe8d710d00637d7d55460cd56af0ac852ad6e04c483fe1a04d31f691d046f0` |
| `gw_check_refs.py` | 1985 | `7edca0a3c4ce7981cf6e2a62e84339285eaae956ff3a151d011613e1c02d7bb3` |
| `gw_verify_results.py` | 6343 | `46b386b5a215868bbe690a268fe5ce023c3343ab3fc27ccc31ed19c39bc7f2b1` |
| `gw_verify_production.py` | 15279 | `e1c3e0caacb43bfb823abf3c8d00e2c4199dbb11fce34e3de70edd4d041da03c` |

Provenance of these rows:

* `gw_omega_core_v2.py`, `source_arb_ldlt_certify.py`, `gw_ckpt.py`,
  `gw_sysmon.ps1`, `gw_watchdog.py` are byte-identical to the versions that
  ran the certified $N=800$ sweep (the engine grew on 2026-09-30:
  checkpoint/resume + heartbeat telemetry).
* `gw_launch_v2.ps1`: the executed argument list is unchanged; a
  **comment-only** edit on 2026-10-01 replaced a cited archive reference
  (`a38cb70e...f18bb`) that exists nowhere -- not on the remote (404), not in
  local history -- with the commit that verifiably holds the $N=400$ record
  (`e65319d`, blob `30ca1467`, file sha256 `5aaab0cf...a4f2` = section 6.2).
* `gw_check_refs.py`, `gw_verify_results.py`, `gw_verify_production.py` were
  made clone-portable on 2026-10-01: defaults resolve relative to each
  script's own directory instead of `C:\Users\...` (overrides: `argv[1]` /
  `GW_FIXTURE_DIR`). Baseline runs before the edit and reruns after it both
  PASS with exit 0 on the same fixtures; the checks performed are unchanged.
  Rationale and disclosure: PROVENANCE.txt section 6.9.
* `gw_verify_production.py` (added 2026-10-01) parses numbers with `mpmath`
  because float64 underflows a $10^{-2877}$ bound to `0.0`.
* `gw_verify_results.py` and `gw_verify_production.py` were edited again on
  2026-10-04 by the F1 audit (F1-Q), so the two rows above now carry their
  post-F1 bytes and the sentence “the checks performed are unchanged” in
  the clone-portable bullet no longer holds. What changed: the fixture read
  and row index are guarded, a missing required key is recorded and skipped
  instead of raising `KeyError`, and the `sha256` test now actually matches
  64 hex characters — 64 non-hex characters reached exit 0 before F1, while
  the message already promised a hex digest. No decision on valid data
  changed: both gates still pass the same fixtures with exit 0, and fault
  injection now reports 14/14 caught by each. Rationale: F1_REPORT.md F1-Q.
  Superseded hashes: `gw_verify_results.py` 4871 / `78ffe1140c6942b4...`,
  `gw_verify_production.py` 3248 / `35ec5d33bc3cca16c...`.
* `gw_verify_production.py` was extended again on 2026-10-05 by the F2-7
  phase, at which point the $N=400$ rerun completed. It now accepts the
  $N=400$ result as `argv[2]` (default: `omega_core_v2_results_N400.json`
  next to the script), applies the certified-row invariants to that row as
  well -- `c == 100`, `N == 400`, `dim == 2N+1`, `n_neg == 0`,
  `undetermined_pivot` null, empty `anomalies` and `caveats`, `anomaly`
  false, `non_result` false -- and on every run reproduces all three
  documentary records of the $N=400$ bound from their own files:
  `PROVENANCE.txt` section 6.2, this file's section 4, and
  `omega_core_v2_run.log` line 51. Each record is compared at its own
  significant-digit count (25 digits for the log, 30 for the other two)
  with a relative tolerance of 1e-20, so a one-digit drift in any of them
  fails the gate. For the whole of 2026-10-01 to 2026-10-05 the gate
  reported the $N=400$ file as absent and exited 1, because the rerun had
  not finished; it exits 0 only now that the artefact exists. Fault
  injection: 26/26 mutants caught, 4/4 missing-document cases reported as
  FAILURES without a traceback, and every case left both shipped result
  files byte-identical. Rationale: F2_REPORT.md section 7.
  Superseded hash: `gw_verify_production.py` 8234 /
  `80f6fbf73c451b4b7...`.
* `gw_even_vs_src.py` and `gw_opt_a_diff.py` (edited 2026-10-02): their
  source-hash lines were reconciled with the 2026-09-30 edit of
  `source_arb_ldlt_certify.py` described in section 1. `gw_even_vs_src.py` now
  pins **both** copies and fails on any third value; `gw_opt_a_diff.py` prints
  the hash it actually loaded instead of asserting one in a header comment.
  The baseline log `gw_even_vs_src_100_200.log` (2026-09-27, `MATCH --
  byte-identical`) is kept unedited, and the rerun
  `gw_even_vs_src_100_200_rerun_20261002.log` (exit 0, 339 s) reproduces the
  same $\delta$, $\delta_{\rm rel}$, median ratio and `V1` verdict -- only
  wall-clock times differ. Disclosure: THIRD_PARTY_SOURCES.md section 1,
  PROVENANCE.txt section 6.10.

`gw_check_refs.py` (static reference check) and `gw_verify_results.py` (JSON
invariant check) are mandatory pre-run gates for any large sweep.

### 6.2 Evidence for $N=400$

| file | bytes | SHA-256 |
|---|---:|---|
| `omega_core_v2_results.json` | 1971 | `5aaab0cfbf26f7fc5a3306bcd6a6e82e5482dad54a0a08d55ed4ebdcf22aa4f2` |
| `omega_core_v2_run.log` | 3337 | `c4714253f841d3f16b5ce60c6f8382e9e1c823c63cf9bc0472ed94d5a278756b` |
| `omega_core_v2_heartbeat.json` | 146 | `3181f896b13e7411c677042e935ab5e8aa415aa93b6143cd80bdadd377385c68` |

`omega_core_v2_run.log` was verified **byte-identical** to the source process's
own log at snapshot time (`C4714253...8756B` on both sides).

These are the $N=400$ bytes; the working-tree file of the same name now holds
the $N=800$ record (section 6.6). The $N=400$ record remains in this
repository's git history — which cannot be inspected from a copy without
`.git`, so that sentence is **not verifiable in this workspace** (F1-D).

F1 also established that the working-tree `omega_core_v2_run.log` (7177
bytes, section 6.6) is **two appended runs**, not one: header #1 at line 2
with `dims=[400,800]` and its verdict at line 54, header #2 at line 76 with
`dims=[800]` and its verdict at line 116. Run 2 overwrote
`omega_core_v2_results.json`, which is why no two-row result file exists
and why $\lambda_{\min}$ at $N=400$ is **log-recorded only**, not
machine-gated. See F1_REPORT.md F1-D.

### 6.3 Telemetry (final, 2026-10-01)

| file | bytes | SHA-256 |
|---|---:|---|
| `omega_v2_sysmon.log` | 526181 | `95a4df23e50430e4e315b5cda08531b687dbdcf4e7d934c5e7d3db42910ef50a` |
| `omega_core_v2_watchdog.log` | 593637 | `11526d8c1f5ff561954f869b482e9f4895ec455529ce68bde99c169090b4d440` |
| `omega_v2_pid.txt` | 6 | `28f7be901cd616d7eae24710c5d2bf41a966eb0b657de3457a7996d4b2a267b7` |
| `omega_v2_stderr.txt` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `wd_selftest.log` | 797 | `2833afef57d2631e4569e77dffca8854584512e396686a1ca03332c4eb6f2780` |

Final bytes: both monitors were stopped after the sweep exited (2026-10-01,
22:12 local). They supersede the 2026-09-29 snapshot values (48,685 and
145,997 bytes), which were taken mid-run.

`omega_v2_pid.txt` holds the certified run's PID (`2356`); the empty
`omega_v2_stderr.txt` (0 bytes, SHA-256 of the empty string) is itself the
evidence that no error was ever written; `wd_selftest.log` is the watchdog's
own polling self-test of 2026-09-28, not a sweep log.

### 6.4 Failed run, kept as audit trail

| file | bytes | SHA-256 |
|---|---:|---|
| `omega_core_v2_run_FAILED_absbug_20260929_011309.log` | 3312 | `bc88f1c03d016a1249e2906c794c07141665957d5699bd500919a407c80d2671` |
| `omega_core_v2_results_FAILED_absbug_20260929_011342.json` | 180 | `ecba9166c19aca9ba10a3bbdb4d2330665ad7e92acc78a9179467bcfab9ed789` |
| `omega_v2_stderr_FAILED_absbug_20260929_011342.txt` | 756 | `56b3b3d9c2e1f4e74f79b413bb111c01dc305b123afe1fae9750ecfffb8550ba` |
| `omega_v2_stdout_FAILED_absbug_20260929_011342.txt` | 2055 | `a56284ea4dad3f166fde36b54aa353eea9726fe8a2bb554c955d31dfeaef7506` |
| `omega_core_v2_heartbeat_DEAD_20260929_011342.json` | 147 | `8de9c502d933db12a0609b90d6701d1d3bf93b960594e48aa7b7db04ebbdd6a8` |

### 6.5 Smoke tests (both gates green)

| file | bytes | SHA-256 |
|---|---:|---|
| `smoke.log` | 11674 | `14450c1694b2d56db4d8b1580c32e0700aa03c5423db11fea14f0a769bbff798` |
| `smoke_escalate.log` | 9798 | `c5d4a7eccc3936dad3d1d06ffb3863e15a382a87c8ba09604f85b1b5b7e83aeb` |
| `smoke_results.json` | 1633 | `d67b9065b78de1c55b440605b299e386eccdf49d1b4181ead1ea831ca0b00959` |
| `smoke_escalate.json` | 1326 | `423f2e2a9907bc9d872742979d330c365f9cec1d39e9653e93c6d4c4e1543d37` |
| `smoke_hb.json` | 99 | `51cf93e2035142d4485a160186e39fdab00d31d897bdebcff15e8a3b02007224` |
| `smoke_escalate_hb.json` | 98 | `eebdaf0a9734268075e305ce6c1649e4b35ee4810a9a9b1ff21667a95a069990` |

### 6.6 Evidence for $N=800$ (completed 2026-10-01 21:06)

Executed argument list: `--c 100 --dims 800 --prec 18000 --escalations 0
--ckpt D:\gw_ckpt` (attempt 1, resumed rows 0). Phase wall times: build
85,213.3 s, certified $LDL^T$ 38,024.0 s, $\lambda_{\min}$ bound 10,354.0 s;
peak 8,251.7 MB.

| file | bytes | SHA-256 |
|---|---:|---|
| `omega_core_v2_results.json` | 1774 | `20ff0378bf72065c75ee8af2e873350d0dcd6801e6384db86eb14d7594119cbc` |
| `omega_v2_stdout.txt` | 3178 | `6f4674bcb7b3c38429cac63bd61b13bf0527780b393d9036ee586c1cbd546b60` |
| `omega_core_v2_run.log` | 7177 | `7c402ca84eb8566f989e65e9ff484cb3d722e4089b2b73240bbe070a4c926ef3` |
| `omega_core_v2_heartbeat.json` | 98 | `c63a0a4d0f10ec2429800c782790ec589693ad8f2cea7ce2c506fa2e58eb97da` |
| `gw_verify_production.py` | 3248 | `35ec5d33bc3cca16c71db98829669b04a04b6d19a73df45d9aaf870f3d5ec2d6` |

The `gw_verify_production.py` row above is deliberately the **2026-10-01
bytes** — the version that ran this gate — and is therefore expected not to
match the working tree. Its current bytes are inventoried in section 6.1;
the reason it changed is recorded there and in F1_REPORT.md.

Measured values, read from `omega_core_v2_results.json` (not recomputed):

* $n_+ = 1601$, $n_- = 0$, undetermined = none -- 1601/1601 certified;
* symmetry exact: mutual-containment deviation `0`, so the spectrum is
  provably real;
* max entry radius `6.053441192729382583443955e-5144`, max pivot radius
  `7.424122759961235085328413e-803`;
* $\min|d_i| = 2.317588938960509279827277e-120$ (pivot sign $+$),
  $\|L^{-1}\|_F \le 1.634469911529859879792978e+1378$, hence
  $\lambda_{\min} \ge 8.67526098867855342892890992571e-2877$
  (the division $2.3176e{-}120 / (1.6345e{+}1378)^2$ checks by hand);
* verdict **VERIFIED POSITIVE DEFINITE** ($n_+=1601$, $n_-=0$, 1601/1601
  certified); `anomalies` empty, `caveats` empty;
* internal record id `e42dad4b16dfe5a9e3e886b8f7ec77f1e5b982730b98a867583aaa1ffd2babb7`
  (the `sha256` field inside the JSON);
* gates: `gw_verify_results.py` PASS (fixtures) and `gw_verify_production.py`
  PASS (production row), both exit 0. The production gate's first run failed
  on float64 underflow of the $10^{-2877}$ bound -- a defect in the check,
  not in the result -- and was fixed to parse with `mpmath`.

**Full run history, as preserved inside `omega_core_v2_run.log` (the log is
appended to, never edited, so all three phases of this target sit in one
file):**

1. *First $N=800$ attempt, 9000 bits* (lines 61-72): build 33,497.2 s,
   $n_{+}=1087$, **`undetermined_pivot=1087`** -> `UNDETERMINED pivot at index
   1087 -> escalating precision`. That is a **non-result**, recorded as one;
   it is the reason the successful run below is at 18000 bits.
2. *Second attempt, 18000 bits* (lines 74-79): header written
   (`start_prec=18000  escalations=0  checkpoint: D:\gw_ckpt`) and then **nothing
   -- the machine lost power on 2026-09-30 03:15:19**. No number from this
   attempt is claimed anywhere.
3. *Relaunch* (lines 93-116): `attempt 1` of a fresh process at 18000 bits,
   resumed from the checkpoint (build `rows recorded, 2.92 GB on disk`;
   LDLT `2.41 GB on disk`), which produced the verdict quoted above.

**Checkpoint corroboration.** The checkpoint directory `D:\gw_ckpt` (deliberately
not shipped -- 5.3 GB) still holds `build.ckpt` (2,916,757,855 bytes,
2026-10-01 07:35:38), `build.ckpt.time` = `85213.334`, `ldlt.ckpt`
(2,407,358,576 bytes, 2026-10-01 18:11:21) and `ldlt.ckpt.time` = `38023.975`.
Those two times are **identical, to the digit, with the phase wall times this
certificate reports** (85,213.3 s build, 38,024.0 s certified $LDL^T$), and the
byte sizes match the 2.92 GB / 2.41 GB printed in the log -- independent
evidence that the reported timings were not typed in.

---

### 6.7 Track C -- the derived layer, machine-checked (2026-10-02)

Everything above describes numbers produced by ball arithmetic. Track C is the
*separate*, post-hoc check of what can be said once those numbers are taken as
**inputs**: the rational/algebraic side conditions behind the
$\lambda_{\min}$ and tolerance bounds, formalised in Lean 4 and discharged again
by an SMT solver.

| file | bytes | SHA-256 |
|---|---:|---|
| `OMEGATrackC.lean` | 16382 | `a5773617d02dc257844dbe1ffac6af08a2ed9c01c8f1968afefe8ef33940a646` |
| `track_c_make_smt.py` | 12714 | `33b4f22e4a09f04c595907ae3c1a2a39245bd6b210a5701b89ad1c406c96775c` |
| `track_c_side_conditions.smt2` | 1532 | `99d485c42feeb6b33e77fbab4fb3b55a1208379dd9f6e52246cf5a412b85aa96` |
| `track_c_lean_verify.log` | 2380 | `68f56e01ba0861cebaaa37a4f2e690124f7f818df9168ea72eb16c385426268a` |
| `track_c_smt_z3.log` | 1383 | `454b49faf30c0aace06b1266992a7eb7ab2e0398d64533cb2fc408d2e6036038` |

> **Superseded build (2026-10-02, recorded, not erased).** Before the
> 2026-10-04 F0 audit these five hashes were, respectively,
> `8894d24b…fea95` / 13837, `42ac3122…00933` / 12714,
> `77456c16…3ee40` / 1533, `46d4b109…8f3b79` / 1810,
> `366c16b1…777da` / 1383. The earlier `OMEGATrackC.lean` built with
> `exit=0` and the same axiom footprint; it is superseded because four of its
> docstrings stated things that are false (see `F0_REPORT.md`), one of which
> (`implied_constant_gt_81`) was a strict inequality holding only by the
> binary64 rounding of `rhoStar`. No numeric literal changed: `lambdaMin`,
> `rhoActual` and `rhoStar` are byte-for-byte the same rationals, and the
> three-way literal cross-check still reports `MATCH` on all 3.

Results, read from those two logs (both `RESULT: PASS`):

* **Lean 4.33.1** (`track_c_lean_verify.log`): the *shipped* `OMEGATrackC.lean`
  was staged byte-identically (`source == stage: IDENTICAL`, sha
  `A5773617...40A646`) and built with `exit=0` in 11.5 s. `#print axioms` on all
  **10/10** theorems returns exactly `[propext, Classical.choice, Quot.sound]`;
  **0 `sorryAx`** / error lines.
* **z3 4.16.0** (`track_c_smt_z3.log`): the three constants used by the
  module (`lambdaMin`, `rhoActual`, `rhoStar`) are cross-checked against their
  values in `README.md` and are `MATCH` on all 3; each of the **7** side
  conditions negated is `UNSAT`, and so is their combined conjunction.
* `track_c_make_smt.py` itself is the generator of both artifacts and is
  included so the `.smt2` file can be re-derived rather than trusted.

**Boundary of Track C.** It checks the *chain of inequalities*, not the sweep.
The constants are read from the certified output; no Arb matrix is rebuilt, no
$LDL^T$ is re-run, and Lean/Z3 never see the numbers as exact reals -- they see
them as literals that must satisfy the stated relations. Track C therefore
cannot certify $n_{+}$ or $n_{-}$; sections 1-6.6 still carry that claim.

---

## 7. Status of the sweep

| target | status |
|---|---|
| $(c,N)=(100,400)$ | **CERTIFIED** -- positive definite, bound above |
| $(c,N)=(100,800)$ | **CERTIFIED** (2026-10-01) -- positive definite, 1601/1601 certified, symmetry exact, bound in section 6.6 |

Both targets carry results and verdicts and are counted toward the claims in
this document. A target without a result is reported without one: the
earlier snapshot recorded $(100,800)$ as in progress, and in progress was
reported as in progress -- never as certified. An undetermined pivot is a
non-result; it is never rounded to a sign.

---

## 8. Reproduction

```powershell
# static reference gate + smoke tests (mandatory before any large run)
python gw_check_refs.py
python gw_omega_core_v2.py --c 100 --dims 20 --prec 9000 --out smoke_results.json
python gw_verify_results.py smoke_results.json

# WARNING: both certified targets write omega_core_v2_results.json by default.
# Running either line below WITHOUT --out overwrites whichever record is
# already there. That is exactly how the 1971-byte N=400 record was lost to
# the N=800 run on 2026-10-01, leaving lambda_min at N=400 with three written
# records and no machine-readable artefact (F1_REPORT.md F1-D). Always pass
# --out, and pass it to the N=800 line too if you do not mean to replace the
# shipped record in section 6.6.
#
# F2-7 regenerates the N=400 target into its own file. gw_verify_production.py
# now requires both result files and cross-checks the N=400 bound against
# PROVENANCE.txt section 6.2, section 4 of this file, and
# omega_core_v2_run.log line 51, each at that record's own precision.
python gw_omega_core_v2.py --c 100 --dims 400 --prec 9000 --escalations 3 \
    --out omega_core_v2_results_N400.json \
    --log omega_core_v2_run_N400.log \
    --heartbeat omega_core_v2_heartbeat_N400.json --ckpt ckpt_N400

# the certified N=800 target exactly as executed 2026-09-30 -> 2026-10-01
# (same argument list as gw_launch_v2.ps1)
python gw_omega_core_v2.py --c 100 --dims 800 --prec 18000 --escalations 0 \
    --ckpt D:\gw_ckpt --log omega_core_v2_run.log \
    --heartbeat omega_core_v2_heartbeat.json --out omega_core_v2_results.json

# production invariant gate (mandatory after any engine result)
python gw_verify_production.py

# Track C (section 6.7) -- re-derives the side-condition SMT file from this
# README and the shipped Lean file, then drives z3; must print RESULT: PASS
python track_c_make_smt.py

# Track C Lean build: stage the shipped file byte-identically, then
# lean -o <stage>/OMEGATrackC.olean <stage>/OMEGATrackC.lean   (must be exit 0)
# full transcript of the run of record: track_c_lean_verify.log
```

Notes: `source_arb_ldlt_certify.py` must be importable from its own directory.
Line 47 of `gw_qinf.py` sets `mp.mp.dps = 40` at module import time, and
`python-flint` uses `flint.ctx.prec`; do not conflate the two. `D:\gw_ckpt` is
the resume state of the certified run and is deliberately not shipped (5.3 GB);
deleting it costs nothing for verification, only for a resumed sweep.

---

*Generated for archival by the OMEGA-CORE session of 2026-09-29; the status
table, sections 6.1, 6.3, 6.6 and the $N=800$ reproduction line were updated
2026-10-01 after the sweep completed. Updated again 2026-10-02: header and
scope extended to both certified targets, tool status narrowed to what was
actually run (Lean/z3 for Track C only), section 6.7 added, the two source-package
SHA-256 values reconciled in section 1, the attempt-1 max-entry-radius typo
corrected to $2.154759$, section 4.3 rewritten from the final telemetry
(0 ALERT during the run, 60 post-completion `SWEEP-DEAD`), the full three-phase
$N=800$ run history and the `D:\gw_ckpt` timing corroboration added to 6.6,
and the overwrite hazard spelled out in section 8. Every number above was read
from an executed run's output files; none was recomputed, rounded, or estimated
for this document.*
