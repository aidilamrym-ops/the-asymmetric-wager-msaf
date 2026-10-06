# -*- coding: utf-8 -*-
import io, json, os, subprocess, hashlib
ROOT = r"D:\THE ASYMMETRIC WAGER"
PY = r"C:\Python314\python.exe"
GATE = os.path.join(ROOT, "provenance_check.py")
J = os.path.join(ROOT, "external_constants.json")
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
base = open(J,"rb").read(); pre = sha(J)
def run():
    p = subprocess.run([PY,"-u",GATE], capture_output=True, encoding="utf-8",
                       errors="replace", timeout=300, cwd=ROOT)
    return p.returncode, (p.stdout or "")+(p.stderr or "")
rc,out = run(); print("baseline rc=%d tb=%s"%(rc,"Traceback" in out))

def probe(name, qid, sf):
    try:
        d = json.loads(base.decode("utf-8"))
        hit=False
        for q in d.get("quantities",[]):
            if q.get("id")==qid:
                q["sig_figs"]=sf; hit=True
        assert hit, "quantity %s not found"%qid
        io.open(J,"w",encoding="utf-8",newline="").write(
            json.dumps(d,indent=2,ensure_ascii=False)+"\n")
        rc,out = run()
        tb = "Traceback" in out
        kind=None
        for l in out.split("\n"):
            s=l.strip()
            for k in ("KeyError","ValueError","TypeError","AttributeError",
                      "ZeroDivisionError","OverflowError"):
                if s.startswith(k): kind=s[:90]; break
            if kind: break
        fails=[l.strip() for l in out.split("\n") if l.startswith("FAIL  ")]
        print("%-42s rc=%-3d tb=%-5s -> %s"%(name,rc,tb,
              "FALSE-PASS" if rc==0 and not tb else ("CRASH" if tb else "caught")))
        if kind: print("        ! "+kind)
        for f in fails[:2]: print("        | "+f)
        if rc==0 and not tb:
            for l in out.split("\n"):
                if "P5" in l and "DERIVED" in l: print("        # "+l.strip()[:130])
    finally:
        open(J,"wb").write(base)
        assert sha(J)==pre, "RESTORE FAILED "+name

print("=== A1: derived quantities actually USE sig_figs (P5) ===")
probe("A1a UNIVERSE_PIXEL_CONSTANT sf=-1","UNIVERSE_PIXEL_CONSTANT",-1)
probe("A1b UNIVERSE_PIXEL_CONSTANT sf='abc'","UNIVERSE_PIXEL_CONSTANT","abc")
probe("A1c UNIVERSE_PIXEL_CONSTANT sf=1","UNIVERSE_PIXEL_CONSTANT",1)
probe("A1d UNIVERSE_PIXEL_CONSTANT sf=None","UNIVERSE_PIXEL_CONSTANT",None)
probe("A1e ZETA_DERIVATIVE sf='abc'","ZETA_DERIVATIVE_FIRST_ZERO","abc")
print()
rc,out=run(); print("final rc=%d restored=%s"%(rc,sha(J)==pre))
raise SystemExit(0)
