param(
    [Parameter(Mandatory=$true)]
    [string]$PingUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoDir = "."
)

$ErrorActionPreference = "Stop"
$DockerBuildTimeout = 600

function Write-Log {
    param([string]$Message)
    $time = Get-Date -Format "HH:mm:ss"
    Write-Host "[$time] $Message"
}

function Write-Pass {
    param([string]$Message)
    $time = Get-Date -Format "HH:mm:ss"
    Write-Host -ForegroundColor Green "[$time] PASSED -- $Message"
}

function Write-Fail {
    param([string]$Message)
    $time = Get-Date -Format "HH:mm:ss"
    Write-Host -ForegroundColor Red "[$time] FAILED -- $Message"
}

$PingUrl = $PingUrl.TrimEnd('/')

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  OpenEnv Submission Validator (PS)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "Repo:     $RepoDir"
Write-Log "Ping URL: $PingUrl`n"

# Step 1
Write-Log "Step 1/3: Pinging HF Space ($PingUrl/reset) ..."
try {
    $response = Invoke-WebRequest -Method Post -Uri "$PingUrl/reset" -ContentType "application/json" -Body "{}" -UseBasicParsing -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Pass "HF Space is live and responds to /reset"
    } else {
        Write-Fail "HF Space /reset returned HTTP $($response.StatusCode) (expected 200)"
        exit 1
    }
} catch {
    Write-Fail "HF Space not reachable (connection failed or timed out)`n  Details: $_"
    exit 1
}

# Step 2
Write-Log "`nStep 2/3: Running docker build ..."
if (Get-Command docker -ErrorAction SilentlyContinue) {
    if (Test-Path "$RepoDir/Dockerfile") {
        $context = $RepoDir
    } elseif (Test-Path "$RepoDir/server/Dockerfile") {
        $context = "$RepoDir/server"
    } else {
        Write-Fail "No Dockerfile found in repo root or server/ directory"
        exit 1
    }
    
    Write-Log "  Found Dockerfile in $context"
    try {
        $process = Start-Process docker -ArgumentList "build $context" -NoNewWindow -Wait -PassThru
        if ($process.ExitCode -eq 0) {
            Write-Pass "Docker build succeeded"
        } else {
            Write-Fail "Docker build failed"
            exit 1
        }
    } catch {
        Write-Fail "Failed to execute Docker build"
        exit 1
    }
} else {
    Write-Fail "docker command not found. Please install Docker Desktop."
    exit 1
}

# Step 3
Write-Log "`nStep 3/3: Running openenv validate ..."
if (Get-Command openenv -ErrorAction SilentlyContinue) {
    Push-Location $RepoDir
    try {
        $output = openenv validate . 2>&1
        $exitcode = $LASTEXITCODE
        if ($exitcode -eq 0) {
            Write-Pass "openenv validate passed"
            Write-Log "  $output"
        } else {
            Write-Fail "openenv validate failed"
            Write-Host $output
            exit 1
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Fail "openenv command not found. Please run 'pip install openenv-core'"
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  All 3/3 checks passed!" -ForegroundColor Green
Write-Host "  Your submission is ready to submit." -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
