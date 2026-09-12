# The AI Playbook one-command ship: build -> gates -> tests -> deploy dist -> live verify.
# Run from the playbook-site repo: .\deploy.ps1   (add -Preview for a preview deploy)
param([switch]$Preview)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "== Build =="
python build.py; if ($LASTEXITCODE -ne 0) { throw "Build failed." }
Write-Host "== Gates =="
python scripts/gates.py dist; if ($LASTEXITCODE -ne 0) { throw "Gates failed. Fix before deploying." }
python -m pytest -q; if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
Write-Host "== Deploy =="
if ($Preview) { npx vercel deploy dist --yes } else { npx vercel deploy dist --prod --yes }
if ($LASTEXITCODE -ne 0) { throw "Vercel deploy failed (a failed Vercel step usually passes on rerun)." }
if ($Preview) { Write-Host "Preview deployed (protected URL; check it in the Vercel dashboard)."; return }
Write-Host "== Live verification =="
$pages = @("", "1-starter/", "1-starter/1-1-know-me/", "4-frontier-operator/4-2-improve-and-survive/", "radar/", "templates/", "plates/", "start/", "sitemap.xml")
$fail = $false
foreach ($p in $pages) {
  $url = "https://playbook.adamabdalla.com/$p"
  try { $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 20; Write-Host ("{0}  {1}" -f $r.StatusCode, $url); if ($r.StatusCode -ne 200) { $fail = $true } }
  catch { Write-Host ("FAIL  {0}" -f $url); $fail = $true }
}
$cover = (Invoke-WebRequest -Uri "https://playbook.adamabdalla.com/" -UseBasicParsing).Content
if ($cover -notmatch "Four stages") { Write-Host "Homepage does not carry the new cover."; $fail = $true }
if ($fail) { throw "Live verification failed." }
Write-Host "Shipped and verified."
