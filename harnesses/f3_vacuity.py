# -*- coding: utf-8 -*-
"""Vacuity probe: does provenance_check.py have an untested false-pass vector?

Two hypotheses from F3_REPORT section 7 residuals:
  H1 (R1) a quantity may declare sig_figs = 0 / 1 / negative, and P4's
          relative tolerance 5*10^-sf then makes the comparison vacuous;
          a non-integer sig_figs may also raise instead of failing cleanly.
  H2 (R2) P8 is `val in flat`, so a REFERENCES.md entry that merely CONTAINS
          the value as a substring satisfies P8 without stating it.

Each probe mutates real files in TEMP copies? No -- provenance_check.py reads
from its own directory, so the probe snapshots the real bytes, mutates, runs,
restores, and asserts byte-identical. One probe at a time, try/finally.
"""
import io, json, os, subprocess, hashlib, traceback

ROOT = r"D:\THE ASYMMETRIC WAGER"
PY = r"C:\Python314\python.exe"
GATE = os.path.join(ROOT, "provenance_check.py")
J = os.path.join(ROOT, "external_constants.json")
R = os.path.join(ROOT, "REFERENCES.md")

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def run():
    p = subprocess.run([PY, "-u", GATE], capture_output=True, encoding="utf-8",
                       errors="replace", timeout=300, cwd=ROOT)
    return p.returncode, (p.stdout or "") + (p.stderr or "")

pre_j, pre_r = sha(J), sha(R)
print("baseline sha  json=%s  refs=%s" % (pre_j[:16], pre_r[:16]))
rc, out = run()
print("baseline rc=%d  traceback=%s" % (rc, "Traceback" in out))
for l in out.strip().split("\n")[:6]:
    print("   | " + l[:140])
print()

results = []

def probe(name, mutate_json=None, mutate_refs=None):
    """Returns (rc, verdict) with files restored in a finally block."""
    global pre_j, pre_r
    try:
        if mutate_json:
            raw = io.open(J, encoding="utf-8", newline="").read()
            d = json.loads(raw)
            mutate_json(d)
            io.open(J, "w", encoding="utf-8", newline="").write(
                json.dumps(d, indent=2, ensure_ascii=False) + "\n")
        if mutate_refs:
            t = io.open(R, encoding="utf-8", newline="").read()
            t2 = mutate_refs(t)
            assert t2 != t, "%s: refs mutation was a no-op" % name
            io.open(R, "w", encoding="utf-8", newline="").write(t2)
        rc, out = run()
        tb = "Traceback" in out
        # which conditions failed
        fails = [l.strip() for l in out.split("\n")
                 if l.startswith("FAIL  ")]
        verdict = "FALSE-PASS" if (rc == 0) else ("crash" if tb else "caught")
        results.append((name, rc, tb, verdict, [f[:95] for f in fails][:2]))
        print("%-34s rc=%-3d traceback=%-5s -> %s"
              % (name, rc, tb, verdict))
        if fails:
            for f in fails[:2]:
                print("        | " + f)
        return rc, out
    finally:
        if mutate_json:
            io.open(J, "w", encoding="utf-8", newline="").write(
                io.open(J, encoding="utf-8", newline="").read())  # placeholder
        # full restore happens below

# real restore machinery
base_J = open(J, "rb").read()
base_R = open(R, "rb").read()

def probe2(name, mutate_json=None, mutate_refs=None):
    try:
        if mutate_json:
            d = json.loads(base_J.decode("utf-8"))
            mutate_json(d)
            io.open(J, "w", encoding="utf-8", newline="").write(
                json.dumps(d, indent=2, ensure_ascii=False) + "\n")
        if mutate_refs:
            t = base_R.decode("utf-8")
            t2 = mutate_refs(t)
            assert t2 != t, "%s: no-op" % name
            io.open(R, "w", encoding="utf-8", newline="").write(t2)
        rc, out = run()
        tb = "Traceback" in out
        fails = [l.strip() for l in out.split("\n") if l.startswith("FAIL  ")]
        verdict = ("FALSE-PASS" if rc == 0 else
                   ("CRASH" if tb else "caught"))
        results.append((name, rc, tb, verdict))
        print("%-36s rc=%-3d tb=%-5s -> %s" % (name, rc, tb, verdict))
        for f in fails[:2]:
            print("        | " + f)
        if tb:
            for l in out.split("\n"):
                if l.strip().startswith(("KeyError","ValueError","TypeError",
                                         "AttributeError","IndexError")):
                    print("        ! " + l.strip())
                    break
        return rc, out
    finally:
        open(J, "wb").write(base_J)
        open(R, "wb").write(base_R)
        assert sha(J) == pre_j and sha(R) == pre_r, "RESTORE FAILED for " + name

def set_sf(sf):
    def f(d):
        for q in d.get("quantities", []):
            if q.get("id") == "PLANCK_LENGTH":
                q["sig_figs"] = sf
    return f

def wrong_planck(sf):
    def f(d):
        for q in d.get("quantities", []):
            if q.get("id") == "PLANCK_LENGTH":
                q["value"] = "1.6e-35"
                q["sig_figs"] = sf
                for s in q.get("sites", []):
                    if "01_PARADOX" in str(s.get("file", "")):
                        s["needle"] = "1{,}6 \\times 10^{-35}"
                        s["doc_value"] = "1.6e-35"
    return f

print("=== H1: sig_figs sanity (P1 / P4) ===")
probe2("H1a sig_figs = 0",              set_sf(0))
probe2("H1b sig_figs = -1",             set_sf(-1))
probe2("H1c sig_figs = 1",              set_sf(1))
probe2("H1d sig_figs = 'abc'",          set_sf("abc"))
probe2("H1e sig_figs = None",           set_sf(None))
probe2("H1f sig_figs = 999999",         set_sf(999999))
probe2("H1g wrong value @ sf=1",        wrong_planck(1))
probe2("H1h wrong value @ sf=0",        wrong_planck(0))

print()
print("=== H2: P8 substring (REFERENCE_FACT_VALUE) ===")
def sub_rail(victim, repl):
    def f(t):
        assert victim in t, "victim %r absent" % victim
        return t.replace(victim, repl, 1)
    return f
probe2("H2a 5.559 -> 5.559123",         None, sub_rail("5.559", "5.559123"))
probe2("H2b 3000175332800 -> x3000175332800", None,
       sub_rail("3000175332800", "930001753328009"))
probe2("H2c 103800788359 -> 1038007883590", None,
       sub_rail("103800788359", "1038007883590"))

print()
print("=== restore + final baseline ===")
rc, out = run()
print("final rc=%d  restored_ok=%s" % (rc, sha(J) == pre_j and sha(R) == pre_r))
print()
fp = [r for r in results if r[3] == "FALSE-PASS"]
cr = [r for r in results if r[3] == "CRASH"]
print("SUMMARY: %d probes, %d FALSE-PASS, %d CRASH"
      % (len(results), len(fp), len(cr)))
for r in fp: print("  FALSE-PASS:", r[0])
for r in cr: print("  CRASH     :", r[0])
raise SystemExit(1 if (fp or cr) else 0)
