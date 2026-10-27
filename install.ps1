# install.ps1 - one-prompt AGI runtime installer (Windows PowerShell 5.1+)
#
#   irm https://github.com/Megasolid/AGI/releases/download/v0.4.3/install.ps1 | iex
#
# It downloads the runtime archive from a *pinned release*, verifies it against the released
# SHA256SUMS before extracting anything, seeds the fresh state, runs the cold boot, and then opens
# the desktop login screen. Nothing is installed as administrator, nothing is written outside
# -Destination, and no personal data is fetched.
#
# Manual, safer form (review the script first, then run it):
#   Invoke-WebRequest https://github.com/Megasolid/AGI/releases/download/v0.4.3/install.ps1 -OutFile install.ps1
#   .\install.ps1 -Version v0.4.3
#
param(
  [string]$Version = "v0.4.3",
  [string]$Destination = "$HOME\AGI",
  [string]$BaseUrl = "",
  [switch]$NoBoot,
  [switch]$NoLaunch,
  [string]$Python = "",
  [switch]$Resume
)
$ErrorActionPreference = "Stop"
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

if (-not $BaseUrl) {
  $BaseUrl = "https://github.com/Megasolid/AGI/releases/download/$Version"
}
$BaseUrl = $BaseUrl.TrimEnd("/")
$zipName = "agi-runtime-$Version.zip"
Write-Host "AGI install: $Version -> $Destination"

# ---- prerequisites ----------------------------------------------------------------
# NOTE: native stderr must never abort the script. Under $ErrorActionPreference="Stop", PS 5.1 turns a
# failing native command's stderr into a terminating NativeCommandError, which is why an earlier version
# died at the cryptography probe on machines that lack the package (the exact case the venv step serves).
function Invoke-Quiet([string]$Exe, [string[]]$Argv) {
  $prev = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    & $Exe @Argv 1>$null 2>$null
    return $LASTEXITCODE
  } catch {
    return 127
  } finally {
    $ErrorActionPreference = $prev
  }
}

function Test-Cryptography([string]$Py) {
  if (-not $Py) { return $false }
  return ((Invoke-Quiet $Py @("-c", "import cryptography")) -eq 0)
}

$candidates = @()
if ($Python) {
  # an explicitly supplied interpreter is authoritative - never silently fall back to another one
  $candidates = @($Python)
} else {
  foreach ($cand in @("python", "python3", "py")) {
    $cmd = Get-Command $cand -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
  }
}
$python = $null
$pythonHasCrypto = $false
foreach ($cand in $candidates) {
  if (-not $cand) { continue }
  $prev = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try { $v = (& $cand --version 2>&1 | Out-String) } catch { $v = "" } finally { $ErrorActionPreference = $prev }
  if ($v -notmatch "Python 3\.(1[1-9]|[2-9][0-9])") { continue }
  if (-not $python) { $python = $cand }
  if (Test-Cryptography $cand) { $python = $cand; $pythonHasCrypto = $true; break }
}
if (-not $python) {
  throw "Python 3.11+ is required and was not found. Install it from https://www.python.org/downloads/ and re-run."
}
Write-Host "python: $python (cryptography: $(if ($pythonHasCrypto) { 'present' } else { 'missing - will use a private venv' }))"

$resuming = $false
if (Test-Path $Destination) {
  $existing = Get-ChildItem -Force $Destination | Select-Object -First 1
  if ($existing) {
    if ($Resume -and (Test-Path (Join-Path $Destination ".agi-runtime-manifest.json"))) {
      $resuming = $true
      Write-Host "resuming an extracted runtime at $Destination (download/extract skipped)"
    } else {
      throw ("Destination '$Destination' already exists and is not empty. Use -Resume to continue an " +
             "interrupted install, or choose another -Destination / remove it.")
    }
  }
}

# ---- download + verify (nothing is extracted before the hash matches) -------------
function Fetch-Url([string]$Url, [string]$OutFile) {
  # 1) Invoke-WebRequest, 2) curl.exe, 3) python urllib. The last two matter on hosts whose
  # schannel/CA configuration breaks IWR (SEC_E_NO_CREDENTIALS / "connection closed"); python can use
  # Git for Windows' CA bundle when the machine's own store is unusable.
  $last = $null
  foreach ($attempt in 1..3) {
    try {
      Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing -TimeoutSec 120
      return
    } catch {
      $last = $_
      Start-Sleep -Seconds (2 * $attempt)
    }
  }
  if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
    & curl.exe -sSL --max-time 180 --retry 2 "$Url" -o "$OutFile" 2>$null
    if ($LASTEXITCODE -eq 0 -and (Test-Path $OutFile) -and (Get-Item $OutFile).Length -gt 0) { return }
  }
  $pyForHttp = $python
  if (Test-Path (Join-Path $env:ProgramFiles "Git\mingw64\etc\ssl\certs\ca-bundle.crt")) {
    $env:SSL_CERT_FILE = Join-Path $env:ProgramFiles "Git\mingw64\etc\ssl\certs\ca-bundle.crt"
  }
  # Never pass Python code through -c from PowerShell 5.1: inner quotes are stripped and the child
  # dies with NameError (D2060, 2026-10-27). Write a verbatim helper script instead.
  $pyHelper = Join-Path ([IO.Path]::GetTempPath()) ("agi-dl-" + [guid]::NewGuid().ToString("N").Substring(0, 8) + ".py")
  $pySource = @'
import ssl
import sys
import urllib.request

ctx = ssl.create_default_context()
with urllib.request.urlopen(sys.argv[1], timeout=180, context=ctx) as r:
    data = r.read()
with open(sys.argv[2], "wb") as fh:
    fh.write(data)
'@
  try {
    Set-Content -Path $pyHelper -Value $pySource -Encoding ASCII -Force
    $rc = Invoke-Quiet $pyForHttp @($pyHelper, $Url, $OutFile)
    if ($rc -eq 0 -and (Test-Path $OutFile) -and (Get-Item $OutFile).Length -gt 0) { return }
  } finally {
    Remove-Item -Force $pyHelper -ErrorAction SilentlyContinue
  }
  throw ("download failed after Invoke-WebRequest, curl and python: $Url ($($last.Exception.Message)). " +
         "If this host has no usable CA bundle, install or repair the Windows certificate store, " +
         "or download the release assets manually and run install.ps1 -BaseUrl <file-uri-or-folder-url>.")
}
if (-not $resuming) {
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("agi-install-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
  $sumsPath = Join-Path $tmp "SHA256SUMS.txt"
  $zipPath = Join-Path $tmp $zipName
  # GitHub serves extensionless asset names inconsistently; the release publishes SHA256SUMS.txt
  try { Fetch-Url "$BaseUrl/SHA256SUMS.txt" $sumsPath }
  catch { Fetch-Url "$BaseUrl/SHA256SUMS" $sumsPath }
  Fetch-Url "$BaseUrl/$zipName" $zipPath
  $line = Select-String -Path $sumsPath -Pattern ([regex]::Escape($zipName)) | Select-Object -First 1
  if (-not $line) { throw "SHA256SUMS does not list $zipName - refusing to install" }
  $expected = ($line.Line -split '\s+')[0].ToLower()
  $actual = (Get-FileHash -Path $zipPath -Algorithm SHA256).Hash.ToLower()
  if ($expected -ne $actual) { throw "checksum mismatch for $zipName (expected $expected, got $actual) - refusing to install" }
  Write-Host "checksum: OK ($actual)"

  Expand-Archive -Path $zipPath -DestinationPath $tmp -Force
  if (Test-Path $Destination) { Remove-Item -Force $Destination }
  New-Item -ItemType Directory -Path $Destination | Out-Null
  Get-ChildItem -Path $tmp -Force | Where-Object { $_.Name -notin @("SHA256SUMS", $zipName) } |
    ForEach-Object { Move-Item -Path $_.FullName -Destination $Destination }
} finally {
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
}

# ---- dependency: cryptography (private venv if missing; never the system python) ---
if (-not (Test-Cryptography $python)) {
  Write-Host "cryptography missing: creating a private venv inside the install (no system change)"
  $venv = Join-Path $Destination ".venv"
  if (-not (Test-Path $venv)) {
    $rc = Invoke-Quiet $python @("-m", "venv", $venv)
    if ($rc -ne 0) {
      throw "could not create a venv (exit $rc). Install Python's venv support, or run: $python -m venv `"$venv`""
    }
  }
  $venvPy = Join-Path $venv "Scripts\python.exe"
  if (-not (Test-Path $venvPy)) { throw "venv python not found at $venvPy" }
  Write-Host "installing cryptography into the venv..."
  $rc = Invoke-Quiet $venvPy @("-m", "pip", "install", "--quiet", "--disable-pip-version-check", "cryptography")
  if ($rc -ne 0) {
    throw ("could not install cryptography (exit $rc). Check the network/proxy, or run: " +
           "`"$venvPy`" -m pip install cryptography")
  }
  $python = $venvPy
  Write-Host "venv python: $python"
}

# ---- seed + cold boot -------------------------------------------------------------
Push-Location $Destination
try {
  if (-not $NoBoot) {
    Write-Host "bootstrapping state..."
    & $python "memory/scripts/bootstrap.py" run | Out-Null
    Write-Host "cold boot..."
    $env:AGI_RAM_ROOT = Join-Path $env:LOCALAPPDATA "AGI\ram"
    & $python "memory/scripts/bios.py"
    if ($LASTEXITCODE -ne 0) { throw "cold boot failed (exit $LASTEXITCODE)" }
  }
} finally { Pop-Location }

# ---- open the login screen --------------------------------------------------------
if (-not $NoLaunch) {
  & $python (Join-Path $Destination "memory/scripts/app.py") launch --login
} else {
  Write-Host ""
  Write-Host "Next:  cd `"$Destination`"; $python memory/scripts/app.py launch --login"
}
Write-Host "AGI installed at $Destination"
