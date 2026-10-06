# FILE: report_claim_check.py
# PURPOSE: the reports are prose, and prose is the one part of this workspace
#          that no other gate reads.  Every other gate checks artefacts; this
#          one checks the sentences that *describe* the artefacts, because a
#          correct gate behind a stale sentence still lets a reader quote the
#          wrong number.  Three classes of claim are checked:
#            P1..P4  CANONICAL -- the current-state numbers in Skill.md and
#                    Brain.MD must equal the live values, with no escape hatch.
#            P5      DATED -- a number in any report that differs from the live
#                    value is allowed only as history, and history must be
#                    anchored (a date, a phase tag, "then", "as of") within one
#                    line of the claim.  An unanchored stale number reads as a
#                    statement about today, which is the defect this catches.
#            P6..P7  REFERENCE -- a path the reports name must exist, and a
#                    file that exists must be registered.
# EXIT:    0 = every claim agrees with the live values (or is honestly dated)
#          1 = at least one claim is wrong or unanchored
#          2 = the live values could not be established (never reported as pass)
# READ-ONLY: this gate never writes to the corpus.

import os
import re
import sys

import checksum_check
import harness_check
import suite_check

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, "Skill.md")
BRAIN = os.path.join(HERE, "Brain.MD")
MANIFEST = os.path.join(HERE, "CHECKSUM.sha256")

# An anchor proves a number is written as history rather than as a fact about
# today.  Anything the writer could have used to date the sentence counts.
ANCHORS = (
    re.compile(r"20\d\d-\d\d-\d\d"),
    re.compile(r"\bat\s+[FA]\d"),
    re.compile(r"\bat\s+v\d"),
    re.compile(r"\bthen\b"),
    re.compile(r"\bas of\b"),
    re.compile(r"\bat the time\b"),
    re.compile(r"\bnow\b"),
    re.compile(r"\bF\d\b"),
    re.compile(r"\bA\d\b"),
    re.compile(r"->|→"),
)

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL  %s" % msg)


def ok(msg):
    print("ok  %s" % msg)


def ordinal(n):
    if 0 <= n < len(ORDINALS):
        return ORDINALS[n]
    return str(n)


# Cardinal and ordinal words are generated rather than written out, because a
# hand-typed list is a list that goes stale: both used to stop at thirty while
# the manifest already held eighty-one rows, so "eighty-one tracked rows" was
# a claim this gate never read.  0..99 now is the range a count here can reach
# for a long while, and the two lists cannot drift apart from each other.
_CARD_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven",
              "eight", "nine", "ten", "eleven", "twelve", "thirteen",
              "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
              "nineteen"]
_CARD_STEMS = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy",
               "eighty", "ninety"]
CARDINALS = list(_CARD_ONES)
for _stem in _CARD_STEMS:
    CARDINALS.append(_stem)
    # one..nine only: "twenty-ten" and "thirty-eleven" are not words, and a
    # generator that emitted them would shift every index above nineteen.
    CARDINALS.extend("%s-%s" % (_stem, _w) for _w in _CARD_ONES[1:10])
WORDNUM = {w: i for i, w in enumerate(CARDINALS)}
SPOKEN = "|".join(re.escape(w) for w in CARDINALS)
# A cardinal word must not be read out of the middle of a longer hyphenated
# one: "nine" inside "ninety-nine" is not a count of nine.  Reading it as one
# both misreports the value and hides the claim that was really there.
SPOKEN = r"(?<![A-Za-z-])(?:" + SPOKEN + r")(?![A-Za-z-])"

_ORD_ONES = ["zeroth", "first", "second", "third", "fourth", "fifth", "sixth",
             "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth",
             "thirteenth", "fourteenth", "fifteenth", "sixteenth",
             "seventeenth", "eighteenth", "nineteenth"]
_ORD_STEMS = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy",
              "eighty", "ninety"]
_ORD_TENS = ["twentieth", "thirtieth", "fortieth", "fiftieth", "sixtieth",
             "seventieth", "eightieth", "ninetieth"]
ORDINALS = list(_ORD_ONES)
for _stem, _ten in zip(_ORD_STEMS, _ORD_TENS):
    ORDINALS.append(_ten)
    ORDINALS.extend("%s-%s" % (_stem, _w) for _w in _ORD_ONES[1:10])


# The determiner is what makes a cardinal a claim about *the* rig.  "across
# six gates", "of two gates" and "pass three gates" count something else;
# "the thirteen gates are a read-only contract" counts the suite.
SPOKEN_GATES = re.compile(r"\b(?:all|the)\s+(" + SPOKEN + r")\s+(?:root\s+)?gates\b",
                          re.I)
SPOKEN_ROOT_GATES = re.compile(r"\b(" + SPOKEN + r")\s+root gates\b", re.I)
SPOKEN_HARNESSES = re.compile(r"\b(?:all|the)\s+(" + SPOKEN + r")\s+(?:proof\s+)?harnesses\b",
                              re.I)
SPOKEN_ROWS = re.compile(r"\b(?:all|the)\s+(" + SPOKEN + r")\s+(?:tracked\s+)?rows\b",
                         re.I)
# "the manifest lists eighty-one rows" and "eighty-one tracked rows" both make
# the same claim about CHECKSUM.sha256.  Only the first used to be read, so a
# writer who spelled the count out and named the manifest in the same breath
# slipped past the gate; the digit form already had this coverage.
SPOKEN_ROWS_BARE = re.compile(r"\b(" + SPOKEN + r")\s+(?:tracked\s+)?rows\b",
                              re.I)
# "N entries" is only a claim about this rig inside an enumeration of the
# `--with-harness` runner, digit or letter.  Without the spelled form, a
# sentence writing the count in words walked straight past this gate.
SPOKEN_ENTRIES = re.compile(r"\b(" + SPOKEN + r")\s+entries\b", re.I)
# "fourteen of the fourteen gates" and "all fifteen of the fifteen harnesses"
# are the same claim as "14 gates": both halves must agree with the live
# value, or neither is a fact about today.
SPOKEN_OF_GATES = re.compile(
    r"\b(" + SPOKEN + r")\s+of\s+(?:all\s+|the\s+)?(" + SPOKEN
    + r")\s+(?:root\s+)?gates\b", re.I)
SPOKEN_OF_HARNESSES = re.compile(
    r"\b(" + SPOKEN + r")\s+of\s+(?:all\s+|the\s+)?(" + SPOKEN
    + r")\s+(?:proof\s+)?harnesses\b", re.I)


def spelled(n):
    return CARDINALS[n] if 0 <= n < len(CARDINALS) else str(n)


def spoken_number(word):
    return WORDNUM.get(word.lower())


def rooted_md():
    """Root-level Markdown documents only: the corpus, not the sub-repository,
    not provenance/evidence (snapshot files are not claims about this workspace)."""
    names = []
    try:
        entries = sorted(os.listdir(HERE))
    except OSError as exc:
        raise SystemExit("cannot list %s: %s" % (HERE, exc))
    for name in entries:
        full = os.path.join(HERE, name)
        if os.path.isfile(full) and name.lower().endswith(".md"):
            names.append(name)
    return names


def readable(path):
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    if raw[:3] == b"\xef\xbb\xbf":
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def manifest_rows():
    """Rows actually present in CHECKSUM.sha256, or None if it is unusable."""
    text = readable(MANIFEST)
    if text is None:
        return None
    rows = 0
    for line in text.splitlines():
        if not line.startswith("SHA-256"):
            continue
        if not re.match(r"^SHA-256\s+[0-9a-f]{64}\s+\d+\s+\S.*$", line):
            return None
        rows += 1
    if rows == 0:
        return None
    # The header's own tally must agree with the rows it introduces: a manifest
    # that under-reports its own length is as misleading as a stale prose count.
    tally = re.findall(r"^TOTAL FILES : (\d+)$", text, re.M)
    if len(tally) != 1 or int(tally[0]) != rows:
        return None
    return rows


def anchor_window(lines, i):
    """True when the claim's own line or an immediate neighbour is dated.

    A fenced code block is quoted evidence rather than prose: its date belongs
    to the sentence that introduced the block, so the search also reaches the
    opening fence and the line above it."""
    idx = {i - 1, i, i + 1}
    for j in range(i, max(-1, i - 8), -1):
        if lines[j].lstrip().startswith("```"):
            idx |= set(range(max(0, j - 3), j + 2))
            break
    for j in sorted(idx):
        if 0 <= j < len(lines):
            for pat in ANCHORS:
                if pat.search(lines[j]):
                    return True
    return False


def tally_object(lines, i):
    """Which rig a `passed=` / `of N` tally belongs to.

    The claim's own line is read first and the window is only a fallback.  The
    old order was the other way round, and it produced a wrong answer that
    looked right: on `suite_check.py --with-harness` the word "harness" sits
    three lines away in a neighbouring table row, so a fifteen-entry runner
    enumeration was classified as a harness count and then "fixed" with a date
    instead of being compared with the live harness count.  A tally that names
    its own runner is not ambiguous, so it is not handed to the window.

    Returns one of:
      "runner entry count"  -- the `--with-harness` enumeration, gates + 1
      "harness count"       -- the harness rig
      "gate count"          -- the suite
      "runner tally"        -- the line names no rig; either live count passes
    """
    line = lines[i].lower()
    if "with-harness" in line or "with_harness" in line:
        return "runner entry count"
    if re.search(r"harness_check|harness rig|harness suite|harnesses[/\\]",
                 line):
        return "harness count"
    if re.search(r"suite_check|suite rig|the suite\b", line):
        return "gate count"
    win = "\n".join(lines[max(0, i - 3):i + 4]).lower()
    if "with-harness" in win or "with_harness" in win:
        return "runner entry count"
    if "harness" in win:
        return "harness count"
    if "suite" in win:
        return "gate count"
    return "runner tally"


def vocabulary_problem():
    """A one-line guard on the generated word lists.

    The first draft of the generator emitted "twenty-ten" and "thirty-eleven",
    so CARDINALS held 180 entries and spelled(81) came out as "fifty-one":
    the gate then reported live values that were not the live values, and did
    so with a green "ok".  A vocabulary that is wrong has to stop the gate,
    not skew it.
    """
    if len(CARDINALS) != 20 + 8 * 10:
        return "CARDINALS holds %d entries, expected %d" % (len(CARDINALS), 100)
    if len(ORDINALS) != 20 + 8 * 10:
        return "ORDINALS holds %d entries, expected %d" % (len(ORDINALS), 100)
    if CARDINALS[:20] != _CARD_ONES:
        return "CARDINALS does not begin with the zero..nineteen table"
    if ORDINALS[:20] != _ORD_ONES:
        return "ORDINALS does not begin with the zeroth..nineteenth table"
    for i, w in enumerate(CARDINALS):
        if WORDNUM.get(w) != i:
            return "WORDNUM does not invert CARDINALS at index %d (%r)" % (i, w)
        if re.search(r"[A-Za-z]-[A-Za-z]+-(ten|eleven|twelve|thirteen|"
                     r"fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)",
                     w):
            return "CARDINALS contains the non-word %r" % w
    if ordinal(14) != "fourteenth" or spelled(14) != "fourteen":
        return "ordinal/spelled disagree at 14 (%r / %r)" % (ordinal(14), spelled(14))
    return None


def live_values():
    """Establish every current-state number.  Any failure here is exit 2."""
    bad = vocabulary_problem()
    if bad:
        return None, "report_claim_check vocabulary is corrupted: %s" % bad
    gates = len(suite_check.GATES)
    harnesses = len(harness_check.HARNESSES)
    rows = manifest_rows()
    brain = readable(BRAIN)
    if rows is None:
        return None, "CHECKSUM.sha256 is missing, empty or malformed"
    if brain is None:
        return None, "Brain.MD is unreadable"
    versions = re.findall(r"Brain\.MD v(\d+\.\d+)", brain)
    if not versions:
        return None, "Brain.MD declares no version string at all"
    try:
        scanned = checksum_check.scan()
    except SystemExit as exc:
        return None, "checksum scope unavailable: %s" % exc
    return {"gates": gates, "harnesses": harnesses, "rows": rows,
            "brain": "v" + versions[-1], "versions": len(versions),
            "scope": len(scanned)}, None


# ---------------------------------------------------------------- P1..P4 ----
def canonical_checks(L):
    """Current-state sentences.  These carry no date and may not have one: if
    the constitution says thirteen, the rig has to have thirteen."""
    groups = [
        ("Skill.md runs the N root gates", "SKILL_GATES",
         SKILL, r"runs the (\d+) root gates", L["gates"]),
        ("Skill.md runs the N proof harnesses", "SKILL_HARNESS",
         SKILL, r"runs the (\d+) proof harnesses", L["harnesses"]),
        ("Brain.MD runs all N sequentially", "BRAIN_HARNESS",
         BRAIN, r"runs all (\d+) sequentially", L["harnesses"]),
        ("Brain.MD suite rig gate count", "BRAIN_GATES",
         BRAIN, r"The rig F5-5 built: (\d+) gates", L["gates"]),
        ("Brain.MD harness folder count", "BRAIN_FOLDER",
         BRAIN, r"The (\d+) proof harnesses, checked into", L["harnesses"]),
        ("Brain.MD manifest row count", "BRAIN_ROWS",
         BRAIN, r"\*\*(\d+) files\*\*", L["rows"]),
        ("Skill.md --with-harness entry ordinal", "SKILL_ENTRY",
         SKILL, r"as a (\w+) entry", ordinal(L["gates"] + 1)),
        ("Brain.MD --with-harness entry ordinal", "BRAIN_ENTRY",
         BRAIN, r"as a (\w+) entry", ordinal(L["gates"] + 1)),
        ("Brain.MD last-gate ordinal", "BRAIN_LAST",
         BRAIN, r"(\w+) and last (?:suite )?gate", ordinal(L["gates"])),
    ]
    for label, key, path, pattern, expected in groups:
        text = readable(path)
        if text is None:
            fail("%s: %s unreadable" % (key, os.path.basename(path)))
            continue
        found = re.findall(pattern, text)
        if not found:
            fail("%s: no sentence of the form /%s/ -- the constitution no "
                 "longer states this number at all" % (key, pattern))
            continue
        bad = [f for f in found if f != str(expected)]
        if bad:
            fail("%s: %s says %s, live value is %s"
                 % (key, os.path.basename(path), " / ".join(sorted(set(bad))), expected))
        else:
            ok("%s -- %s" % (label, expected))


def brain_version_check(L):
    if L["versions"] == 1:
        ok("P4 Brain.MD declares exactly one version, %s" % L["brain"])
    else:
        fail("P4 Brain.MD declares %d version strings (%s is the last one); a "
             "reader has no way to know which is current"
             % (L["versions"], L["brain"]))


# -------------------------------------------------------------------- P3 ----
def scope_check(L):
    if L["scope"] == L["rows"]:
        ok("P3 CHECKSUM.sha256 lists %d rows and exactly %d files are in scope"
           % (L["rows"], L["scope"]))
    else:
        fail("P3 manifest lists %d rows but %d files are in scope -- run "
             "checksum_check.py --update after a legitimate edit" % (L["rows"], L["scope"]))


# -------------------------------------------------------------------- P5 ----
# A number is only a claim about *this* rig when it is not glued to a letter:
# "F4 gates" is a phase label, not four gates.  `=` is excluded for the same
# reason and closes a real hole: the header "suite=14 harnesses=21" was read
# as "fourteen harnesses" because the digit sat against an equals sign, so the
# live harness count was never compared with anything the line actually said.
# The keyed form is checked for its own right, in KEYED below.
BARE_NUM = r"(?<![A-Za-z0-9_=])(\d+)"
# Only a *positional* ordinal counts.  "the twelfth gate" and "as a fourteenth
# entry" say where something sits in a list; "a second harness" is prose about
# running one more thing, and "F4 gates" is a phase label.
ORD_HEAD = r"(?:(?<=\bthe )|(?<=\bas a )|(?<=\bas the )|(?<=\bas an ))"
# Built from ORDINALS itself, so the two lists cannot drift apart.  They used
# to: ordinal(22) spelled "twenty-second" while this alternation stopped at
# "twentieth", so a corpus that ever held twenty-two gates would have been
# read as saying nothing at all.
ORD_WORDS = "|".join(re.escape(w) for w in ORDINALS[1:])
# Same hyphen guard as SPOKEN: "second" is not what "twenty-second" says.
ORD_WORDS = r"(?<![A-Za-z-])(?:" + ORD_WORDS + r")(?![A-Za-z-])"
ORD_GATE = re.compile(ORD_HEAD + r"\b(" + ORD_WORDS + r")\b"
                      r"(?:\s+and\s+last)?(?:\s+suite)?\s+(gate|entry)\b",
                      re.I)
ORD_HARNESS = re.compile(ORD_HEAD + r"\b(" + ORD_WORDS + r")\b\s+harness\b",
                         re.I)
# "a 14-gate suite" and "the 22-harness rig" carry the same claim as their
# bare form and used to be invisible to every pattern here.
COMPOUND_GATE = re.compile(BARE_NUM + r"-gate\b")
COMPOUND_HARNESS = re.compile(BARE_NUM + r"-harness\b")
# The header a report is allowed to quote from a gate run.  Each key is
# compared with its own live value; none of these was read before, so a
# report could quote "suite=14 harnesses=21 manifest=81 brain=v1.14" and be
# silently wrong about three of the four.
KEYED = [
    ("gate count",       re.compile(r"\bsuite=(\d+)\b")),
    ("gate count",       re.compile(r"\bgates=(\d+)\b")),
    ("harness count",    re.compile(r"\bharnesses=(\d+)\b")),
    ("manifest rows",    re.compile(r"\bmanifest=(\d+)\b")),
    ("Brain.MD version", re.compile(r"\bbrain=(v\d+\.\d+)\b")),
]
OF_GATES = re.compile(r"\b(\d+)\s+of\s+(?:all\s+|the\s+)?(\d+)\s+(?:root\s+)?gates\b",
                      re.I)
OF_HARNESSES = re.compile(r"\b(\d+)\s+of\s+(?:all\s+|the\s+)?(\d+)\s+(?:proof\s+)?harnesses\b",
                          re.I)


def dated_claims(L):
    """Every numeric claim about a rig or the manifest, compared with the live
    value.  Divergence is permitted only as history, and history is only
    history when the sentence says when it was true."""
    live_gates = str(L["gates"])
    live_harnesses = str(L["harnesses"])
    live_entries = str(L["gates"] + 1)
    expected = {
        "gate count": {live_gates},
        "harness count": {live_harnesses},
        "runner tally": {live_gates, live_harnesses},
        "manifest rows": {str(L["rows"])},
        "Brain.MD version": {L["brain"]},
        "suite gate ordinal": {ordinal(L["gates"])},
        "harness-append ordinal": {ordinal(L["gates"] + 1)},
        "runner entry count": {live_entries},
        "harness ordinal": {ordinal(L["harnesses"])},
    }
    exact = [
        ("gate count",    re.compile(BARE_NUM + r"\s+(?:root\s+)?gates\b")),
        ("harness count", re.compile(BARE_NUM + r"\s+(?:proof\s+)?harnesses\b")),
        ("gate count",    COMPOUND_GATE),
        ("harness count", COMPOUND_HARNESS),
        ("Brain.MD version", re.compile(r"`?Brain\.MD`?\s+(?:at\s+)?(v\d+\.\d+)")),
    ]
    # The same claims spelled out.  "the thirteen gates are a read-only
    # contract" counts the suite exactly as "13 gates" does; a sweep that only
    # reads digits laps over the moment anyone writes a number in words.
    spoken_expected = {
        "gate count": {spelled(L["gates"])},
        "harness count": {spelled(L["harnesses"])},
        "manifest rows": {spelled(L["rows"])},
        "runner entry count": {spelled(L["gates"] + 1)},
    }
    # Only the `--with-harness` enumeration means "entries"; a manifest or a
    # register has entries too, and those are not counts of the suite.
    entries_re = re.compile(BARE_NUM + r"\s+entries\b")
    passed_re = re.compile(r"\bpassed=(\d+)\b")
    # "as of 2026-10-06" is a date, not a tally of 2026 things.
    of_re = re.compile(r"(?<!as )\bof (\d+)(?!\-)")
    suspect = clean = 0
    seen = set()

    def note(label, value, expected_set):
        nonlocal suspect, clean
        if expected_set is None or (name, i, label, value) in seen:
            return
        seen.add((name, i, label, value))
        if value in expected_set:
            clean += 1
            return
        suspect += 1
        want = "/".join(sorted(expected_set))
        if anchor_window(lines, i):
            ok("P5 %s:%d history, not current -- %s=%s, live %s"
               % (name, i + 1, label, value, want))
        else:
            fail("P5 %s:%d %s=%s but the live value is %s and the line "
                 "carries no date, phase tag or 'then' -- a reader "
                 "will take it as current" % (name, i + 1, label, value, want))

    for name in rooted_md():
        text = readable(os.path.join(HERE, name))
        if text is None:
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines):
            # "N rows" is only about the manifest when the line names it; a
            # Markdown table of five rows is not a claim about CHECKSUM.sha256.
            if re.search(r"CHECKSUM|manifest", line, re.I):
                m = re.search(BARE_NUM + r"\s+(?:tracked\s+)?rows\b", line)
                if m:
                    note("manifest rows", m.group(1), expected["manifest rows"])
                m = SPOKEN_ROWS_BARE.search(line)
                if m:
                    note("manifest rows", m.group(1).lower(),
                         spoken_expected["manifest rows"])
            for label, pat in exact:
                for m in pat.finditer(line):
                    note(label, m.group(1), expected.get(label))
            for label, pat in KEYED:
                for m in pat.finditer(line):
                    note(label, m.group(1), expected.get(label))
            # A tally is `passed=N ... of N`; both halves name the same rig.
            if "passed=" in line:
                obj = tally_object(lines, i)
                for m in passed_re.finditer(line):
                    note(obj, m.group(1), expected.get(obj))
                m = of_re.search(line)
                if m:
                    note(obj, m.group(1), expected.get(obj))
            # `--with-harness` enumerates entries; nothing else does.
            if re.search(r"with-harness|enumerat", line):
                for m in entries_re.finditer(line):
                    note("runner entry count", m.group(1),
                         expected["runner entry count"])
                for m in SPOKEN_ENTRIES.finditer(line):
                    note("runner entry count", m.group(1).lower(),
                         spoken_expected["runner entry count"])
            # "fourteen of the fourteen gates": both halves are the claim.
            for m in OF_GATES.finditer(line):
                note("gate count", m.group(1), expected["gate count"])
                note("gate count", m.group(2), expected["gate count"])
            for m in OF_HARNESSES.finditer(line):
                note("harness count", m.group(1), expected["harness count"])
                note("harness count", m.group(2), expected["harness count"])
            for m in ORD_GATE.finditer(line):
                note("harness-append ordinal" if m.group(2) == "entry"
                     else "suite gate ordinal", m.group(1),
                     expected["harness-append ordinal" if m.group(2) == "entry"
                             else "suite gate ordinal"])
            for m in ORD_HARNESS.finditer(line):
                note("harness ordinal", m.group(1),
                     expected["harness ordinal"])

            if re.search(r"CHECKSUM|manifest", line, re.I):
                m = SPOKEN_ROWS.search(line)
                if m:
                    note("manifest rows", m.group(1).lower(),
                         spoken_expected["manifest rows"])
            for m in SPOKEN_GATES.finditer(line):
                note("gate count", m.group(1).lower(),
                     spoken_expected["gate count"])
            for m in SPOKEN_ROOT_GATES.finditer(line):
                note("gate count", m.group(1).lower(),
                     spoken_expected["gate count"])
            for m in SPOKEN_HARNESSES.finditer(line):
                note("harness count", m.group(1).lower(),
                     spoken_expected["harness count"])
            for m in SPOKEN_OF_GATES.finditer(line):
                note("gate count", m.group(1).lower(),
                     spoken_expected["gate count"])
                note("gate count", m.group(2).lower(),
                     spoken_expected["gate count"])
            for m in SPOKEN_OF_HARNESSES.finditer(line):
                note("harness count", m.group(1).lower(),
                     spoken_expected["harness count"])
                note("harness count", m.group(2).lower(),
                     spoken_expected["harness count"])

    if suspect == 0:
        ok("P5 all %d numeric claims across %d documents agree with the live values"
           % (clean, len(rooted_md())))
    else:
        ok("P5 %d claims checked, %d carry history honestly" % (clean + suspect, clean))


# -------------------------------------------------------------------- P6 ----
def reference_check():
    """A report may only cite harnesses that are actually in the folder, and
    every harness in the folder must be reachable from the rig."""
    cited = set()
    for name in rooted_md():
        t = readable(os.path.join(HERE, name))
        if not t:
            continue
        for m in re.finditer(r"harnesses[/\\]([A-Za-z0-9_]+\.py)", t):
            cited.add(m.group(1)[:-3])
        for m in re.finditer(r"`harnesses[/\\]([A-Za-z0-9_]+)`", t):
            cited.add(m.group(1))
    missing = 0
    for c in sorted(cited):
        if not os.path.isfile(os.path.join(HERE, "harnesses", c + ".py")):
            missing += 1
            fail("P6 reports name harnesses\\%s.py which does not exist" % c)
    if missing == 0:
        ok("P6 all %d harnesses named in the reports exist in harnesses\\"
           % len(cited))

    # A row that says "(harnesses/)" makes the same claim as a path that says
    # `harnesses\name.py`, and P6 above only reads the second form.  F4's
    # artefacts table named three survey scripts that exist in no folder and
    # no gate noticed, because the folder lived in its own column.
    ghosts = 0
    for name in rooted_md():
        t = readable(os.path.join(HERE, name))
        if not t:
            continue
        for i, line in enumerate(t.splitlines(), 1):
            if not re.search(r"harnesses[/\\]", line):
                continue
            for m in re.finditer(r"`([A-Za-z0-9_]+\.py)`", line):
                fn = m.group(1)
                if os.path.isfile(os.path.join(HERE, fn)):
                    continue
                if os.path.isfile(os.path.join(HERE, "harnesses", fn)):
                    continue
                ghosts += 1
                fail("P6 %s:%d names %s on a line that claims it lives in "
                     "harnesses\\, and no such file exists" % (name, i, fn))
    if ghosts == 0:
        ok("P6 every .py named on a harnesses/ line resolves to a file")

    on_disk = set()
    hdir = os.path.join(HERE, "harnesses")
    if os.path.isdir(hdir):
        for fn in sorted(os.listdir(hdir)):
            if fn.lower().endswith(".py"):
                on_disk.add(fn[:-3])
    registered = set()
    for entry in harness_check.HARNESSES:
        registered.add(os.path.basename(entry[0])[:-3])
    for extra in sorted(on_disk - registered):
        fail("P6 harnesses\\%s.py exists but is not in harness_check.HARNESSES"
             % extra)
    for gone in sorted(registered - on_disk):
        fail("P6 harness_check.HARNESSES lists %s.py which does not exist" % gone)
    if on_disk == registered:
        ok("P6 harness folder and harness_check.HARNESSES agree on %d files"
           % len(registered))


# -------------------------------------------------------------------- P7 ----
def registration_check():
    bad = 0
    for label, path, _argv, _t in suite_check.GATES:
        if not os.path.isfile(path):
            bad += 1
            fail("P7 suite_check.GATES names %s which is not a file" % label)
    if bad == 0:
        ok("P7 all %d suite gates resolve to a file" % len(suite_check.GATES))


# -------------------------------------------------------------------- P8 ----
def map_check():
    """Brain.MD is the knowledge map of the workspace, so every file at the
    root has to appear in it.  A6 added four files and nothing said so; the
    map is the first thing an agent reads and the last thing anyone audits."""
    text = readable(BRAIN)
    if text is None:
        fail("P8 Brain.MD is unreadable")
        return
    missing = []
    for f in sorted(os.listdir(HERE)):
        if not os.path.isfile(os.path.join(HERE, f)):
            continue
        if "`%s`" % f in text:
            continue
        missing.append(f)
    if missing:
        for f in missing:
            fail("P8 Brain.MD does not name %s, which is a file at the root "
                 "of the workspace it claims to map" % f)
    else:
        ok("P8 Brain.MD names every one of the %d files at the workspace root"
           % len([f for f in os.listdir(HERE)
                  if os.path.isfile(os.path.join(HERE, f))]))


# --------------------------------------------------------- C1 (spelled) ----
def spoken_canonical_checks(L):
    """The constitution has no escape hatch: if it spells a rig total in words,
    the words must equal the live value.  A report may carry dated history; the
    document an agent is told to read at startup may not."""
    expect = {"gates": spelled(L["gates"]), "harnesses": spelled(L["harnesses"])}
    sites = [
        ("SPOKEN_SKILL_GATES",    "Skill.md", SKILL,    SPOKEN_GATES,      "gates"),
        ("SPOKEN_BRAIN_GATES",    "Brain.MD", BRAIN,    SPOKEN_GATES,      "gates"),
        ("SPOKEN_BRAIN_ROOTGATE", "Brain.MD", BRAIN,    SPOKEN_ROOT_GATES, "gates"),
        ("SPOKEN_SKILL_HARNESSES", "Skill.md", SKILL,   SPOKEN_HARNESSES,  "harnesses"),
        ("SPOKEN_BRAIN_HARNESSES", "Brain.MD", BRAIN,   SPOKEN_HARNESSES,  "harnesses"),
    ]
    for key, name, path, pattern, kind in sites:
        text = readable(path)
        if text is None:
            fail("%s: %s unreadable" % (key, name))
            continue
        found = [m.group(1) for m in pattern.finditer(text)]
        bad = [w for w in found if w.lower() != expect[kind]]
        if bad:
            fail("%s: %s spells %r where the live value is %d (%s)"
                 % (key, name, ", ".join(sorted(set(bad))), L[kind], expect[kind]))
        elif found:
            ok("%s -- %s %s" % (key, ", ".join(sorted(set(found))), kind))


def main(argv):
    L, err = live_values()
    if L is None:
        # Same shape as url_liveness_check: a FAIL that names the defect,
        # then a non-zero exit.  A gate that cannot establish its live values
        # has not passed, and the reason must be greppable as FAIL.
        print("FAIL  live values unavailable: %s" % err)
        print("report_claim_check: SKIP")
        return 2
    print("report_claim_check: suite=%d harnesses=%d manifest=%d brain=%s"
          % (L["gates"], L["harnesses"], L["rows"], L["brain"]))
    canonical_checks(L)
    spoken_canonical_checks(L)
    brain_version_check(L)
    scope_check(L)
    dated_claims(L)
    reference_check()
    registration_check()
    map_check()
    if failures:
        print("report_claim_check: FAIL -- %d defective claim(s)" % len(failures))
        return 1
    print("report_claim_check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
