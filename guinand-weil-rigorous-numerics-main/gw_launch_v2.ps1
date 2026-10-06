# Launch the OMEGA-CORE v2 sweep and its watchdog completely detached from
# the calling process tree.
#
# Why this exists: two sweeps died with no forensic trail. The second one lost
# its harness shell record (/api/shell/<id>/output -> 404) and its process tree
# went with it, so the stdout pipe broke and no evidence survived. Running the
# launcher from Windows Task Scheduler puts the python processes in a different
# job object entirely, so harness teardown cannot reach them.
#
# The watchdog is started by this script (not by the agent shell) so that it
# outlives the launcher and can record the target's death time and last
# CPU/memory state.

$ErrorActionPreference = "Stop"

$py   = "C:\Python314\python.exe"
$dir  = "C:\Users\usER\oracle-toe\GUINAND_WEIL"
$log  = Join-Path $dir "omega_core_v2_run.log"
$out  = Join-Path $dir "omega_core_v2_results.json"
$hb   = Join-Path $dir "omega_core_v2_heartbeat.json"
$pidf = Join-Path $dir "omega_v2_pid.txt"
$wdl  = Join-Path $dir "omega_core_v2_watchdog.log"

Set-Location $dir

# A previous heartbeat must not masquerade as a live one.
Remove-Item $hb -ErrorAction SilentlyContinue

# Parameters fixed by the Arsitek on 2026-09-30, after the 03:15 power cut
# destroyed attempt 2 of N=800:
#   --dims 800         N=400 is already VERIFIED POSITIVE DEFINITE and is
#                      preserved in this repository's history: commit
#                      e65319d (blob 30ca1467), omega_core_v2_results.json
#                      sha256 5aaab0cfbf26f7fc5a3306bcd6a6e82e5482dad54a0a08d55ed4ebdcf22aa4f2,
#                      1971 B, identical to certificate section 6.2.
#                      Rerunning it costs ~6 h and proves nothing new.
#   --prec 18000       attempt 1 @9000 was a MEASURED non-result (undetermined
#                      at pivot 1087/1601, evidence kept in omega_core_v2_run
#                      .log and BRAIN).  Starting at 18000 goes straight to the
#                      attempt being locked in and saves ~12 h of exposure.
#   --escalations 0    there is no path to 36000 bits -- explicitly deferred.
#   --ckpt             resumable build / LDL^T stages.  On D: because C: has
#                      only ~11 GB free and the pagefile still needs room to
#                      grow; D: has ~52 GB.
$sweep = Start-Process -FilePath $py `
    -ArgumentList @(
        "gw_omega_core_v2.py",
        "--c", "100",
        "--dims", "800",
        "--prec", "18000",
        "--escalations", "0",
        "--ckpt", "D:\gw_ckpt",
        "--log", $log,
        "--heartbeat", $hb,
        "--out", $out
    ) `
    -WorkingDirectory $dir `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $dir "omega_v2_stdout.txt") `
    -RedirectStandardError  (Join-Path $dir "omega_v2_stderr.txt") `
    -PassThru

$sweep.Id | Out-File -FilePath $pidf -Encoding ascii

Start-Sleep -Seconds 8

if (-not (Get-Process -Id $sweep.Id -ErrorAction SilentlyContinue)) {
    Write-Output "LAUNCH-FAILED: sweep pid $($sweep.Id) already gone"
    Get-Content (Join-Path $dir "omega_v2_stderr.txt") -ErrorAction SilentlyContinue
    exit 1
}

Start-Process -FilePath $py `
    -ArgumentList @(
        "gw_watchdog.py",
        "--pid", "$($sweep.Id)",
        "--heartbeat", $hb,
        "--out", $wdl,
        "--interval", "60"
    ) `
    -WorkingDirectory $dir `
    -WindowStyle Hidden

Write-Output "LAUNCHED sweep_pid=$($sweep.Id) at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
exit 0
