#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""External provenance gate -- F3-1, workspace D:\\THE ASYMMETRIC WAGER.

Purpose
-------
Before this gate existed the corpus used l_P, D_obs and |zeta'(rho_1)| inside
its own documents with no bibliography anywhere in the root tree: the numbers
were right, the provenance was absent. This gate ties every such number to an
external authority, an edition, a retrieval date and a hashable evidence
snapshot.

Design rules (inherited from landauer_check.py / zeta_pixel_producer.py /
znone_check.py and from the F2-7 hardening notes):

  * Claims are read OUT of the documents. Deleting a claim fails the gate.
  * Missing or malformed input produces FAILURES lines, never a traceback.
  * Tolerances are derived from the declared significant-figure count of the
    value being compared, never chosen ad hoc.
  * Exit code: 0 = PASS, 1 = FAIL, 2 = TOOL NOT RUN.
  * Line prefix: "ok  " / "FAIL  " / "SKIP  ", summary line "GATE: ...".

Scope note: this gate does not re-derive the subjects of msaf_zeta_check.py,
landauer_check.py or gw_verify_production.py. Those remain the gates of record
for their own claims; this gate certifies the external provenance chain.

A9 addition (P11): the register used to carry a *retrieval date* and nothing
else about a source's present state, so learning that a cited URL had moved
meant rereading it by hand -- F7-R3. `url_liveness_check.py` now re-fetches the
whole set on demand and writes `provenance/url_liveness.json`; P11 is the
offline half, and it is what keeps this gate a gate: the record must exist,
must cover exactly the register's URL set, must restate the register's own
pins rather than its own, and must not sit on top of a contradiction the probe
already found.  The probe itself is deliberately outside this file, because a
gate whose answer depends on a publisher's uptime is not a gate.
"""

import hashlib
import io
import json
import os
import re
import sys
from decimal import Decimal, InvalidOperation

# Declared-precision ceiling. P5 feeds agrees() mp.nstr(x, 40), so a quantity
# demanding more than 40 significant figures is asking this gate to confirm
# digits it never computes. The floor of 1 is not arbitrary either: sig_figs
# of 0 would mean "no significant figures declared", and a negative value
# makes 5 * 10**-sf larger than 1, i.e. a vacuous comparison.
SF_CAP = 40

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "external_constants.json")
REFS_PATH = os.path.join(HERE, "REFERENCES.md")
LIVENESS_PATH = os.path.join(HERE, "provenance", "url_liveness.json")

# One entry per numbered condition P1..P11, so the "N conditions" line cannot
# drift away from the checks that actually run.  "Conditions" counts the
# numbers, not the print statements: P3 and P4 share one section header and
# one "delta" line, and F3_REPORT.md §9 records the convention ("the 9th is
# P9 LAYER_CONSISTENCY, the 10th is P10 REF_MARKERS").
CONDITIONS = (
    "P1  SCHEMA",
    "P2  EVIDENCE_HASH",
    "P3  SITE_FOUND",
    "P4  SITE_VALUE",
    "P5  DERIVED",
    "P6  PROVENANCE",
    "P7  REFERENCES_COVERAGE",
    "P8  REFERENCE_FACT_VALUE",
    "P9  LAYER_CONSISTENCY",
    "P10 REF_MARKERS",
    "P11 LIVENESS_RECORD",
)

failures = []
notes = []


def fail(msg):
    failures.append(msg)


def check(cond, msg):
    if not cond:
        fail(msg)
    return bool(cond)


# ---------------------------------------------------------------- numerics --

def norm_mantissa(s):
    """'1{,}616255' / '1,836653' / '8.8' -> '1.616255' / '1.836653' / '8.8'."""
    return str(s).replace("{,}", ".").replace(",", ".")


def sf_of(declared):
    """Return a validated significant-figure count, or None.

    sig_figs drives agrees() as 5 * 10**-sf, so an unbounded or non-integer
    declaration does not merely look sloppy: -1 gives a 5000 % tolerance and
    switches the comparison off entirely. P1 rejects these, and this helper
    lets P5 decline to use a value P1 has already condemned rather than
    letting int() raise halfway through the report.
    """
    if isinstance(declared, bool) or not isinstance(declared, int):
        return None
    if not 1 <= declared <= SF_CAP:
        return None
    return declared


_NUM_TOKEN = re.compile(r"(?<![\d.])\d+(?:[.,]\d+)*(?!\d)")


def _as_decimal(s):
    """Exact Decimal for a corpus number, or None if it is not one.

    norm_mantissa() maps the corpus's two decimal separators (',' and '{,}')
    onto '.' before Decimal sees them, so 1,836653 and 1{,}836653 both parse.
    """
    try:
        return Decimal(norm_mantissa(str(s)))
    except (InvalidOperation, ValueError, ArithmeticError):
        return None


def numeric_token_present(val, text):
    """True iff some complete number in text equals val numerically.

    F5-4: the exact spelling is tried first by token_present(); this is the
    fallback for a value written differently but equal as a number. The
    comparison is exact Decimal equality, never float equality, so 5.5590
    equals 5.559 while 1038007883590 does not equal 103800788359 -- no padding
    or truncation is ever applied to force a match.
    """
    want = _as_decimal(val)
    if want is None:
        return False
    for m in _NUM_TOKEN.finditer(text):
        got = _as_decimal(m.group(0))
        if got is not None and got == want:
            return True
    return False


def token_present(val, text):
    """True iff val occurs in text as a complete number.

    `5.559` must not be satisfied by `5.559123`, `103800788359` must not be
    satisfied by `1038007883590`, and `3000175332800` must not be satisfied
    by `930001753328009`.

    The exact spelling is tried first and keeps its original fail-closed
    behaviour. Only if that misses does numeric_token_present() compare the
    complete numbers in the text numerically, which accepts an equal value
    written with different trailing zeros after a decimal point (`5.5590` for
    `5.559`) -- closed residual R7 by numeric equality rather than by loosening
    the text match. A false PASS is invisible and a false FAIL is not, so every
    numeric acceptance is still an exact-equality one.
    """
    esc = re.escape(str(val))
    if re.search(r"(?<![\d.])%s(?!\d)" % esc, text) is not None:
        return True
    return numeric_token_present(val, text)


def sig_digits(s):
    """Significant digits in a decimal/exponent string. 0.7931604334 -> 10."""
    t = str(s).strip().lower()
    if "e" in t:
        t = t.split("e")[0]
    t = t.lstrip("+-").replace(".", "")
    t = t.lstrip("0")
    return len(t) if t else 1


def agrees(observed, expected, sf):
    """True iff observed matches expected to sf significant figures."""
    from decimal import Decimal, getcontext, InvalidOperation
    getcontext().prec = 80
    try:
        o = Decimal(str(observed))
        e = Decimal(str(expected))
    except (InvalidOperation, ValueError):
        return False
    if e == 0:
        return o == 0
    tol = Decimal(5) * (Decimal(10) ** (-int(sf)))
    return abs(o - e) / abs(e) <= tol


def value_from_needle(needle):
    """Decode the numeric value encoded in a literal needle.

    '1{,}616255 \\times 10^{-35}' -> '1.616255e-35'
    '1{,}380649\\times10^{-23}'   -> '1.380649e-23'
                                     (SOLVABLE_FINITE_PARADOX.md writes the
                                     operator with no spaces; requiring them
                                     would have made that site undecodable)
    '0,7931604334'                -> '0.7931604334'
    """
    for marker in (" \\times 10^{", "\\times10^{"):
        if marker in needle:
            head, tail = needle.split(marker, 1)
            tail = tail.rstrip("}")
            return norm_mantissa(head) + "e" + tail
    return norm_mantissa(needle)


# ---------------------------------------------------------------- loading --

def load_or_die(path, label):
    if not os.path.isfile(path):
        print("FAIL  --  %s is missing: %s" % (label, path))
        return None
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # malformed input is TOOL NOT RUN, not a crash
        print("FAIL  --  %s is unreadable: %s" % (label, exc))
        return None


def main(argv):
    data = load_or_die(JSON_PATH, "external_constants.json")
    if data is None:
        return 2
    try:
        with io.open(REFS_PATH, encoding="utf-8") as fh:
            refs_text = fh.read()
    except Exception:
        refs_text = None  # handled by P7 as a FAIL, not a crash

    ev_list = data.get("evidence") or []
    qu_list = data.get("quantities") or []
    rf_list = data.get("reference_facts") or []
    ev_by_id = {e.get("id"): e for e in ev_list if isinstance(e, dict)}
    q_by_id = {q.get("id"): q for q in qu_list if isinstance(q, dict)}

    # ---------------------------------------------------- P1 SCHEMA --------
    label = "P1  SCHEMA"
    check(isinstance(data.get("schema"), str) and data["schema"],
          "%s: schema key missing" % label)
    check(data.get("schema") == "msaf-external-provenance/v1",
          "%s: unexpected schema %r" % (label, data.get("schema")))
    check(len(ev_list) >= 1, "%s: no evidence entries" % label)
    check(len(qu_list) >= 1, "%s: no quantities" % label)
    check(len(rf_list) >= 1, "%s: no reference_facts" % label)

    for e in ev_list:
        if not isinstance(e, dict):
            fail("%s: evidence entry is not an object" % label)
            continue
        for k in ("id", "title", "url", "retrieved_utc", "access"):
            check(bool(e.get(k)), "%s: evidence %r missing %s"
                  % (label, e.get("id"), k))
        if e.get("access") == "full_text_local_copy":
            for k in ("sha256", "bytes", "local_copy"):
                check(bool(e.get(k)), "%s: evidence %r missing %s"
                      % (label, e.get("id"), k))

    for q in qu_list:
        if not isinstance(q, dict):
            fail("%s: quantity entry is not an object" % label)
            continue
        qid = q.get("id")
        for k in ("id", "kind", "value", "exact", "unit",
                  "authority", "retrieved_utc"):
            check(bool(q.get(k)) or k == "exact",
                  "%s: quantity %r missing %s" % (label, qid, k))
        # sig_figs is validated by type and range instead of by truth.
        # bool(0) is False, so the loop above used to report sig_figs = 0 as
        # "missing", while -1, a non-integer and an absurd magnitude passed
        # unnoticed -- each of which reaches agrees() as 5 * 10**-sf and
        # switches the comparison off. Vacuity probe 2026-10-05: sig_figs = -1
        # on a derived quantity made P5 pass a check whose tolerance was
        # 5000 %.
        _sf = q.get("sig_figs")
        if check("sig_figs" in q and _sf is not None,
                 "%s: quantity %r missing sig_figs" % (label, qid)):
            if check(isinstance(_sf, int) and not isinstance(_sf, bool),
                     "%s: quantity %r sig_figs must be an integer, got %r"
                     % (label, qid, _sf)):
                if check(1 <= _sf <= SF_CAP,
                         "%s: quantity %r sig_figs %d is outside 1..%d. Below 1 "
                         "agrees() compares at 5 * 10**-sf and switches itself "
                         "off (sig_figs -1 is a 5000 %% tolerance); above %d it "
                         "asks for agreement with digits P5 never produces, "
                         "because it feeds agrees() mp.nstr(x, %d)."
                         % (label, qid, _sf, SF_CAP, SF_CAP, SF_CAP)):
                    # The declared precision must equal the precision actually
                    # written in the declared value. Without this, sig_figs on
                    # a measured quantity is decoration -- P4 compares at
                    # sig_digits(doc_value) and never reads it -- so dropping
                    # it to 1 would leave the gate green while quietly
                    # weakening P5 for a derived quantity to a 50 % tolerance.
                    # Vacuity probe 2026-10-05: that was the one vector the
                    # range check alone did not close.
                    check(_sf == sig_digits(q.get("value")),
                          "%s: quantity %r declares sig_figs %d but its value "
                          "carries %d significant figure(s)"
                          % (label, qid, _sf, sig_digits(q.get("value"))))
        if q.get("kind") == "derived":
            ok_der = bool(q.get("derived_from")) or bool(q.get("recompute"))
            check(ok_der, "%s: derived quantity %r declares neither "
                          "derived_from nor recompute" % (label, qid))
        if q.get("exact") is True:
            check(str(q.get("uncertainty", "")).strip().lower() == "exact",
                  "%s: exact quantity %r must declare uncertainty 'exact'"
                  % (label, qid))
        else:
            check(bool(q.get("uncertainty")),
                  "%s: inexact quantity %r must declare an uncertainty"
                  % (label, qid))
        sites = q.get("sites")
        check(isinstance(sites, list) and len(sites) >= 1,
              "%s: quantity %r must carry at least one site" % (label, qid))
        for i, s in enumerate(sites or []):
            sid = "%s#%d" % (qid, i)
            if not isinstance(s, dict):
                fail("%s: site %s is not an object" % (label, sid))
                continue
            for k in ("file", "needle", "mantissa", "count", "mode",
                      "doc_value"):
                check(bool(s.get(k)) or s.get(k) == 0 or s.get(k) is False,
                      "%s: site %s missing %s" % (label, sid, k))
            if s.get("mode") == "declared_variance":
                for k in ("source_value", "correct_rounding", "rounding_sf",
                          "rel_dev", "rel_dev_sf"):
                    check(s.get(k) is not None,
                          "%s: declared_variance site %s missing %s"
                          % (label, sid, k))

    for r in rf_list:
        if not isinstance(r, dict):
            fail("%s: reference_fact is not an object" % label)
            continue
        for k in ("id", "value", "source_id", "claim"):
            check(bool(r.get(k)), "%s: reference_fact %r missing %s"
                  % (label, r.get("id"), k))
        if isinstance(r, dict) and r.get("source_id"):
            check(r["source_id"] in ev_by_id,
                  "%s: reference_fact %r cites unknown evidence %r"
                  % (label, r.get("id"), r.get("source_id")))
    n_p1 = len(failures)
    print("%s %-34s failures so far: %d"
          % ("ok  " if n_p1 == 0 else "FAIL  ", label, n_p1))

    # ------------------------------------------------ P2 EVIDENCE_HASH -----
    base = len(failures)
    for e in ev_list:
        if not isinstance(e, dict) or e.get("access") != "full_text_local_copy":
            continue
        eid = e.get("id")
        path = os.path.join(HERE, str(e.get("local_copy")))
        if not os.path.isfile(path):
            fail("P2  EVIDENCE_HASH: local copy missing for %s (%s)"
                 % (eid, e.get("local_copy")))
            continue
        size = os.path.getsize(path)
        if not check(size == int(e.get("bytes", -1)),
                     "P2  EVIDENCE_HASH: %s size %d != declared %s"
                     % (eid, size, e.get("bytes"))):
            continue
        h = hashlib.sha256()
        with io.open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 16), b""):
                h.update(chunk)
        got = h.hexdigest()
        check(got == str(e.get("sha256", "")).lower(),
              "P2  EVIDENCE_HASH: %s sha256 %s != declared %s"
              % (eid, got, e.get("sha256")))
    print("%s P2  EVIDENCE_HASH               delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ------------------------------------------- P3 + P4 SITES -------------
    base = len(failures)
    for q in qu_list:
        if not isinstance(q, dict):
            continue
        qid = q.get("id")
        for i, s in enumerate(q.get("sites") or []):
            if not isinstance(s, dict):
                continue
            sid = "%s#%d" % (qid, i)
            path = os.path.join(HERE, str(s.get("file", "")))
            if not os.path.isfile(path):
                fail("P3  SITE_FOUND: document missing for %s (%s)"
                     % (sid, s.get("file")))
                continue
            try:
                with io.open(path, encoding="utf-8") as fh:
                    text = fh.read()
            except Exception as exc:
                fail("P3  SITE_FOUND: document unreadable for %s: %s"
                     % (sid, exc))
                continue
            needle = str(s.get("needle", ""))
            count = text.count(needle)
            if not check(count == int(s.get("count", -1)),
                         "P3  SITE_FOUND: %s needle occurs %d times, "
                         "declared %s" % (sid, count, s.get("count"))):
                continue
            # needle must encode exactly the mantissa/exponent the JSON claims
            if not check(str(s.get("mantissa")) in needle,
                         "P3  SITE_FOUND: %s mantissa %r absent from needle"
                         % (sid, s.get("mantissa"))):
                continue
            exp = s.get("exponent")
            if exp is not None:
                check("10^{%d}" % int(exp) in needle,
                      "P3  SITE_FOUND: %s needle does not carry exponent %s"
                      % (sid, exp))
            actual = value_from_needle(needle)
            doc_value = s.get("doc_value")
            if not check(agrees(actual, doc_value, sig_digits(doc_value)),
                         "P4  SITE_VALUE: %s decodes to %s but doc_value "
                         "says %s" % (sid, actual, doc_value)):
                continue
            if s.get("mode") == "declared_variance":
                src = s.get("source_value")
                computed = (abs(_num(doc_value) - _num(src)) / abs(_num(src))
                            if _num(src) else None)
                if check(computed is not None,
                         "P4  SITE_VALUE: %s variance source_value is not "
                         "numeric" % sid):
                    if not agrees(computed, s.get("rel_dev"),
                                  int(s.get("rel_dev_sf", 4))):
                        fail("P4  SITE_VALUE: %s declared rel_dev %s but "
                             "doc/source imply %s"
                             % (sid, s.get("rel_dev"), computed))
                    corr = round_sig(_num(src), int(s.get("rounding_sf", 3)))
                    if not agrees(corr, s.get("correct_rounding"),
                                  int(s.get("rounding_sf", 3))):
                        fail("P4  SITE_VALUE: %s correct_rounding declared %s "
                             "but source rounds to %s"
                             % (sid, s.get("correct_rounding"), corr))
                    if agrees(_num(doc_value), s.get("correct_rounding"),
                              int(s.get("rounding_sf", 3))):
                        fail("P4  SITE_VALUE: %s is declared a variance but "
                             "doc_value equals the correct rounding" % sid)
            else:
                check(agrees(doc_value, q.get("value"),
                             sig_digits(doc_value)),
                      "P4  SITE_VALUE: %s doc_value %s disagrees with the "
                      "authoritative value %s at %d s.f."
                      % (sid, doc_value, q.get("value"),
                         sig_digits(doc_value)))
    print("%s P3/P4 SITE_FOUND + SITE_VALUE   delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ------------------------------------------------- P5 DERIVED ----------
    base = len(failures)
    try:
        import mpmath as mp
        mp.mp.dps = 100
        have_mp = True
    except Exception:
        have_mp = False
        fail("P5  DERIVED: mpmath unavailable -- cannot re-derive quantities")
    for q in qu_list:
        if not isinstance(q, dict) or q.get("kind") != "derived":
            continue
        qid = q.get("id")
        mode = q.get("recompute")
        if mode == "quotient":
            deps = q.get("derived_from") or []
            if not all(d in q_by_id for d in deps):
                fail("P5  DERIVED: %s derived_from %s not resolvable"
                     % (qid, deps))
                continue
            if not have_mp:
                continue
            num = mp.mpf(q_by_id[deps[0]]["value"])
            den = mp.mpf(q_by_id[deps[1]]["value"])
            got = num / den
            _sf = sf_of(q.get("sig_figs"))
            if _sf is None:
                # P1 has already reported the bad declaration; using it here
                # would either raise or compare against a vacuous tolerance.
                continue
            if not check(agrees(mp.nstr(got, 40), q.get("value"), _sf),
                         "P5  DERIVED: %s recomputes to %s, declared %s "
                         "at %s s.f." % (qid, mp.nstr(got, 20),
                                         q.get("value"), _sf)):
                continue
            print("ok    P5  DERIVED %s = %s" % (qid, mp.nstr(got, 16)))
        elif mode == "zeta_prime_abs_first_zero":
            if not have_mp:
                continue
            try:
                z = mp.zetazero(1)
                val = abs(mp.diff(mp.zeta, z))
            except Exception as exc:
                fail("P5  DERIVED: %s recomputation failed: %s" % (qid, exc))
                continue
            _sf = sf_of(q.get("sig_figs"))
            if _sf is None:
                continue
            if not check(agrees(mp.nstr(val, 40), q.get("value"), _sf),
                         "P5  DERIVED: %s recomputes to %s, declared %s"
                         % (qid, mp.nstr(val, 20), q.get("value"))):
                continue
            print("ok    P5  DERIVED %s = %s" % (qid, mp.nstr(val, 30)))
        elif mode == "planck_vacuum_cutoff":
            # rho = hbar * c / (8 * pi^2 * lP^4): the zero-point density with
            # the Planck angular-frequency cutoff omega_P = c / lP.  Added A10
            # so the vacuum-catastrophe document cites a recomputeable number
            # rather than an order-of-magnitude assertion.
            deps = q.get("derived_from") or []
            if not all(d in q_by_id for d in deps):
                fail("P5  DERIVED: %s derived_from %s not resolvable"
                     % (qid, deps))
                continue
            if not have_mp:
                continue
            try:
                hbar = mp.mpf(q_by_id["REDUCED_PLANCK_CONSTANT"]["value"])
                cval = mp.mpf(q_by_id["SPEED_OF_LIGHT"]["value"])
                lp = mp.mpf(q_by_id["PLANCK_LENGTH"]["value"])
                got = hbar * cval / (8 * mp.pi ** 2 * lp ** 4)
            except Exception as exc:
                fail("P5  DERIVED: %s recomputation failed: %s" % (qid, exc))
                continue
            _sf = sf_of(q.get("sig_figs"))
            if _sf is None:
                continue
            if not check(agrees(mp.nstr(got, 40), q.get("value"), _sf),
                         "P5  DERIVED: %s recomputes to %s, declared %s "
                         "at %s s.f." % (qid, mp.nstr(got, 20),
                                         q.get("value"), _sf)):
                continue
            print("ok    P5  DERIVED %s = %s" % (qid, mp.nstr(got, 16)))
        elif mode:
            fail("P5  DERIVED: %s unknown recompute mode %r" % (qid, mode))
    print("%s P5  DERIVED                    delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ------------------------------------------- P6 PROVENANCE -------------
    base = len(failures)
    for q in qu_list:
        if not isinstance(q, dict):
            continue
        qid = q.get("id")
        check(bool(str(q.get("authority", "")).strip()),
              "P6  PROVENANCE: %s has no authority" % qid)
        check(bool(str(q.get("retrieved_utc", "")).strip()),
              "P6  PROVENANCE: %s has no retrieval date" % qid)
        eid = q.get("evidence_id")
        status = q.get("evidence_status")
        if eid is None:
            check(status in ("recomputed_in_gate", "not_archived"),
                  "P6  PROVENANCE: %s has neither evidence_id nor a declared "
                  "evidence_status" % qid)
        else:
            check(eid in ev_by_id,
                  "P6  PROVENANCE: %s cites unknown evidence %r"
                  % (qid, eid))
        probe = q.get("evidence_probe")
        waived = q.get("probe_waived")
        # B1-a (F3-R8 / F5-R2).  evidence_probe used to be opt-in: P1 only
        # forces sig_figs to equal the digits already written into `value`,
        # which is self-consistency and not authority, so a measured quantity
        # could simply omit the probe and never have `value` read back out of
        # the snapshot at all.  For a non-derived quantity that tie is now
        # mandatory.  If the cited evidence is archived there is nothing to
        # waive -- the probe must exist and must pass.  If it is not archived
        # there is no text to read, so the absence has to be stated in
        # probe_waived instead of passed over in silence.
        if q.get("kind") != "derived":
            _ev = ev_by_id.get(eid) if eid is not None else None
            _archived = bool(_ev) and bool(_ev.get("local_copy"))
            _waived = (waived if isinstance(waived, str) and waived.strip()
                       else None)
            if _archived:
                check(probe is not None,
                      "P6  PROVENANCE: %s cites archived evidence %s but "
                      "declares no evidence_probe -- the value must be read "
                      "back out of the snapshot, or the quantity must be "
                      "declared derived" % (qid, eid))
            else:
                check(_waived is not None or probe is not None,
                      "P6  PROVENANCE: %s cites evidence %s with no local "
                      "copy, so no probe can run -- declare an "
                      "evidence_probe against an archived snapshot or state a "
                      "probe_waived reason" % (qid, eid))
                if _waived is not None and probe is None:
                    print("ok    P6  PROVENANCE probe waived %s: %s"
                          % (qid, _waived))
        if probe:
            pid = probe.get("evidence_id")
            ev = ev_by_id.get(pid)
            if not check(ev is not None,
                         "P6  PROVENANCE: %s probe cites unknown evidence %r"
                         % (qid, pid)):
                continue
            lp = ev.get("local_copy")
            path = os.path.join(HERE, str(lp)) if lp else ""
            if not os.path.isfile(path):
                fail("P6  PROVENANCE: %s probe evidence has no local copy"
                     % qid)
                continue
            with io.open(path, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().split("\n")
            needles = probe.get("line_needles") or []
            hit = [ln for ln in lines if needles and needles[0] in ln]
            if not check(hit, "P6  PROVENANCE: %s probe line %r not found in "
                              "%s" % (qid, needles[0], lp)):
                continue
            for extra in needles[1:]:
                check(any(extra in ln for ln in hit),
                      "P6  PROVENANCE: %s probe value %r not on the %r line"
                      % (qid, extra, needles[0]))
            print("ok    P6  PROVENANCE probe %s -> %s" % (qid, pid))
    print("%s P6  PROVENANCE                 delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # -------------------------------------- P7 REFERENCES_COVERAGE ---------
    base = len(failures)
    if refs_text is None:
        fail("P7  REFERENCES_COVERAGE: REFERENCES.md is missing or unreadable")
    else:
        wanted = ([q.get("id") for q in qu_list if isinstance(q, dict)] +
                  [e.get("id") for e in ev_list if isinstance(e, dict)] +
                  [r.get("id") for r in rf_list if isinstance(r, dict)])
        for wid in wanted:
            if not wid:
                continue
            ok = any(ln.strip() == "### %s" % wid
                     for ln in refs_text.replace("\r", "").split("\n"))
            check(ok, "P7  REFERENCES_COVERAGE: no '### %s' heading in "
                      "REFERENCES.md" % wid)
        print("ok    P7  REFERENCES_COVERAGE ids checked: %d" % len(wanted))
    print("%s P7  REFERENCES_COVERAGE        delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ---------------------------------------- P8 REFERENCE_FACT_VALUE ------
    base = len(failures)
    if refs_text is None:
        fail("P8  REFERENCE_FACT_VALUE: REFERENCES.md unavailable")
    else:
        flat = refs_text.replace(",", "").replace("`", "")
        for r in rf_list:
            if not isinstance(r, dict):
                continue
            rid, val = r.get("id"), str(r.get("value"))
            check(token_present(val, flat),
                  "P8  REFERENCE_FACT_VALUE: value %s of %s is not present "
                  "in REFERENCES.md as a complete number" % (val, rid))
    print("%s P8  REFERENCE_FACT_VALUE       delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # --------------------------------------- P9 LAYER_CONSISTENCY ----------
    # Layered evidence archive (F5-2).  The layer decides what may be stored:
    # only layer A may hold content, and P2 already hash-verifies that content.
    # A layer that disagrees with its access class, or a pointer that names a
    # source which is not actually archived, fails here rather than being
    # silently accepted as provenance.
    base = len(failures)
    LAYERS = {"A": "full_text_local_copy",
              "B": "publisher_landing_page",
              "C": "inaccessible"}
    by_id = {}
    for e in ev_list:
        if not isinstance(e, dict):
            fail("P9  LAYER_CONSISTENCY: evidence entry is not an object")
            continue
        eid = str(e.get("id", ""))
        if eid in by_id:
            fail("P9  LAYER_CONSISTENCY: duplicate evidence id %s" % eid)
        by_id[eid] = e
        layer = e.get("layer")
        if layer not in LAYERS:
            fail("P9  LAYER_CONSISTENCY: %s layer %r is not one of A/B/C"
                 % (eid, layer))
            continue
        check(e.get("access") == LAYERS[layer],
              "P9  LAYER_CONSISTENCY: %s is layer %s but access is %r"
              % (eid, layer, e.get("access")))
        check(bool(str(e.get("license_basis", "")).strip()),
              "P9  LAYER_CONSISTENCY: %s carries no licence basis" % eid)
        if layer == "A":
            for k in ("bytes", "sha256", "local_copy"):
                check(k in e,
                      "P9  LAYER_CONSISTENCY: %s is layer A but has no %s"
                      % (eid, k))
        else:
            check(not e.get("local_copy"),
                  "P9  LAYER_CONSISTENCY: %s is layer %s but declares a "
                  "local_copy -- only layer A may hold content"
                  % (eid, layer))

    for q in qu_list:
        if not isinstance(q, dict):
            continue
        qid = q.get("id")
        ev = q.get("evidence_id")
        if ev is None:
            check(bool(q.get("evidence_status")),
                  "P9  LAYER_CONSISTENCY: %s has neither evidence_id nor "
                  "evidence_status" % qid)
        else:
            tgt = by_id.get(str(ev))
            check(tgt is not None,
                  "P9  LAYER_CONSISTENCY: %s names unknown evidence %r"
                  % (qid, ev))
        snap = q.get("snapshot_evidence_id")
        if snap is not None:
            tgt = by_id.get(str(snap))
            if check(tgt is not None,
                     "P9  LAYER_CONSISTENCY: %s names unknown snapshot %r"
                     % (qid, snap)):
                check(tgt.get("layer") == "A",
                      "P9  LAYER_CONSISTENCY: %s snapshot %s is layer %s, "
                      "not A -- a snapshot must be archived"
                      % (qid, snap, tgt.get("layer")))

    for r in rf_list:
        if not isinstance(r, dict):
            continue
        sid = r.get("source_id")
        check(sid in by_id,
              "P9  LAYER_CONSISTENCY: reference fact %s names unknown "
              "source %r" % (r.get("id"), sid))

    print("%s P9  LAYER_CONSISTENCY          delta: %d"
          % ("ok  " if len(failures) == base else "FAIL  ",
             len(failures) - base))

    # ------------------------------------------------- P10 REF_MARKERS ------
    # Phase B. A line that carries an externally sourced number also carries,
    # inside an HTML comment so that the rendered document is byte-for-byte
    # the same text it was before, the evidence id that authorises it.
    # Three directions are checked, so a marker cannot be added, altered or
    # dropped on its own:
    #   RESOLVES - the marker names an evidence id that exists;
    #   REQUIRED - a site line carries the marker of its own quantity;
    #   PLACED   - the marker sits on a line that really is such a site line.
    p10_base = len(failures)
    ref_re = re.compile(r"\[REF-([A-Za-z0-9_.\-]+)\]")
    site_files = sorted({s.get("file")
                         for q in qu_list if isinstance(q, dict)
                         for s in (q.get("sites") or [])
                         if isinstance(s, dict) and s.get("file")})
    # (file, evidence id) -> needles of the quantities that authorise it there
    allowed = {}
    for q in qu_list:
        if not isinstance(q, dict):
            continue
        marks = [q.get("evidence_id"), q.get("snapshot_evidence_id")]
        for s in (q.get("sites") or []):
            if not isinstance(s, dict):
                continue
            for m in marks:
                if m:
                    allowed.setdefault((s.get("file"), str(m)), set()).add(
                        str(s.get("needle")))
    markers_seen = 0
    for fname in site_files:
        path = os.path.join(HERE, str(fname))
        if not check(os.path.isfile(path),
                     "P10  REF_MARKERS: site file %r does not exist" % fname):
            continue
        with io.open(path, encoding="utf-8", newline="") as fh:
            lines = fh.read().split("\n")
        for lineno, line in enumerate(lines, 1):
            for m in ref_re.findall(line):
                markers_seen += 1
                if not check(m in ev_by_id,
                             "P10  REF_MARKERS: %s:%d marker [REF-%s] names "
                             "no evidence entry" % (fname, lineno, m)):
                    continue
                got = allowed.get((fname, m))
                if not check(got is not None,
                             "P10  REF_MARKERS: %s:%d marker [REF-%s] is not "
                             "authorised for this document"
                             % (fname, lineno, m)):
                    continue
                check(any(needle and needle in line for needle in got),
                      "P10  REF_MARKERS: %s:%d marker [REF-%s] does not sit "
                      "on a line carrying its own site needle"
                      % (fname, lineno, m))
        for q in qu_list:
            if not isinstance(q, dict):
                continue
            need = ([str(q.get("evidence_id"))]
                    if q.get("evidence_id") else [])
            if q.get("snapshot_evidence_id"):
                need.append(str(q.get("snapshot_evidence_id")))
            for s in (q.get("sites") or []):
                if not isinstance(s, dict) or s.get("file") != fname:
                    continue
                needle = s.get("needle")
                if not needle:
                    continue
                for lineno, line in enumerate(lines, 1):
                    if needle not in line:
                        continue
                    for m in need:
                        check("[REF-%s]" % m in line,
                              "P10  REF_MARKERS: %s:%d carries %s but no "
                              "[REF-%s] marker" % (fname, lineno, needle, m))
    # A marker only means something in a document this register points at;
    # one pasted anywhere else is dead weight and is refused.
    stray = 0
    for name in sorted(os.listdir(HERE)):
        if not name.lower().endswith(".md"):
            continue
        if name in site_files:
            continue
        with io.open(os.path.join(HERE, name), encoding="utf-8",
                     newline="") as fh:
            text = fh.read()
        for lineno, line in enumerate(text.split("\n"), 1):
            for m in ref_re.findall(line):
                markers_seen += 1
                stray += 1
                fail("P10  REF_MARKERS: %s:%d marker [REF-%s] sits in a "
                     "document no site points at" % (name, lineno, m))
    print("%s P10  REF_MARKERS               delta: %d (markers seen: %d, "
          "stray: %d)"
          % ("ok  " if len(failures) == p10_base else "FAIL  ",
             len(failures) - p10_base, markers_seen, stray))

    # ------------------------------------------------ P11 LIVENESS_RECORD ---
    # The offline half of F7-R3.  `url_liveness_check.py` re-fetches every URL
    # the register knows about and writes provenance/url_liveness.json; this
    # condition refuses to let that record drift away from the register or sit
    # on top of a contradiction the probe has already found.
    #
    # Deliberately NOT checked here:
    #   * freshness -- the record carries `checked_utc`, and a gate that fails
    #     by the clock would break the offline contract the suite exists to
    #     keep.  Age is reported by the probe, not judged by this gate.
    #   * whether the live bodies still match the archived snapshots -- see
    #     "WHY DIVERGED DOES NOT FAIL" in url_liveness_check.py: the register
    #     pins a snapshot taken at `retrieved_utc`, and P2 already verifies
    #     those bytes on disk.
    p11_base = len(failures)
    if not check(os.path.isfile(LIVENESS_PATH),
                 "P11  LIVENESS_RECORD: %s is missing -- run "
                 "python url_liveness_check.py and commit the record"
                 % os.path.relpath(LIVENESS_PATH, HERE).replace("\\", "/")):
        doc = None
    else:
        doc = load_or_die(LIVENESS_PATH, "provenance/url_liveness.json")
    if doc is None and os.path.isfile(LIVENESS_PATH):
        pass  # load_or_die already recorded the reason
    elif doc is not None:
        check(isinstance(doc, dict),
              "P11  LIVENESS_RECORD: the record is not a JSON object")
        if isinstance(doc, dict):
            check(doc.get("schema") == "msaf-url-liveness/v1",
                  "P11  LIVENESS_RECORD: unexpected schema %r"
                  % doc.get("schema"))
            stamp = doc.get("generated_utc")
            check(isinstance(stamp, str) and stamp.endswith("Z") and len(stamp) >= 19,
                  "P11  LIVENESS_RECORD: generated_utc is missing or malformed: %r"
                  % stamp)
            check(doc.get("tool") == "url_liveness_check.py",
                  "P11  LIVENESS_RECORD: tool field is %r"
                  % doc.get("tool"))
            check(doc.get("probe") in ("network", "fixture"),
                  "P11  LIVENESS_RECORD: probe field is %r" % doc.get("probe"))
            recs = doc.get("records")
            check(isinstance(recs, list) and recs,
                  "P11  LIVENESS_RECORD: records is missing or empty")
            recs = recs if isinstance(recs, list) else []
            by_url = {}
            for rec in recs:
                if not check(isinstance(rec, dict),
                             "P11  LIVENESS_RECORD: a record is not an object"):
                    continue
                u = rec.get("url")
                if not check(isinstance(u, str) and u.startswith(("http://", "https://")),
                             "P11  LIVENESS_RECORD: a record has no http url: %r" % (u,)):
                    continue
                check(u not in by_url,
                      "P11  LIVENESS_RECORD: %s is probed twice" % u)
                by_url[u] = rec
                v = rec.get("verdict")
                check(v in ("OK", "CHANGED", "UNREACHABLE", "DIVERGED"),
                      "P11  LIVENESS_RECORD: %s has verdict %r" % (u, v))
                st = rec.get("status")
                check(st is None or isinstance(st, int),
                      "P11  LIVENESS_RECORD: %s has status %r" % (u, st))
                check(isinstance(rec.get("checked_utc"), str)
                      and rec.get("checked_utc").endswith("Z"),
                      "P11  LIVENESS_RECORD: %s has no checked_utc" % u)
                check("sources" in rec and "bytes" in rec
                      and "body_sha256" in rec and "detail" in rec
                      and "error" in rec,
                      "P11  LIVENESS_RECORD: %s is missing a recorded field" % u)
            # The record must name exactly the register's URL set: a gap is a
            # source nobody re-checked, an extra is a source this register has
            # never heard of.
            expected = {}
            try:
                import url_liveness_check as ulc
            except Exception as exc:
                ulc = None
                fail("P11  LIVENESS_RECORD: url_liveness_check.py cannot be "
                     "imported: %s" % exc)
            if ulc is not None:
                for u, srcs in ulc.collect_urls():
                    expected[u] = srcs
                missing = sorted(set(expected) - set(by_url))
                extra = sorted(set(by_url) - set(expected))
                check(not missing,
                      "P11  LIVENESS_RECORD: %d URL(s) the register knows are "
                      "absent from the record: %s"
                      % (len(missing), ", ".join(missing[:5])))
                check(not extra,
                      "P11  LIVENESS_RECORD: %d URL(s) are in the record but "
                      "not in the register: %s"
                      % (len(extra), ", ".join(extra[:5])))
                exp = ulc.expectations()
                for u, e in exp.items():
                    rec = by_url.get(u)
                    if rec is None:
                        continue
                    if e.get("expected_status") is not None:
                        check(rec.get("expected_status") == e["expected_status"],
                              "P11  LIVENESS_RECORD: %s restates status %r, "
                              "the register says %r"
                              % (u, rec.get("expected_status"),
                                 e["expected_status"]))
                    if e.get("layer"):
                        check(rec.get("layer") == e["layer"],
                              "P11  LIVENESS_RECORD: %s restates layer %r, "
                              "the register says %r"
                              % (u, rec.get("layer"), e["layer"]))
                    if e.get("archived_sha256"):
                        check(rec.get("archived_sha256") == e["archived_sha256"],
                              "P11  LIVENESS_RECORD: %s restates sha256 %r, "
                              "the register pins %r -- the record may not "
                              "invent its own pin"
                              % (u, rec.get("archived_sha256"),
                                 e["archived_sha256"]))
                    if e.get("retrieved_utc"):
                        check(rec.get("retrieved_utc") == e["retrieved_utc"],
                              "P11  LIVENESS_RECORD: %s restates retrieved_utc "
                              "%r, the register says %r"
                              % (u, rec.get("retrieved_utc"),
                                 e["retrieved_utc"]))
                # A contradiction the probe already saw and the record kept is
                # an unresolved defect, not a fact to be filed away.
                contradictions = sorted(
                    u for u, rec in by_url.items()
                    if rec.get("verdict") in ("CHANGED", "UNREACHABLE"))
                check(not contradictions,
                      "P11  LIVENESS_RECORD: %d URL(s) recorded as contradicting "
                      "the register are still in the record: %s -- fix the "
                      "register or the source, then re-run the probe"
                      % (len(contradictions), ", ".join(contradictions[:5])))
            n_div = sum(1 for rec in by_url.values()
                        if rec.get("verdict") == "DIVERGED")
            n_ok = sum(1 for rec in by_url.values() if rec.get("verdict") == "OK")
            print("%s P11  LIVENESS_RECORD          delta: %d (urls: %d, "
                  "ok: %d, diverged: %d)"
                  % ("ok  " if len(failures) == p11_base else "FAIL  ",
                     len(failures) - p11_base, len(by_url), n_ok, n_div))
    else:
        print("FAIL  P11  LIVENESS_RECORD          record unreadable")

    # ------------------------------------------------------ verdict --------
    if failures:
        print("")
        for f in failures:
            print("FAIL  %s" % f)
        print("")
        print("GATE: FAIL -- %d condition(s) not met" % len(failures))
        return 1
    print("")
    print("GATE: PASS -- %d quantities, %d evidence snapshots, %d reference "
          "facts, %d conditions"
          % (len(qu_list), len(ev_list), len(rf_list), len(CONDITIONS)))
    return 0


def _num(s):
    from decimal import Decimal
    return Decimal(str(s).replace("e", "E"))


def round_sig(dec, sf):
    """Round a Decimal to sf significant figures, returned as Decimal."""
    from decimal import Decimal, ROUND_HALF_UP
    dec = Decimal(dec)
    if dec == 0:
        return dec
    exp = dec.adjusted() - (int(sf) - 1)
    q = Decimal(1).scaleb(exp)
    return dec.quantize(q, rounding=ROUND_HALF_UP)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print(__doc__)
        sys.exit(0)
    try:
        sys.exit(main(sys.argv))
    except SystemExit:
        raise
    except Exception as exc:  # never let a gate crash into a traceback
        print("FAIL  --  unhandled error: %r" % (exc,))
        print("")
        print("GATE: FAIL -- unhandled error")
        sys.exit(1)
