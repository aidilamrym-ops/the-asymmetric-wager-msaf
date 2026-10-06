# -*- coding: utf-8 -*-
"""
Where does the positivity of Q_inf come from, numerically?

Statement under test: arXiv:2607.02828v3 (PREPRINT, LLM-assisted; the paper
explicitly disclaims RH, Weil positivity and prime-counting results).

For each (c, N) this prints
  - the FULL eigenvalue list of Q_inf on the real even sector,
  - for the lowest eigenvector v0, the per-block Rayleigh quotients
        r_prime = <v0, Q_prime v0>,  r_arch = <v0, Q_arch v0>,
        r_pole  = <v0, Q_pole  v0>,
    whose sum must equal lambda_min.
That decomposition is the quantitative statement of the degeneracy: if the
blocks are each O(1) but cancel to ~1e-35, the sign of lambda_min is decided
by the last digits of every block, and no finite precision can be assumed
sufficient a priori.

Everything below the working precision floor is printed with its dps so the
reader can see which digits are digits and which are noise.
"""

import sys

import mpmath as mp

import gw_qinf as G


def detail(c, N, dps):
    mp.mp.dps = dps
    bl = G.build_blocks(c, N)
    M = G.even_matrix(bl, N, block="all")
    w, V = mp.eigsy(M)
    order = sorted(range(len(w)), key=lambda i: +w[i])

    print("=" * 96)
    print("FULL SPECTRUM OF Q_inf AT (c, N) = (%d, %d)   [dps = %d]" % (c, N, dps))
    print("=" * 96)
    for rank, i in enumerate(order):
        mark = ""
        if rank < 3:
            mark = "   <-- lowest cluster"
        print("   lambda[%2d] = %-22s%s" % (rank, mp.nstr(w[i], 14), mark))
    lmin, lmax = w[order[0]], w[order[-1]]
    print("   lambda_min / lambda_max = %s" % mp.nstr(lmin / lmax, 8))
    print("   digits available at this dps = %d ; |log10 lambda_min| = %.1f"
          % (dps, float(-mp.log10(abs(lmin))) if lmin != 0 else 0))
    print()

    # lowest eigenvector and its per-block Rayleigh quotients
    k = order[0]
    v = mp.matrix([V[i, k] for i in range(len(w))])
    nrm = mp.sqrt(mp.fsum(abs(v[i]) ** 2 for i in range(len(v))))
    v = v / nrm

    print("   PER-BLOCK RAYLEIGH QUOTIENTS ALONG THE lambda_min EIGENVECTOR")
    parts = {}
    for name in ("prime", "arch", "pole"):
        Mv = G.even_matrix(bl, N, block=name)
        r = mp.fsum(mp.conj(v[i]) * Mv[i, j] * v[j]
                    for i in range(len(v)) for j in range(len(v)))
        r = mp.re(r) if abs(mp.im(r)) < 1e-30 else r
        parts[name] = r
        print("     <v, %-5s v> = %s" % (name, mp.nstr(r, 14)))
    total = parts["prime"] + parts["arch"] + parts["pole"]
    print("     sum            = %s" % mp.nstr(total, 14))
    print("     lambda_min     = %s" % mp.nstr(lmin, 14))
    print("     |sum - lmin|   = %s   (closure of the decomposition)" % mp.nstr(abs(total - lmin), 6))
    print("     cancellation ratio: O(%.1f) terms cancel to %s -> factor %s"
          % (max(abs(parts[n]) for n in parts), mp.nstr(abs(lmin), 6),
             mp.nstr(max(abs(parts[n]) for n in parts) / max(abs(lmin), mp.mpf(10) ** -dps), 4)))
    print()


def main():
    print("#" * 96)
    print("# PER-BLOCK DECOMPOSITION OF THE lambda_min DIRECTION")
    print("# statement: arXiv:2607.02828v3  (PREPRINT, LLM-assisted, no RH claim)")
    print("#" * 96)
    print()
    detail(13, 4, 40)
    detail(13, 16, 60)
    detail(13, 24, 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
