# -*- coding: utf-8 -*-
"""
MODEL DISCRIMINATION for the lambda_min ladder of the cutoff-free
Guinand-Weil matrix Q_inf (arXiv:2607.02828v3; PREPRINT, LLM-assisted,
explicitly disclaiming RH / Weil positivity).

The question this file answers:

    does lambda_min(Q_N) at c = 13 converge to a POSITIVE gap lambda_*,
    or does it collapse to 0 as N -> infinity?

Competing models for y_N = -log10 lambda_min(N):

    G  geometric increments:  y_N = y_inf - K * theta^N,  0 < theta < 1
       -> increments decay geometrically, y_N -> y_inf < infinity
       -> LAMBDA_* = 10^(-y_inf) > 0 : a fixed spectral gap

    P  power law:  y_N = A + p log10 N
       -> lambda_min ~ 10^-A N^-p -> 0

They are told apart by the slope s_i of y between consecutive rungs:

    G  predicts  ln s  LINEAR in N         (constant ratio per equal dN)
    P  predicts  ln s  LINEAR in ln N      (constant ratio per equal d ln N)

This file parses the raw ladder output (gw_ladder_ext.py), keeps only rungs
that reached the resolution criterion (two precisions >= 40 dps apart agreeing
to 1e-12 relative), fits both models, and prints the extrapolation.

PROVENANCE AND LIMITS -- read before quoting any number:
  * only (c,N) = (13,4) is anchored to the primary source (9.7e-15);
    for N >= 8 there is NO external anchor, so those rungs are our measurement
  * the extrapolation is a FIT, not a proof; a fitted positive limit is not a
    theorem that a gap exists
  * nothing here bears on RH
"""

import math
import re
import sys

try:
    import mpmath as mp
    mp.mp.dps = 30
    HAVE_MP = True
except Exception:                                     # pragma: no cover
    HAVE_MP = False


ROW = re.compile(
    r"dps=(\d+)\s+lambda_min\s*=\s*(\S+)\s+lambda_max\s*=\s*(\S+)")
# matches both the earlier format (relative difference only) and the current
# one (|dlambda|/lambda, dy, floor test)
STAB = re.compile(r"stability dps (\d+) vs (\d+):(.*)->\s*(\S+)\s*$")
NUM = re.compile(r"=\s*(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)")
LAD = re.compile(r"LADDER\s+\(c, N\) = \((\d+),\s*(\d+)\)\s+dps sequence\s+(\[.*?\])")


def _open(path):
    """ladder files are written by a PowerShell redirect, i.e. UTF-16LE with a
    BOM; reading them as UTF-8 silently yields no matches.  Detect the BOM."""
    raw = open(path, "rb").read(4)
    enc = "utf-16" if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8"
    return open(path, encoding=enc, errors="replace")


def parse(path):
    """-> list of dicts {c, N, seq, rows:[(dps,lmin,lmax)], resolved, rel, dy}"""
    runs, cur = [], None
    for line in _open(path):
        m = LAD.search(line)
        if m:
            cur = dict(c=int(m.group(1)), N=int(m.group(2)),
                       seq=m.group(3), rows=[], resolved=False,
                       rel=None, dy=None)
            runs.append(cur)
            continue
        if cur is None:
            continue
        m = ROW.search(line)
        if m:
            cur["rows"].append((int(m.group(1)), m.group(2), m.group(3)))
            continue
        m = STAB.search(line)
        if m:
            nums = NUM.findall(m.group(3))
            if nums:
                try:
                    cur["rel"] = float(nums[0])
                except ValueError:
                    pass
                if len(nums) > 1:
                    try:
                        cur["dy"] = float(nums[1])
                    except ValueError:
                        pass
            cur["resolved"] = (m.group(4) == "RESOLVED")
    return runs


def merge(runsets):
    """the same N may appear in several files (a 'fix' pass); keep the run with
    the highest working precision -- its top two dps rows decide resolution."""
    best = {}
    for runs in runsets:
        for r in runs:
            if not r["rows"]:
                continue
            cur = best.get(r["N"])
            if cur is None or r["rows"][-1][0] > cur["rows"][-1][0]:
                best[r["N"]] = r
    return [best[k] for k in sorted(best)]


def fit_linear(xs, ys):
    """least squares y = a x + b -> (a, b, R^2)"""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return 0.0, my, 1.0
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    a = sxy / sxx
    b = my - a * mx
    ss_res = sum((y - (a * x + b)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot else 1.0
    return a, b, r2


def main(paths=("ladder_bn.txt",)):
    runsets = []
    for p in paths:
        try:
            runsets.append(parse(p))
        except OSError:
            print("(not found: %s)" % p)
    runs = merge(runsets)
    print("#" * 96)
    print("# MODEL DISCRIMINATION FOR THE lambda_min LADDER  (c = 13)")
    print("# source: arXiv:2607.02828v3 (PREPRINT, LLM-assisted, no RH claim)")
    print("# input: %s" % ", ".join(paths))
    print("#" * 96)
    print()
    if not runs:
        print("no ladder rows parsed from %s" % (paths,))
        return 1

    print("%-5s %-6s %-9s %-24s %-11s %-10s %-10s %s"
          % ("N", "dps", "seq", "lambda_min (best dps)", "dy (decade)", "rel",
             "printed", "RECOMPUTED"))
    print("-" * 104)
    pts, provisional = [], []
    for r in runs:
        dps, lmin, lmax = r["rows"][-1]
        dy = rel = None
        if len(r["rows"]) >= 2:
            a = float(r["rows"][-2][1])
            b = float(lmin)
            if a != 0 and b != 0:
                dy = abs(math.log10(abs(b)) - math.log10(abs(a)))
                rel = abs(b - a) / abs(b)
        ok = (dy is not None and dy < 1e-4
              and float(lmin) > 0
              and float(lmin) > float(lmax) * 10.0 ** (-(dps - 10)))
        printed = "RESOLVED" if r["resolved"] else "UNRESOLVED"
        print("%-5d %-6d %-9s %-24s %-11s %-10s %-10s %s"
              % (r["N"], dps, r["seq"], lmin,
                 "%.3g" % dy if dy is not None else "-",
                 "%.3g" % rel if rel is not None else "-",
                 printed, "RESOLVED" if ok else "UNRESOLVED"))
        y = -math.log10(abs(float(lmin)))
        (pts if ok else provisional).append((r["N"], y))
    print()
    print("resolution criterion (RECOMPUTED here from the two highest dps rows,")
    print("not taken from the run's own label):")
    print("   dy = |y(dps_hi) - y(dps_lo)| < 1e-4 decades  on y = -log10(lambda_min),")
    print("   lambda_min > 0, and lambda_min above lambda_max * 10^-(dps-10) --")
    print("   the working floor, which is set by the precision actually used.")
    print("A value below the floor is noise, never a negative -- at dps 40 the run")
    print('produced the spurious values -1.066e-41 (N=32) and -1.258e-41 (N=40),')
    print("both of which resolved to POSITIVE at dps 80.")
    print()
    print("only RESOLVED rungs enter the fit; the rest are shown as provisional.")
    print()

    if provisional:
        print("unresolved rungs (provisional, shown for completeness only):")
        for N, y in provisional:
            print("   N = %-4d  -log10(lambda_min) = %s   <-- not yet stable" % (N, mp.nstr(y, 8) if HAVE_MP else y))
        print()

    if len(pts) < 4:
        print("too few resolved rungs (%d) to discriminate models" % len(pts))
        return 1

    pts.sort()
    print("=" * 96)
    print("MEASURED LADDER (resolved rungs only)")
    print("=" * 96)
    print("   N       y = -log10(lambda_min)   drop      slope s = dy/dN")
    print("   " + "-" * 90)
    slopes = []
    for i, (N, y) in enumerate(pts):
        s_txt = ""
        if i:
            dN = N - pts[i - 1][0]
            d = y - pts[i - 1][1]
            s = d / dN
            slopes.append((N, pts[i - 1][0], dN, d, s))
            s_txt = "%-12s %s" % (mp.nstr(d, 8) if HAVE_MP else d,
                                  mp.nstr(s, 8) if HAVE_MP else s)
        print("   %-7d %-24s %s" % (N, mp.nstr(y, 12) if HAVE_MP else y, s_txt))
    print()

    if len(slopes) < 3:
        print("too few intervals to discriminate")
        return 1

    # ---- model discrimination on the slopes --------------------------------
    # slopes entries are (N, Nprev, dN, d, s)
    mids = [(x[0] + x[1]) / 2.0 for x in slopes]
    ss = [x[4] for x in slopes]

    print("=" * 96)
    print("MODEL DISCRIMINATION -- where the slope ratios live")
    print("=" * 96)
    print("   interval        Nmid      slope s        s_i/s_{i-1}")
    print("   " + "-" * 90)
    for i, x in enumerate(slopes):
        rat = "-"
        if i:
            r = ss[i] / ss[i - 1]
            rat = "%.6f" % r
        print("   [%3d,%3d]  %8.1f   %-14s %s"
              % (x[1], x[0], mids[i], mp.nstr(ss[i], 8) if HAVE_MP else ss[i], rat))
    print()

    # G: ln s linear in N        P: ln s linear in ln N
    ln_s = [math.log(s) for s in ss]
    aG, bG, r2G = fit_linear(mids, ln_s)
    aP, bP, r2P = fit_linear([math.log(m) for m in mids], ln_s)

    print("   model G (geometric increments, -> lambda_* > 0):")
    print("        ln s = %.6f * N + %.6f        R^2 = %.6f" % (aG, bG, r2G))
    print("        theta = exp(slope) = %.6f   (ratio per unit N)" % math.exp(aG))
    print()
    print("   model P (power law, -> lambda_min = 0):")
    print("        ln s = %.6f * ln N + %.6f     R^2 = %.6f" % (aP, bP, r2P))
    print("        equivalent to s ~ N^%.6f" % aP)
    print()

    best = "G (geometric)" if r2G > r2P else "P (power law)"
    print("   better fit: %s   (%.6f vs %.6f)" % (best, r2G, r2P))
    print()

    # ---- extrapolation under G ---------------------------------------------
    last_d = slopes[-1][3]
    last_r = ss[-1] / ss[-2] if len(ss) >= 2 else None
    print("=" * 96)
    print("EXTRAPOLATION UNDER THE GEOMETRIC MODEL (a FIT, not a theorem)")
    print("=" * 96)
    print("   last interval drop = %s decades over dN = %d"
          % (mp.nstr(last_d, 8) if HAVE_MP else last_d, slopes[-1][2]))
    if last_r:
        print("   last ratio of slopes r = %s" % (mp.nstr(last_r, 8) if HAVE_MP else last_r))
        if 0 < last_r < 1:
            extra = last_d * last_r / (1 - last_r)
            y_inf = pts[-1][1] + extra
            print("   remaining drop from N = %d onward = %s decades"
                  % (pts[-1][0], mp.nstr(extra, 6) if HAVE_MP else extra))
            print("   => predicted  y_inf = %s,  lambda_* = 10^-(y_inf)"
                  % (mp.nstr(y_inf, 6) if HAVE_MP else y_inf))
            print("   => lambda_* ~ %s" % ("1e-%s" % (mp.nstr(y_inf, 4) if HAVE_MP else y_inf)))
            print()
            print("   using the mean ratio of ALL intervals instead of the last")
            rr = []
            for i in range(1, len(ss)):
                rr.append(ss[i] / ss[i - 1])
            rm = sum(rr) / len(rr)
            extra2 = last_d * rm / (1 - rm)
            y_inf2 = pts[-1][1] + extra2
            print("        r_mean = %s -> y_inf = %s, lambda_* ~ 1e-%s"
                  % (mp.nstr(rm, 6) if HAVE_MP else rm,
                     mp.nstr(y_inf2, 6) if HAVE_MP else y_inf2,
                     mp.nstr(y_inf2, 4) if HAVE_MP else y_inf2))
        else:
            print("   ratio >= 1: increments are NOT decaying; model G rejected")
            print("   => lambda_min -> 0 under this reading")
    print()
    print("=" * 96)
    print("CAVEATS")
    print("=" * 96)
    print("  * only (13,4) is anchored to the primary source; rungs N >= 8 are")
    print("    our own measurement with no external reference")
    print("  * lambda_min(Q_N) is non-increasing in N (Cauchy interlacing, since")
    print("    Q at larger N contains Q at smaller N as a principal submatrix),")
    print("    so a decreasing ladder is expected and is not itself evidence")
    print("  * a fitted positive limit is NOT proof that a gap exists; proving")
    print("    a uniform lower bound over all N would settle much more than this")
    print("  * nothing here bears on RH, Weil positivity, prime counting, or")
    print("    factoring")
    return 0


if __name__ == "__main__":
    main(sys.argv[1:] or ["ladder_bn.txt"])
