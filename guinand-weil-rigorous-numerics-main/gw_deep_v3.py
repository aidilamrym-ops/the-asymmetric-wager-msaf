# -*- coding: utf-8 -*-
"""Corrected archimedean closed forms -- psi and psi'.

Why this file exists
--------------------
gw_deep_v2.closed_dpsi evaluates its Lerch term with mp.lerchphi(z, 2, an).
At dps <= ~224, for z = exp(-2L) = 1e-4 and an = 1/4 + i*pi*n/L with
n = 40, mp.lerchphi returns a value that is perfectly dps-STABLE yet wrong
by

    |mp - defining series| = 8.42831291456e-100
    Re gap                 = -3.12332701278e-100

Because closed_dpsi depends on Re(L2) with coefficient -2*(1/L)*(-e^{-L/2}/4)
= 0.0108573620475813, that gap propagates to exactly

    0.0108573620475813 * 3.12332701278e-100 = 3.391109217077509e-102

which is precisely the psi' identity residual that failed the (100,40) gate
(3.391109217077509e-102 against lambda_min = 1.32105051975e-102).  The
defining-integral side and an independent reconstruction from the Lerch
definition agree to 3.912055399093736e-159; gw_deep_v2.closed_dpsi is the
outlier.

Note the asymmetry this explains: closed_psi never calls lerchphi, so psi
reached the dps floor (9.381409e-140) while psi' stalled at 1e-102.

The replacement below is the definition itself,

    Phi(z, s, a) = sum_{k>=0} z^k / (k + a)^s,   |z| < 1,

which for z = 1e-4 terminates in ~42 terms for 160 digits.

Only that single call site is changed; the surrounding arithmetic is copied
byte-for-byte from gw_deep_v2 so the two differ in one place and one place
only.

Read-only with respect to every other file.
"""
import mpmath as mp

# NOTE ON IMPORT ORDER -- read before adding imports below or above this line.
# gw_qinf.py sets mp.mp.dps = 40 at MODULE LEVEL, and gw_arch_check,
# gw_deep_v2 and gw_tail_deep all import it transitively.  Any import placed
# AFTER a mp.mp.dps assignment therefore silently resets the precision to 40.
# All correction/testing code in this directory sets mp.mp.dps inside main(),
# after every import has already run -- keep it that way.
import gw_deep_v2 as V2


def lerchphi_series(z, s, a, tol=None):
    """Lerch transcendent from its defining series, |z| < 1.

    Drop-in replacement for mp.lerchphi.  See the module docstring for why
    the replacement is needed.
    """
    if tol is None:
        tol = mp.mpf(10) ** (-(mp.mp.dps + 10))
    out = mp.mpc(0)
    zk = mp.mpf(1)
    for k in range(1000000):
        t = zk / (k + a) ** s
        out += t
        if abs(t) < tol:
            break
        zk *= z
    return out


def closed_psi(n, L):
    """Identical to gw_deep_v2.closed_psi -- that function never calls
    lerchphi, so it needs no correction.  Re-declared here so this module is
    self-contained."""
    if n == 0:
        return mp.mpf(0)
    z = mp.e ** (-2 * L)
    an = mp.mpf(1) / 4 + mp.pi * 1j * n / L
    F = mp.hyp2f1(1, an, an + 1, z)
    return (mp.e ** (-L / 2) * mp.im((2 * L / (L + 4 * mp.pi * 1j * n)) * F)
            + mp.mpf(1) / 2 * mp.im(mp.digamma(an))) / mp.pi


def closed_dpsi(n, L):
    """gw_deep_v2.closed_dpsi with mp.lerchphi replaced by lerchphi_series.

    Everything else is unchanged.
    """
    z = mp.e ** (-2 * L)
    an = mp.mpf(1) / 4 + mp.pi * 1j * n / L
    F = mp.hyp2f1(1, an, an + 1, z)
    t1 = -L * mp.e ** (-L / 2) * mp.im((2 * L / (4 * mp.pi * n - 1j * L)) * F)
    t2 = -(mp.e ** (-L / 2) / 4) * mp.re(lerchphi_series(z, 2, an))   # <-- only change
    t3 = mp.mpf(1) / 4 * mp.re(mp.polygamma(1, an))
    beta = (t1 + t2 + t3) / L
    gamma = (-mp.e ** (-L / 2) * mp.re((2 * L / (L + 4 * mp.pi * 1j * n)) * F)
             + 2 * mp.e ** (-L / 2) * mp.hyp2f1(mp.mpf(1) / 4, 1,
                                                mp.mpf(5) / 4, z)
             - mp.mpf(1) / 2 * (mp.re(mp.digamma(an)) - mp.digamma(mp.mpf(1) / 4))
             + (mp.mpf(1) / 2 * mp.log((mp.e ** (L / 2) - 1) / (mp.e ** (L / 2) + 1))
                + mp.atan(mp.e ** (L / 2)) - mp.pi / 4 + mp.euler / 2
                + mp.mpf(1) / 2 * mp.log(8 * mp.pi)))
    return -2 * (gamma - beta)


if __name__ == "__main__":
    import sys
    mp.mp.dps = int(sys.argv[1]) if len(sys.argv) > 1 else 160
    c = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    L = mp.log(c)
    old = V2.closed_dpsi(n, L)
    new = closed_dpsi(n, L)
    print("gw_deep_v2.closed_dpsi = %s" % mp.nstr(old, 60))
    print("gw_deep_v3.closed_dpsi = %s" % mp.nstr(new, 60))
    print("|difference|           = %s" % mp.nstr(abs(old - new), 16))
    print("the failed gate value  = 3.391109217077509e-102")
