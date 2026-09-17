<#
  Re-apply the Windows console-window fix to the globally installed hyperframes.

  WHY THIS EXISTS
  @puppeteer/browsers launch.js sets `opts.detached ??= true`. On Windows that
  forces DETACHED_PROCESS, which cancels the `windowsHide: true` four lines
  below it — so every render worker pops a chrome-headless-shell console window
  that steals focus. Measured 2026-08-27 on hyperframes 0.8.16: one feeltest
  render produced 14 visible windows before the patch and 0 after, with an
  identical successful render both times.

  HeyGen believe this is already fixed (v0.8.7, PR #3394). It is not, on Windows.

  `npm i -g hyperframes@latest` reinstalls node_modules and wipes the patch.
  Run this after EVERY hyperframes upgrade.

  USAGE
    pwsh -File $REPO/tools/hyperframes-fix\fix-windows-console.ps1
    pwsh -File ... -Verify     # report only, change nothing
#>
param([switch]$Verify)

$ErrorActionPreference = 'Stop'

$root = & npm root -g 2>$null
if (-not $root) { throw "npm root -g returned nothing — is npm on PATH?" }
$target = Join-Path $root 'hyperframes\node_modules\@puppeteer\browsers\lib\launch.js'

if (-not (Test-Path $target)) {
  Write-Host "NOT FOUND: $target" -ForegroundColor Red
  Write-Host "hyperframes may not be installed globally, or the bundled puppeteer moved." -ForegroundColor Red
  exit 2
}

$ver = (Get-Content (Join-Path $root 'hyperframes\package.json') -Raw |
        ConvertFrom-Json).version
$src = [IO.File]::ReadAllText($target)

$bad   = 'opts.detached ??= true;'
$good  = "opts.detached ??= process.platform !== 'win32';"

$hasBad  = $src.Contains($bad)
$hasGood = $src.Contains($good)

Write-Host "hyperframes : $ver"
Write-Host "launch.js   : $target"

if ($hasGood -and -not $hasBad) {
  Write-Host "STATUS      : PATCHED — renders will not pop console windows." -ForegroundColor Green
  exit 0
}

if (-not $hasBad) {
  Write-Host "STATUS      : UNKNOWN — neither the original nor the patched line is present." -ForegroundColor Yellow
  Write-Host "              Upstream changed this file. Re-measure before trusting it:" -ForegroundColor Yellow
  Write-Host "              probe-render-windows.ps1 in the session scratchpad." -ForegroundColor Yellow
  exit 3
}

Write-Host "STATUS      : UNPATCHED — every render worker will pop a console window." -ForegroundColor Red

if ($Verify) { exit 1 }

$bak = "$target.BAK-pre-detached-fix"
if (-not (Test-Path $bak)) {
  Copy-Item $target $bak
  Write-Host "backup      : $bak"
}

$patched = $src.Replace(
  $bad,
  @"
// LOCAL PATCH (Chris / cougar 2026-08-27): on Windows, detached:true forces
        // DETACHED_PROCESS, which cancels the windowsHide:true below and pops a
        // console window per render worker. Backup: launch.js.BAK-pre-detached-fix
        $good
"@.Trim())

[IO.File]::WriteAllText($target, $patched, [Text.UTF8Encoding]::new($false))

$after = [IO.File]::ReadAllText($target)
if ($after.Contains($good) -and -not $after.Contains($bad)) {
  Write-Host "STATUS      : PATCH APPLIED — verified in the written file." -ForegroundColor Green
  exit 0
}

Write-Host "STATUS      : PATCH FAILED TO VERIFY — restoring backup." -ForegroundColor Red
Copy-Item $bak $target -Force
exit 4
