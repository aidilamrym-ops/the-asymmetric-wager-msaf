# -*- coding: utf-8 -*-
"""Probe what python-flint actually offers before claiming anything about it.

Goal: find out, empirically and without assumption, whether arb_mat.eig exists,
what it returns, and -- critically -- whether its output carries error radii
(genuine interval enclosure) or is a bare floating approximation.

Nothing in this file is a result; it is an API audit.

Run: python probe_flint_eig.py
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

import flint  # noqa: E402

print("python      :", sys.version.split()[0])
print("python-flint:", getattr(flint, "__version__", "?"))
print("flint ctx   : prec =", flint.ctx.prec, " bits")
print()

# --- what does arb_mat expose? -------------------------------------------
print("=== arb_mat public callables ===")
names = [n for n in dir(flint.arb_mat) if not n.startswith("_")]
print(", ".join(names))
print()

for meth in ("eig", "det", "solve", "charpoly", "ldlt", "cholesky", "svd"):
    has = meth in names
    print("  arb_mat.%-10s %s" % (meth, "PRESENT" if has else "-- absent --"))
print()

# --- signatures / docstrings --------------------------------------------
for meth in ("eig", "charpoly"):
    if meth in names:
        obj = getattr(flint.arb_mat, meth)
        print("=== arb_mat.%s ===" % meth)
        print("doc:", (obj.__doc__ or "(no docstring)").strip()[:600])
        print()

# --- empirical: does eig carry radii? ------------------------------------
print("=== empirical: symmetric 2x2 with exactly known eigenvalues ===")
print("    A = [[2, 1], [1, 2]]  -> exact eigenvalues 1 and 3")
print()

flint.ctx.prec = 200
A = flint.arb_mat([[2, 1], [1, 2]])
print("A =", A)
print()

try:
    out = A.eig()
    print("type of eig() return :", type(out).__name__)
    if isinstance(out, (tuple, list)):
        print("len                  :", len(out))
        for i, part in enumerate(out):
            print("  [%d] type=%s" % (i, type(part).__name__))
            print("      value =", part)
    else:
        print("value =", out)
except Exception as exc:  # pragma: no cover - audit path
    print("A.eig() RAISED:", type(exc).__name__, exc)

print()

# --- do the entries actually retain radius information? -------------------
print("=== do arb entries keep a radius at all? ===")
x = flint.arb(1) / flint.arb(3)
print("1/3          =", x)
print("mid          =", x.mid)
print("rad          =", x.rad)
print("lower/upper  =", x.lower, "/", x.upper)
print()

print("=== sqrt of a perfect square: does radius collapse? ===")
y = flint.arb(2).sqrt()
print("sqrt(2)      =", y)
print("rad          =", y.rad)
