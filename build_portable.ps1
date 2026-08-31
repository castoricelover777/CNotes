$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $ProjectRoot ".venv"
$Dist = Join-Path $ProjectRoot "dist"
$Release = Join-Path $ProjectRoot "releases"

New-Item -ItemType Directory -Force -Path $Dist, $Release | Out-Null

function Find-Python {
    $Candidates = @("python", "py")
    foreach ($Candidate in $Candidates) {
        $Command = Get-Command $Candidate -ErrorAction SilentlyContinue
        if ($Command) {
            return $Command.Source
        }
    }
    throw "Python was not found. Install Python from python.org and enable 'Add python.exe to PATH'."
}

$SystemPython = Find-Python

Write-Host "Checking Tkinter..."
& $SystemPython -c "import tkinter; print('tkinter available')"
if ($LASTEXITCODE -ne 0) { throw "This Python installation does not include Tkinter." }

if (-not (Test-Path (Join-Path $Venv "Scripts\python.exe"))) {
    Write-Host "Creating virtual environment..."
    & $SystemPython -m venv $Venv
    if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
}

$PythonExe = Join-Path $Venv "Scripts\python.exe"

Write-Host "Installing build dependency..."
& $PythonExe -m pip install --disable-pip-version-check --no-warn-script-location -r (Join-Path $ProjectRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

Write-Host "Running self-test..."
$env:CNOTES_TEST = "1"
& $PythonExe (Join-Path $ProjectRoot "src\c_notes.py")
if ($LASTEXITCODE -ne 0) { throw "Self-test failed." }
Remove-Item Env:CNOTES_TEST

Write-Host "Building CNotes.exe..."
& $PythonExe -m PyInstaller --noconfirm --clean --onefile --windowed --name CNotes --distpath $Dist --workpath (Join-Path $ProjectRoot "build\pyinstaller") --specpath (Join-Path $ProjectRoot "build") (Join-Path $ProjectRoot "src\c_notes.py")
if ($LASTEXITCODE -ne 0) { throw "Executable build failed." }

Copy-Item (Join-Path $ProjectRoot "README.md") (Join-Path $Dist "README.md") -Force

$ZipPath = Join-Path $Release "CNotes-Windows.zip"
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
Compress-Archive -LiteralPath (Join-Path $Dist "CNotes.exe"), (Join-Path $Dist "README.md") -DestinationPath $ZipPath -CompressionLevel Optimal

Write-Host ""
Write-Host "Build complete: $ZipPath"
