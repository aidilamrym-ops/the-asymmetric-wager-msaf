#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent liveness watchdog for a long-running OMEGA-CORE sweep.

Why this exists: two sweeps died and left no usable forensic trail.

  run 1 (gw_omega_core.py)    killed by a shell timeout I set myself.
  run 2 (gw_omega_core_v2.py) vanished with its harness shell record
                              (/api/shell/<id>/output -> 404). No crash event,
                              no OOM event, no dump -- only silence.

`build_arb_tau` prints nothing for hours, so a silent log cannot distinguish
"healthy and building" from "dead". This watchdog samples the process
independently of the harness and records, once per interval:

  pid alive?, cumulative CPU seconds, working set MB, heartbeat file contents

When the target dies it writes the exact death timestamp plus the last
observed CPU/memory state, which is what was missing both times.

It deliberately does NOT restart or kill the target -- it only observes.

usage:
    python gw_watchdog.py --pid 1234 --heartbeat omega_core_v2_heartbeat.json \
        --out omega_core_v2_watchdog.log [--interval 60]
"""

import argparse
import json
import os
import time

import psutil


def working_set(proc):
    """Working set in bytes, portable across psutil backends.

    psutil 7.2.2 on Windows exposes 'wset', NOT 'wss'. The AttributeError from
    using 'wss' killed all three first watchdogs inside their first loop
    iteration, right after they wrote only a start line -- silently, which is
    the exact failure mode this tool exists to prevent.
    """
    mi = proc.memory_info()
    for name in ("wss", "wset", "rss"):
        val = getattr(mi, name, None)
        if val is not None:
            return val
    return 0


def read_heartbeat(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return {"stage": data.get("stage"),
                "ts": data.get("ts"),
                "age_s": round(time.time()
                               - time.mktime(time.strptime(
                                   data["ts"], "%Y-%m-%d %H:%M:%S")), 1)
                if data.get("ts") else None}
    except Exception as exc:
        return {"error": repr(exc)}


def main():
    ap = argparse.ArgumentParser(description="OMEGA-CORE sweep watchdog")
    ap.add_argument("--pid", type=int, required=True)
    ap.add_argument("--heartbeat", type=str, default=None)
    ap.add_argument("--out", type=str, default="gw_watchdog.log")
    ap.add_argument("--interval", type=int, default=60)
    args = ap.parse_args()

    # Write the log file FIRST and never let stdout kill this process. Under a
    # scheduled task there is often no valid console handle: an unguarded
    # print() raises, and the first launch died before writing a single byte
    # -- exactly the missing-forensics failure this watchdog exists to prevent.
    log = open(args.out, "a", encoding="utf-8")

    def say(msg):
        log.write(msg + "\n")
        log.flush()
        try:
            print(msg, flush=True)
        except Exception:
            pass

    say("[%s] WATCHDOG start pid=%d interval=%ds"
        % (time.strftime("%Y-%m-%d %H:%M:%S"), args.pid, args.interval))

    try:
        proc = psutil.Process(args.pid)
        proc.cpu_percent(None)  # prime the counter
    except psutil.NoSuchProcess:
        say("[%s] TARGET pid=%d ALREADY GONE at watchdog start"
            % (time.strftime("%Y-%m-%d %H:%M:%S"), args.pid))
        log.close()
        return 1

    last_cpu = 0.0
    last_ws = 0.0
    prev_cpu = None
    ticks = 0
    while True:
        time.sleep(args.interval)
        ticks += 1
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            cpu = proc.cpu_times().user + proc.cpu_times().system
            ws = working_set(proc)
        except psutil.NoSuchProcess:
            say("[%s] TARGET pid=%d DIED after ~%ds observed. "
                "last_cpu=%.1fs last_ws=%.1fMB cpu_delta_last_interval=%s" % (
                    now, args.pid, ticks * args.interval, last_cpu,
                    last_ws / 1e6,
                    "%.1fs" % (cpu - prev_cpu) if prev_cpu is not None
                    else "n/a (first interval)"))
            if args.heartbeat:
                say("[%s] last heartbeat: %s"
                    % (now, json.dumps(read_heartbeat(args.heartbeat),
                                       default=str)))
            log.close()
            return 2
        except Exception as exc:
            # A watchdog that dies is worse than no watchdog: it leaves silence
            # that looks identical to a healthy silent build. Log and continue.
            say("[%s] WATCHDOG probe error (continuing): %r" % (now, exc))
            continue

        delta = cpu - last_cpu
        last_cpu, last_ws, prev_cpu = cpu, ws, cpu
        hb = read_heartbeat(args.heartbeat) if args.heartbeat else {}
        # cpu stalled while the heartbeat also stopped => the process is wedged
        # or was frozen; cpu moving with a stale heartbeat is normal (build is
        # a single silent call).
        status = "ACTIVE" if delta > 0.5 else "IDLE/ZERO-CPU"
        say("[%s] pid=%d %s cpu=%.1fs(+%.1fs) ws=%.0fMB hb=%s" % (
            now, args.pid, status, cpu, delta, ws / 1e6,
            json.dumps(hb, default=str)))


if __name__ == "__main__":
    raise SystemExit(main())
