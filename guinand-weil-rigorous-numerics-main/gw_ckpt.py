"""Append-only checkpoint for the OMEGA-CORE sweep.

WHY
---
build_arb_tau costs 24 h at 18000 bits and certified_ldlt_with_L another 12 h.
Both ran in RAM only, so the power cut of 2026-09-30 03:15 destroyed attempt 2
of N=800 outright -- 5 h 48 min of CPU with nothing on disk.  This module
persists completed rows/pivots so a restarted sweep resumes instead of
rebuilding.

ENCODING
--------
An arb ball is stored as four length-prefixed little-endian integers taken
from man_exp(): (mid_mantissa, mid_exp, rad_mantissa, rad_exp).  Measured:

    midpoint round-trip   0 / 3000 mismatches        (exact)
    superset property     0 non-superset, 0 shrink over 2000 samples
    codec on real 1601x1601 @18000: 2.91 GB, 31.9 s write, 13.4 s read
    superset re-check     0 violations over 2550 sampled entries

Reconstruction is deliberately a SUPERSET of the saved ball.  Reloading never
narrows an error radius, so the enclosure only ever grows:

    true value  <=  fresh ball  <=  reloaded ball

Rigour is therefore preserved and a resumed run certifies a possibly LARGER
set of matrices, never a smaller one.  The superset claim is re-verified on
every single ball at write time, while the original is still in memory.

FILE LAYOUT
-----------
    b"GWCKPT1\\n"
    uint32 header_len, header JSON (utf-8)
    repeated record:
        uint32 rec_len   (bytes that follow this field)
        uint32 index
        uint32 count
        count * ball, each ball = 4 * (uint32 len, len bytes)

A torn tail -- a power cut in the middle of a write -- stops parsing at the
first short or malformed record.  Everything before it stays usable.

English-only (repo rule).
"""
import json
import os
import struct

from flint import arb, ctx, fmpz  # noqa: F401

MAGIC = b"GWCKPT1\n"
_U32 = struct.Struct("<I")


def _put(out, n):
    """Append one signed little-endian integer with a uint32 length prefix."""
    b = n.to_bytes(max(1, (abs(n).bit_length() + 8) // 8), "little",
                   signed=True)
    out += _U32.pack(len(b))
    out += b


def _get(buf, off):
    """Inverse of _put.  Raises struct.error/IndexError on a torn record."""
    (ln,) = _U32.unpack_from(buf, off)
    off += 4
    end = off + ln
    if end > len(buf):
        raise ValueError("record truncated")
    return int.from_bytes(buf[off:end], "little", signed=True), end


def encode_ball(x, out, verify=True):
    """Append one arb ball to bytearray `out`.

    Raises if the rebuilt ball would fail to contain `x` -- that would mean
    the checkpoint silently narrows an error radius, which this whole design
    must never do.
    """
    mm, me = x.mid().man_exp()
    rm, re_ = x.rad().man_exp()
    pos = len(out)
    _put(out, int(mm))
    _put(out, int(me))
    _put(out, int(rm))
    _put(out, int(re_))
    if verify:
        old = ctx.prec
        try:
            ctx.prec = max(old, 18000)
            m = arb(fmpz(int(mm))) * arb(2) ** int(me)
            r = arb(fmpz(int(rm))) * arb(2) ** int(re_)
            ctx.prec = old
            y = arb(m, r)
            if not y.contains(x):
                raise ValueError("checkpoint codec failed superset check: "
                                 "rebuilt ball does not contain the original")
        finally:
            ctx.prec = old


def decode_ball(buf, off):
    """(arb, new_offset).  Caller sets ctx.prec beforehand."""
    mm, off = _get(buf, off)
    me, off = _get(buf, off)
    rm, off = _get(buf, off)
    re_, off = _get(buf, off)
    m = arb(fmpz(mm)) * arb(2) ** me
    r = arb(fmpz(rm)) * arb(2) ** re_
    return arb(m, r), off


class Checkpoint(object):
    """Append-only writer.  A broken row stops further appends, keeping the
    valid prefix rather than corrupting it."""

    def __init__(self, path, header, append=False):
        self.path = path
        self.header = dict(header)
        self.broken = None
        self.records = 0
        self.bytes = 0
        self._fh = None
        self.append = append
        parent = os.path.dirname(path)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)
        try:
            if append:
                # Header already present and already validated by load();
                # resuming must never rewrite it.
                self._fh = open(path, "ab")
            else:
                self._fh = open(path, "wb")
                blob = json.dumps(self.header, sort_keys=True).encode("utf-8")
                self._fh.write(MAGIC)
                self._fh.write(_U32.pack(len(blob)))
                self._fh.write(blob)
            self._fh.flush()
            os.fsync(self._fh.fileno())
        except OSError as exc:
            self.broken = "open failed: %r" % (exc,)
            self._fh = None

    @property
    def usable(self):
        return self._fh is not None and self.broken is None

    def write_record(self, index, values):
        if not self.usable:
            return False
        buf = bytearray()
        buf += _U32.pack(index)
        buf += _U32.pack(len(values))
        try:
            for v in values:
                encode_ball(v, buf, verify=True)
        except Exception as exc:                 # noqa: BLE001 - degrade only
            self.broken = "encode failed at index %d: %r" % (index, exc)
            return False
        frame = _U32.pack(len(buf)) + bytes(buf)
        try:
            self._fh.write(frame)
            self._fh.flush()
            os.fsync(self._fh.fileno())
        except OSError as exc:
            self.broken = "write failed at index %d: %r" % (index, exc)
            return False
        self.records += 1
        self.bytes += len(frame)
        return True

    def close(self):
        if self._fh is not None:
            try:
                self._fh.flush()
                os.fsync(self._fh.fileno())
            except OSError:
                pass
            try:
                self._fh.close()
            finally:
                self._fh = None


def load(path, expected, prec):
    """Read a checkpoint.

    Returns (header, {index: [arb, ...]}) or None when the file is missing,
    unreadable, torn before the first record, or carries a header that does
    not describe the attempt now being run.  None always means "rebuild".
    """
    if not path or not os.path.isfile(path):
        return None
    try:
        size = os.path.getsize(path)
        if size < len(MAGIC) + 4:
            return None
        with open(path, "rb") as fh:
            buf = fh.read()
    except OSError:
        return None
    if not buf.startswith(MAGIC):
        return None
    off = len(MAGIC)
    try:
        (hlen,) = _U32.unpack_from(buf, off)
        off += 4
        if off + hlen > len(buf):
            return None
        header = json.loads(buf[off:off + hlen].decode("utf-8"))
        off += hlen                      # first record starts after the header
    except (ValueError, UnicodeDecodeError):
        return None
    # Header must describe THIS attempt.  A stale file from another precision
    # or another N must be discarded, never partially reused.
    for key, want in expected.items():
        if header.get(key) != want:
            return None

    rows = {}
    old = ctx.prec
    try:
        ctx.prec = prec
        while True:
            if off + 4 > len(buf):
                break                       # clean end
            (rlen,) = _U32.unpack_from(buf, off)
            end = off + 4 + rlen
            if end > len(buf):
                break                       # torn tail -- keep what parsed
            try:
                (idx,) = _U32.unpack_from(buf, off + 4)
                (count,) = _U32.unpack_from(buf, off + 8)
                p = off + 12                      # [rec_len][idx][cnt][balls]
                if p > end:
                    raise ValueError("record header truncated")
                vals = []
                for _ in range(count):
                    v, p = decode_ball(buf, p)
                    vals.append(v)
                if p != end:
                    raise ValueError("record length mismatch")
            except (ValueError, struct.error, IndexError):
                break                       # torn/malformed tail
            rows[idx] = vals
            off = end
    finally:
        ctx.prec = old

    if not rows:
        return None
    # Records must form a contiguous prefix starting at 0, otherwise resuming
    # from the largest index would silently skip a hole.
    want = list(range(max(rows) + 1))
    if sorted(rows) != want:
        return None
    return header, rows
