# Measure whether a HyperFrames render pops a VISIBLE console window.
# Symptom-level probe: poll for chrome-headless-shell / conhost processes that
# own a real window handle while a render runs. Prints a verdict, not a guess.
param(
  [string]$Project = '<a HyperFrames project dir>',
  [string]$Label   = 'baseline'
)
$ErrorActionPreference = 'Continue'
$Out = '%TEMP%/pattern-extract'
$log = Join-Path $Out "probe-$Label.log"
"LABEL $Label" | Set-Content $log
"hyperframes: $(& hyperframes --version 2>&1)" | Add-Content $log
"START $(Get-Date -Format o)" | Add-Content $log

$seen = @{}
$job = Start-Job -ScriptBlock {
  param($p)
  Set-Location $p
  & hyperframes render 2>&1
} -ArgumentList $Project

$deadline = (Get-Date).AddMinutes(6)
while ($job.State -eq 'Running' -and (Get-Date) -lt $deadline) {
  foreach ($p in (Get-Process -ErrorAction SilentlyContinue |
                  Where-Object { $_.ProcessName -in @('chrome-headless-shell','conhost','ffmpeg') })) {
    $key = "$($p.ProcessName)#$($p.Id)"
    if ($seen.ContainsKey($key)) { continue }
    $visible = ($p.MainWindowHandle -ne 0)
    $seen[$key] = $visible
    if ($visible) {
      "VISIBLE_WINDOW $($p.ProcessName) pid=$($p.Id) title='$($p.MainWindowTitle)' $(Get-Date -Format HH:mm:ss.fff)" | Add-Content $log
    } else {
      "hidden        $($p.ProcessName) pid=$($p.Id) $(Get-Date -Format HH:mm:ss.fff)" | Add-Content $log
    }
  }
  Start-Sleep -Milliseconds 150
}

$render = Receive-Job $job -ErrorAction SilentlyContinue
Remove-Job $job -Force -ErrorAction SilentlyContinue
"--- render output tail ---" | Add-Content $log
($render | Select-Object -Last 25) | Out-String | Add-Content $log

$vis = ($seen.GetEnumerator() | Where-Object { $_.Value }).Count
$hid = ($seen.GetEnumerator() | Where-Object { -not $_.Value }).Count
"END $(Get-Date -Format o)" | Add-Content $log
"VERDICT visible=$vis hidden=$hid total=$($seen.Count)" | Add-Content $log
"[$Label] visible_windows=$vis  hidden=$hid  total_procs=$($seen.Count)  log=$log"
