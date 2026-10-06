# -*- coding: utf-8 -*-
"""F5-1 stage C: update the two registers that still described the variance
as live.  Historical reports record what was found; they are amended only by
adding a closure, never by erasing the finding.
"""
import hashlib
import io
import os
import sys

ROOT = r"D:\THE ASYMMETRIC WAGER"
REFS = os.path.join(ROOT, "REFERENCES.md")
F3R = os.path.join(ROOT, "F3_REPORT.md")
fails = []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def read(p):
    b = open(p, "rb").read()
    if b.startswith(b"\xef\xbb\xbf") or b"\r" in b:
        fails.append("%s: baseline encoding problem" % p)
    return b.decode("utf-8")


def write(p, text):
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    b = open(p, "rb").read()
    if b.startswith(b"\xef\xbb\xbf") or b"\r" in b:
        fails.append("%s: encoding violated after write" % p)
    try:
        b.decode("utf-8")
    except Exception as exc:
        fails.append("%s: not UTF-8 after write: %r" % (p, exc))


def sub(text, old, new, what):
    n = text.count(old)
    if n != 1:
        fails.append("%s: expected exactly 1 match, found %d for:\n%s"
                     % (what, n, old[:160]))
        return text
    return text.replace(old, new)


print("=" * 90)
print("F5-1 STAGE C -- close the finding in REFERENCES.md and F3_REPORT.md")
print("=" * 90)

# --------------------------------------------------------------- REFERENCES
b0 = sha(REFS)
t = read(REFS)

t = sub(t,
        "| `01_PARADOX_AND_SCALE.md` L25 and L29 | `1.63 \\times 10^{-35}` "
        "| **declared variance, see below** |",
        "| `01_PARADOX_AND_SCALE.md` L25 and L29 | `1.62 \\times 10^{-35}` "
        "| agrees with the source at 3 s.f. (corrected by F5-1, 2026-10-05) |",
        "REFERENCES.md row")

OLD_PARA = """**Declared variance (found by F3-1, 2026-10-05; recorded, not silently corrected).**
The correctly rounded 3-significant-figure form of `1.616255e-35` is
`1.62e-35`, not `1.63e-35`. The relative deviation of the value used in
`01_PARADOX_AND_SCALE.md` from the CODATA 2022 value is `8.504e-3` (+0.8504 %).
This does **not** change the downstream conclusion: both `1.62e-35` and
`1.63e-35` reproduce $N_{\\text{steps}} \\approx 5{,}4 \\times 10^{61}$ at the two
significant figures the corpus declares for $N_{\\text{steps}}$. The variance is
registered here so that the gate fails if either side is edited without the
other being updated, and so that an examiner sees it rather than discovers it.
Remediation is deferred to a phase that explicitly permits editing
`01_PARADOX_AND_SCALE.md`."""

NEW_PARA = """**Variance found by F3-1 and closed by F5-1 (both 2026-10-05).**
F3-1 recorded openly, rather than editing silently, that
`01_PARADOX_AND_SCALE.md` read `1.63e-35` where the correctly rounded
3-significant-figure form of `1.616255e-35` is `1.62e-35` -- a relative
deviation of `8.504e-3` (+0.8504 %). F5-1, the phase permitted to edit that
file, corrected both sites (L25 and L29) and moved the register entry from
`declared_variance` to `source_agree`. Nothing downstream moved: both values
reproduce $N_{\\text{steps}} \\approx 5{,}4 \\times 10^{61}$ at the two
significant figures the corpus declares for $N_{\\text{steps}}$. The gate
now rejects the old value -- reverting the document, the register, or both
each produces a P3 or P4 failure (verified by the F5-1 stage-B probes)."""

t = sub(t, OLD_PARA, NEW_PARA, "REFERENCES.md paragraph")

if not fails:
    write(REFS, t)
    print("ok    REFERENCES.md               row + variance paragraph closed"
          "   sha %s -> %s" % (b0[:16], sha(REFS)[:16]))

# ----------------------------------------------------------------- F3_REPORT
b1 = sha(F3R)
t = read(F3R)

t = sub(t,
        "### F3-C \u2014 Documented variance in $\\ell_P$ "
        "(found, recorded, not silently corrected)",
        "### F3-C \u2014 Documented variance in $\\ell_P$ "
        "(found, recorded, closed by F5-1)",
        "F3_REPORT.md F3-C heading")

t = sub(t,
        "Remediation is deferred to a phase permitted to edit `01_PARADOX_AND_SCALE.md`.",
        "Remediation was deferred to a phase permitted to edit "
        "`01_PARADOX_AND_SCALE.md`; **F5-1 closed it on 2026-10-05** by correcting "
        "both sites to `1.62 \\times 10^{-35}` and switching the register from "
        "`declared_variance` to `source_agree`. The pre-fix state now fails the gate "
        "(stage-B probe B4: `P4 SITE_VALUE ... disagrees with the authoritative value "
        "1.616255e-35 at 3 s.f.`).",
        "F3_REPORT.md F3-C closure")

t = sub(t,
        "| R4 | Decide the F3-C remediation (change `1.63` to `1.62` in "
        "`01_PARADOX_AND_SCALE.md`) | open \u2014 needs a phase permitted to edit "
        "that file |",
        "| R4 | Decide the F3-C remediation (change `1.63` to `1.62` in "
        "`01_PARADOX_AND_SCALE.md`) | **CLOSED 2026-10-05 (F5-1)** \u2014 both sites "
        "corrected, register `declared_variance` -> `source_agree`, and reverting "
        "either side fails P3/P4 (probes B1--B4) |",
        "F3_REPORT.md R4 row")

t = sub(t,
        "Nothing in \u00a78 is asserted as solved.",
        "Rows in \u00a78 marked **CLOSED** carry their own proof; nothing marked "
        "*open* or *deferred* is asserted as solved.",
        "F3_REPORT.md closing sentence")

if not fails:
    write(F3R, t)
    print("ok    F3_REPORT.md                F3-C heading + closure + R4  "
          "   sha %s -> %s" % (b1[:16], sha(F3R)[:16]))

print()
if fails:
    print("FAILURES (%d):" % len(fails))
    for f in fails:
        print("  - " + f)
    print("STAGE C: FAIL")
    sys.exit(1)
print("STAGE C: PASS")
sys.exit(0)
