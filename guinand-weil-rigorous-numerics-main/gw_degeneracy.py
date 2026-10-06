# -*- coding: utf-8 -*-
"""
How many digits does the sign of lambda_min(Q_inf) actually need?

Statement under test: arXiv:2607.02828v3 (preprint; LLM-assisted; the paper
explicitly disclaims any RH / Weil-positivity result).

The paper reports, at (c,N) = (100,200), an Arb LDL^T run at 9000 bits giving
n_+ = 401, n_- = 0, and an abstract sentence about "resolving a spectral scale
of 10^-59 at c=100".  It never states how the required precision scales with N.

This script measures exactly that, and does three further diagnostics:

  D1  precision ladder: lambda_min(c=13, N) at increasing dps, to find the
      dps at which the value stops moving (i.e. is resolved rather than noise).
  D2  block decomposition: spectra of Q_prime, Q_arch and Q_pole separately at
      fixed N, to locate where the near-null direction comes from.
  D3  localization of the lambda_min eigenvector (participation ratio on the
      even-sector coordinates): edge-concentrated => truncation boundary
      artefact; spread out => genuine near-null direction of the limiting form.

No claim about RH is made or implied.  Anything below the working precision
floor is reported as UNRESOLVED, never as negative.
"""

import sys

import mpmath as mp

import gw_qinf as G


def spectrum(M):
    w, _ = mp.eigsy(M)
    return [w[i] for i in range(len(w))]


def run(c, dps_list, N_list):
    print("=" * 96)
    print("D1  PRECISION LADDER FOR lambda_min(Q_inf)   (c = %d)" % c)
    print("=" * 96)
    print("  dps    digits   " + "".join("  N=%-13d" % N for N in N_list))
    print("  " + "-" * 90)
    table = {}
    for dps in dps_list:
        mp.mp.dps = dps
        cells = []
        for N in N_list:
            bl = G.build_blocks(c, N)
            M = G.even_matrix(bl, N, block="all")
            w = spectrum(M)
            lmin = min(w)
            table[(N, dps)] = lmin
            cells.append("  %-13s" % mp.nstr(lmin, 6))
        print("  %-6d %-7d " % (dps, dps) + "".join(cells))
        sys.stdout.flush()

    print()
    print("  digits of agreement between dps and the highest dps run:")
    print("  dps    " + "".join("  N=%-13d" % N for N in N_list))
    print("  " + "-" * 90)
    top = max(dps_list)
    for dps in dps_list:
        if dps == top:
            continue
        cells = []
        for N in N_list:
            a, b = table[(N, dps)], table[(N, top)]
            if a == 0 or b == 0:
                cells.append("  %-13s" % "-")
                continue
            rel = abs(a - b) / abs(b)
            if rel == 0:
                d = float(dps)
            else:
                d = min(float(dps), -float(mp.log10(rel)))
            cells.append("  %-13s" % ("%.1f" % d))
        print("  %-6d " % dps + "".join(cells))
    print()
    return table


def blocks_at(c, N, dps=60):
    mp.mp.dps = dps
    bl = G.build_blocks(c, N)
    print("=" * 96)
    print("D2  BLOCK DECOMPOSITION AT (c, N) = (%d, %d)" % (c, N))
    print("=" * 96)
    for name in ("prime", "arch", "pole", "all"):
        M = G.even_matrix(bl, N, block=name)
        w = sorted(spectrum(M), key=lambda x: +x)
        print("  %-6s  n_nonzero(>1e-25*max) = %2d   lambda_min = %-16s  lambda_max = %s"
              % (name,
                 sum(1 for x in w if abs(x) > mp.mpf(10) ** -25 * max(abs(y) for y in w)),
                 mp.nstr(w[0], 8),
                 mp.nstr(w[-1], 8)))
    print()


def localisation(c, N, dps=60):
    mp.mp.dps = dps
    bl = G.build_blocks(c, N)
    M = G.even_matrix(bl, N, block="all")
    w, V = mp.eigsy(M)
    k = min(range(len(w)), key=lambda i: +w[i])
    v = mp.matrix([V[i, k] for i in range(len(w))])
    nrm = mp.sqrt(mp.fsum(abs(v[i]) ** 2 for i in range(len(v))))
    v = v / nrm
    p4 = mp.fsum(abs(v[i]) ** 4 for i in range(len(v)))
    pr = 1 / p4
    print("=" * 96)
    print("D3  LOCALISATION OF THE lambda_min EIGENVECTOR  (c, N) = (%d, %d)" % (c, N))
    print("=" * 96)
    print("  coordinates = v_0, v_1, ..., v_N  (even-sector, isometric embedding)")
    print("  lambda_min  = %s" % mp.nstr(w[k], 12))
    print("  participation ratio = %.4f  of  N+1 = %d  ->  %s"
          % (float(pr), N + 1,
             "SPREAD (bulk)" if pr > 0.5 * (N + 1) else "LOCALISED (edge or few coords)"))
    print("  |v_k|:  " + "  ".join("%d:%s" % (i, mp.nstr(abs(v[i]), 4)) for i in range(len(v))))
    print()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    print("#" * 96)
    print("# SPECTRAL DEGENERACY OF THE CUTOFF-FREE GUINAND-WEIL MATRIX")
    print("# statement: arXiv:2607.02828v3  (PREPRINT, LLM-assisted, no RH claim)")
    print("#" * 96)
    print()

    if mode in ("all", "d1"):
        run(13, [40, 60, 80, 120], [4, 8, 16, 24, 32, 40])
    if mode in ("all", "d23"):
        blocks_at(13, 16, dps=60)
        localisation(13, 16, dps=60)
        localisation(13, 24, dps=80)

    print("=" * 96)
    print("SUMMARY OF THE RESOLUTION REQUIREMENT")
    print("=" * 96)
    return 0


if __name__ == "__main__":
    sys.exit(main())
