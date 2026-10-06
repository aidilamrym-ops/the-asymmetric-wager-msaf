"""Apply gw_verify_results.py invariants to BOTH production OMEGA results.

Add-on (new file).  gw_verify_results.py was left untouched in F0; F1 then
fixed two verdict-shaped holes in it as well (unguarded fixture read and a
length-only sha256 check), because its own message promised a 64-hex digest.
Both gates are now fault-injection proven at 14/14.
Imports the gate so its fixture CASES run first and share one failure list,
then adds omega_core_v2_results.json as a production "certified" case.

Exit 0 only when BOTH the smoke fixtures AND the production N=800 row
satisfy every invariant.

F1 hardening.  A mutation harness fed 19 corrupted variants of the
production row through this gate and found five defects:

  1. lambda_min_lower_bound was tested only for > 0, so the absurd values
     '1' and '1e-99999' were accepted and bound_detail was never read.
  2. The inputs of the bound (min_abs_pivot, norm_Linv_F_upper) were never
     checked, so a corrupted decomposition passed alongside an intact bound.
  3. dim == 2N+1 was never asserted; N=7 with dim=1601 passed.
  4. sha256 was only length-checked, so 'x' * 64 passed.
  5. A missing key raised an unhandled KeyError (a traceback) instead of a
     clean FAILURES verdict.

deep_invariants() closes 1-4 and is applied to the two fixtures as well as to
the production row, so the strengthened checks run against three independent
records instead of being validated only on the data they were written for.

F2-7 addendum (closes F1 residual 2, "F1-D").  The N=400 run's result file was
overwritten by the N=800 run, so lambda_min at N=400 was recorded in three
documents and machine-readable nowhere -- "three documentary records, zero
machine-readable artefacts".  F2-7 regenerated the run into its OWN file
(omega_core_v2_results_N400.json; --out is never left at the default, because
the default is exactly what destroyed the original) and this gate now:

  * subjects the N=400 row to the identical certified-row checks as N=800;
  * requires N == 400, c == 100, dim == 801;
  * re-reads the three surviving documentary records FROM THEIR FILES and
    requires every one of them to agree with the freshly computed bound.

The records are parsed for their first numeric `lambda_min >=` (and the
certificate for its single `lambda_min_lower_bound` JSON field).  The N=400
run was appended to omega_core_v2_run.log and PROVENANCE.txt section 6.2
before the N=800 run, so "first match" is the N=400 record in each file; that
ordering is part of what this gate asserts, because a reordered log would
silently swap in the N=800 value and fail the cross-check.
"""
import io
import json
import os
import re
import sys

import mpmath as mp

import gw_verify_results as gv  # importing runs the fixture CASES (prints OK)

# float64 underflows bounds like 1e-2877 (and entry radii like 1e-5144) to
# 0.0, which would make "> 0" silently trivial -- parse with arbitrary
# precision instead so the sign check is meaningful at the real scale.
mp.mp.dps = 60

# Relative tolerance for re-deriving lambda_min_lower_bound from bound_detail.
# bound_detail strings carry ~25 significant digits while the bound carries
# ~29, so the round-trip is reproducible only to about 1e-25: measured
# 1.679e-25 on the smoke fixture and 3.269e-26 on the production row.
# 1e-20 keeps five orders of headroom over that serialization residue while
# still rejecting any bound that is not the one the recorded decomposition
# actually implies (the corrupt cases all land at rel ~ 1).
BOUND_REL_TOL = mp.mpf("1e-20")

SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")

HERE = os.path.dirname(os.path.abspath(__file__))

# Production results default to this script's own directory (a fresh clone
# works from any working directory); pass explicit file paths as argv[1],
# argv[2].
PROD = os.path.join(HERE, "omega_core_v2_results.json")
N400 = os.path.join(HERE, "omega_core_v2_results_N400.json")
if len(sys.argv) > 1:
    PROD = os.path.abspath(sys.argv[1])
if len(sys.argv) > 2:
    N400 = os.path.abspath(sys.argv[2])


def get(row, key, tag):
    """Fetch row[key], reporting absence through the shared failure list.

    Never raises: a corrupt row must produce a FAILURES line, not a traceback.
    """
    if key not in row:
        gv.check(False, "%s missing required key %r" % (tag, key))
        return None
    return row[key]


def deep_invariants(r, tag):
    """Structural invariants a row must satisfy to count as evidence.

    Bound checks run only when the row actually carries a bound; non-result
    rows legitimately hold lambda_min_lower_bound = null and a textual
    bound_detail, and their certified-status is asserted by the caller.
    """
    N = get(r, "N", tag)
    dim = get(r, "dim", tag)
    if N is not None and dim is not None:
        gv.check(dim == 2 * N + 1,
                 "%s dim must equal 2N+1, got dim=%r N=%r" % (tag, dim, N))

    sha = get(r, "sha256", tag)
    if sha is not None:
        gv.check(bool(SHA256_RE.match(str(sha))),
                 "%s sha256 must be 64 hex characters, got %r" % (tag, sha))

    lb = get(r, "lambda_min_lower_bound", tag)
    bd = get(r, "bound_detail", tag)
    if lb is None or not isinstance(bd, dict):
        return

    for key in ("min_abs_pivot", "norm_Linv_F_upper"):
        if key not in bd:
            gv.check(False, "%s bound_detail missing %r" % (tag, key))
            return

    try:
        declared = mp.mpf(str(lb))
        implied = (mp.mpf(str(bd["min_abs_pivot"]))
                   / mp.mpf(str(bd["norm_Linv_F_upper"])) ** 2)
    except (TypeError, ValueError) as exc:
        gv.check(False, "%s bound arithmetic is not parseable: %s" % (tag, exc))
        return

    gv.check(implied > 0,
             "%s bound_detail implies a non-positive bound (%s)" % (tag, implied))
    rel = abs(declared - implied) / implied
    gv.check(rel <= BOUND_REL_TOL,
             "%s lambda_min_lower_bound is not the bound bound_detail implies: "
             "declared=%s implied=%s rel=%.3e > %.0e"
             % (tag, declared, implied, rel, BOUND_REL_TOL))
    gv.check(str(bd.get("pivot_sign")) == "+",
             "%s pivot_sign must be '+' on a positive definite certificate, "
             "got %r" % (tag, bd.get("pivot_sign")))


def load_row(path, tag):
    """Read a one-row production result, or fail cleanly through gv.check."""
    if not os.path.isfile(path):
        gv.check(False, "%s result file is missing: %s" % (tag, path))
        return None
    try:
        rows = json.load(io.open(path, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        gv.check(False, "%s result file unreadable: %s" % (tag, exc))
        return None
    if not isinstance(rows, list):
        gv.check(False, "%s expected a JSON list of rows, got %s"
                 % (tag, type(rows).__name__))
        return None
    gv.check(len(rows) == 1, "%s expected exactly 1 row, got %d"
             % (tag, len(rows)))
    if len(rows) != 1 or not isinstance(rows[0], dict):
        return None
    return rows[0]


def certified_row_checks(r, tag):
    """Every invariant a production row must satisfy to be evidence.

    This body was inlined for N=800 in F1 and is now shared with N=400, so the
    two rows are held to one standard rather than to two.
    """
    for key in gv.REQUIRED:
        if key not in r:
            gv.check(False, "%s missing required key %r" % (tag, key))

    anomaly = get(r, "anomaly", tag)
    gv.check(anomaly is False, "%s anomaly must be False" % tag)
    anomalies = get(r, "anomalies", tag)
    gv.check(anomalies == [], "%s anomalies must be EMPTY, got %r" % (tag, anomalies))
    gv.check("non_result_reason" not in r,
             "%s certified path must NOT carry non_result_reason" % tag)
    non_result = get(r, "non_result", tag)
    gv.check(non_result is False, "%s non_result must be False" % tag)
    gv.check(get(r, "undetermined_pivot", tag) is None,
             "%s undetermined_pivot must be null" % tag)
    n_pos = get(r, "n_pos", tag)
    n_neg = get(r, "n_neg", tag)
    dim = get(r, "dim", tag)
    gv.check(n_pos == dim, "%s n_pos must equal dim" % tag)
    gv.check(n_neg == 0, "%s n_neg must be 0" % tag)
    if n_pos is not None and n_neg is not None and dim is not None:
        gv.check(n_pos + n_neg == dim,
                 "%s every sign determined (n_pos + n_neg == dim)" % tag)

    lb = get(r, "lambda_min_lower_bound", tag)
    gv.check(lb is not None, "%s lambda_min_lower_bound must be present" % tag)
    if lb is not None:
        try:
            gv.check(mp.mpf(str(lb)) > 0,
                     "%s lambda_min_lower_bound must be > 0" % tag)
        except (TypeError, ValueError) as exc:
            gv.check(False, "%s lambda_min_lower_bound not parseable: %s"
                     % (tag, exc))

    gv.check(get(r, "symmetry_exact", tag) is True,
             "%s symmetry_exact must be True" % tag)
    gv.check(get(r, "symmetry_dev", tag) == "0",
             "%s symmetry_dev must be exactly '0', got %r"
             % (tag, r.get("symmetry_dev")))
    caveats = get(r, "caveats", tag)
    gv.check(caveats == [], "%s caveats must be EMPTY, got %r" % (tag, caveats))
    mer = get(r, "max_entry_radius", tag)
    if mer is not None:
        try:
            gv.check(abs(mp.mpf(str(mer))) < mp.mpf("1e-50"),
                     "%s max_entry_radius = %s exceeds 1e-50" % (tag, mer))
        except (TypeError, ValueError) as exc:
            gv.check(False, "%s max_entry_radius not parseable: %s" % (tag, exc))
    attempts = get(r, "attempts", tag)
    gv.check(bool(attempts) and attempts[0].get("n_pos") is not None,
             "%s attempts record must carry the measured n_pos" % tag)

    deep_invariants(r, tag)


def sig_digits(txt):
    """Significant decimal digits carried by a numeric string like 6.747e-509."""
    mant = re.split(r"[eE]", txt)[0]
    mant = mant.replace("+", "").replace("-", "").replace(".", "")
    return len(mant.lstrip("0"))


def documentary_records():
    """Locate the three surviving written records of the N=400 bound.

    Each is read from its own file at check time; none of them is copied into
    this source, so a document edited tomorrow is compared against tomorrow's
    bytes rather than against a frozen quotation of it.  A record that cannot
    be opened is reported as absent rather than allowed to raise: the F1 rule
    is that a corrupt input produces a FAILURES line, never a traceback.
    """
    found = {}

    def first(pattern, filename, flags=0):
        try:
            text = io.open(os.path.join(HERE, filename),
                           encoding="utf-8", errors="replace").read()
        except OSError:
            return None
        m = re.search(pattern, text, flags)
        return m.group(1) if m else None

    found["PROVENANCE.txt section 6.2"] = first(
        r"lambda_min\s*>=\s*([0-9][0-9.eE+-]*)", "PROVENANCE.txt")
    found["OMEGA_CORE_CERTIFICATE.md section 4"] = first(
        r'"lambda_min_lower_bound"\s*:\s*"([^"]+)"',
        "OMEGA_CORE_CERTIFICATE.md")
    # omega_core_v2_run.log holds two appended runs; the N=400 run was first,
    # so the first match is its line 51.  The ordering is part of what this
    # gate asserts: a reordered or truncated log would swap in the N=800
    # value and fail the cross-check.
    found["omega_core_v2_run.log line 51"] = first(
        r"lambda_min\s*>=\s*([0-9][0-9.eE+-]*)", "omega_core_v2_run.log")

    return found


DOCUMENTARY = documentary_records()


# --- strengthened checks on the fixtures, so they are exercised too ---------
for _path, _kind in gv.CASES:
    try:
        _rows = json.load(open(_path, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        gv.check(False, "fixture %s unreadable: %s" % (_path, exc))
        continue
    for _i, _fr in enumerate(_rows):
        deep_invariants(_fr, "[fixture %s row %d]"
                        % (os.path.basename(_path), _i))

# --- the production N=800 row ----------------------------------------------
tag = "[production N=800]"
r = load_row(PROD, tag)
if r is not None:
    certified_row_checks(r, tag)

# --- the production N=400 row (F2-7) ---------------------------------------
tag400 = "[production N=400]"
r400 = load_row(N400, tag400)
if r400 is not None:
    certified_row_checks(r400, tag400)
    gv.check(r400.get("N") == 400,
             "%s N must be 400, got %r" % (tag400, r400.get("N")))
    gv.check(r400.get("c") == 100,
             "%s c must be 100, got %r" % (tag400, r400.get("c")))
    gv.check(r400.get("dim") == 801,
             "%s dim must be 801, got %r" % (tag400, r400.get("dim")))

    # The point of F2-7: the value is re-read from the artefact the run just
    # wrote, and held against every document that still records it.
    art_txt = r400.get("lambda_min_lower_bound")
    try:
        art = mp.mpf(str(art_txt))
    except (TypeError, ValueError):
        art = None
        gv.check(False, "%s lambda_min_lower_bound not parseable: %r"
                 % (tag400, art_txt))

    if art is not None:
        gv.check(art > 0, "%s bound must be positive" % tag400)
        for name, txt in sorted(DOCUMENTARY.items()):
            if txt is None:
                gv.check(False,
                         "documentary record %r no longer contains a numeric "
                         "`lambda_min >=` / bound field" % name)
                continue
            try:
                val = mp.mpf(txt)
            except (TypeError, ValueError):
                gv.check(False, "documentary record %r is not parseable: %r"
                         % (name, txt))
                continue
            # Each record is held to ITS OWN precision -- the log carries 25
            # significant digits, PROVENANCE and the certificate 30 -- so the
            # comparison never depends on a magic tolerance: a record must be
            # the value the fresh run computed, rounded to what that record
            # was capable of writing down.
            n = sig_digits(txt)
            if n < 1:
                gv.check(False, "documentary record %r carries no digits: %r"
                         % (name, txt))
                continue
            rec_at = mp.nstr(val, n)
            art_at = mp.nstr(art, n)
            gv.check(rec_at == art_at,
                     "documentary record %r disagrees with the regenerated "
                     "N=400 artefact at that record's own %d significant "
                     "digits: record=%s artefact=%s"
                     % (name, n, txt, art_txt))
        print("%s OK  bound=%s reproduces all %d documentary records"
              % (tag400, art_txt, len(DOCUMENTARY)))

if gv.failures:
    print("\nFAILURES:")
    for f in gv.failures:
        print("  - " + f)
    sys.exit(1)

print("%s OK  n_pos=%s n_neg=%s bound=%s sha256=%s..."
      % (tag, r["n_pos"], r["n_neg"],
         r["lambda_min_lower_bound"], r["sha256"][:16]))
print("%s OK  n_pos=%s n_neg=%s bound=%s sha256=%s..."
      % (tag400, r400["n_pos"], r400["n_neg"],
         r400["lambda_min_lower_bound"], r400["sha256"][:16]))
print("\nALL JSON INVARIANTS PASS (fixtures + production N=800 + production "
      "N=400 + 3 documentary records)")
