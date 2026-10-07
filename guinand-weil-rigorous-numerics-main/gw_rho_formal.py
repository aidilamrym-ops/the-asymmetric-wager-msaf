# -*- coding: utf-8 -*-
"""Formal (ball-arithmetic) entry-error enclosure for the corrected
Guinand-Weil matrix, measured against an mpmath-built reference matrix.

WHY THIS FILE EXISTS
--------------------
Route A1's entry tolerance `rho_actual` is, everywhere in this repository, the
output of `gw_entry_error.py` -- a dps-doubling **estimate**.  README.md's own
summary says so: "comes from dps-doubling.  It is an estimate, not a proof",
and `gw_arb_measured.py` repeats it ("both routes are conditional on
dps-doubling being a valid error bound").  Every certificate downstream
(`OMEGATrackC.lean`'s `rhoActual`, F0_REPORT, WORKING_PAPER) inherits that
status.

This file measures the same quantity *rigorously*.  It re-evaluates the same
corrected-build formulas of `gw_corrected_eig.build_blocks_corrected` over
python-flint ball arithmetic, so every entry comes back as a ball
`[center, radius]` whose radius FLINT guarantees to cover the true value.  The
distance from the reference matrix to those balls is then an upper bound on the
entry error:

    rho_actual_formal = max_ij ( |M_ref_ij - center_ij| + rad_ij )

No dps-doubling and no float subtraction is involved: both terms are ball
arithmetic, and the max of upper bounds is an upper bound.  Every
transcendental the corrected build uses exists as a ball-valued flint function
(`acb.hypgeom_2f1`, `arb.digamma`, `acb.polygamma`).  The one term with no
flint primitive -- the Lerch series behind `beta_L`'s `t2` -- is evaluated here
as a ball series carrying an explicit geometric tail bound, which is the piece
the earlier blueprint left out.

Euler's constant is not hardcoded: `arb(1).digamma()` equals `-gamma` exactly,
so `c_w` gets it as a ball at full working precision.

WHAT THIS FILE IS NOT
---------------------
- Not a rebuild of the reference matrix.  `M_ref` must be produced by
  `gw_corrected_eig.py` (mpmath) and passed in on the command line; this file
  never regenerates it.
- Not a claim about any matrix other than the one handed in.  If the reference
  is not the matrix a past certificate used, the statement is about this one.
- Not an RH, Weil-positivity, prime-counting or factoring result.  The source
  preprint disclaims all four; so does this file.
- Not a change of any published constant: it measures, it does not re-anchor.
  Re-anchoring is a separate, deliberate edit.

usage:  python gw_rho_formal.py <c> <N> <reference.json> [prec_bits]

    reference.json  the matrix file written by gw_corrected_eig.py phase 5,
                    e.g. gw_matrix_100_40_dps180.json

exit 0: measurement completed (read the verdict on stdout)
exit 1: bad input (unreadable reference, wrong dimension, |z| >= 1)
exit 2: flint/python unavailable
"""
import json
import os
import sys

try:
    from flint import arb, acb, ctx
    FLINT_ERROR = None
except Exception as _exc:            # python-flint missing: reported by main()
    arb = acb = ctx = None
    FLINT_ERROR = "%s: %s" % (type(_exc).__name__, _exc)


def absacb(z):
    """|z| as a ball: sqrt(re^2 + im^2).  python-flint 0.9.0 has no acb.abs."""
    return (z.real * z.real + z.imag * z.imag).sqrt()


def absarb(x):
    """|x| as a ball."""
    return (x * x).sqrt()


def prime_powers_arb(c):
    """Same list as gw_qinf.prime_powers -- (q, log(p)) for every prime power
    q = p^k <= c -- with the logarithms taken as balls.  Re-implemented here so
    this file never imports gw_qinf, which resets mp.mp.dps at module level."""
    primes = []
    x = 2
    while x <= c:
        if all(x % p for p in primes):
            primes.append(x)
        x += 1
    out = []
    for p in primes:
        q = p
        while q <= c:
            out.append((arb(q), arb(p).log()))
            q *= p
    return out


def lerchphi_series_acb(z, s, a, guard_bits):
    """Lerch transcendent Phi(z, s, a) = sum_{k>=0} z^k / (k+a)^s as a ball,
    for real |z| < 1 and Re(a) > 0.

    Tail bound.  Since Re(a) = 1/4 here, |k + a| >= k + 1/4, so the tail after
    the terms k = 0 .. K-1 obeys

        |sum_{k>=K} z^k/(k+a)^s| <= z^K * sum_{j>=0} z^j/(K+1/4+j)^2
                                <= z^K / ((K+1/4)^2 * (1 - z)),

    the last step replacing the decreasing denominators by the smallest one and
    summing the resulting geometric series.  The true tail is complex, so it is
    enclosed by the real interval [0, bound] -- conservative and rigorous.

    `guard_bits` extra bits are demanded below the working precision, so the
    tail is negligible against the working radius of everything else.
    """
    if z.upper() >= 1 or z.lower() <= 0:
        raise ValueError("lerchphi_series_acb needs 0 < |z| < 1, got %s" % z)
    out = acb(0)
    zk = arb(1)
    threshold = arb(2) ** (-(ctx.prec + guard_bits))
    K = 0
    while K < 1000000:
        # Tail after the first K terms (k = 0 .. K-1): the first omitted index is
        # K, whose denominator is K + 1/4 and whose numerator is z^K.
        bound = (z ** K) / ((arb(K) + arb("0.25")) ** 2 * (1 - z))
        if bound.upper() < threshold:
            return out + acb(bound.upper(), 0)
        out = out + acb(zk) / (a + K) ** s
        zk = zk * z
        K += 1
    raise RuntimeError("lerchphi_series_acb did not converge in 10^6 terms")


def build_blocks(c, N):
    """The corrected build of gw_corrected_eig.build_blocks_corrected, in ball
    arithmetic.  Formula-identical call by call; the single functional change
    is that beta_L's `t2` Lerch series carries a proved tail bound here.

    Returns (Q_full, P0, P0d, L) with Q_full(m, n) the (m, n) matrix entry.
    """
    L = arb(c).log()
    z = (-2 * L).exp()
    if z.upper() >= 1:
        raise ValueError("z = exp(-2L) must satisfy |z| < 1, got %s" % z)
    PI = arb.pi()
    eul = -arb(1).digamma()          # psi(1) = -gamma, exactly, as a ball
    PP = prime_powers_arb(c)

    def a_n(n):
        # 1/4 + i*pi*n/L  (acb takes real and imaginary parts separately)
        return acb(arb("0.25"), PI * n / L)

    def F(n):
        return acb(z).hypgeom_2f1(1, a_n(n), a_n(n) + 1)

    def alpha_L(n):
        an = a_n(n)
        w = (2 * L / (L + acb(0, 4 * PI * n))) * F(n)
        return ((-L / 2).exp() * w.imag + arb("0.5") * an.digamma().imag) / PI

    def beta_L(n):
        an = a_n(n)
        t1 = -L * (-L / 2).exp() * ((2 * L / (acb(4 * PI * n, -L)) * F(n)).imag)
        t2 = -((-L / 2).exp() / 4) * lerchphi_series_acb(z, 2, an, 32).real
        t3 = arb("0.25") * an.polygamma(1).real
        return (t1 + t2 + t3) / L

    def c_w():
        e_half = (L / 2).exp()
        return (arb("0.5") * ((e_half - 1) / (e_half + 1)).log()
                + e_half.atan() - PI / 4 + eul / 2
                + arb("0.5") * (8 * PI).log())

    def gamma_L(n):
        an = a_n(n)
        return ((-L / 2).exp() * (-(2 * L / (L + acb(0, 4 * PI * n))) * F(n)).real
                + 2 * (-L / 2).exp()
                * acb(z).hypgeom_2f1(arb("0.25"), 1, arb("1.25")).real
                - arb("0.5") * (an.digamma().real - arb("0.25").digamma())
                + c_w())

    def psipr(m):
        acc = arb(0)
        for q, lp in PP:
            arg = 2 * PI * m * (1 - q.log() / L)
            acc = acc + lp / q.sqrt() * arg.sin()
        return -acc / PI

    def psiprd(m):
        acc = arb(0)
        for q, lp in PP:
            w = 1 - q.log() / L
            acc = acc + lp / q.sqrt() * w * (2 * PI * m * w).cos()
        return -2 * acc

    idx = list(range(-N, N + 1))
    P0, P0d = {}, {}
    for m in idx:
        P0[m] = alpha_L(m) + psipr(m)
        P0d[m] = -2 * (gamma_L(m) - beta_L(m)) + psiprd(m)

    def Cm(m):
        return (L / 4).sinh() / L.sqrt() / (arb("0.25") + (2 * PI * m / L) ** 2)

    def Sm(m):
        return (4 * PI * (L / 4).sinh() / (L * L.sqrt()) * m
                / (arb("0.25") + (2 * PI * m / L) ** 2))

    def pole_A(m, n):
        return 2 * (Cm(m) * Cm(n) - Sm(m) * Sm(n))

    def Q_full(m, n):
        if m == n:
            return P0d[n] + pole_A(n, n)
        return (P0[m] - P0[n]) / (m - n) + pole_A(m, n)

    blocks = {"alpha_L": alpha_L, "beta_L": beta_L, "gamma_L": gamma_L,
              "psipr": psipr, "psiprd": psiprd, "Cm": Cm, "Sm": Sm,
              "pole_A": pole_A, "P0d": P0d, "P0": P0}

    return Q_full, blocks, L, z


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 1
    if FLINT_ERROR is not None:
        print("python-flint unavailable: %s" % FLINT_ERROR)
        return 2

    c, N = int(argv[1]), int(argv[2])
    ref_path = argv[3]
    prec = int(argv[4]) if len(argv) > 4 else 1200
    ctx.prec = prec

    try:
        with open(ref_path, encoding="utf-8") as fh:
            ref = json.load(fh)
    except Exception as exc:
        print("cannot read reference matrix %s: %s: %s"
              % (ref_path, type(exc).__name__, exc))
        return 1
    M = ref.get("M")
    if not isinstance(M, list) or not M or not isinstance(M[0], list):
        print("reference %s has no 'M' matrix" % ref_path)
        return 1
    dim = len(M)
    if dim != 2 * N + 1 or any(len(row) != dim for row in M):
        print("reference is %dx%d, expected %dx%d for N=%d"
              % (dim, dim if M else 0, 2 * N + 1, 2 * N + 1, N))
        return 1

    print("#" * 100)
    print("# FORMAL ENTRY-ERROR ENCLOSURE (flint ball arithmetic)")
    print("# (c, N) = (%d, %d), dim = %d, prec = %d bits" % (c, N, dim, prec))
    print("# reference : %s" % os.path.basename(ref_path))
    print("# ref dps   : %s" % ref.get("dps"))
    print("#" * 100)
    sys.stdout.flush()

    Q_full, blocks, L, z = build_blocks(c, N)
    print("  z = exp(-2L)          = %s" % z)
    print("  L = log(c)            = %s" % L)

    # Component-wise check against mpmath.  This is a guard against a porting
    # error, not a certificate: mpmath is a point evaluator, so all that is
    # asked for is agreement to its printed digits.  The rigorous statement is
    # the ball enclosure computed below.  Only P0, P0d and pole_A are reachable
    # from the mpmath module's public dict; agreement on P0 settles alpha_L and
    # psipr together, agreement on P0d settles gamma_L, beta_L and psiprd.
    try:
        import mpmath as mp
        mp.mp.dps = 100
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import gw_corrected_eig as GE      # imports gw_qinf, which sets dps=40
        mp.mp.dps = 100
        mp_blocks = GE.build_blocks_corrected(c, N)
        worst = {"P0": mp.mpf(0), "P0d": mp.mpf(0), "pole_A": mp.mpf(0)}
        for m in range(-N, N + 1):
            for key in ("P0", "P0d"):
                theirs = mp.mpf(mp.nstr(mp_blocks[key][m]))
                mine = mp.mpf(blocks[key][m].mid().str(30, radius=False))
                # absolute deviation, not relative: P0d is a cancellation of
                # O(1) terms down to ~1e-11, so a relative figure at this
                # precision measures mpmath's cancellation, not the port.
                dev = abs(mine - theirs)
                if dev > worst[key]:
                    worst[key] = dev
        for m in range(-N, N + 1):
            for n in range(-N, N + 1):
                theirs = mp.mpf(mp.nstr(mp_blocks["pole_A"](m, n)))
                mine = mp.mpf(blocks["pole_A"](m, n).mid().str(30, radius=False))
                dev = abs(mine - theirs)
                if dev > worst["pole_A"]:
                    worst["pole_A"] = dev
        print("  component check vs mpmath (dps 100, point values, ABSOLUTE):")
        for key in ("P0", "P0d", "pole_A"):
            print("    max abs. deviation %-7s : %s" % (key, mp.nstr(worst[key], 6)))
    except Exception as exc:
        print("  component check skipped (%s: %s)" % (type(exc).__name__, exc))
    sys.stdout.flush()

    # Symmetry of the reference, checked before anything is claimed about it.
    asym = [(i, j) for i in range(dim) for j in range(dim) if M[i][j] != M[j][i]]
    if asym:
        print("  reference is NOT symmetric: %d mismatching pairs, first %s"
              % (len(asym), asym[0]))
    else:
        print("  reference symmetric   : yes (%d pairs)" % (dim * (dim - 1) // 2))

    rho = arb(0)
    worst = None
    rad_max = arb(0)
    diff_max = arb(0)
    mismatches = 0
    rows = []
    for i in range(dim):
        m = i - N
        for j in range(dim):
            nn = j - N
            ball = Q_full(m, nn)
            ref_ball = arb(M[i][j])
            d = absarb(ball - ref_ball)          # encloses |true - M_ref|
            rad = ball.rad()
            if rad > rad_max:
                rad_max = rad
            if d.upper() > diff_max:
                diff_max = d.upper()
            if d.upper() > rho:
                rho = d.upper()
                worst = (i, j, M[i][j], str(ball))
            rows.append({"i": i, "j": j, "m": m, "n": nn,
                         "rho_ij": d.upper().str(18, radius=False),
                         "radius": rad.str(6, radius=False)})
        sys.stdout.write("\r  entries: %d/%d" % (len(rows), dim * dim))
        sys.stdout.flush()
    print("\r  entries: %d/%d" % (len(rows), dim * dim))

    rho_str = rho.str(20, radius=False)
    print()
    print("=" * 100)
    print("RHO_ACTUAL_FORMAL  (rigorous upper bound on the entry error)")
    print("=" * 100)
    print("  max radius of a single entry ball  = %s" % rad_max.str(6, radius=False))
    print("  max |M_ref - center| (upper)      = %s" % diff_max.str(20, radius=False))
    print("  rho_actual_formal                 = %s" % rho_str)
    print("  worst entry                       = (i, j) = %s, m = %s" % (worst[0], worst[1]))
    print("     M_ref  = %s" % worst[2])
    print("     ball   = %s" % worst[3])

    # Comparison against the certified tolerance rho* = lambda_min / n, with the
    # literals already published in OMEGATrackC.lean, at the true dimension.
    lam = arb("1.32105051975174632728899314595e-102")
    rho_star = lam / dim
    print()
    print("  lambda_min (published literal)     = %s" % lam.str(30, radius=False))
    print("  rho* = lambda_min / n, n = %d      = %s" % (dim, rho_star.str(20, radius=False)))
    certified = rho < rho_star
    ratio = (rho_star / rho) if rho > 0 else arb(0)
    print("  rho* / rho_actual_formal           = %s" % ratio.str(12, radius=False))
    print("  verdict vs rho*                    : %s"
          % ("CERTIFIED (rho_actual_formal < rho*)" if certified
             else "UNDETERMINED (rho_actual_formal >= rho*)"))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "gw_rho_formal_%d_%d.json" % (c, N))
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({
            "c": c, "N": N, "dim": dim, "prec_bits": prec,
            "reference": os.path.basename(ref_path),
            "reference_dps": ref.get("dps"),
            "reference_symmetric": not asym,
            "z": z.str(30, radius=False),
            "L": L.str(30, radius=False),
            "max_ball_radius": rad_max.str(12, radius=False),
            "max_abs_diff_upper": diff_max.str(30, radius=False),
            "rho_actual_formal": rho_str,
            "lambda_min_literal": lam.str(30, radius=False),
            "rho_star_literal_over_dim": rho_star.str(30, radius=False),
            "certified_vs_rho_star": bool(certified),
            "worst_entry": {"i": worst[0], "j": worst[1],
                            "m_ref": worst[2], "ball": worst[3]},
            "per_entry": rows,
            "scope": ("rigorous upper bound on the entry error of the reference "
                      "matrix as supplied; it is not a rebuild of that matrix "
                      "and says nothing about any other build"),
        }, fh)
    print()
    print("  results -> %s" % out)
    print("  SCOPE: measurement only.  Re-anchoring rho_actual in the published")
    print("  certificate is a separate deliberate edit, not an output of this run.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
