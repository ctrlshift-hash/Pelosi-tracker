# Find Python installation
Write-Host "Searching for Python installations..." -ForegroundColor Yellow

$pythonPaths = @(
    "$env:LOCALAPPDATA\Programs\Python",
    "C:\Python*",
    "C:\Program Files\Python*",
    "C:\Program Files (x86)\Python*",
    "$env:USERPROFILE\AppData\Local\Programs\Python"
)

$found = $false
foreach ($path in $pythonPaths) {
    $dirs = Get-ChildItem $path -ErrorAction SilentlyContinue
    foreach ($dir in $dirs) {
        $pythonExe = Join-Path $dir.FullName "python.exe"
        if (Test-Path $pythonExe) {
            Write-Host "Found Python at: $pythonExe" -ForegroundColor Green
            & $pythonExe --version
            $found = $true
        }
    }
}

if (-not $found) {
    Write-Host "`nPython not found in common locations." -ForegroundColor Red
    Write-Host "Please install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
}







