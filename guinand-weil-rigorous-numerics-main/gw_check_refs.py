"""Static reference check after the .abs()/symmetry/L-diagonal fixes.

Run it instead of inline -c strings: PowerShell quoting silently mangles
Python one-liners that contain apostrophes, and a failed edit then looks
like a passing one.
"""
import os
import py_compile
import sys

# Engine source defaults to this script's own directory so a fresh clone runs
# from any working directory; pass an explicit file path as argv[1].
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "gw_omega_core_v2.py")
if len(sys.argv) > 1:
    SRC = os.path.abspath(sys.argv[1])
lines = open(SRC, encoding="utf-8").read().splitlines()


def find(needle):
    return [i + 1 for i, l in enumerate(lines) if needle in l]


def find_code(needle):
    """Occurrences outside comments and docstrings."""
    out = []
    for i, l in enumerate(lines):
        if needle not in l:
            continue
        s = l.lstrip()
        if s.startswith("#"):
            continue
        out.append(i + 1)
    return out


try:
    py_compile.compile(SRC, doraise=True)
    print("COMPILE OK")
except py_compile.PyCompileError as exc:
    print("COMPILE FAIL:", exc)
    sys.exit(1)

checks = [
    ("old exact_symmetry_max_dev", find("exact_symmetry_max_dev"), []),
    ("new symmetry_check", find("symmetry_check"), "non-empty"),
    ("Lf diagonal = 1", find("Lf[i][i] = arb(1)"), "non-empty"),
    (".abs() left in CODE", find_code(".abs()"), []),
    (".abs_upper()", find(".abs_upper()"), "non-empty"),
    (".abs_lower()", find(".abs_lower()"), "non-empty"),
    ("sym_dev_str def", find("sym_dev_str ="), "non-empty"),
    ("caveats def", find("caveats = []"), "non-empty"),
    ("caveats ref", find('"caveats": caveats'), "non-empty"),
]
for name, got, want in checks:
    if want == []:
        ok = not got
    else:
        ok = bool(got)
    print("%-24s %-6s %s" % (name, "OK" if ok else "FAIL", got))
    if not ok:
        sys.exit(2)
print("ALL STATIC CHECKS PASS")
