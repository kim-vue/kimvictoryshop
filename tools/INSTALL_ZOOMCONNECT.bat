@echo off
setlocal
set "ZOOMCONNECT_INSTALLER=%~f0"
powershell.exe -NoProfile -Command "try { $text=[IO.File]::ReadAllText($env:ZOOMCONNECT_INSTALLER); $body=($text -split '(?m)^# POWERSHELL\r?$',2)[1]; & ([scriptblock]::Create($body)) } catch { Write-Host $_ -ForegroundColor Red; exit 1 }"
set "INSTALL_RESULT=%ERRORLEVEL%"
echo.
pause
exit /b %INSTALL_RESULT%
# POWERSHELL
$ErrorActionPreference = 'Stop'
$python = $null
$pythonArgs = @()
foreach ($name in @('py', 'python')) {
    $candidate = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $candidate) { continue }
    $prefix = @()
    if ($name -eq 'py') { $prefix = @('-3') }
    & $candidate.Source @prefix -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'
    if ($LASTEXITCODE -eq 0) {
        $python = $candidate.Source
        $pythonArgs = $prefix
        break
    }
}
if (-not $python) {
    throw 'Install Python 3.11 or newer from https://www.python.org/downloads/ and run this file again.'
}
$probe = New-Object System.Net.Sockets.TcpListener([Net.IPAddress]::Loopback, 8765)
try { $probe.Start() } catch { throw 'Port 8765 is already in use. Close the existing server and run this file again.' } finally { $probe.Stop() }
$target = 'C:\project\AiWork\gpt\ZOOMCONNECT5'
$tempDir = Join-Path $env:TEMP ('zoomconnect-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
try {
    Write-Host '[1/4] Downloading from GitHub...'
    $zip = Join-Path $tempDir 'source.zip'
    Invoke-WebRequest -UseBasicParsing -Uri 'https://github.com/kim-vue/kimvictoryshop/archive/refs/heads/master.zip' -OutFile $zip
    Write-Host '[2/4] Extracting...'
    Expand-Archive -LiteralPath $zip -DestinationPath $tempDir
    $source = Get-ChildItem -LiteralPath $tempDir -Directory | Where-Object {
        (Test-Path (Join-Path $_.FullName 'pyproject.toml')) -and
        (Test-Path (Join-Path $_.FullName 'zoomconnect\__main__.py'))
    } | Select-Object -First 1
    if (-not $source) { throw 'The downloaded archive does not contain ZOOMCONNECT.' }
    Write-Host '[3/4] Installing...'
    if (Test-Path -LiteralPath $target) {
        $backup = $target + '-backup-' + [guid]::NewGuid().ToString('N')
        Move-Item -LiteralPath $target -Destination $backup
        Write-Host ('Previous folder saved: ' + $backup)
    }
    New-Item -ItemType Directory -Path (Split-Path $target) -Force | Out-Null
    Copy-Item -LiteralPath $source.FullName -Destination $target -Recurse
} finally {
    Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host '[4/4] Starting server in a separate window...'
$server = Start-Process -FilePath $python -ArgumentList ($pythonArgs + @('-m','zoomconnect','serve','--port','8765')) -WorkingDirectory $target -PassThru
$ready = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    if ($server.HasExited) { throw 'The server stopped. Read the server window for the error.' }
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8765/' -TimeoutSec 5
        if ($response.StatusCode -eq 200 -and $response.Content -match 'ZOOMCONNECT') { $ready = $true; break }
    } catch { }
    Start-Sleep -Milliseconds 500
}
if (-not $ready) { throw 'Server readiness was not confirmed. Check the server window.' }
Start-Process 'http://127.0.0.1:8765/'
Write-Host ('Installed: ' + $target)
Write-Host 'Ready. Keep the SERVER window open while using ZOOMCONNECT.'
