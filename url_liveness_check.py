# -*- coding: utf-8 -*-
"""URL liveness probe for the MSAF external-provenance register (Fase A9).

WHY THIS EXISTS
---------------
`F7_REPORT.md` residual F7-R3 records the gap this closes: the register stores
a *retrieval date*, not a *liveness guarantee*, and until now the only way to
learn that a cited source had moved was for a reader to notice.  A7 found two
such sentences by hand (the Pitt page and the SEP Zeno path both said 404 and
both had been reachable for some time).  Hand-reading does not repeat.

This tool repeats it.  It re-fetches every URL the register knows about and
writes what happened to `provenance/url_liveness.json`.

WHAT IT DECIDES, AND WHAT IT DOES NOT
-------------------------------------
A source is *live* when it still says what the register says it said:

  OK           the fetched status equals `observed_status` in the register,
               or the register states no status and the fetch succeeded.
  CHANGED      the register records one status and the source now answers
               with another -- the sentence `REFERENCES.md` would let a reader
               write is no longer true.
  UNREACHABLE  the source could not be fetched at all.
  DIVERGED     the status is unchanged but the live body no longer hashes to
               the archived layer-A copy: the page was edited upstream after
               the snapshot was taken.

CHANGED and UNREACHABLE contradict the register and make this tool exit 1.
An unreachable *everywhere* is exit 2: that is no network, not a verdict
about the sources, and a tool that cannot run never reports success.

WHY DIVERGED DOES NOT FAIL
--------------------------
It was made to fail first, and the first real probe proved that rule wrong.
`theorem_provenance.json` layer-A records make exactly two claims: "the fetch
of <url> at <retrieved_utc> returned status <observed_status>" and "we kept
the bytes, sha256 <sha>".  P2 `provenance_check.py` already proves the second
against the file on disk.  Nothing in the register asserts that a page
served a year later still carries byte-identical HTML, and the probe of
2026-10-06 showed how little that would mean:

  Countably_additive_measure  archive 650480 B  live 650737 B
  Ihara_zeta_function         archive 118173 B  live 118173 B, different sha
  Ultraviolet_catastrophe     archive 133784 B  live 134101 B

Wikipedia re-renders these pages constantly; equal length with a different
hash is one timestamp somewhere in the payload.  Failing on it would report a
defect in *this* corpus that exists only in the outside world, which is the
false-positive half of the same error this rig was built to stop.  The
divergence is still measured, written to the record and printed, so a reader
can see it; it is a fact about the source, not a contradiction of the register.

`final_url` is recorded but likewise not gated: for the one record whose
redirect target differs (`doi.org/10.1098/rspa.1970.0021`, HTTP 403) the
register's own `final_url` is simply the request URL, so the field carries no
redirect claim there either.  `final_url_changed` is written to every record.

WHAT IT IS NOT
--------------
It is deliberately **not** one of the `suite_check.py` gates.  The suite is
the offline contract: every gate in it must give the same answer on a machine
with no network.  A gate that fetches would make `SUITE: PASS` depend on a
publisher's uptime, and this workspace has already recorded `HTTP 403` from
two DOIs it considers healthy.  The offline half of the answer lives in
`provenance_check.py` `P11 LIVENESS_RECORD`, which checks that the record
exists, covers exactly the register's URL set and restates its pins.

OFFLINE USE
-----------
`--fixture FILE` replaces the network with a JSON document mapping each URL to
either {"status": N, "sha256": "..."} or {"error": "..."}.  Every URL must be
listed; a URL the fixture does not know is UNREACHABLE.  This is what makes
the fault-injection harness `harnesses/a9_drift_inj.py` deterministic.

Exit codes: 0 = every URL still says what the register says, 1 = a
contradiction was found, 2 = the probe could not run (no network, unusable
fixture, nothing to probe).
"""
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
EC_PATH = os.path.join(HERE, "external_constants.json")
TP_PATH = os.path.join(HERE, "theorem_provenance.json")
REFS_PATH = os.path.join(HERE, "REFERENCES.md")
OUT_PATH = os.path.join(HERE, "provenance", "url_liveness.json")

SCHEMA = "msaf-url-liveness/v1"
VERDICTS = ("OK", "CHANGED", "UNREACHABLE", "DIVERGED")
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
TIMEOUT = 30
TRIES = 2


def _load(path):
    if not os.path.isfile(path):
        return None
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def collect_urls():
    """Every URL the register knows about, in a stable order.

    Sources, and why each one counts:
      external_constants.json `evidence[].url`     the archive entries the
                                                   quantity register points at
      theorem_provenance.json `archive[].url`      the borrowed-authority
                                                   archive itself
      theorem_provenance.json `license_basis_url`  the page that authorises a
                                                   layer-B/C record keeping no
                                                   body (non-empty only)
      REFERENCES.md `* URL:` lines                 the prose register a reader
                                                   actually copies from

    Returning a list of (url, [sources]) rather than a set keeps duplicates
    probing once while still letting a missing source be reported as a gap.
    """
    found = {}

    def add(url, source):
        url = (url or "").strip()
        if not url.startswith(("http://", "https://")):
            return
        found.setdefault(url, [])
        if source not in found[url]:
            found[url].append(source)

    ec = _load(EC_PATH)
    if isinstance(ec, dict):
        for rec in ec.get("evidence") or []:
            if isinstance(rec, dict):
                add(rec.get("url"), "external_constants.json:evidence")

    tp = _load(TP_PATH)
    if isinstance(tp, dict):
        for rec in tp.get("archive") or []:
            if isinstance(rec, dict):
                add(rec.get("url"), "theorem_provenance.json:archive")
                add(rec.get("license_basis_url"),
                    "theorem_provenance.json:license_basis_url")

    if os.path.isfile(REFS_PATH):
        try:
            with io.open(REFS_PATH, encoding="utf-8") as fh:
                refs = fh.read()
            for m in re.finditer(r"^\*\s*URL:\s*`([^`]+)`", refs, re.M):
                add(m.group(1), "REFERENCES.md:url")
        except (OSError, UnicodeDecodeError):
            pass

    return [(u, found[u]) for u in sorted(found)]


def expectations():
    """url -> the register's own claim about it.

    Only `theorem_provenance.json` `archive[]` states an observed status; the
    quantity register stores a retrieval date and nothing a probe can compare
    against, so those URLs carry no expectation and are judged reachable-only.
    """
    out = {}
    tp = _load(TP_PATH)
    if not isinstance(tp, dict):
        return out
    for rec in tp.get("archive") or []:
        if not isinstance(rec, dict):
            continue
        url = (rec.get("url") or "").strip()
        if not url:
            continue
        status = rec.get("observed_status")
        entry = {
            "expected_status": status if isinstance(status, int) else None,
            "layer": rec.get("layer"),
            "retrieved_utc": rec.get("retrieved_utc"),
            "archived_sha256": rec.get("sha256"),
            "local_copy": rec.get("local_copy"),
            "final_url": rec.get("final_url"),
        }
        prev = out.get(url)
        if prev is None or (prev.get("expected_status") is None
                            and entry["expected_status"] is not None):
            out[url] = entry
    return out


def probe(url):
    """One GET.  Returns (status, final_url, body, body_sha, error)."""
    last = None
    for _ in range(TRIES):
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
        })
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.getcode(), resp.geturl(), resp.read(), None, None
        except urllib.error.HTTPError as exc:
            # A 4xx/5xx is an *answer*, not a transport failure: it is the
            # status the comparison below has to see.
            try:
                body = exc.read()
            except Exception:
                body = None
            return exc.code, exc.geturl() or url, body, None, None
        except Exception as exc:  # URLError, timeout, ssl, ...
            last = "%s: %s" % (type(exc).__name__, exc)
            time.sleep(0.5)
    return None, url, None, None, last


def load_fixture(path):
    """Read a --fixture document.  Raises ValueError on anything unusable."""
    if not os.path.isfile(path):
        raise ValueError("fixture file does not exist: %s" % path)
    with io.open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    if not isinstance(doc, dict):
        raise ValueError("fixture must be a JSON object mapping url -> answer")
    for url, ans in doc.items():
        if not isinstance(ans, dict):
            raise ValueError("fixture entry for %r is not an object" % url)
        if "error" in ans:
            continue
        if not isinstance(ans.get("status"), int):
            raise ValueError("fixture entry for %r has no integer status"
                             % url)
    return doc


def fetch(url, fixture):
    """(status, final_url, body, body_sha, error) from fixture or network.

    A fixture answers with a hash instead of bytes, so the two are returned
    separately and `run` never has to guess which one it is holding.
    """
    if fixture is None:
        return probe(url)
    ans = fixture.get(url)
    if ans is None:
        return None, url, None, None, "url absent from fixture"
    if "error" in ans:
        return None, url, None, None, str(ans["error"])
    sha = ans.get("body_sha256")
    return ans["status"], url, None, sha, None


def classify(url, exp, status, body_sha, error):
    """Return (verdict, detail).

    Verdicts that contradict the register are CHANGED and UNREACHABLE; both
    make the tool exit 1.  DIVERGED is measured and reported but never fails
    -- see the "WHY DIVERGED DOES NOT FAIL" section of the module docstring,
    which records the probe of 2026-10-06 that falsified the original rule.
    """
    if error is not None or status is None:
        return "UNREACHABLE", error or "no status returned"
    if exp and exp.get("expected_status") is not None:
        if status != exp["expected_status"]:
            return "CHANGED", "register records HTTP %s, source answered %s" % (
                exp["expected_status"], status)
    if exp and exp.get("expected_status") is None and status >= 400:
        return "CHANGED", "register states no status, source answered %s" % status
    archived = (exp or {}).get("archived_sha256")
    has_copy = bool((exp or {}).get("local_copy"))
    if has_copy and archived and status is not None and status < 400:
        if body_sha and body_sha != archived:
            return "DIVERGED", ("status unchanged; live body sha256 %s... "
                                "differs from the archived snapshot %s..., "
                                "which P2 still verifies on disk"
                                % (body_sha[:16], archived[:16]))
    return "OK", ""


def now_utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run(fixture_path=None, out_path=OUT_PATH, quiet=False):
    """Probe everything and write the record.  Returns the exit code."""
    urls = collect_urls()
    if not urls:
        print("url_liveness_check: nothing to probe -- no URL in the register")
        return 2

    fixture = None
    if fixture_path:
        try:
            fixture = load_fixture(fixture_path)
        except ValueError as exc:
            print("FAIL  fixture unusable: %s" % exc)
            print("url_liveness_check: TOOL NOT RUN")
            return 2

    exp = expectations()
    stamp = now_utc()
    records = []
    tally = {v: 0 for v in VERDICTS}
    reached = 0

    for url, sources in urls:
        status, final, body, body_sha, error = fetch(url, fixture)
        if body_sha is None and body:
            body_sha = hashlib.sha256(body).hexdigest()
        verdict, detail = classify(url, exp.get(url), status, body_sha, error)
        tally[verdict] += 1
        if error is None and status is not None:
            reached += 1
        e = exp.get(url) or {}
        recorded_final = e.get("final_url")
        rec = {
            "url": url,
            "sources": sources,
            "status": status,
            "final_url": final,
            "expected_final_url": recorded_final,
            "final_url_changed": bool(recorded_final)
            and recorded_final != (final or url),
            "bytes": None if body is None else len(body),
            "body_sha256": body_sha,
            "expected_status": e.get("expected_status"),
            "layer": e.get("layer"),
            "retrieved_utc": e.get("retrieved_utc"),
            "archived_sha256": e.get("archived_sha256"),
            "verdict": verdict,
            "detail": detail,
            "error": error,
            "checked_utc": stamp,
        }
        records.append(rec)
        if not quiet and verdict != "OK":
            print("%-11s %s" % (verdict, url))
            if detail:
                print("             %s" % detail)

    doc = {
        "schema": SCHEMA,
        "tool": "url_liveness_check.py",
        "generated_utc": stamp,
        "probe": "fixture" if fixture else "network",
        "urls": len(records),
        "tally": {k: tally[k] for k in VERDICTS},
        "records": records,
    }
    d = os.path.dirname(out_path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(doc, indent=2, sort_keys=False,
                            ensure_ascii=False) + "\n")

    bad = tally["CHANGED"] + tally["UNREACHABLE"]
    print("")
    print("probed %d URL(s): OK=%d CHANGED=%d UNREACHABLE=%d DIVERGED=%d"
          % (len(records), tally["OK"], tally["CHANGED"],
             tally["UNREACHABLE"], tally["DIVERGED"]))
    if reached == 0:
        print("url_liveness_check: TOOL NOT RUN -- no URL could be reached, "
              "so nothing was established about any of them")
        return 2
    if bad:
        try:
            shown = os.path.relpath(out_path, HERE)
        except ValueError:
            shown = out_path
        print("url_liveness_check: FAIL -- %d URL(s) contradict the register "
              "(record written to %s)" % (bad, shown))
        return 1
    if tally["DIVERGED"]:
        print("url_liveness_check: %d source(s) edited upstream since the "
              "snapshot -- recorded, not a register defect"
              % tally["DIVERGED"])
    print("url_liveness_check: PASS -- every URL still answers with the status "
          "the register records")
    return 0


def main(argv):
    fixture = None
    out = OUT_PATH
    argv = list(argv[1:])
    while argv:
        a = argv.pop(0)
        if a == "--fixture" and argv:
            fixture = argv.pop(0)
        elif a == "--out" and argv:
            out = argv.pop(0)
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            print("FAIL  unknown argument %r" % a)
            return 2
    env = os.environ.get("URL_LIVENESS_FIXTURE")
    if fixture is None and env:
        fixture = env
    return run(fixture, out)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
