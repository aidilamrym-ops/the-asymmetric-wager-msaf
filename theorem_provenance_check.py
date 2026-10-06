#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F4 gate -- external mathematical provenance of the MSAF corpus.

Every time a corpus document leans on a theorem, a school, a named result or an
open problem that it did not prove itself, that authority is BORROWED.  This
gate makes the borrowing explicit and checkable.

It reads `theorem_provenance.json` and the in-scope corpus documents, and asks
seven questions.  Nothing here is inferred from the prose: every number of hits,
every anchor and every coverage decision is computed from the files as they are
on disk.

Checks
  P1  REGISTER_SCHEMA     the register parses, every entry has every required
                          field, ids are unique and well formed, enums are legal
  P2  ANCHOR_RESOLVES     every entry's `document` exists and its `anchor`
                          regex matches EXACTLY ONCE in that document (whole
                          file; line numbers are never trusted)
  P3  COVERAGE            every line in an in-scope document that invokes an
                          external authority must be covered by an entry
                          REGISTERED FOR THAT SAME DOCUMENT -- an unregistered
                          borrowed claim fails
  P4  EVIDENCE            each entry carries a real, non-placeholder citation:
                          source, identifier, retrieval date, quote >= 40 chars
  P5  DEFECT_CLOSED       an entry with a finding of severity "defect" or
                          "note" must carry a `correction`; a "defect" must in
                          addition have its marker (the finding id) actually
                          present in the document -- a recorded but unfixed
                          defect fails
  P6  MACHINE_GATE_LINK   an entry declaring `machine_gated_by` must name a gate
                          file that exists on disk
  P7  FINDING_SHAPE       finding ids are unique, severity is legal, and a
                          non-defect entry may not claim a correction it does
                          not need
  P8  MARKER_LEDGER       two-way binding: every [F4-x] marker found in an
                          in-scope document must be a registered finding, and
                          every registered defect must have its marker -- so a
                          finding cannot be silenced by editing only one side
  P9  ARCHIVE_CONSISTENCY the layered evidence archive (F5-2): every layer is
                          A/B/C and agrees with its access class, every layer-A
                          snapshot exists on disk with the declared size and
                          sha256, layers B and C carry no content, and every
                          borrowed identifier is archived exactly once and
                          cited by at least one entry

Exit 0 = every claim verified.
Exit 1 = a claim failed.
Exit 2 = tool not run (register or a required document is unavailable).

usage: python theorem_provenance_check.py
"""
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXIT_OK, EXIT_FAIL, EXIT_NOTRUN = 0, 1, 2

REGISTER = "theorem_provenance.json"

# Authorities that belong to some other body of work.  A corpus line matching
# any of these is a line that borrows; it must therefore be covered by an entry.
# Nothing invented by MSAF appears here on purpose.
#
# These rules are deliberately written to catch paraphrases, not just one
# spelling: under-detection silently voids the coverage check, while
# over-detection only adds entries that must be justified.  f4_brittleness.py
# re-tests every rule against natural paraphrases of the authority.
EXTERNAL = {
    "DENSITY":    r"(?i)density of real numbers|rationals?.{0,60}\bdens"
                  r"|dense.{0,60}rationals?|density of (the )?(rationals|reals)"
                  r"|dense (in|subset of) (the )?(real|R)",
    "ZENO":       r"(?i)\bZeno('?s)?\b",
    "COUNTADD":   r"(?i)countabl[ye]\s*additiv|countabl[ye]\s+sum"
                  r"|(sigma|\u03c3)-?additiv|uncountabl[ye] additiv",
    "LEBESGUE":   r"(?i)Lebesgue",
    "BROUWER":    r"(?i)\bBrouwer(ian)?\b|\bintuitionis(m|tic|t|tically)\b",
    "STRICTFIN":  r"(?i)strict finitis",
    "CONSTRMATH": r"(?i)constructive (mathematics|math)\b|\bconstructivis(m|t)\b",
    "HAWKPEN":    r"(?i)hawking.{0,40}penrose|penrose.{0,40}hawking",
    "LANDAUER":   r"(?i)Landauer",
    "MILLENNIUM": r"(?i)millennium (prize|problems?|challenge)|clay millennium",
    "NAVIER":     r"(?i)navier[-\u2013 ]stokes",
    "LANGLANDS":  r"(?i)Langlands",
    "IHARA":      r"(?i)\bIhara\b",
    "GALOIS":     r"(?i)\bGalois\b",
    "RENORMAL":   r"(?i)renormali[sz]",
    "UVCATA":     r"(?i)ultraviolet catastrophe|\bUV catastrophe\b",
    "WIMP":       r"(?i)\bWIMPs?\b|weakly interacting (massive|minor) particles",
    "SHANNON":    r"(?i)Shannon",
    "RAYLEIGH":   r"(?i)Rayleigh",
    "GR":         r"(?i)general relativity|einstein'?s (field )?equations",
    "GODEL":      r"G(?:\u00f6|o|oe|&ouml;|&#246;)del",
}

REQUIRED = ("id", "named_result", "document", "anchor", "covers", "status",
            "attributed_to", "corpus_usage", "evidence")
STATUS_ENUM = ("standard-theorem", "open-problem", "conjecture", "heuristic",
               "empirical-claim", "machine-gated")
SEVERITY_ENUM = ("none", "note", "defect")
ID_RE = re.compile(r"^T\d{3}$")
FIND_RE = re.compile(r"^F\d-[A-Z]$")
MARK_RE = re.compile(r"\[(F\d+-[A-Z])\]")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
IDENT_RE = re.compile(r"(?i)(arxiv|doi:|doi\.org|https?://|isbn|local:)")
QUOTE_MIN = 40

_failures = []


def fail(tag, msg):
    _failures.append("%s  %s" % (tag, msg))
    print("FAIL  %s  %s" % (tag, msg))


def ok(tag, msg):
    print("ok    %s  %s" % (tag, msg))


def skip(tag, msg):
    print("SKIP  %s  %s" % (tag, msg))


def load_text(path):
    """Strict UTF-8 read.  A file that will not decode is a hard error."""
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def nonempty(value):
    return isinstance(value, str) and value.strip() != ""


def main():
    reg_path = os.path.join(HERE, REGISTER)
    if not os.path.isfile(reg_path):
        skip("P1  REGISTER_SCHEMA", "%s is missing" % REGISTER)
        return EXIT_NOTRUN
    try:
        raw = load_text(reg_path)
        reg = json.loads(raw)
    except (UnicodeDecodeError, ValueError) as exc:
        fail("P1  REGISTER_SCHEMA", "%s will not parse: %s" % (REGISTER, exc))
        return EXIT_FAIL

    # ---------------------------------------------------------------- P1
    if not isinstance(reg, dict) or not isinstance(reg.get("entries"), list):
        fail("P1  REGISTER_SCHEMA", "register must be an object with an 'entries' list")
        return EXIT_FAIL
    if not isinstance(reg.get("schema"), str) or not reg["schema"]:
        fail("P1  REGISTER_SCHEMA", "'schema' must be a non-empty string")

    scope = reg.get("scope")
    if not isinstance(scope, list) or not scope:
        fail("P1  REGISTER_SCHEMA", "'scope' must be a non-empty list of documents")
        return EXIT_FAIL
    if not all(isinstance(s, str) and s for s in scope):
        fail("P1  REGISTER_SCHEMA", "every scope entry must be a non-empty string")

    entries = reg["entries"]
    seen_ids = set()
    problems = 0
    for n, e in enumerate(entries):
        label = "entries[%d]" % n
        if not isinstance(e, dict):
            fail("P1  REGISTER_SCHEMA", "%s is not an object" % label)
            problems += 1
            continue
        for field in REQUIRED:
            if field not in e:
                fail("P1  REGISTER_SCHEMA", "%s is missing field '%s'" % (label, field))
                problems += 1
        eid = e.get("id")
        if not isinstance(eid, str) or not ID_RE.match(eid):
            fail("P1  REGISTER_SCHEMA", "%s has id %r, expected Tnnn" % (label, eid))
            problems += 1
        elif eid in seen_ids:
            fail("P1  REGISTER_SCHEMA", "duplicate id %s" % eid)
            problems += 1
        else:
            seen_ids.add(eid)
        if e.get("status") not in STATUS_ENUM:
            fail("P1  REGISTER_SCHEMA", "%s status %r not in %s"
                 % (label, e.get("status"), "/".join(STATUS_ENUM)))
            problems += 1
        cov = e.get("covers")
        if not isinstance(cov, list) or not cov or not all(isinstance(c, str) for c in cov):
            fail("P1  REGISTER_SCHEMA", "%s 'covers' must be a non-empty list of strings" % label)
            problems += 1
        for rx in list(cov if isinstance(cov, list) else []):
            try:
                re.compile(rx)
            except re.error as exc:
                fail("P1  REGISTER_SCHEMA", "%s bad covers regex %r: %s" % (label, rx, exc))
                problems += 1
        anc = e.get("anchor")
        if isinstance(anc, str):
            try:
                re.compile(anc)
            except re.error as exc:
                fail("P1  REGISTER_SCHEMA", "%s bad anchor regex %r: %s" % (label, anc, exc))
                problems += 1
        else:
            fail("P1  REGISTER_SCHEMA", "%s 'anchor' must be a string" % label)
            problems += 1
    if not problems:
        ok("P1  REGISTER_SCHEMA", "%d entries, %d scope documents, ids unique, enums legal"
           % (len(entries), len(scope)))

    # ------------------------------------------------------- documents
    bodies = {}
    missing = []
    for name in scope:
        path = os.path.join(HERE, name)
        if not os.path.isfile(path):
            missing.append(name)
            continue
        try:
            bodies[name] = load_text(path)
        except (UnicodeDecodeError, OSError) as exc:
            missing.append("%s (%s)" % (name, exc))
    # every entry must name a document, in scope or not; scope is the coverage
    # universe, but a stray document reference is still a defect worth reporting
    for e in entries:
        doc = e.get("document")
        if isinstance(doc, str) and doc not in bodies and os.path.isfile(os.path.join(HERE, doc)):
            try:
                bodies[doc] = load_text(os.path.join(HERE, doc))
            except (UnicodeDecodeError, OSError) as exc:
                missing.append("%s (%s)" % (doc, exc))
    if missing:
        for m in missing:
            fail("P1  REGISTER_SCHEMA", "required document unavailable: %s" % m)
        return EXIT_NOTRUN

    # ---------------------------------------------------------------- P2
    p2 = 0
    for e in entries:
        doc, anc = e.get("document"), e.get("anchor")
        if not isinstance(doc, str) or doc not in bodies:
            fail("P2  ANCHOR_RESOLVES", "%s names document %r which is not in scope"
                 % (e.get("id"), doc))
            p2 += 1
            continue
        hits = len(re.findall(anc, bodies[doc]))
        if hits != 1:
            fail("P2  ANCHOR_RESOLVES", "%s anchor %r matched %d times in %s (want 1)"
                 % (e.get("id"), anc, hits, doc))
            p2 += 1
    if not p2:
        ok("P2  ANCHOR_RESOLVES", "all %d anchors resolve exactly once" % len(entries))

    # ---------------------------------------------------------------- P3
    p3 = 0
    covered = 0
    uncovered_lines = []
    for name in scope:
        body = bodies.get(name)
        if body is None:
            continue
        own = [e for e in entries if e.get("document") == name]
        compiled = []
        for e in own:
            for rx in e.get("covers") or []:
                try:
                    compiled.append((e.get("id"), re.compile(rx)))
                except re.error:
                    pass
        for lineno, line in enumerate(body.split("\n"), 1):
            tags = [k for k, p in EXTERNAL.items() if re.search(p, line)]
            if not tags:
                continue
            if any(rx.search(line) for _, rx in compiled):
                covered += 1
            else:
                p3 += 1
                uncovered_lines.append((name, lineno, tags, line.strip()[:100]))
    for name, lineno, tags, line in uncovered_lines:
        fail("P3  COVERAGE", "%s:%d invokes [%s] but no entry registered for that "
                             "document covers it | %s"
             % (name, lineno, ",".join(tags), line))
    if not p3:
        ok("P3  COVERAGE", "%d borrowed-authority lines covered, 0 unregistered" % covered)

    # ---------------------------------------------------------------- P4
    p4 = 0
    for e in entries:
        ev = e.get("evidence")
        if not isinstance(ev, dict):
            fail("P4  EVIDENCE", "%s has no evidence object" % e.get("id"))
            p4 += 1
            continue
        for field in ("source", "identifier", "retrieved", "quote"):
            if not nonempty(ev.get(field)):
                fail("P4  EVIDENCE", "%s evidence.%s is empty" % (e.get("id"), field))
                p4 += 1
        ident = ev.get("identifier")
        if nonempty(ident) and not IDENT_RE.search(ident):
            fail("P4  EVIDENCE", "%s identifier %r carries no arXiv/DOI/URL/local marker"
                 % (e.get("id"), ident))
            p4 += 1
        retrieved = ev.get("retrieved")
        if nonempty(retrieved) and not DATE_RE.match(retrieved):
            fail("P4  EVIDENCE", "%s retrieved %r is not YYYY-MM-DD" % (e.get("id"), retrieved))
            p4 += 1
        quote = ev.get("quote")
        if nonempty(quote) and len(quote.strip()) < QUOTE_MIN:
            fail("P4  EVIDENCE", "%s quote is %d chars, placeholder threshold is %d"
                 % (e.get("id"), len(quote.strip()), QUOTE_MIN))
            p4 += 1
        for field in ("source", "identifier", "quote"):
            val = ev.get(field)
            if nonempty(val) and val.strip().lower() in ("todo", "tbd", "xxx", "n/a", "none"):
                fail("P4  EVIDENCE", "%s evidence.%s is a placeholder (%r)"
                     % (e.get("id"), field, val))
                p4 += 1
    if not p4:
        ok("P4  EVIDENCE", "all %d citations carry source, identifier, date and a real quote"
           % len(entries))

    # ---------------------------------------------------------------- P5
    p5 = 0
    defects = 0
    for e in entries:
        f = e.get("finding")
        if f is None:
            continue
        if not isinstance(f, dict):
            fail("P5  DEFECT_CLOSED", "%s 'finding' must be an object or null" % e.get("id"))
            p5 += 1
            continue
        sev = f.get("severity")
        if sev not in SEVERITY_ENUM:
            fail("P5  DEFECT_CLOSED", "%s severity %r not in %s"
                 % (e.get("id"), sev, "/".join(SEVERITY_ENUM)))
            p5 += 1
            continue
        fid = f.get("id")
        if not isinstance(fid, str) or not FIND_RE.match(fid):
            fail("P5  DEFECT_CLOSED", "%s finding id %r is not of the form F<n>-<A>"
                 % (e.get("id"), fid))
            p5 += 1
        if sev == "none":
            continue
        # Any finding that is not explicitly "none" is a disposition that had to
        # be written down.  Without this clause a defect can be silenced by
        # downgrading its severity and deleting its correction -- that hole was
        # found by f4_inj.py ("severity downgraded to dodge the fix").
        if not nonempty(e.get("correction")):
            fail("P5  DEFECT_CLOSED", "%s (%s) has severity=%s but no 'correction' -- "
                                       "a recorded finding must say what was done"
                 % (e.get("id"), fid, sev))
            p5 += 1
        if sev != "defect":
            continue
        defects += 1
        doc = e.get("document")
        body = bodies.get(doc)
        if body is None:
            fail("P5  DEFECT_CLOSED", "%s defect marker cannot be checked, %s unreadable"
                 % (e.get("id"), doc))
            p5 += 1
        elif fid not in body:
            fail("P5  DEFECT_CLOSED", "%s defect %s is recorded but marker %r does not "
                                       "appear in %s -- the defect is not fixed"
                 % (e.get("id"), fid, fid, doc))
            p5 += 1
    if not p5:
        ok("P5  DEFECT_CLOSED", "%d defects, all corrected in-document with markers present"
           % defects)

    # ---------------------------------------------------------------- P6
    p6 = 0
    links = 0
    for e in entries:
        gate = e.get("machine_gated_by")
        if gate is None:
            continue
        links += 1
        if not nonempty(gate):
            fail("P6  MACHINE_GATE_LINK", "%s machine_gated_by is empty" % e.get("id"))
            p6 += 1
            continue
        if not os.path.isfile(os.path.join(HERE, gate)):
            fail("P6  MACHINE_GATE_LINK", "%s points at %r which does not exist"
                 % (e.get("id"), gate))
            p6 += 1
    if not p6:
        ok("P6  MACHINE_GATE_LINK", "%d cross-links, every named gate exists" % links)

    # ---------------------------------------------------------------- P7
    p7 = 0
    seen_find = set()
    for e in entries:
        f = e.get("finding")
        if not isinstance(f, dict):
            continue
        fid = f.get("id")
        if fid in seen_find:
            fail("P7  FINDING_SHAPE", "finding id %s appears more than once" % fid)
            p7 += 1
        seen_find.add(fid)
        # "none" means "nothing to do"; defect and note both document a
        # disposition, so both must carry a correction (see P5).
        if f.get("severity") == "none" and e.get("correction"):
            fail("P7  FINDING_SHAPE", "%s carries a correction but severity=none -- "
                                       "severity and correction disagree" % e.get("id"))
            p7 += 1
    if not p7:
        ok("P7  FINDING_SHAPE", "%d findings, ids unique, severity agrees with correction"
           % len(seen_find))

    # ---------------------------------------------------------------- P8
    # Two-way binding.  Neither side of this ledger can be edited alone to make
    # a finding disappear: the document cannot drop a marker that the register
    # still claims, and the register cannot drop a finding whose marker the
    # document still carries.
    p8 = 0
    findings = [e["finding"] for e in entries
                if isinstance(e.get("finding"), dict)]
    markers = {}
    for doc in scope:
        body = bodies.get(doc)
        if body is None:
            continue
        for m in MARK_RE.finditer(body):
            markers.setdefault(m.group(1), []).append(doc)
    registered = {f.get("id") for f in findings if isinstance(f.get("id"), str)}
    orphan = sorted(set(markers) - registered)
    for mk in orphan:
        fail("P8  MARKER_LEDGER", "%s appears in %s but no register entry claims it -- "
                                  "an unregistered marker cannot be audited"
             % (mk, ", ".join(sorted(set(markers[mk])))))
        p8 += 1
    unmarked = sorted(registered - set(markers))
    for fid in unmarked:
        fail("P8  MARKER_LEDGER", "finding %s is registered but its marker is absent from "
                                  "every scope document -- nothing anchors it in the corpus"
             % fid)
        p8 += 1
    # A marker in a document means "we did something about this finding".
    # severity=none means "there was nothing".  Both cannot hold: downgrading a
    # defect to none while its correction marker stays put would otherwise pass.
    fid_entry = {}
    for e in entries:
        f = e.get("finding")
        if isinstance(f, dict) and isinstance(f.get("id"), str):
            fid_entry[f["id"]] = e
    for mk in sorted(set(markers) & registered):
        ent = fid_entry.get(mk)
        if ent is not None and ent["finding"].get("severity") == "none":
            fail("P8  MARKER_LEDGER", "%s is marked fixed in %s but its register entry %s "
                                      "claims severity=none -- a fix and 'no finding' disagree"
                 % (mk, ", ".join(sorted(set(markers[mk]))), ent.get("id")))
            p8 += 1
    if not p8:
        ok("P8  MARKER_LEDGER", "%d markers and %d registered findings, both directions agree"
           % (len(markers), len(registered)))

    # ---------------------------------------------------------------- P9
    # Layered evidence archive (F5-2).  A source claimed as archived must be
    # on disk with the recorded size and hash; a source that could not be
    # retrieved must not claim a copy; every borrowed identifier must appear
    # in the ledger exactly once and be cited by at least one entry.
    p9 = 0
    archive = reg.get("archive")
    if not isinstance(archive, list) or not archive:
        fail("P9  ARCHIVE_CONSISTENCY",
             "register has no non-empty 'archive' list")
        p9 += 1
        archive = []
    LAYERS = {"A": "full_text_local_copy",
              "B": "publisher_landing_page",
              "C": "inaccessible"}

    def norm_ident(ident):
        if not isinstance(ident, str):
            return None
        if ident.startswith("local:"):
            return None
        if ident.startswith("doi:"):
            return "https://doi.org/" + ident[4:]
        if ident.startswith("arXiv:"):
            return "https://arxiv.org/abs/" + ident[6:]
        # A trailing slash is a spelling choice, not a different source.
        return ident.rstrip("/")

    seen_ident = set()
    for rec in archive:
        if not isinstance(rec, dict):
            fail("P9  ARCHIVE_CONSISTENCY", "archive entry is not an object")
            p9 += 1
            continue
        ident = rec.get("identifier")
        if not isinstance(ident, str) or not ident.strip():
            fail("P9  ARCHIVE_CONSISTENCY", "archive entry with no identifier")
            p9 += 1
            continue
        if ident in seen_ident:
            fail("P9  ARCHIVE_CONSISTENCY",
                 "%s appears twice in the archive" % ident)
            p9 += 1
        seen_ident.add(ident)
        layer = rec.get("layer")
        if layer not in LAYERS:
            fail("P9  ARCHIVE_CONSISTENCY",
                 "%s layer %r is not one of A/B/C" % (ident, layer))
            continue
        if rec.get("access_class") != LAYERS[layer]:
            fail("P9  ARCHIVE_CONSISTENCY",
                 "%s layer %s disagrees with access_class %r"
                 % (ident, layer, rec.get("access_class")))
            p9 += 1
        if not isinstance(rec.get("license_basis"), str) \
                or not rec["license_basis"].strip():
            fail("P9  ARCHIVE_CONSISTENCY",
                 "%s carries no licence basis" % ident)
            p9 += 1
        if not re.match(r"^\d{4}-\d{2}-\d{2}$",
                        str(rec.get("retrieved_utc", ""))):
            fail("P9  ARCHIVE_CONSISTENCY",
                 "%s retrieved_utc %r is not YYYY-MM-DD"
                 % (ident, rec.get("retrieved_utc")))
            p9 += 1
        if layer == "A":
            rel = rec.get("local_copy")
            if not isinstance(rel, str) or not rel:
                fail("P9  ARCHIVE_CONSISTENCY",
                     "%s is layer A but declares no local_copy" % ident)
                p9 += 1
                continue
            path = os.path.join(HERE, rel)
            if not os.path.isfile(path):
                fail("P9  ARCHIVE_CONSISTENCY",
                     "%s layer A snapshot %s is missing from the workspace"
                     % (ident, rel))
                p9 += 1
                continue
            size = os.path.getsize(path)
            if size != rec.get("bytes"):
                fail("P9  ARCHIVE_CONSISTENCY",
                     "%s snapshot is %d bytes, register declares %r"
                     % (ident, size, rec.get("bytes")))
                p9 += 1
            h = hashlib.sha256()
            with io.open(path, "rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    h.update(chunk)
            if h.hexdigest() != str(rec.get("sha256", "")).lower():
                fail("P9  ARCHIVE_CONSISTENCY",
                     "%s snapshot sha256 %s != declared %s"
                     % (ident, h.hexdigest(), rec.get("sha256")))
                p9 += 1
        elif rec.get("local_copy"):
            fail("P9  ARCHIVE_CONSISTENCY",
                 "%s is layer %s but declares a local_copy -- only layer A "
                 "may hold content" % (ident, layer))
            p9 += 1

    cited = set()
    for e in entries:
        n = norm_ident((e.get("evidence") or {}).get("identifier"))
        if n:
            cited.add(n)
    in_ledger = {n for n in (norm_ident(i) for i in seen_ident) if n}
    for i in sorted(cited - in_ledger):
        fail("P9  ARCHIVE_CONSISTENCY",
             "%s is cited by an entry but absent from the archive" % i)
        p9 += 1
    for i in sorted(in_ledger - cited):
        fail("P9  ARCHIVE_CONSISTENCY",
             "%s is archived but cited by no entry" % i)
        p9 += 1
    if not p9:
        ok("P9  ARCHIVE_CONSISTENCY",
           "%d archived sources, layers agree with access, every layer-A "
           "snapshot hash-verifies, no uncited record" % len(archive))

    print()
    if _failures:
        print("FURTHEMORE:")
        print("  total failures: %d" % len(_failures))
        return EXIT_FAIL
    print("THEOREM PROVENANCE CHECK: every borrowed authority is registered, "
          "evidenced and closed.")
    return EXIT_OK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # a harness bug must not masquerade as a result
        import traceback
        traceback.print_exc()
        print("FAIL  HARNESS  unexpected exception: %r" % (exc,))
        sys.exit(EXIT_FAIL)
