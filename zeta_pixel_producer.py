"""Produce the per-pixel zeta deviation numbers of F1-H from first principles.

F1_REPORT.md section 5 item 1 recorded this residual:

    Re = 1.43864420885e-62, Im = 2.2903036742e-63,
    |Delta zeta| = 1.45676081388e-62 reproduce to 7 digits, but NO SCRIPT IN
    THIS WORKSPACE PRODUCES THEM.  msaf_zeta_check.py re-derives the claim from
    the DRAF and the identity, which is not the same as recovering the original
    computation.

This file is that missing script.  Nothing here is taken on trust:

  1. rho_1 is obtained from mpmath's own zetazero(1) at the documented
     100 dps, NOT from a truncated 14-digit literal.  The distinction matters:
     with 14 digits zeta(0.5 + rho_1 i) bottoms out near 5e-16 from the error
     in the root, which is fifteen orders of magnitude away from the published
     -6.1299e-102.  Only a root accurate to the working precision reproduces it.
  2. Delta_univ is the exact quotient of the two declared inputs L_P / D_OBS.
  3. s_tergeser = s_kritis + Delta_univ along the real axis.
  4. Every published figure is read OUT OF DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md
     and compared at the document's own significant figures, so editing the
     paper without recomputing turns this script red.
  5. The full-precision derivation is written to zeta_pixel_results.json, and
     the written file is re-read and re-checked before exit.

What this script does NOT do: it does not assert that the root or the value is
a result of this workspace's OMEGA-CORE run.  mpmath's zetazero is the tool
that ran, and the tool status is printed.

Exit 0 = every published figure reproduced and the artifact agrees.
Exit 1 = a figure is missing, wrong, or the artifact disagrees.
Exit 2 = tool not run (interpreter, mpmath, or document unavailable).

usage: python zeta_pixel_producer.py
"""
import io
import json
import os
import sys

import mpmath as mp

import msaf_zeta_check as MZ

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = MZ.DOC                      # the same document the other gate reads
ARTIFACT = os.path.join(HERE, "zeta_pixel_results.json")

EXIT_OK, EXIT_FAIL, EXIT_NOTRUN = 0, 1, 2
DPS = MZ.DPS

failures = []
notes = []


def fail(msg):
    failures.append(msg)
    print("  FAIL  %s" % msg)


def ok(msg):
    print("  ok    %s" % msg)


def to_str(v, digits=50):
    return mp.nstr(v, digits, strip_zeros=False)


def parse_declared(match, label):
    """Return (re_value, im_value, nsig) for a two-term scientific claim."""
    if match is None:
        fail("%s: not found in the document" % label)
        return None
    g = match.groups()
    re_part = MZ.to_mpf(g[0]) * MZ.mp_power10(int(g[1]))
    im_part = MZ.to_mpf(g[3]) * MZ.mp_power10(int(g[4]))
    sign = -1 if g[2] == "-" else 1
    return re_part, sign * im_part, MZ.mantissa_nsig(g[0]) + 0


def compare(label, computed, declared, nsig):
    e = MZ.rel_err(declared, computed)
    tol = MZ.sig_tol(nsig)
    if e > tol:
        fail("%-22s computed=%s declared=%s rel=%s > tol=%s"
             % (label, mp.nstr(computed, 16), mp.nstr(declared, 16),
                mp.nstr(e, 4), mp.nstr(tol, 4)))
        return
    ok("%-22s computed=%-24s declared=%-24s rel=%s" % (
        label, mp.nstr(computed, 12), mp.nstr(declared, 12), mp.nstr(e, 4)))
    # Tolerance alone is not enough: at 5 sf the half-unit window is 5e-5, and
    # a misrounded last digit ("6,1298" instead of "6,1299") sits inside it.
    # The published figure must also be the correctly rounded one.
    got, want = mp.nstr(computed, nsig), mp.nstr(declared, nsig)
    if got == want:
        ok("%-22s correctly rounded to %d sf (%s)" % ("", nsig, got))
    else:
        fail("%-22s misrounded: computed rounds to %s, document states %s"
             % (label, got, want))


def main():
    print("=" * 78)
    print("ZETA PIXEL PRODUCER -- F1-H provenance")
    print("=" * 78)

    if not os.path.isfile(DOC):
        print("\nPRODUCER: TOOL NOT RUN -- %s missing" % os.path.basename(DOC))
        return EXIT_NOTRUN
    try:
        src = io.open(DOC, encoding="utf-8").read()
    except Exception as exc:
        print("\nPRODUCER: TOOL NOT RUN -- cannot read document: %s" % exc)
        return EXIT_NOTRUN

    print("\n--- 1. read the published figures out of the DRAF --------------")
    mk = MZ.RE_KRITIS.search(src)
    mt = MZ.RE_TERGESER.search(src)
    md = MZ.RE_DZETA.search(src)
    pub_k = parse_declared(mk, "zeta(s_kritis)")
    pub_t = parse_declared(mt, "zeta(s_tergeser)")
    if md is None:
        fail("|Delta zeta|: not found in the document")
        pub_d, nsig_d = None, 1
    else:
        g = md.groups()
        pub_d = MZ.to_mpf(g[0]) * MZ.mp_power10(int(g[1]))
        nsig_d = MZ.mantissa_nsig(g[0])
        ok("|Delta zeta| read from the document: %s e%d, %d sf"
           % (g[0], int(g[1]), nsig_d))
    if pub_k:
        ok("zeta(s_kritis)  read from the document")
    if pub_t:
        ok("zeta(s_tergeser) read from the document")

    print("\n--- 2. recompute from first principles -------------------------")
    mp.mp.dps = DPS
    L_P = mp.mpf(MZ.L_P)
    D_OBS = mp.mpf(MZ.D_OBS)
    Delta = L_P / D_OBS
    print("  dps                     = %d" % DPS)
    print("  L_P / D_OBS             = %s" % to_str(Delta, 20))
    print("  tool status             = mpmath %s, zetazero(1)" % mp.__version__)

    s0 = mp.zetazero(1)
    s1 = s0 + Delta
    print("  rho_1 (first 40 sf)     = %s" % mp.nstr(s0, 40))
    if abs(mp.im(s0) - mp.mpf("14.1347251417346937904572519835624702707")) > mp.mpf("1e-30"):
        fail("rho_1 does not match the documented first non-trivial root")
    else:
        ok("rho_1 matches the documented first non-trivial root")

    z0 = mp.zeta(s0)
    z1 = mp.zeta(s1)
    dz = z1 - z0
    zp = mp.diff(mp.zeta, s0)
    ident = abs(zp) * Delta

    print("\n--- 3. compare at the document's own significant figures ------")
    if pub_k:
        compare("zeta_kritis Re", mp.re(z0), pub_k[0], pub_k[2])
        compare("zeta_kritis Im", mp.im(z0), pub_k[1], pub_k[2])
    if pub_t:
        compare("zeta_tergeser Re", mp.re(z1), pub_t[0], pub_t[2])
        compare("zeta_tergeser Im", mp.im(z1), pub_t[1], pub_t[2])
    if pub_d is not None:
        compare("|Delta zeta|", abs(dz), pub_d, nsig_d)

    e_ident = MZ.rel_err(ident, abs(dz))
    if e_ident <= mp.mpf("1e-40"):
        ok("|zeta'(rho_1)| * Delta == |Delta zeta|, rel=%s" % mp.nstr(e_ident, 4))
    else:
        fail("|zeta'(rho_1)| * Delta != |Delta zeta|, rel=%s" % mp.nstr(e_ident, 6))

    print("\n--- 4. write the derivation artifact ---------------------------")
    artifact = {
        "producer": "zeta_pixel_producer.py",
        "provenance": "F1-H: produced from first principles; msaf_zeta_check.py "
                      "re-derives the claim, this script recovers the computation.",
        "tool": "mpmath %s" % mp.__version__,
        "dps": DPS,
        "inputs": {"L_P": MZ.L_P, "D_OBS": MZ.D_OBS},
        "Delta_univ": to_str(Delta, 40),
        "rho1": to_str(s0, 60),
        "zeta_kritis": {"re": to_str(mp.re(z0), 50), "im": to_str(mp.im(z0), 50)},
        "zeta_tergeser": {"re": to_str(mp.re(z1), 50), "im": to_str(mp.im(z1), 50)},
        "dzeta": {"re": to_str(mp.re(dz), 50), "im": to_str(mp.im(dz), 50),
                  "abs": to_str(abs(dz), 50)},
        "identity": {"abs_zeta_prime_times_Delta": to_str(ident, 50),
                     "rel_err_vs_dzeta": to_str(e_ident, 8)},
        "published": {
            "zeta_kritis_re": to_str(pub_k[0], 25) if pub_k else None,
            "zeta_kritis_im": to_str(pub_k[1], 25) if pub_k else None,
            "zeta_tergeser_re": to_str(pub_t[0], 25) if pub_t else None,
            "zeta_tergeser_im": to_str(pub_t[1], 25) if pub_t else None,
            "dzeta_abs": to_str(pub_d, 25) if pub_d is not None else None,
        },
        "verdict": "PASS" if not failures else "FAIL",
    }
    with io.open(ARTIFACT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(artifact, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    ok("wrote %s (%d bytes)" % (os.path.basename(ARTIFACT),
                                os.path.getsize(ARTIFACT)))

    print("\n--- 5. read back what was just written, as a write check ------")
    # This is a WRITE-INTEGRITY check, not tamper detection: step 4 overwrites
    # the file unconditionally, so a pre-existing corrupted artifact is replaced
    # before it is read here.  Detecting tampering in an already-written file is
    # the job of the consumer, msaf_zeta_check.py check C9, which reads the
    # artifact without rewriting it.
    try:
        with io.open(ARTIFACT, encoding="utf-8") as fh:
            back = json.load(fh)
    except Exception as exc:
        fail("artifact is not readable JSON: %s" % exc)
        back = None
    if back is not None:
        probes = [
            ("dps", back.get("dps"), DPS),
            ("Delta_univ", back.get("Delta_univ"), to_str(Delta, 40)),
            ("rho1", back.get("rho1"), to_str(s0, 60)),
            ("zeta_kritis.re", back.get("zeta_kritis", {}).get("re"), to_str(mp.re(z0), 50)),
            ("zeta_tergeser.re", back.get("zeta_tergeser", {}).get("re"), to_str(mp.re(z1), 50)),
            ("dzeta.abs", back.get("dzeta", {}).get("abs"), to_str(abs(dz), 50)),
        ]
        for name, got, want in probes:
            if got == want:
                ok("artifact %-22s round-trips" % name)
            else:
                fail("artifact %-22s does not round-trip: %r != %r" % (name, got, want))
        if back.get("verdict") == ("PASS" if not failures else "FAIL"):
            ok("artifact verdict matches this run")
        else:
            fail("artifact verdict is %r but this run is %s"
                 % (back.get("verdict"), "PASS" if not failures else "FAIL"))

    print("\n" + "=" * 78)
    if failures:
        print("PRODUCER: FAIL -- %d condition(s):" % len(failures))
        for f in failures:
            print("  - %s" % f)
        print("TOOL STATUS: mpmath %s, dps=%d, zetazero(1)." % (mp.__version__, DPS))
        print("lean/coqc/isabelle/dkcheck/z3 NOT RUN.")
        return EXIT_FAIL
    print("PRODUCER: every published figure reproduced from first principles.")
    print("TOOL STATUS: mpmath %s, dps=%d, zetazero(1)." % (mp.__version__, DPS))
    print("lean/coqc/isabelle/dkcheck/z3 NOT RUN.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
