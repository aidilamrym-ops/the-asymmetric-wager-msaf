#!/usr/bin/env python3
"""Negative fixtures for report_claim_check.py (audit B-MW3).

Why this file exists
--------------------
`report_claim_check.py` is a gate that can only ever be run against the
real corpus, where every historical sentence is already dated and every
stale one is already fixed. A sweep like that is unfalsifiable: it exits 0,
and there is no evidence that it *would* have exited 1. Three defects
survived exactly that way -- `now` and `->` counted as history anchors,
bare phase tags dating every number on their line, and a case-sensitive
`at F\d` that called a properly dated sentence undated.

Each fixture below builds a one-file corpus in a temp directory, runs the
real `dated_claims` against it, and asserts the verdict. A fixture whose
gate returns the wrong answer fails here, before it can pass silently on
the corpus.

Reading it as a contract: a fixture named `defect_*` asserts the gate
FLAGS the line; a fixture named `ok_*` asserts the gate ACCEPTS it.
Both directions are required -- a gate that flags everything would pass
the first family and be useless.

Not registered as an 18th suite gate on purpose: adding one would change
the live gate count that 40+ report sentences quote, which is churn this
audit has no budget for. CI runs it directly.
"""

import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import report_claim_check as rcc  # noqa: E402  (needs HERE on sys.path)

# Live values the fixtures are checked against. Deliberately NOT read from
# the corpus: a fixture that followed the live rig would stop being a
# fixture the moment the rig moved.
LIVE = {"gates": 16, "harnesses": 28, "rows": 105, "brain": "v1.26"}


class Fixture(unittest.TestCase):
    """Runs the real P5 sweep over a synthetic corpus."""

    def sweep(self, text, filename="FIXTURE.md", binary=False):
        """Run the real sweep; return (failures, skips, gate transcript).

        The gate's own `ok`/`fail` output is captured rather than printed:
        19 fixtures x 3 lines each would bury the verdict. It is returned
        instead of discarded, and quoted in the assertion message, so a
        fixture failure shows what the gate actually said."""
        tmp = tempfile.mkdtemp(prefix="p5fix-")
        self.addCleanup(shutil.rmtree, tmp, True)
        if binary:
            with open(os.path.join(tmp, filename), "wb") as fh:
                fh.write(text)
        else:
            with io.open(os.path.join(tmp, filename), "w",
                         encoding="utf-8", newline="\n") as fh:
                fh.write(text)

        orig_here, orig_md = rcc.HERE, rcc.rooted_md
        orig_fails, orig_skips = list(rcc.failures), list(rcc.skips)
        rcc.HERE = tmp
        rcc.rooted_md = lambda: [filename]
        rcc.failures.clear()
        del rcc.skips[:]
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rcc.dated_claims(LIVE)
            return (list(rcc.failures), list(rcc.skips), buf.getvalue())
        finally:
            rcc.HERE, rcc.rooted_md = orig_here, orig_md
            rcc.failures[:] = orig_fails
            rcc.skips[:] = orig_skips

    def flagged(self, text, needle=None):
        fails, _, _ = self.sweep(text)
        if needle is not None:
            fails = [m for m in fails if needle in m]
        return fails

    def assert_flagged(self, text, needle):
        fails, _, said = self.sweep(text)
        fails = [m for m in fails if needle in m]
        self.assertTrue(
            fails,
            "gate accepted a line it must reject: %r\ngate said:\n%s"
            % (text, said))
        return fails[0]

    def assert_accepted(self, text):
        fails, _, said = self.sweep(text)
        self.assertEqual(
            [], fails,
            "gate rejected a properly dated/true line: %r\ngate said:\n%s"
            % (text, said))


class TestDefectsMustBeFlagged(Fixture):
    """A stale number the reader would take as current. Each of these is a
    defect the corpus happened not to contain any more."""

    def test_plain_stale_count(self):
        self.assert_flagged(
            "| `Skill.md` | 21 proof harnesses |\n",
            "harness count")

    def test_now_does_not_date(self):
        # Regression: `now` was in ANCHORS. "now 21 proof harnesses" reads
        # as currency, so it must never launder a stale number.
        self.assert_flagged(
            "The rig now runs 21 proof harnesses.\n",
            "harness count")

    def test_arrow_does_not_date(self):
        # Regression: `->` and the unicode arrow were in ANCHORS. An arrow
        # is a change marker; it dates nothing.
        self.assert_flagged(
            "The rig runs 21 proof harnesses -> more later\n",
            "harness count")

    def test_bare_phase_tag_does_not_date(self):
        # Regression: `\\bF\\d\\b` and `\\bA\\d\\b` were anchors, so ANY line
        # mentioning a phase dated every number on it. Here the phase
        # belongs to a different clause of the sentence.
        self.assert_flagged(
            "F8-R1 and F8-R2 are closed; the rig runs 21 proof harnesses.\n",
            "harness count")

    def test_stale_gate_count(self):
        self.assert_flagged("The rig has 14 gates.\n", "gate count")

    def test_stale_manifest_rows(self):
        self.assert_flagged(
            "CHECKSUM.sha256 lists 81 rows.\n", "manifest rows")

    def test_stale_ordinal(self):
        # "the fourteenth gate" vs the live sixteenth, spelled in words.
        self.assert_flagged(
            "Only the fourteenth gate is optional.\n", "ordinal")

    def test_stale_compound_form(self):
        self.assert_flagged(
            "Reproduce with the 22-harness rig.\n", "harness count")


class TestDatedLinesMustBeAccepted(Fixture):
    """Historical sentences are not defects. A gate that flagged these would
    push the corpus into deleting its own history."""

    def test_explicit_date(self):
        self.assert_accepted(
            "As of 2026-10-06 the rig ran 21 proof harnesses.\n")

    def test_explicit_phase(self):
        self.assert_accepted(
            "At A5 the rig ran 21 proof harnesses.\n")

    def test_explicit_phase_capitalised(self):
        # Regression: TIER1 was case-sensitive, so "At F5's start, eleven
        # root gates were runnable" -- a correctly dated sentence -- was
        # reported as an undated claim.
        self.assert_accepted(
            "At F5's start, eleven root gates were runnable individually.\n")

    def test_version_anchor(self):
        self.assert_accepted("At v1.9 the rig ran 21 proof harnesses.\n")

    def test_then(self):
        self.assert_accepted("Then the rig ran 21 proof harnesses.\n")

    def test_era_stamp(self):
        # A bracketed stamp is an explicit declaration by the writer, and
        # is how a table row dates itself.
        self.assert_accepted(
            "| 1 | `Brain.MD` | all six harnesses | 21 | ambiguous (A5) |\n")

    def test_live_value_is_never_flagged(self):
        # Positive control: the fixture's own live values must sail through,
        # so a fixture suite that flags everything cannot pass.
        self.assert_accepted(
            "The rig runs 28 proof harnesses behind 16 gates; "
            "CHECKSUM.sha256 lists 105 rows; `Brain.MD` is v1.26.\n")

    def test_blockquote_is_quoted_evidence(self):
        # A `>` line asserts nothing in the reporter's voice, same as a
        # fenced block.
        self.assert_accepted("> the rig ran 21 proof harnesses\n")


class TestKnownGaps(Fixture):
    """Defects the gate does NOT catch, recorded rather than forgotten.

    Each test here is an expectedFailure: it documents a real blind spot,
    and it starts failing loudly the moment someone closes the gap, which
    is the signal to move it up into the defect family.
    """

    @unittest.expectedFailure
    def test_bare_noun_before_number(self):
        """`harnesses 21` is not read as a claim at all.

        REVERSED_CLAIMS only knows the keyed form `harnesses=21` /
        `harnesses: 21`. A report that writes the noun first and the number
        in bare prose escapes the sweep entirely. Deliberately not widened
        here: a bare `noun <digits>` pattern would also match ordinary
        sentences such as "the 3 gates and 21 harnesses cover", and a false
        positive that cries wolf is worse than a documented gap. Closing it
        needs a narrower pattern plus a corpus dry-run, not one regex."""
        self.assert_flagged("harnesses 21 in total.\n", "harness count")


class TestLoudSkips(Fixture):
    """An unreadable file must be named, not silently dropped."""

    def test_non_utf8_is_skipped_loudly(self):
        fails, skips, _ = self.sweep(b"\xff\xfe\x00binary\x00", binary=True)
        self.assertEqual([], fails)
        self.assertEqual(1, len(skips))
        self.assertIn("FIXTURE.md", skips[0])
        self.assertIn("unreadable", skips[0])

    def test_bom_is_skipped_loudly(self):
        text = b"\xef\xbb\xbf| `Skill.MD` | 21 proof harnesses |\n"
        fails, skips, _ = self.sweep(text, binary=True)
        self.assertEqual([], fails)
        self.assertEqual(1, len(skips))


if __name__ == "__main__":
    print("=" * 78)
    print("REPORT CLAIM CHECK -- negative fixtures (audit B-MW3)")
    print("=" * 78)
    res = unittest.main(argv=[sys.argv[0], "-v"], exit=False).result
    if res.wasSuccessful():
        print("FIXTURES: PASS -- %d fixture(s)" % res.testsRun)
        sys.exit(0)
    print("FIXTURES: FAIL")
    sys.exit(1)
