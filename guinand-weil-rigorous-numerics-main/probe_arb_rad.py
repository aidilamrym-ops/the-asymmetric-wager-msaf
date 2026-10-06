# -*- coding: utf-8 -*-
"""Probe how to attach an EXPLICIT absolute radius to an arb entry.

Motivation: gw_corrected_eig phase 6 parsed decimals into arb and got
radius ~1.5e-308 -- that is only FLINT's binary parse rounding at prec=1024
bits.  It says nothing about the mpmath origin of the digits (~1e-180 at
dps 180).  To test whether lambda_min stays locked when the entry error is
what it actually is, each entry must be handed a chosen absolute radius.

This probe finds the constructor that does that, and checks that arithmetic
on such balls widens as interval arithmetic requires.

Run: python probe_arb_rad.py
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

import flint  # noqa: E402

flint.ctx.prec = 1024

print("=== candidate constructors for a zero-centre ball of radius rho ===")
rho = "1e-180"

tries = [
    ("arb(0, rho)  as float", lambda: flint.arb(0, 1e-180)),
    ("arb(0, rho)  as str", lambda: flint.arb(0, rho)),
    ("arb('0 +/- rho')", lambda: flint.arb("0 +/- %s" % rho)),
    ("arb(0) with rad set", lambda: flint.arb(0)),
]
made = None
for name, fn in tries:
    try:
        b = fn()
        print("  %-28s -> %s   rad=%s" % (name, str(b)[:70], str(b.rad())[:40]))
        if made is None and b.rad() != 0:
            made = (name, b)
    except Exception as exc:
        print("  %-28s -> FAIL %s: %s" % (name, type(exc).__name__, exc))

print()
if made is None:
    print("NO constructor produced a nonzero radius -- sweep cannot proceed")
    sys.exit(1)

name, zero_ball = made
print("using constructor: %s" % name)

print()
print("=== does adding the ball widen an entry correctly? ===")
a = flint.arb("1.5e-5")
print("  a                  =", str(a)[:80])
print("  a.rad() parse only =", str(a.rad())[:40])
c = a + zero_ball
print("  a + zero_ball      =", str(c)[:80])
print("  c.rad()            =", str(c.rad())[:40])
print("  c > 0 (rigorous)   =", c > 0)
print("  c contains 0       =", c.contains(0))

print()
print("=== does it stay rigorous when the ball straddles zero? ===")
d = flint.arb("1e-190") + flint.arb(0, 1e-180)
print("  1e-190 +- 1e-180   =", str(d)[:80])
print("  d > 0              =", d > 0, " (expected False: not provably positive)")
print("  d contains 0       =", d.contains(0), " (expected True)")

print()
print("=== sanity: enclosure still contains the true value ===")
e = flint.arb("1.0") + zero_ball
print("  1.0 +- 1e-180      =", str(e)[:80])
print("  e.contains(1)      =", e.contains(1))
