# Mirror the complete HyperFrames docs site as byte-exact markdown.
# Every URL in sitemap.xml -> <path>.md . No sampling, no ranges.
$ErrorActionPreference = 'Stop'
$Root = '$HF_DOCS'
$Base = 'https://hyperframes.heygen.com'
$Pages = Join-Path $Root 'pages'
New-Item -ItemType Directory -Force -Path $Pages | Out-Null

$log = Join-Path $Root '_mirror.log'
"START $(Get-Date -Format o)" | Set-Content $log

# --- whole-corpus files first ---
foreach ($f in @('llms-full.txt','llms.txt','sitemap.xml')) {
  $r = Invoke-WebRequest -Uri "$Base/$f" -UseBasicParsing
  [IO.File]::WriteAllText((Join-Path $Root $f), $r.Content, [Text.UTF8Encoding]::new($false))
  "CORPUS $f $($r.Content.Length)" | Add-Content $log
}

$sm = [IO.File]::ReadAllText((Join-Path $Root 'sitemap.xml'))
$urls = [regex]::Matches($sm,'<loc>([^<]+)</loc>') | ForEach-Object { $_.Groups[1].Value }
"SITEMAP_COUNT $($urls.Count)" | Add-Content $log

$results = $urls | ForEach-Object -ThrottleLimit 8 -Parallel {
  $u    = $_
  $Base = 'https://hyperframes.heygen.com'
  $Pages = $using:Pages
  $rel  = $u -replace [regex]::Escape("$Base/"), ''
  $dest = Join-Path $Pages ("$rel.md" -replace '/','\')
  New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
  $status = 'OK'; $len = 0
  for ($try = 1; $try -le 3; $try++) {
    try {
      $r = Invoke-WebRequest -Uri "$u.md" -UseBasicParsing -TimeoutSec 60
      $len = $r.Content.Length
      if ($len -eq 0) { throw "empty body" }
      [IO.File]::WriteAllText($dest, $r.Content, [Text.UTF8Encoding]::new($false))
      break
    } catch {
      $status = "FAIL:$($_.Exception.Message)"
      Start-Sleep -Milliseconds (400 * $try)
    }
  }
  [pscustomobject]@{ url = $u; rel = $rel; bytes = $len; status = $status }
}

$results | Export-Csv -NoTypeInformation -Path (Join-Path $Root '_manifest.csv')
$ok   = ($results | Where-Object { $_.status -eq 'OK' -and $_.bytes -gt 0 }).Count
$bad  = $results | Where-Object { $_.status -ne 'OK' -or $_.bytes -le 0 }
"FETCHED_OK $ok / $($urls.Count)" | Add-Content $log
"FAILED $($bad.Count)" | Add-Content $log
$bad | ForEach-Object { "BAD $($_.url) $($_.status)" } | Add-Content $log
$total = ($results | Measure-Object bytes -Sum).Sum
"TOTAL_BYTES $total" | Add-Content $log
"DONE $(Get-Date -Format o)" | Add-Content $log
"FETCHED_OK $ok / $($urls.Count)  FAILED $($bad.Count)  BYTES $total"
