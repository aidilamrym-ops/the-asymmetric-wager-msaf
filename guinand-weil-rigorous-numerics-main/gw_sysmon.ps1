# System monitor for the OMEGA-CORE sweep.
#
# The existing gw_watchdog.py only watches the sweep process itself (CPU, WS,
# heartbeat).  It says nothing about the machine around it, and this run dies
# for machine reasons, not code reasons: the laptop has a critical 0% battery
# on AC power, so a loose adapter is an instant power-cut with no buffer.
#
# This monitor therefore samples the four threats the process watchdog cannot
# see -- physical RAM, commit charge (the real OOM boundary), free disk, and AC
# presence -- plus sweep liveness, and appends one line per tick.
#
# It only LOGS.  It never kills, never restarts, never changes power settings.
# A monitor that takes action is a second thing that can go wrong during a
# nine-hour run; the evidence trail is the product here.
#
# Alerts are prefixed ALERT so they can be found with a single Select-String.

param(
    [int]$Interval = 60,
    [string]$Out = "C:\Users\usER\oracle-toe\GUINAND_WEIL\omega_v2_sysmon.log",
    [string]$SweepPidFile = "C:\Users\usER\oracle-toe\GUINAND_WEIL\omega_v2_pid.txt",
    [int]$CommitAlertMb = 2048,
    [int]$RamAlertMb = 1024,
    [int]$DiskAlertGb = 2
)

$ErrorActionPreference = "SilentlyContinue"

# ACLineStatus from the Win32 API, not WMI: Win32_Battery.BatteryStatus reported
# DC (2) while the machine was demonstrably plugged in and running for hours.
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class SysMonPower {
    [StructLayout(LayoutKind.Sequential)]
    public struct SPS {
        public byte ACLineStatus;
        public byte BatteryFlag;
        public byte BatteryLifePercent;
        public byte SystemStatusFlag;
        public int BatteryLifeTime;
        public int BatteryFullLifeTime;
    }
    [DllImport("kernel32.dll")]
    public static extern bool GetSystemPowerStatus(ref SPS s);
}
"@

function Sample-System {
    $os   = Get-CimInstance Win32_OperatingSystem
    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    $ps   = New-Object SysMonPower+SPS
    [void][SysMonPower]::GetSystemPowerStatus([ref]$ps)

    $sweepPid = $null
    if (Test-Path $SweepPidFile) {
        $sweepPid = (Get-Content $SweepPidFile -ErrorAction SilentlyContinue |
                     Select-Object -First 1).Trim()
    }
    $sweep = $null
    if ($sweepPid) { $sweep = Get-Process -Id ([int]$sweepPid) -ErrorAction SilentlyContinue }

    # Private bytes, not working set: Windows trims the working set aggressively
    # during a long fill and WS looks like it is falling while committed memory
    # keeps rising.  Private bytes is what the commit charge is made of.
    $privMb = if ($sweep) { [math]::Round($sweep.PrivateMemorySize64 / 1MB, 0) } else { -1 }
    $cpu    = if ($sweep) { [math]::Round($sweep.CPU, 0) } else { -1 }

    return [pscustomobject]@{
        RamFreeMb    = [math]::Round($os.FreePhysicalMemory / 1KB, 0)
        CommitFreeMb = [math]::Round($os.FreeVirtualMemory / 1KB, 0)
        DiskFreeGb   = [math]::Round($disk.FreeSpace / 1GB, 1)
        Ac           = $ps.ACLineStatus
        BattPct      = $ps.BatteryLifePercent
        SweepAlive   = [bool]$sweep
        SweepPid     = $sweepPid
        PrivMb       = $privMb
        CpuS         = $cpu
    }
}

function Get-Stage {
    $hb = "C:\Users\usER\oracle-toe\GUINAND_WEIL\omega_core_v2_heartbeat.json"
    if (-not (Test-Path $hb)) { return "-" }
    $j = Get-Content $hb -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
    if (-not $j) { return "?" }
    return ("{0}/N{1}/p{2}/a{3}" -f $j.stage, $j.N, $j.prec, $j.attempt)
}

function Write-Alert($s, $msg) {
    Add-Content -Path $Out -Encoding UTF8 -Value (
        "[{0}] ALERT {1}  ram={2}MB commit={3}MB disk={4}GB ac={5} priv={6}MB pid={7} stage={8}" -f
        (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg, $s.RamFreeMb, $s.CommitFreeMb,
        $s.DiskFreeGb, $s.Ac, $s.PrivMb, $s.SweepPid, (Get-Stage)
    )
}

Add-Content -Path $Out -Encoding UTF8 -Value ("[{0}] sysmon start interval={1}s commitAlert={2}MB ramAlert={3}MB diskAlert={4}GB" -f
    (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Interval, $CommitAlertMb, $RamAlertMb, $DiskAlertGb)

while ($true) {
    $s = Sample-System
    Add-Content -Path $Out -Encoding UTF8 -Value (
        "[{0}] ram={1}MB commit={2}MB disk={3}GB ac={4} batt={5}% alive={6} pid={7} priv={8}MB cpu={9}s stage={10}" -f
        (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $s.RamFreeMb, $s.CommitFreeMb, $s.DiskFreeGb,
        $s.Ac, $s.BattPct, $s.SweepAlive, $s.SweepPid, $s.PrivMb, $s.CpuS, (Get-Stage)
    )

    if (-not $s.SweepAlive)          { Write-Alert $s "SWEEP-DEAD (proses hilang)" }
    if ($s.Ac -ne 1)                 { Write-Alert $s "AC-LOST (baterai $($s.BattPct)% -- mati mendadak)" }
    if ($s.CommitFreeMb -lt $CommitAlertMb) { Write-Alert $s "COMMIT-LOW (batas OOM)" }
    if ($s.RamFreeMb -lt $RamAlertMb)       { Write-Alert $s "RAM-LOW (akan thrashing)" }
    if ($s.DiskFreeGb -lt $DiskAlertGb)     { Write-Alert $s "DISK-LOW" }

    Start-Sleep -Seconds $Interval
}
