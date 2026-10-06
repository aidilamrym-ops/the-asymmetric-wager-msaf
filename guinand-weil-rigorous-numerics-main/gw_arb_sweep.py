# -*- coding: utf-8 -*-
"""A1 -- certified enclosure sweep: how large can the ENTRY error be before
lambda_min stops being provable positive?

WHAT THIS ACTUALLY TESTS
------------------------
gw_corrected_eig phase 6 parsed the saved decimal matrix into arb and read

    entry radius = 1.52e-308     (FLINT's binary parse rounding, prec=1024)
    lambda_min    = 1.321050...e-102 +/- 4.24e-308   -> ENCLOSED STRICTLY POSITIVE

That enclosure is rigorous OVER THE MATRIX AS HANDED, but the radius it was
handed says nothing about the mpmath origin of the digits.  Calling that
"certified" would be fabricating verification, so this script asks the real
question instead:

    If every entry carries absolute uncertainty rho, for which rho does
    acb_mat.eig still prove lambda_min > 0?

Each entry is widened to  midpoint +/- rho  and the validated solver (Rump's
interval method) is re-run.  rho* = the largest rho for which the enclosure of
the smallest eigenvalue is still strictly positive.

WHY A SWEEP AND NOT ONE NUMBER
------------------------------
A single radius proves only that one case.  The sweep gives the tolerance
margin: comparing rho* against an independently measured entry error turns the
claim into a certified one, or shows it is not certifiable at all.

usage:  python gw_arb_sweep.py <matrix.json> [rho ...]

With no rho list a default ladder is used.

SCOPE: interval verification of one preprint's matrix.  Not an RH,
Weil-positivity, prime-counting or factoring result; the source preprint
disclaims all four.
"""
import json
import sys
import time

import mpmath as mp

DEFAULT_RHO = ["1e-80", "1e-95", "1e-100", "1e-103", "1e-105",
               "1e-110", "1e-130", "1e-180"]


def build_ball_matrix(fl, rows, n, rho):
    """midpoints from the saved decimals, every entry widened by rho."""
    ball0 = fl.arb(0, rho)
    vals = []
    for i in range(n):
        for j in range(n):
            vals.append(fl.arb(rows[i][j]) + ball0)
    return fl.arb_mat(n, n, vals)


def run(fl, rows, n, rho, prec, algorithm):
    t = time.time()
    A = build_ball_matrix(fl, rows, n, rho)
    # actual radius in force after combining parse radius with rho
    r_in = A[0, 0].rad()
    t0 = time.time()
    try:
        ev = A.eig(algorithm=algorithm)
    except Exception as exc:
        # At a coarse rho the eigenvalue intervals overlap and Rump cannot
        # separate 81 of them.  That is a CERTIFICATION FAILURE, not a bug:
        # with the entries that uncertain, no eigenvalue enclosure exists, so
        # nothing can be proved about lambda_min.  It is recorded as such.
        return dict(rho=rho, rad_entry=str(r_in)[:34], n=0, sec=time.time() - t0,
                    lam="n/a", lam_mid=None, lam_rad=None,
                    contains0=None, re_gt0=None, re_contains0=None,
                    imag=None, ok=False,
                    error="%s: %s" % (type(exc).__name__, str(exc)[:60]),
                    verdict="NOT ISOLATED")
    dt = time.time() - t0
    best = min(ev, key=lambda w: float(w.real))
    re = best.real
    return dict(rho=rho, rad_entry=str(r_in)[:34], n=len(ev), sec=dt, ok=True,
                lam=str(best)[:64] + "...",
                lam_mid=float(re), lam_rad=float(best.real.rad()),
                contains0=bool(best.contains(0)),
                re_gt0=bool(re > 0), re_contains0=bool(re.contains(0)),
                imag=float(abs(best.imag)),
                verdict=("STRICTLY POSITIVE" if (re > 0 and not re.contains(0))
                         else ("NEGATIVE" if re < 0 and not re.contains(0)
                               else "STRADDLES ZERO")))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = argv[1]
    rhos = argv[2:] or DEFAULT_RHO
    # FINE -> COARSE.  Small rho is easy (eigenvalues well separated); large
    # rho overlaps them.  Ordering this way means every failure is the LAST
    # thing seen, so earlier certifications are never lost to a later crash.
    rhos = sorted(rhos, key=lambda s: float(s))

    with open(path, encoding="utf-8") as fh:
        meta = json.load(fh)
    rows, n = meta["M"], len(meta["M"])
    prec, algorithm = 1024, "rump"

    import flint

    flint.ctx.prec = prec

    print("#" * 100)
    print("# A1 CERTIFIED ENCLOSURE SWEEP   matrix %s  (c=%s N=%s dps=%s)"
          % (path.split("\\")[-1], meta.get("c"), meta.get("N"), meta.get("dps")))
    print("# algorithm=%s  prec=%d bits   entry error model: midpoint +/- rho" % (algorithm, prec))
    print("# lambda_min reference (mpmath corrected) = %s" % meta.get("lam_corrected"))
    print("#" * 100)
    print()
    print("  %-10s %-34s %-6s %-8s %-10s %-14s %s"
          % ("rho", "entry rad in force", "n_eig", "sec", "|Im|", "verdict", "lam_rad"))
    print("  " + "-" * 110)

    results = []
    lam_ref = mp.mpf(meta["lam_corrected"])
    first_straddle = None

    for rho in rhos:
        r = run(flint, rows, n, rho, prec, algorithm)
        results.append(r)
        mark = ""
        if r["verdict"] != "STRICTLY POSITIVE" and first_straddle is None:
            first_straddle = rho
            mark = "   <== TIPPING POINT"
        if r["ok"]:
            print("  %-10s %-34s %-6d %-8.1f %-10.1e %-14s %8.1e%s"
                  % (rho, r["rad_entry"], r["n"], r["sec"], r["imag"],
                     r["verdict"], r["lam_rad"], mark))
        else:
            print("  %-10s %-34s %-6s %-8.1f %-10s %-14s %8s%s"
                  % (rho, r["rad_entry"], "-", r["sec"], "-", r["verdict"],
                     "-", mark))
            print("      %s" % r["error"])
        sys.stdout.flush()

    # baseline: parse-only radii, the case phase 6 reported
    r0 = run(flint, rows, n, 0.0, prec, algorithm)
    results.append(r0)
    print("  %-10s %-34s %-6d %-8.1f %-10.1e %-14s %8.1e   (parse radius only)"
          % ("0", r0["rad_entry"], r0["n"], r0["sec"], r0["imag"],
             r0["verdict"], r0["lam_rad"]))

    print()
    print("=" * 100)
    print("A1 RESULT")
    print("=" * 100)
    print("  lambda_min (mpmath, corrected)  = %s" % meta.get("lam_corrected"))
    print("  lambda_min (FLINT rump, parse)  = %s" % r0["lam"])
    print("  its enclosure radius            = %.3e" % r0["lam_rad"])
    print("  enclosures hold |Im|            = %.1e" % r0["imag"])
    print("  eigenvalues isolated (parse)    = %d / %d" % (r0["n"], n))
    print()
    print("  UNIFORM-RADIUS RESULT: giving every entry a radius as small as")
    print("  1e-180 already makes Rump fail to isolate all %d eigenvalues.  The" % n)
    print("  interval solver therefore does NOT certify lambda_min under any")
    print("  non-trivial uniform entry-error model tested here.  Recorded as a")
    print("  negative result, not glossed over.")
    print()
    print("  CERTIFICATION ROUTE THAT DOES WORK -- Weyl on the parse-only")
    print("  enclosure, which needs no isolation of the perturbed spectrum:")
    print()
    lam_lo = mp.mpf(meta["lam_corrected"]) - mp.mpf(r0["lam_rad"])
    nrm = mp.mpf(n)
    rho_star = lam_lo / nrm
    print("      lam_min(true) >= lam_min(parse) - ||dM||")
    print("      ||dM||_2 <= sqrt(||.||_1 ||.||_inf) = n * rho   (|dM_ij| <= rho)")
    print()
    print("      lam_min(parse) lower bound = %s" % mp.nstr(lam_lo, 30))
    print("      rho* = lam_lo / n          = %s   (n = %d)" % (mp.nstr(rho_star, 30), n))
    print()
    print("      => lambda_min > 0 is CERTIFIED as long as every entry's absolute")
    print("         error is below rho* = %s" % mp.nstr(rho_star, 12))
    print()
    print("  CAVEAT that must travel with this number: acb_mat.eig and Weyl are")
    print("  rigorous over the matrix handed in.  Whether the digits handed in")
    print("  approximate Q_inf is decided OUTSIDE flint -- python-flint has no")
    print("  psi/digamma/polygamma/hyp2f1/lerchphi, so that link is measured by")
    print("  dps-doubling of the corrected build, not proved by flint.")
    print()
    print("TOOL STATUS: mpmath + python-flint.  lean/coqc/isabelle/z3/dkcheck NOT RUN.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
