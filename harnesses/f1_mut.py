# -*- coding: utf-8 -*-
"""F1 fault injection: mutate the production result and see which defects the
gate catches.  A gate that cannot fail is not evidence."""
import json, os, shutil, subprocess, sys, tempfile

D = r"D:\THE ASYMMETRIC WAGER\guinand-weil-rigorous-numerics-main"
SRC = os.path.join(D, "omega_core_v2_results.json")
PY  = sys.executable
base = json.load(open(SRC, encoding="utf-8"))

MUT = [
  ("baseline (unmutated)",                 lambda r: None),
  ("lambda_min_lower_bound -> '1' (absurd but > 0)", lambda r: r.__setitem__("lambda_min_lower_bound", "1")),
  ("lambda_min_lower_bound -> '1e-99999'",  lambda r: r.__setitem__("lambda_min_lower_bound", "1e-99999")),
  ("lambda_min_lower_bound -> '-1'",        lambda r: r.__setitem__("lambda_min_lower_bound", "-1")),
  ("bound_detail deleted",                  lambda r: r.pop("bound_detail")),
  ("bound_detail.norm_Linv_F -> 1e-1",      lambda r: r["bound_detail"].__setitem__("norm_Linv_F_upper", "1e-1")),
  ("N -> 7 (dim no longer 2N+1)",           lambda r: r.__setitem__("N", 7)),
  ("dim -> 999",                            lambda r: r.__setitem__("dim", 999)),
  ("n_neg -> 1",                            lambda r: r.__setitem__("n_neg", 1)),
  ("max_entry_radius -> '1e-40' (too big)", lambda r: r.__setitem__("max_entry_radius", "1e-40")),
  ("symmetry_dev -> '0.0001'",              lambda r: r.__setitem__("symmetry_dev", "0.0001")),
  ("symmetry_exact -> False",               lambda r: r.__setitem__("symmetry_exact", False)),
  ("sha256 -> 64 x's (length only)",        lambda r: r.__setitem__("sha256", "x"*64)),
  ("caveats -> ['something']",              lambda r: r.__setitem__("caveats", ["something"])),
  ("anomalies -> ['something']",            lambda r: r.__setitem__("anomalies", ["something"])),
  ("non_result -> True",                    lambda r: r.__setitem__("non_result", True)),
  ("undetermined_pivot -> 42",              lambda r: r.__setitem__("undetermined_pivot", 42)),
  ("anomaly -> True",                       lambda r: r.__setitem__("anomaly", True)),
  ("n_pos -> 1600 (breaks n_pos==dim)",     lambda r: r.__setitem__("n_pos", 1600)),
  ("whole row deleted",                     lambda r: r.pop("lambda_min_lower_bound")),
]

tmp = tempfile.mkdtemp(prefix="f1_mut_")
print("%-46s %-8s %s" % ("MUTATION", "CAUGHT", "reason"))
print("-"*118)
results = []
for name, fn in MUT:
    rows = json.loads(json.dumps(base))
    fn(rows[0])
    path = os.path.join(tmp, "m.json")
    json.dump(rows, open(path, "w", encoding="utf-8"), indent=2, default=str)
    p = subprocess.run([PY, os.path.join(D,"gw_verify_production.py"), path],
                       cwd=D, capture_output=True, text=True, encoding="utf-8", errors="replace")
    caught = (p.returncode != 0)
    reason = ""
    if caught:
        for line in (p.stdout or "").splitlines():
            if line.strip().startswith("-"):
                reason = line.strip()[:64]; break
        if not reason: reason = (p.stderr or "")[:64].replace("\n"," ")
    else:
        # find what the gate printed
        reason = "gate passed"
    results.append((name, caught, reason))
    print("%-46s %-8s %s" % (name, "YES" if caught else "*** NO ***", reason))

ncaught = sum(1 for _,c,_ in results if c)
print("-"*118)
print("gate caught %d / %d injected defects" % (ncaught, len(results)))
missed = [n for n,c,_ in results if not c]
if missed:
    print("NOT caught (gate blind):")
    for m in missed: print("   -", m)
shutil.rmtree(tmp, ignore_errors=True)
