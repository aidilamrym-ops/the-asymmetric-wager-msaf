#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Timing probe for the arb LDL^T falsification route.

Measures build_arb_tau + certified_inertia wall time at one (c, N, prec)
so the sweep budget can be extrapolated from real numbers instead of guesses.

usage:
    python gw_ldlt_probe.py 100 100 2000
"""

import sys
import time
import hashlib
import json

from flint import arb, arb_mat, ctx

import source_arb_ldlt_certify as src


def peak_mb():
    try:
        import ctypes

        class PMC(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_uint32),
                ("PageFaultCount", ctypes.c_uint32),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        ctypes.windll.psapi.GetProcessMemoryInfo(
            ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
        return pmc.PeakWorkingSetSize / 1e6
    except Exception:
        return float("nan")


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    c = int(sys.argv[1])
    N = int(sys.argv[2])
    prec = int(sys.argv[3])
    dim = 2 * N + 1

    print("=" * 88, flush=True)
    print("LDLT PROBE  c=%d N=%d prec=%d  dim=%d" % (c, N, prec, dim), flush=True)
    print("=" * 88, flush=True)

    t0 = time.time()
    A, DIM = src.build_arb_tau(c, N, prec)
    t_build = time.time() - t0
    print("  build_arb_tau      : %.1f s" % t_build, flush=True)

    # widest radius over all entries, as a rigor signal
    max_rad = arb(0)
    for i in range(DIM):
        for j in range(DIM):
            r = A[i, j].rad()
            if r > max_rad:
                max_rad = r
    print("  max entry radius   : %s" % max_rad.str(12, radius=False), flush=True)

    t0 = time.time()
    n_pos, n_neg, undet, transcript = src.certified_inertia(A, DIM, heartbeat=0)
    t_ldlt = time.time() - t0
    print("  certified_inertia  : %.1f s" % t_ldlt, flush=True)
    print("  RESULT n_pos=%d n_neg=%d undetermined_pivot=%s"
          % (n_pos, n_neg, undet), flush=True)

    # smallest |pivot| and whether ||L - I||_F < 1 (for a lambda_min lower bound)
    min_abs_piv = None
    for line in transcript:
        parts = line.split()
        if len(parts) >= 4:
            mid = float(parts[2])
            rad = float(parts[3])
            a = abs(mid) - rad
            if min_abs_piv is None or a < min_abs_piv:
                min_abs_piv = a
    if min_abs_piv is not None:
        print("  min(|pivot|)       : %.6e" % min_abs_piv, flush=True)

    verdict = "CERTIFIED POSITIVE DEFINITE" if (n_neg == 0 and undet is None) \
        else ("ANOMALY n_neg=%d" % n_neg if n_neg else "UNDETERMINED at %s" % undet)

    print("  VERDICT            : %s" % verdict, flush=True)
    print("  peak memory        : %.1f MB" % peak_mb(), flush=True)

    state = {
        "c": c, "N": N, "prec": prec, "dim": dim,
        "n_pos": n_pos, "n_neg": n_neg, "undetermined_pivot": undet,
        "build_s": round(t_build, 1), "ldlt_s": round(t_ldlt, 1),
        "max_entry_radius": max_rad.str(20, radius=False),
        "min_abs_pivot": min_abs_piv,
        "verdict": verdict,
    }
    digest = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
    state["sha256"] = digest
    print("  SHA-256(state)     : %s" % digest, flush=True)

    out = "ldlt_probe_%d_%d.json" % (c, N)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)
    print("  saved -> %s" % out, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
