param(
    [string]$EnvDir = "",
    [string]$PythonVersion = "3.10",
    [switch]$DownloadFoundation1,
    [switch]$DownloadT5
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not $EnvDir) {
    $EnvDir = Join-Path $RepoRoot "env"
}

function Resolve-CondaExe {
    $candidates = @(
        (Join-Path $RepoRoot "miniconda3\Scripts\conda.exe"),
        "conda.exe",
        "conda"
    )

    foreach ($candidate in $candidates) {
        if ($candidate -like "*.exe" -and (Test-Path $candidate)) {
            return $candidate
        }

        try {
            $command = Get-Command $candidate -ErrorAction Stop
            if ($command.Source) {
                return $command.Source
            }
        } catch {
        }
    }

    throw "Conda was not found. Install Miniconda and make sure conda.exe is available, or place it at $RepoRoot\miniconda3\Scripts\conda.exe."
}

$CondaExe = Resolve-CondaExe

Write-Host "Using conda:" $CondaExe
Write-Host "Creating environment at:" $EnvDir
& $CondaExe create -p $EnvDir python=$PythonVersion pip -y

Write-Host "Upgrading pip"
& $CondaExe run -p $EnvDir python -m pip install --upgrade pip

Write-Host "Installing CUDA-enabled PyTorch"
& $CondaExe run -p $EnvDir python -m pip install --upgrade --force-reinstall torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu128

Push-Location $RepoRoot
try {
    Write-Host "Installing repository dependencies"
    & $CondaExe run -p $EnvDir python -m pip install --force-reinstall numpy==1.23.5
    & $CondaExe run -p $EnvDir python -m pip install .

    if ($DownloadFoundation1 -or $DownloadT5) {
        $DownloadArgs = @("scripts\download_models.py")
        if (-not $DownloadFoundation1) {
            $DownloadArgs += "--skip-model"
        }
        if ($DownloadT5) {
            $DownloadArgs += "--download-t5"
        }

        Write-Host "Downloading model assets"
        & $CondaExe run -p $EnvDir python @DownloadArgs
    }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "Start the app with: .\\start-foundation1.bat"
