"""Gate the Section 2 zeta claims of DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md.

Before F1 the paper's "REAL ZETA FUNCTION SENSITIVITY TEST SIMULATION DATA"
existed only as prose: no script in this workspace evaluated zeta, and
msaf_visual.py generated its stem plot from a hardcoded literal.  The numbers
were therefore assertable but not re-runnable.

This checker closes that gap.  It reads the claims OUT OF THE DOCUMENT (so a
claim that is deleted, reworded or edited also fails), recomputes them with
mpmath at the documented 100 dps, and compares at the document's own
significant figures.  Editing the document without correcting the arithmetic
turns this checker red; correcting the document without arithmetic behind it
does too.

Checks
  C1  zeta(s_kritis)                    recomputed vs declared
  C2  zeta(s_tergeser)                  recomputed vs declared
  C3  |Delta zeta|                      recomputed vs declared
  C4  internal consistency              |z(shifted) - z(critical)| == declared C3
  C5  the stated law |dzeta| ~ Delta    proportionality constant == declared ratio
  C6  the exact identity                |dzeta| == |zeta'(rho_1)| * Delta_univ
  C7  the tabular rows are n x |dzeta|  all five, n = 1..5, labelled OUTSIDE
  C8  (folded into C7) the ambiguous "NON-EXISTENCE ZONE" label must be gone
  C9  the F1-H provenance artifact      zeta_pixel_results.json exists, says
                                        PASS, was written at this dps, and its
                                        dzeta.abs agrees with the document

C9 is what closes the F1-H residual: the published figures are now produced by
zeta_pixel_producer.py and that production file is a condition of this gate
passing, not optional evidence.

Exit 0 = every claim verified.  Exit 1 = a claim is missing or wrong.
Exit 2 = tool not run (interpreter/document unavailable).

usage: python msaf_zeta_check.py
"""
import io
import os
import re
import sys

EXIT_NOT_RUN = 2
EXIT_FAIL = 1
EXIT_OK = 0

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "DRAF_AKADEMIS_DAN_SIMULASI_RIIL.md")

# Document-declared constants (SI, CODATA 2022 for the Planck length).
L_P = "1.616255e-35"
D_OBS = "8.8e26"

DPS = 100  # the document states "(100 DPS Precision)"

# --- number handling --------------------------------------------------------
NUM = r"([+-]?[0-9][0-9,]*)"


def to_mpf(text):
    """Parse an Indonesian-formatted decimal ('3,187') into a Decimal-free float
    via mpmath, so 1e-62 magnitudes keep their precision."""
    import mpmath as mp
    return mp.mpf(text.replace(",", "."))


def mantissa_nsig(text):
    """Significant figures the document printed: '1,456760' -> 7."""
    digits = text.lstrip("+-").replace(",", "").lstrip("0")
    digits = digits.rstrip("0") if set(digits) <= {"0"} else digits
    return len(digits) or 1


def sci_pair(mant_text, exp_text):
    return to_mpf(mant_text) * mp_power10(int(exp_text))


def mp_power10(e):
    import mpmath as mp
    return mp.mpf(10) ** e


def rel_err(declared, computed):
    import mpmath as mp
    if declared == 0:
        return mp.mpf(0) if computed == 0 else mp.inf
    return abs(declared - computed) / abs(declared)


def sig_tol(nsig):
    import mpmath as mp
    # half a unit in the last stated significant figure
    return mp.mpf("0.5") * mp_power10(1 - nsig)


def check_scalar(tag, label, declared, computed, nsig):
    """Tolerance is necessary but not sufficient.

    At 5 sf the half-unit window is 5e-5, so a misrounded last digit -- the
    document stating -6,1298 where the value rounds to -6,1299 -- sits inside
    it and passes a pure relative-error test.  The published figure must also
    be the correctly rounded one.
    """
    import mpmath as mp
    e = rel_err(declared, computed)
    tol = sig_tol(nsig)
    (ok if e <= tol else fail)(
        "%s %s: %d sf, rel=%.3e, tol=%.1e" % (tag, label, nsig, e, tol))
    if e > tol:
        return
    got, want = mp.nstr(computed, nsig), mp.nstr(declared, nsig)
    (ok if got == want else fail)(
        "%s %s rounded to %d sf: computed %s, document states %s"
        % (tag, label, nsig, got, want))


# --- claim extraction -------------------------------------------------------
RE_KRITIS = re.compile(
    r"\\zeta\(s_\{\\text\{kritis\}\}\)\s*\\approx\s*(?:\\mathbf\{)?"
    + NUM + r"\s*\\times\s*10\^\{(-?\d+)\}\s*([+-])\s*"
    + NUM + r"\s*\\times\s*10\^\{(-?\d+)\}i")

RE_TERGESER = re.compile(
    r"\\zeta\(s_\{\\text\{tergeser\}\}\)\s*\\approx\s*(?:\\mathbf\{)?"
    + NUM + r"\s*\\times\s*10\^\{(-?\d+)\}\s*([+-])\s*"
    + NUM + r"\s*\\times\s*10\^\{(-?\d+)\}i")

RE_DZETA = re.compile(
    r"Deviation Magnitude.*?\\approx\s*(?:\\mathbf\{)?"
    + NUM + r"\s*\\times\s*10\^\{(-?\d+)\}")

RE_GRADIENT = re.compile(r"gradient ratio\s*\$?\s*\\approx\s*" + NUM)

# Superscript exponent of the tabular rows, which use Unicode 'x 10^-62'.
SUPS = {"\u2070": "0", "\u00b9": "1", "\u00b2": "2", "\u00b3": "3",
        "\u2074": "4", "\u2075": "5", "\u2076": "6", "\u2077": "7",
        "\u2078": "8", "\u2079": "9", "\u207b": "-"}

failures = []


def fail(msg):
    failures.append(msg)
    print("  FAIL  %s" % msg)


def ok(msg):
    print("  ok    %s" % msg)


def parse_sci(match, label, groups):
    """groups = (index_of_mantissa, index_of_exponent) -> (value, nsig)."""
    import mpmath as mp
    txt = match.group(groups[0])                 # e.g. '3,187' or '-6,1299'
    mant = mp.mpf(txt.replace(",", "."))         # Indonesian decimal comma
    exp = int(match.group(groups[1]))
    return mant * mp_power10(exp), mantissa_nsig(txt)


def main():
    try:
        import mpmath as mp
    except ImportError:
        print("TOOL NOT RUN: mpmath is unavailable.")
        return EXIT_NOT_RUN

    if not os.path.isfile(DOC):
        print("TOOL NOT RUN: document not found at %s" % DOC)
        return EXIT_NOT_RUN

    src = io.open(DOC, encoding="utf-8").read()
    print("=" * 96)
    print("# MSAF zeta-shift gate -- %s" % os.path.basename(DOC))
    print("# mpmath %s at dps=%d ; Delta_univ = lP / D_obs" % (mp.__version__, DPS))
    print("=" * 96)

    m_kr = RE_KRITIS.search(src)
    m_te = RE_TERGESER.search(src)
    m_dz = RE_DZETA.search(src)
    m_gr = RE_GRADIENT.search(src)
    for name, match in (("zeta(s_kritis)", m_kr), ("zeta(s_tergeser)", m_te),
                        ("|Delta zeta|", m_dz), ("gradient ratio", m_gr)):
        if match is None:
            fail("claim %r not found in the document" % name)

    if failures:
        print("\nGATE: FAIL (claims missing -- cannot verify what is not stated)")
        return EXIT_FAIL

    # --- declared values, straight from the document ------------------------
    # group indices: 1=Re mantissa, 2=Re exponent, 3=sign before Im,
    #                4=Im mantissa, 5=Im exponent
    d_kr_re, ns_kr_re = parse_sci(m_kr, "zeta(s_kritis) Re", (1, 2))
    d_kr_im = ((mp.mpf(1) if m_kr.group(3) == "+" else mp.mpf(-1))
               * to_mpf(m_kr.group(4)) * mp_power10(int(m_kr.group(5))))
    ns_kr_im = mantissa_nsig(m_kr.group(4))

    d_te_re, ns_te_re = parse_sci(m_te, "zeta(s_tergeser) Re", (1, 2))
    d_te_im = ((mp.mpf(1) if m_te.group(3) == "+" else mp.mpf(-1))
               * to_mpf(m_te.group(4)) * mp_power10(int(m_te.group(5))))
    ns_te_im = mantissa_nsig(m_te.group(4))

    d_dz, ns_dz = parse_sci(m_dz, "|Delta zeta|", (1, 2))
    d_grad = to_mpf(m_gr.group(1))
    ns_grad = mantissa_nsig(m_gr.group(1))

    # --- independent recomputation -----------------------------------------
    mp.mp.dps = DPS
    Delta = mp.mpf(L_P) / mp.mpf(D_OBS)
    z0 = mp.zetazero(1)
    z_kr = mp.zeta(z0)
    z_te = mp.zeta(mp.mpc(mp.re(z0) + Delta, mp.im(z0)))
    dz = z_te - z_kr
    dzp = mp.diff(mp.zeta, z0)

    print("\n--- C1 zeta(s_kritis) ---------------------------------------------")
    print("  declared  = %s + %s i" % (mp.nstr(d_kr_re, 8), mp.nstr(d_kr_im, 8)))
    print("  computed  = %s + %s i" % (mp.nstr(mp.re(z_kr), 10),
                                       mp.nstr(mp.im(z_kr), 10)))
    for lbl, dec, got, ns in (("Re", d_kr_re, mp.re(z_kr), ns_kr_re),
                              ("Im", d_kr_im, mp.im(z_kr), ns_kr_im)):
        check_scalar("C1", lbl, dec, got, ns)

    print("\n--- C2 zeta(s_tergeser) -------------------------------------------")
    print("  declared  = %s + %s i" % (mp.nstr(d_te_re, 10), mp.nstr(d_te_im, 10)))
    print("  computed  = %s + %s i" % (mp.nstr(mp.re(z_te), 12),
                                       mp.nstr(mp.im(z_te), 12)))
    for lbl, dec, got, ns in (("Re", d_te_re, mp.re(z_te), ns_te_re),
                              ("Im", d_te_im, mp.im(z_te), ns_te_im)):
        check_scalar("C2", lbl, dec, got, ns)

    print("\n--- C3 |Delta zeta| ------------------------------------------------")
    print("  declared  = %s" % mp.nstr(d_dz, 10))
    print("  computed  = %s" % mp.nstr(abs(dz), 12))
    check_scalar("C3", "|dzeta|", d_dz, abs(dz), ns_dz)

    print("\n--- C4 internal consistency of the document's own numbers ---------")
    implied = abs(mp.mpc(d_te_re, d_te_im) - mp.mpc(d_kr_re, d_kr_im))
    print("  |declared z(shifted) - declared z(critical)| = %s" % mp.nstr(implied, 12))
    print("  declared |Delta zeta|                        = %s" % mp.nstr(d_dz, 10))
    e = rel_err(d_dz, implied)
    tol = sig_tol(ns_dz)
    (ok if e <= tol else fail)("C4 rel=%.3e, tol=%.1e" % (e, tol))

    print("\n--- C5 the stated proportionality constant ------------------------")
    ratio = abs(dz) / Delta
    print("  declared gradient ratio = %s" % mp.nstr(d_grad, 8))
    print("  computed |dzeta|/Delta  = %s  (= |zeta'(rho_1)|)" % mp.nstr(ratio, 14))
    e = rel_err(d_grad, ratio)
    tol = sig_tol(ns_grad)
    (ok if e <= tol else fail)(
        "C5 %d sf, rel=%.3e, tol=%.1e" % (ns_grad, e, tol))

    print("\n--- C6 the exact identity |dzeta| = |zeta'(rho_1)| * Delta_univ ----")
    lhs = abs(dz)
    rhs = abs(dzp) * Delta
    print("  |dzeta|                = %s" % mp.nstr(lhs, 14))
    print("  |zeta'(rho_1)| * Delta = %s" % mp.nstr(rhs, 14))
    e = rel_err(rhs, lhs)
    (ok if e <= mp.mpf("1e-40") else fail)("C6 rel=%.3e, tol=1e-40" % e)

    print("\n--- C7 the tabular rows must be n x |Delta zeta| -------------------")
    # F2-2: the rows are pixel shifts n >= 1, which lie at distance >= Delta_univ
    # and are therefore OUTSIDE Z_none.  The old label called them the zone.
    OUT = "OUTSIDE $\\mathcal{Z}_{\\text{none}}$"
    if "NON-EXISTENCE ZONE" in src:
        fail("C7 the ambiguous 'NON-EXISTENCE ZONE' row label is back: those rows "
             "are at n >= 1 Delta_univ and are outside Z_none, not inside it")
    checked_rows = 0
    for ln in src.split("\n"):
        fields = ln.split("\t")
        if len(fields) != 4 or OUT not in fields[3]:
            continue
        shift = re.match(r"\s*([0-9]+)", fields[1])
        cell = re.match(r"\s*([+-]?[0-9][0-9,]*)\s*\u00d7\s*10(.*?)(?:\s|$)",
                        fields[2])
        if shift is None or cell is None:
            fail("C7 unparsable table row: %r" % fields[2])
            continue
        n = int(shift.group(1))
        exp_txt = "".join(SUPS.get(ch, ch) for ch in cell.group(2))
        declared_row = to_mpf(cell.group(1)) * mp_power10(int(exp_txt))
        expected = n * abs(dz)
        checked_rows += 1
        e = rel_err(expected, declared_row)
        tol = sig_tol(mantissa_nsig(cell.group(1)))
        (ok if e <= tol else fail)(
            "C7 n=%d: declared=%s expected=%s rel=%.3e tol=%.1e"
            % (n, mp.nstr(declared_row, 10), mp.nstr(expected, 10), e, tol))
    if checked_rows == 0:
        fail("C7 no OUTSIDE-Z_none sweep rows found in the document")
    else:
        print("  (%d tabular rows checked)" % checked_rows)

    # --- C9: the F1-H provenance artifact must exist and agree -----------
    # F1-H recorded that the published figures had no producer in this
    # workspace: the claim was re-derivable but the computation was not
    # recoverable.  zeta_pixel_producer.py is that producer; this check makes
    # its output file a condition of passing rather than optional evidence.
    print("\n--- C9 the F1-H provenance artifact must exist and agree -------")
    ART = os.path.join(HERE, "zeta_pixel_results.json")
    if not os.path.isfile(ART):
        fail("C9 zeta_pixel_results.json is missing -- the F1-H computation "
             "has no provenance file; run zeta_pixel_producer.py")
    else:
        try:
            import json
            with io.open(ART, encoding="utf-8") as fh:
                art = json.load(fh)
        except Exception as exc:
            art = None
            fail("C9 the provenance artifact is not readable JSON: %s" % exc)
        if art is not None:
            if art.get("producer") == "zeta_pixel_producer.py":
                ok("C9 artifact names its producer")
            else:
                fail("C9 artifact producer is %r" % art.get("producer"))
            if art.get("verdict") == "PASS":
                ok("C9 artifact verdict is PASS")
            else:
                fail("C9 artifact verdict is %r, not PASS" % art.get("verdict"))
            if int(art.get("dps", -1)) == DPS:
                ok("C9 artifact dps = %d" % DPS)
            else:
                fail("C9 artifact dps is %r, expected %d" % (art.get("dps"), DPS))
            got = art.get("dzeta", {}).get("abs")
            if got is None:
                fail("C9 artifact has no dzeta.abs")
            elif m_dz is None:
                fail("C9 cannot compare: |Delta zeta| claim not in the document")
            else:
                import mpmath as mp
                g = m_dz.groups()
                declared = to_mpf(g[0]) * mp_power10(int(g[1]))
                e = rel_err(declared, mp.mpf(got))
                if e <= sig_tol(mantissa_nsig(g[0])):
                    ok("C9 artifact dzeta.abs matches the document, rel=%s"
                       % mp.nstr(e, 4))
                else:
                    fail("C9 artifact dzeta.abs=%s disagrees with the document's %s "
                         "(rel=%s)" % (got, mp.nstr(declared, 12), mp.nstr(e, 4)))
            # rho_1 must be the root this run itself just computed, otherwise a
            # forged artifact could carry any root and still have a plausible
            # dzeta.abs copied from the paper.
            fresh_rho = mp.nstr(z0, 60, strip_zeros=False)
            if art.get("rho1") == fresh_rho:
                ok("C9 artifact rho1 is this run's zetazero(1)")
            else:
                fail("C9 artifact rho1 does not match zetazero(1): %r"
                     % art.get("rho1"))
            # internal consistency of the artifact's own complex values
            try:
                re_t, im_t = art["zeta_tergeser"]["re"], art["zeta_tergeser"]["im"]
                re_k, im_k = art["zeta_kritis"]["re"], art["zeta_kritis"]["im"]
                mag = ((mp.mpf(re_t) - mp.mpf(re_k)) ** 2
                       + (mp.mpf(im_t) - mp.mpf(im_k)) ** 2) ** mp.mpf("0.5")
                e_ic = rel_err(mag, mp.mpf(art["dzeta"]["abs"]))
                (ok if e_ic <= mp.mpf("1e-45") else fail)(
                    "C9 artifact |dzeta| equals |tergeser - kritis|, rel=%s"
                    % mp.nstr(e_ic, 4))
                # and dzeta.re / dzeta.im must reproduce from those same two
                # components: they are separately stored, so abs alone would
                # not notice a forged real or imaginary part.
                e_re = rel_err(mp.mpf(re_t) - mp.mpf(re_k),
                               mp.mpf(art["dzeta"]["re"]))
                e_im = rel_err(mp.mpf(im_t) - mp.mpf(im_k),
                               mp.mpf(art["dzeta"]["im"]))
                (ok if e_re <= mp.mpf("1e-45") else fail)(
                    "C9 artifact dzeta.re == tergeser.re - kritis.re, rel=%s"
                    % mp.nstr(e_re, 4))
                (ok if e_im <= mp.mpf("1e-45") else fail)(
                    "C9 artifact dzeta.im == tergeser.im - kritis.im, rel=%s"
                    % mp.nstr(e_im, 4))
            except Exception as exc:
                fail("C9 artifact complex fields unusable: %s" % exc)
            # every stored value must be this run's own computation, not a
            # plausible-looking copy of the published rounded figures.
            fmt = lambda v: mp.nstr(v, 50, strip_zeros=False)
            for key, fresh in (("zeta_kritis", z_kr), ("zeta_tergeser", z_te),
                               ("dzeta", dz)):
                pair = art.get(key) or {}
                if key == "dzeta":
                    exp = {"re": fmt(mp.re(fresh)), "im": fmt(mp.im(fresh)),
                           "abs": fmt(abs(fresh))}
                else:
                    exp = {"re": fmt(mp.re(fresh)), "im": fmt(mp.im(fresh))}
                bad = [c for c, v in exp.items() if pair.get(c) != v]
                if bad:
                    fail("C9 artifact %s.%s does not match this run's "
                         "recomputation" % (key, ", ".join(bad)))
                else:
                    ok("C9 artifact %s matches the recomputation" % key)

    print("\n" + "=" * 96)
    if failures:
        print("GATE: FAIL -- %d claim(s) not verified:" % len(failures))
        for f in failures:
            print("  - %s" % f)
        print("TOOL STATUS: mpmath %s, dps=%d, recomputed from definitions." % (mp.__version__, DPS))
        return EXIT_FAIL

    print("GATE: PASS -- every Section 2 claim reproduced at its stated precision.")
    print("TOOL STATUS: mpmath %s, dps=%d, recomputed from definitions." % (mp.__version__, DPS))
    print("lean/coqc/isabelle/dkcheck/z3 NOT RUN.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
