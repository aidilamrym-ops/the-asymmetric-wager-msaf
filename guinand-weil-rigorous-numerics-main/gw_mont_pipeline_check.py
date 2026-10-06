# -*- coding: utf-8 -*-
"""Validate the OPSI (d) pipeline on SYNTHETIC spectra of KNOWN class BEFORE
the pipeline is pointed at the real Guinand-Weil spectrum.

WHY THIS EXISTS
---------------
If the instrument cannot tell a Poisson spectrum from an RMT spectrum at
N = 401, then whatever it says about the real matrix is worthless. Running
this check FIRST -- before gw_montgomery.py ever sees real data -- is what
keeps the thresholds from being calibrated on the answer.

PRE-REGISTERED CHECK EXPECTATIONS (written before running)
----------------------------------------------------------
  K1  Poisson fixture: S1 must NOT classify as "CONSISTENT WITH RMT".
      (A spectrum with no level repulsion must not be reported as RMT-like.)
  K2  GUE fixture: S1 must NOT classify as "CONSISTENT WITH POISSON".
  K3  GOE fixture: S1 must NOT classify as "CONSISTENT WITH POISSON".
  K4  every fixture must produce BOTH an S1 FINAL and an S2 FINAL line, i.e.
      the pipeline must run to completion on both charts without crashing.
  K5  the GUE fixture's S2 on chart L must not be "INCONSISTENT WITH
      MONTGOMERY AT THIS RESOLUTION". (A true GUE spectrum that the pipeline
      rejects means the estimator or the binning is wrong.) A single fixture
      is one draw, so a borderline result is reported as WARN, not silently
      dropped.

HONEST LIMIT OF THIS CHECK
--------------------------
Fixtures are shifted to be strictly positive so that chart T = ln(x) is
defined. A shift leaves chart-L statistics EXACTLY invariant (gaps and the
Gaussian unfolding depend only on differences), so chart L is a genuine
statistical validation. Chart T of a shifted spectrum is NOT GUE -- chart T is
exercised here only as a code path, and its verdicts are reported but not
counted toward K1..K3, K5.

usage:
    python gw_mont_pipeline_check.py
    python gw_mont_pipeline_check.py --samples 400
"""

import json
import math
import os
import subprocess
import sys
import tempfile
import time

import numpy as np

# Directory this checker lives in; every child script is resolved against it
# so the result does not depend on the caller's working directory.
HERE = os.path.dirname(os.path.abspath(__file__))

N_LEV = 401
SEED = 20260927


def ckpt(msg):
    print(msg, flush=True)


def make_spectrum(kind, rng):
    if kind == "poisson":
        e = np.sort(rng.uniform(0.0, N_LEV, N_LEV))
    elif kind == "goe":
        A = rng.standard_normal((N_LEV, N_LEV))
        M = (A + A.T) / math.sqrt(2.0 * N_LEV)
        e = np.linalg.eigvalsh(M)
    else:
        A = rng.standard_normal((N_LEV, N_LEV))
        B = rng.standard_normal((N_LEV, N_LEV))
        H = (A + 1j * B) / math.sqrt(2.0 * N_LEV)
        H = (H + H.conj().T) / 2.0
        e = np.linalg.eigvalsh(H)
    e = np.sort(e)
    # shift to strictly positive so chart T = ln(x) is defined (see docstring)
    return e - e.min() + abs(e.min()) * 1e-3 + 1e-3


def write_fixture(path, kind, lam):
    payload = {
        "c": 0, "N": 200, "dps": 400, "prec": 2048,
        "algo": "SYNTHETIC-%s" % kind.upper(),
        "n": int(lam.size),
        "eig_seconds": 0.0,
        "gate_GM0": {"G-M0a_finite": True, "G-M0b_inertia": True,
                     "G-M0c_strict": True, "G-M0d_trace": True,
                     "G-M0e_frob": True},
        "gate_verdict": "G-M0 PASS (SYNTHETIC FIXTURE -- not a real matrix)",
        "inertia": {"n_pos": int(lam.size), "n_neg": 0, "indeterminate": 0},
        "im_max_float": 0.0,
        "trace_mid": repr(float(lam.sum())),
        "frob2_mid": repr(float((lam ** 2).sum())),
        "eig": [{"re": repr(float(v)), "re_rad": "0", "im_abs": "0"}
                for v in lam],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)


def run_pipeline(path, samples):
    # Anchor the child script to this file's own directory.  Before F1 the
    # name was bare, so running this checker from any other working directory
    # made every fixture fail with "gw_montgomery.py: No such file or
    # directory" and the report then read "PROBLEMS = K1..K6 -- do NOT run the
    # real analysis": a false alarm that looked like a scientific failure.
    target = os.path.join(HERE, "gw_montgomery.py")
    if not os.path.isfile(target):
        raise SystemExit("FATAL: cannot find the child script %r" % target)
    cmd = [sys.executable, target, path, "--samples", str(samples)]
    ckpt("  $ %s" % " ".join(cmd))
    t = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=HERE,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    ckpt("  exit=%d  %.1f s" % (p.returncode, time.time() - t))
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode != 0:
        ckpt("  --- tail of output ---")
        for line in out.splitlines()[-25:]:
            ckpt("    " + line)
    return p.returncode, out


def grab(out, key):
    for line in out.splitlines():
        if key in line:
            return line.strip()
    return "(missing)"


def grab_s1_chart(out, token):
    """S1 line for one chart: 'S1 chart <name> r_bar = ... -> <verdict>'."""
    for line in out.splitlines():
        if "S1 chart" in line and token in line and "->" in line:
            return line.split("->", 1)[1].strip()
    return "(missing)"


def grab_s2_chart(out, token):
    """S2 verdict for one chart.

    The grid prints four lines per point (numbers, p_GUE, p_GOE, p_Pois) and
    the verdict '-> ...' last. Scan a few lines ahead rather than assuming the
    verdict is on the immediately following line -- that assumption broke K5
    after the print format was widened (defect 14: a parser bug in THIS check
    script, not in gw_montgomery).
    """
    lines = out.splitlines()
    for k, line in enumerate(lines):
        if "sigma_u" in line and "chi2" in line and token in line:
            for nxt in lines[k + 1:k + 7]:
                if "->" in nxt:
                    return nxt.split("->", 1)[1].strip()
    return "(missing)"


def grab_chi2_grid(out, token):
    """chi^2 for one chart across the sigma_u grid, in print order.

    Regression guard for defect 15: sigma_u was accepted as a parameter but
    never applied to the unfolding bandwidth, so all three grid points came out
    BIT-IDENTICAL (816.3241 / 816.3241 / 816.3241) and the pre-registered
    6-point stability test was vacuous rather than passed. K1..K5 could not see
    it -- every fixture agreed trivially -- so this K6 exists specifically to
    notice a collapsed grid. Added AFTER defect 15 was found; it changes no
    K1..K5 criterion and no real-data threshold.
    """
    vals = []
    for line in out.splitlines():
        if "sigma_u" in line and "chi2" in line and token in line:
            try:
                vals.append(float(line.rsplit("=", 1)[1].strip()))
            except (ValueError, IndexError):
                pass
    return vals


def main(argv):
    samples = 400
    if "--samples" in argv:
        samples = int(argv[argv.index("--samples") + 1])

    ckpt("#" * 96)
    ckpt("# OPSI (d) PIPELINE CHECK -- synthetic spectra of known class")
    ckpt("# run BEFORE gw_montgomery.py is pointed at the real matrix")
    ckpt("# N = %d, samples = %d, seed = %d" % (N_LEV, samples, SEED))
    ckpt("#" * 96)
    ckpt("")
    ckpt("PRE-REGISTERED CHECK EXPECTATIONS:")
    ckpt("  K1  Poisson fixture  -> S1 must NOT be 'CONSISTENT WITH RMT'")
    ckpt("  K2  GUE fixture      -> S1 must NOT be 'CONSISTENT WITH POISSON'")
    ckpt("  K3  GOE fixture      -> S1 must NOT be 'CONSISTENT WITH POISSON'")
    ckpt("  K4  every fixture    -> both S1 FINAL and S2 FINAL present")
    ckpt("  K5  GUE fixture, chart L, S2 must NOT be 'INCONSISTENT WITH MONTGOMERY'")
    ckpt("  K6  sigma_u grid must ACTUALLY VARY: the 3 chi2 of any chart of any")
    ckpt("      fixture must not be bit-identical (defect 15 regression guard;")
    ckpt("      added after that defect was found -- K1..K5 unchanged)")
    ckpt("  (chart T of a shifted spectrum is a CODE PATH check only -- its")
    ckpt("   verdicts are printed but do not count toward K1..K3, K5)")
    ckpt("")

    rng = np.random.default_rng(SEED)
    tmp = tempfile.gettempdir()
    outcomes = {}
    fails = []
    for kind in ("poisson", "gue", "goe"):
        ckpt("=" * 96)
        ckpt("FIXTURE %s" % kind.upper())
        ckpt("=" * 96)
        lam = make_spectrum(kind, rng)
        path = os.path.join(tmp, "gw_mont_fixture_%s.json" % kind)
        write_fixture(path, kind, lam)
        ckpt("  wrote %s  (levels %d, min %.6g, max %.6g)"
             % (path, lam.size, lam.min(), lam.max()))
        rc, out = run_pipeline(path, samples)
        s1 = grab(out, "S1 FINAL")
        s2 = grab(out, "S2 FINAL")
        # chart L is the fixture's NATIVE chart: a constant shift leaves gaps
        # and the Gaussian unfolding exactly invariant, so chart-L statistics
        # of these fixtures are the ensemble's true statistics.
        s1_L = grab_s1_chart(out, "L (lambda")
        s1_T = grab_s1_chart(out, "T (ln lambda")
        s2_L = grab_s2_chart(out, "L (lambda")
        s2_T = grab_s2_chart(out, "T (ln lambda")
        ckpt("  S1 FINAL   : %s" % s1)
        ckpt("  S2 FINAL   : %s" % s2)
        ckpt("  S1 chart L : %s   <- native chart, counts toward K1/K2/K3" % s1_L)
        ckpt("  S1 chart T : %s   <- code path only (log of a shifted spectrum)" % s1_T)
        ckpt("  S2 chart L : %s" % s2_L)
        ckpt("  S2 chart T : %s" % s2_T)
        outcomes[kind] = {"rc": rc, "s1": s1, "s2": s2, "out": out,
                          "s1_L": s1_L, "s1_T": s1_T, "s2_L": s2_L, "s2_T": s2_T}
        ckpt("")

    ckpt("#" * 96)
    ckpt("# PIPELINE CHECK -- RESULT vs PRE-REGISTERED K1..K6")
    ckpt("#" * 96)
    for k, label in (("poisson", "K1"), ("gue", "K2"), ("goe", "K3")):
        s1 = outcomes[k]["s1_L"]
        if label == "K1":
            ok = ("CONSISTENT WITH RMT" not in s1) and ("missing" not in s1)
        else:
            ok = ("CONSISTENT WITH POISSON" not in s1) and ("missing" not in s1)
        ckpt("  %s  %-8s %s   [chart L: %s]" % (label, k, "PASS" if ok else "FAIL", s1))
        if not ok:
            fails.append(label)
    for k, label in (("poisson", "K4a"), ("gue", "K4b"), ("goe", "K4c")):
        ok = ("missing" not in outcomes[k]["s1"]) and ("missing" not in outcomes[k]["s2"])
        ckpt("  %s  %-8s %s   [S1 FINAL present=%s, S2 FINAL present=%s]" % (
            label, k, "PASS" if ok else "FAIL",
            "missing" not in outcomes[k]["s1"], "missing" not in outcomes[k]["s2"]))
        if not ok:
            fails.append(label)
    gue_l2 = outcomes["gue"]["s2_L"]
    k5_ok = gue_l2 != "(missing)" and "INCONSISTENT WITH MONTGOMERY" not in gue_l2
    ckpt("  K5  gue/chart-L %s   [%s]" % ("PASS" if k5_ok else "WARN", gue_l2))
    if not k5_ok:
        fails.append("K5")

    # K6 -- sigma_u grid must actually move the statistic (defect 15 guard)
    k6_all_ok = True
    for k in ("poisson", "gue", "goe"):
        for token, cname in (("L (lambda", "L"), ("T (ln lambda", "T")):
            g = grab_chi2_grid(outcomes[k]["out"], token)
            ok = len(g) == 3 and len(set(g)) > 1
            k6_all_ok = k6_all_ok and ok
            ckpt("  K6  %-8s chart %s %s   [chi2 grid = %s]"
                 % (k, cname, "PASS" if ok else "FAIL",
                    "identical -> GRID COLLAPSED" if (g and len(set(g)) == 1)
                    else ", ".join("%.4f" % v for v in g) or "(missing)"))
    if not k6_all_ok:
        fails.append("K6")

    ckpt("")
    ckpt("  ALL CHART-L VERDICTS (the ones that count):")
    for k in ("poisson", "gue", "goe"):
        ckpt("     %-8s S1 = %s" % (k, outcomes[k]["s1_L"]))
        ckpt("     %-8s S2 = %s" % (k, outcomes[k]["s2_L"]))
    ckpt("  ALL CHART-T VERDICTS (code path only):")
    for k in ("poisson", "gue", "goe"):
        ckpt("     %-8s S1 = %s | S2 = %s"
             % (k, outcomes[k]["s1_T"], outcomes[k]["s2_T"]))
    ckpt("")
    if fails:
        ckpt("  PIPELINE CHECK: PROBLEMS = %s" % ", ".join(fails))
        ckpt("  -> do NOT run the real analysis until these are understood.")
        rc = 1
    else:
        ckpt("  PIPELINE CHECK: ALL OF K1..K6 SATISFIED.")
        ckpt("  -> the instrument can separate these classes at N = %d." % N_LEV)
        rc = 0
    ckpt("")
    ckpt("TOOL STATUS: python 3.14 + numpy + scipy + subprocess on synthetic data.")
    ckpt("These are SYNTHETIC fixtures, not the Guinand-Weil matrix.")
    ckpt("lean/coqc/isabelle/dkcheck/z3/gcc NOT RUN.")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
