# The AI Playbook one-command ship: clean tree -> build -> gates -> tests -> deploy dist -> live verify.
# Run from the playbook-site repo: .\deploy.ps1   (add -Preview for a preview deploy)
param([switch]$Preview)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "== Working tree =="
# What ships must be what is committed: a dirty tree means dist was rendered from
# content no one can check out again.
$dirty = git status --porcelain
if ($LASTEXITCODE -ne 0) { throw "git status failed." }
if ($dirty) {
  $dirty | ForEach-Object { Write-Host "  $_" }
  throw "Working tree is dirty. Commit or stash before deploying."
}
Write-Host "clean"
Write-Host "== Reader source =="
# The reader is compiled from the curriculum clone; what shipped must be what the owner merged and pushed.
$cur = Join-Path (Split-Path $PSScriptRoot -Parent) "ai-playbook-curriculum"
if (-not (Test-Path $cur)) { throw "Curriculum clone not found at $cur. Clone OrangeOnyx/ai-playbook-curriculum beside this repo." }
$recorded = (Get-Content -Raw "content/generated/curriculum/read/SOURCE").Trim()
$head = (git -C $cur rev-parse HEAD).Trim()
$remote = ((git -C $cur ls-remote origin master) -split "\s+")[0]
if ($LASTEXITCODE -ne 0) { throw "Could not read the curriculum remote." }
if ($recorded -ne $head) { throw "Reader was built from $recorded but the curriculum clone is at $head. Run: python scripts/build_reader.py and commit." }
if ($recorded -ne $remote) { throw "Reader was built from $recorded but origin/master is $remote. Push the curriculum first." }
Write-Host "reader source $recorded matches the clone and origin/master"
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
Write-Host "== Reader redirect walk =="
$renames = Get-Content -Raw "content/reader-renames.json" | ConvertFrom-Json
$walked = 0
foreach ($prop in $renames.PSObject.Properties) {
  $src = "https://playbook.adamabdalla.com/curriculum/read/$($prop.Name).html"
  $want = "/curriculum/read/$($prop.Value).html"
  # -MaximumRedirection 0 returns the 3xx but also emits a non-terminating error; silence it and judge the response.
  try { $r = Invoke-WebRequest -Uri $src -Method Head -MaximumRedirection 0 -SkipHttpErrorCheck -UseBasicParsing -TimeoutSec 20 -ErrorAction SilentlyContinue }
  catch { Write-Host ("FAIL  no answer  {0}" -f $src); $fail = $true; continue }
  $loc = [string]$r.Headers["Location"]
  if ($r.StatusCode -ne 308 -or -not $loc.EndsWith($want)) { Write-Host ("FAIL  {0}  {1} -> {2}" -f $r.StatusCode, $prop.Name, $loc); $fail = $true }
  $walked++
}
Write-Host ("walked {0} reader redirects" -f $walked)
$cover = (Invoke-WebRequest -Uri "https://playbook.adamabdalla.com/" -UseBasicParsing).Content
if ($cover -notmatch "Four stages") { Write-Host "Homepage does not carry the new cover."; $fail = $true }
if ($fail) { throw "Live verification failed." }
Write-Host "Shipped and verified."
