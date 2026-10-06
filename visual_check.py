#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F2-6: the R_tail panel must say what it actually shows.

Residual F1-N #4 left a design question open: "whether the `p` axis should be
plotted at all, given it carries no information over 2000-18000 bits."

F2-6 answered it -- keep the axis, because the inertness over a *stated range*
is the finding -- and then found that the panel was not self-contained: the
two numbers that make "flat" meaningful were printed to stdout only, and the
two vertical markers were labelled as if the curve moved through them.

This gate renders `msaf_visual.py` under a headless backend and inspects the
**drawn artists**, not the source text:

  V1  the module runs and produces exactly two panels
  V2  panel 1's x-axis names the parameter p
  V3  panel 1's title states that the curve is flat
  V4  panel 1 carries the analytic span, the float64-observed span, the
      bits-per-decade figure, and the marker clarification
  V5  both vertical markers identify themselves as certificate operating
      points, not as features of the curve
  V6  the drawn curve is exactly flat in float64, and the span the figure
      declares equals the span that was drawn
  V7  the analytic span equals -(p_hi - p_lo) * Delta_univ * log10(2) at 7 sf
  V8  the bits-per-decade figure equals 1 / (Delta_univ * log10(2)) at 7 sf
  V9  panel 1's legend carries the curve and both markers

Exit 0 = PASS, 1 = FAIL, 2 = TOOL NOT RUN (the module did not render).
"""

import importlib.util
import math
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VISUAL = os.path.join(ROOT, "msaf_visual.py")

_results = []


def ok(msg):
    _results.append(("ok", msg))
    print("ok    " + msg)


def fail(msg):
    _results.append(("FAIL", msg))
    print("FAIL  " + msg)


def half_ulp(nsig):
    return 0.5 * 10.0 ** (1 - nsig)


def close(a, b, nsig=7, tag=""):
    rel = abs(a - b) / abs(b) if b else abs(a - b)
    if rel <= half_ulp(nsig):
        ok("%s matches to %d sf (rel=%.3e)" % (tag, nsig, rel))
    else:
        fail("%s disagrees: got %r, want %r (rel=%.3e, tol=%.1e)"
             % (tag, a, b, rel, half_ulp(nsig)))


def main():
    del _results[:]
    os.environ["MPLBACKEND"] = "Agg"
    import warnings
    warnings.filterwarnings("ignore")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not os.path.isfile(VISUAL):
        fail("V0 %s is missing" % VISUAL)
        print("\nGATE: TOOL NOT RUN -- the module does not exist.")
        return 2

    print("F2-6 VISUAL CHECK -- what the panel draws, not what the source says\n")
    print("-- rendering ----------------------------------------------------")
    try:
        spec = importlib.util.spec_from_file_location("msaf_visual_under_test",
                                                      VISUAL)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as exc:
        fail("V0 msaf_visual.py did not render: %s: %s"
             % (type(exc).__name__, str(exc)[:300]))
        print("\nGATE: TOOL NOT RUN -- nothing was drawn.")
        return 2

    figs = plt.get_fignums()
    if len(figs) != 1:
        fail("V1 expected one figure, got %d" % len(figs))
        print("\nGATE: TOOL NOT RUN -- the figure is unavailable.")
        return 2
    fig = plt.figure(figs[0])
    axes = fig.axes

    print("\n-- V1 panel structure -------------------------------------------")
    if len(axes) == 2:
        ok("V1 exactly two panels")
    else:
        fail("V1 expected two panels, got %d" % len(axes))
    if len(axes) < 1:
        print("\nGATE: TOOL NOT RUN -- no panel to inspect.")
        return 2
    ax1 = axes[0]

    print("\n-- V2 the x-axis names the parameter -----------------------------")
    xl = ax1.get_xlabel()
    if "p" in xl and "Precision" in xl:
        ok("V2 x-axis labels the computational bit precision p: %r" % xl)
    else:
        fail("V2 x-axis does not name the precision parameter: %r" % xl)

    print("\n-- V3 the title states flatness ---------------------------------")
    title = ax1.get_title()
    if "flat" in title.lower():
        ok("V3 title declares the curve flat: %r" % title)
    else:
        fail("V3 title does not declare flatness: %r" % title)

    print("\n-- V4 the panel is self-contained --------------------------------")
    blob = "\n".join(t.get_text() for t in ax1.texts)
    need = {
        "analytic span": lambda s: s.split("\n")[0].startswith("flat:")
                                  and "bits =" in s.split("\n")[0],
        "float64 observed span": lambda s: "float64 observed span" in s,
        "bits per decade": lambda s: "decade would need" in s and "bits" in s,
        "markers are not curve features": lambda s: "not features of this curve" in s,
    }
    for name, pred in need.items():
        if pred(blob):
            ok("V4 figure states the %s" % name)
        else:
            fail("V4 figure does not state the %s; annotation reads:\n%s"
                 % (name, blob or "<empty>"))

    print("\n-- V5 markers are certificate operating points -------------------")
    # The authoritative label list is the legend: axvline artists do not expose
    # their labels through get_lines() reliably across matplotlib versions.
    leg = ax1.get_legend()
    leg_labels = [t.get_text() for t in leg.get_texts()] if leg else []
    markers = [l for l in leg_labels if "certificate" in l.lower()
               or "pivot" in l.lower() or "verified" in l.lower()]
    if len(markers) != 2:
        fail("V5 expected two certificate markers in the legend, got %r" % leg_labels)
    else:
        bad = [m for m in markers if not m.lower().startswith("certificate")]
        if bad:
            fail("V5 marker(s) do not identify themselves as certificate "
                 "operating points: %r" % bad)
        else:
            ok("V5 both markers are labelled as certificate operating points: %r"
               % markers)

    print("\n-- V6 the drawn curve really is flat -----------------------------")
    ys = list(ax1.get_lines()[0].get_ydata()) if ax1.get_lines() else []
    if not ys:
        fail("V6 panel 1 has no curve to measure")
    else:
        drawn = float(max(ys)) - float(min(ys))
        declared = float(getattr(mod, "log10_span_f64", float("nan")))
        if drawn == 0.0:
            ok("V6 drawn span is exactly 0.0 in float64 (%d points)" % len(ys))
        else:
            fail("V6 drawn curve is not flat: span = %r -- the title and every "
                 "document describing this sweep would now be wrong" % drawn)
        close(drawn, declared, 9, "V6 declared float64 span")

    print("\n-- V7 the analytic span is the exact formula ---------------------")
    delta = float(getattr(mod, "Delta_univ", float("nan")))
    try:
        p_lo = min(int(x) for x in getattr(mod, "precisions"))
        p_hi = max(int(x) for x in getattr(mod, "precisions"))
    except Exception as exc:
        fail("V7 cannot read the sweep bounds: %s" % exc)
        p_lo = p_hi = None
    want_span = -(p_hi - p_lo) * delta * math.log10(2.0)
    close(float(getattr(mod, "log10_span", float("nan"))), want_span, 7,
          "V7 analytic span")

    print("\n-- V8 bits per decade -------------------------------------------")
    close(float(getattr(mod, "decade_bits", float("nan"))),
          1.0 / (delta * math.log10(2.0)), 7, "V8 bits per decade")

    print("\n-- V9 legend -----------------------------------------------------")
    got = len(leg_labels)
    if got >= 3:
        ok("V9 legend carries the curve and both markers: %r" % leg_labels)
    else:
        fail("V9 legend has %d entries, expected at least 3: %r" % (got, leg_labels))

    plt.close("all")
    n_ok = sum(1 for k, _ in _results if k == "ok")
    n_fail = sum(1 for k, _ in _results if k == "FAIL")
    print("\n%d ok, %d FAIL" % (n_ok, n_fail))
    if n_fail:
        print("GATE: FAIL -- the R_tail panel does not say what it shows.")
        return 1
    print("GATE: PASS -- every %d panel condition holds on the drawn figure."
          % n_ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
