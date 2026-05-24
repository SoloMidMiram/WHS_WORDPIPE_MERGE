<#
.SYNOPSIS
    Chronicle pipeline: ingest -> verify -> merge -> categorize

.DESCRIPTION
    One-command wrapper for the chronicle pipeline. Runs all stages in sequence
    with error handling and logging.

.PARAMETER InputDir
    Directory containing raw .md files (required).

.PARAMETER OutputDir
    Directory for output files (required; created if missing).

.PARAMETER Config
    Theme config file for categorize.py (JSON or YAML). Optional.

.PARAMETER Verify
    Switch: run verify_ingest.py before merging.

.PARAMETER SkipCategorize
    Switch: stop after merge (skip categorisation).

.PARAMETER Verbose
    Switch: enable debug logging in all stages.

.EXAMPLE
    .\chain.ps1 -InputDir raw/ -OutputDir output/

.EXAMPLE
    .\chain.ps1 -InputDir raw/ -OutputDir output/ -Verify -Config themes.yaml

.EXAMPLE
    .\chain.ps1 -InputDir raw/ -OutputDir output/ -SkipCategorize

.NOTES
    Exit codes:
      0 - All stages completed successfully
      1 - Ingestion stage failed
      2 - Verification stage failed (only with -Verify)
      3 - Merge stage failed
      4 - Categorisation stage failed
#>

param(
    [string]$InputDir,
    [string]$OutputDir,
    [string]$Config,
    [switch]$Verify,
    [switch]$SkipCategorize,
    [switch]$Verbose
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path "$ScriptDir/../.."
$IngestPy = "$ScriptDir/ingest.py"
$VerifyPy = "$ScriptDir/verify_ingest.py"
$MergePy = "$ScriptDir/merge.py"
$CategorizePy = "$ScriptDir/categorize.py"

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
function Show-Help {
    @"
chain.ps1 - Chronicle pipeline: ingest -> verify -> merge -> categorize

Usage:
  .\chain.ps1 -InputDir <dir> -OutputDir <dir> [options]

Required:
  -InputDir <dir>   Directory containing raw .md files
  -OutputDir <dir>  Directory for output files (created if missing)

Options:
  -Config <file>    Theme config for categorize.py (JSON or YAML)
  -Verify           Run verify_ingest.py before merging
  -SkipCategorize   Stop after merge (skip categorisation)
  -Verbose          Enable debug logging in all stages

Exit codes:
  0  All stages completed successfully
  1  Ingestion failed
  2  Verification failed (only with -Verify)
  3  Merge failed
  4  Categorisation failed

Examples:
  .\chain.ps1 -InputDir raw/ -OutputDir output/
  .\chain.ps1 -InputDir raw/ -OutputDir output/ -Verify -Config themes.yaml
  .\chain.ps1 -InputDir raw/ -OutputDir output/ -SkipCategorize
"@
    exit 0
}

if (-not $InputDir -and -not $OutputDir) {
    Show-Help
}

# ---------------------------------------------------------------------------
# Validate input directory
# ---------------------------------------------------------------------------
if (-not (Test-Path $InputDir -PathType Container)) {
    Write-Error "Input directory does not exist: $InputDir"
    exit 1
}
$InputDirAbs = (Resolve-Path $InputDir).Path

# Create output directory
$OutputDirAbs = if (Test-Path $OutputDir -PathType Container) {
    (Resolve-Path $OutputDir).Path
} else {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    (Resolve-Path $OutputDir).Path
}

# ---------------------------------------------------------------------------
# Validate tool scripts
# ---------------------------------------------------------------------------
foreach ($script in @($IngestPy, $MergePy, $CategorizePy)) {
    if (-not (Test-Path $script)) {
        Write-Error "Required script not found: $script"
        exit 1
    }
}
if ($Verify -and -not (Test-Path $VerifyPy)) {
    Write-Error "-Verify requested but verify_ingest.py not found: $VerifyPy"
    exit 1
}

# ---------------------------------------------------------------------------
# Stage helpers
# ---------------------------------------------------------------------------
function Write-StageHeader {
    param([int]$Number, [string]$Name)
    Write-Host ""
    Write-Host ("=" * 72) -ForegroundColor Cyan
    Write-Host "  Stage $Number : $Name" -ForegroundColor Cyan
    Write-Host ("=" * 72) -ForegroundColor Cyan
}

function Write-StageOk {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-StageFail {
    param([string]$Message)
    Write-Host "  [FAIL] $Message" -ForegroundColor Red
}

# ---------------------------------------------------------------------------
# Stage 1: Ingestion
# ---------------------------------------------------------------------------
Write-StageHeader 1 "Ingestion - $IngestPy"

$NormalisedDir = "$OutputDirAbs/normalised"
New-Item -ItemType Directory -Path $NormalisedDir -Force | Out-Null

$RawFiles = Get-ChildItem -Path "$InputDirAbs\*.md" -File
if ($RawFiles.Count -eq 0) {
    Write-Error "No .md files found in $InputDirAbs"
    exit 1
}

$IngestCount = 0
$IngestFailures = 0
$IngestFiles = @()

foreach ($rawFile in $RawFiles) {
    $filename = $rawFile.Name
    $outFile = "$NormalisedDir/$filename"
    Write-Host "  Processing: $filename"

    $verboseFlag = if ($Verbose) { "--verbose" } else { "" }

    $ingestArgs = @("--input", $rawFile.FullName, "--output", $outFile)
    if ($Verbose) { $ingestArgs += "--verbose" }
    $result = & python.exe $IngestPy $ingestArgs 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        $IngestCount++
        $IngestFiles += $outFile
        Write-StageOk $filename
    } else {
        $IngestFailures++
        Write-StageFail "$filename (exit code $exitCode)"
        if ($Verbose) {
            Write-Host "  stderr: $result" -ForegroundColor DarkGray
        }
    }
}

Write-Host ""
Write-Host "  Ingestion complete: $IngestCount succeeded, $IngestFailures failed"

if ($IngestCount -eq 0) {
    Write-Error "No files were successfully ingested. Aborting."
    exit 1
}

# ---------------------------------------------------------------------------
# Stage 2: Verification (optional)
# ---------------------------------------------------------------------------
if ($Verify) {
    Write-StageHeader 2 "Verification - $VerifyPy"

    $verboseFlag = if ($Verbose) { "--verbose" } else { "" }
    $verifyArgs = @("--dir", $InputDirAbs, "--ingest", $IngestPy)
    if ($Verbose) { $verifyArgs += "--verbose" }
    $result = & python.exe $VerifyPy $verifyArgs 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-StageOk "All files verified successfully"
    } else {
        Write-StageFail "Verification failed (exit code $exitCode)"
        if ($Verbose) {
            Write-Host "  Output: $result" -ForegroundColor DarkGray
        }
        Write-Error "Verification failed. Aborting."
        exit 2
    }
}

# ---------------------------------------------------------------------------
# Stage 3: Merge
# ---------------------------------------------------------------------------
Write-StageHeader 3 "Merge - $MergePy"

$MergedFile = "$OutputDirAbs/merged.md"
$verboseFlag = if ($Verbose) { "--verbose" } else { "" }

$mergeArgs = @("--input-dir", $NormalisedDir, "--output", $MergedFile, "--conflict-mode", "keep-both")
if ($Verbose) { $mergeArgs += "--verbose" }
$result = & python.exe $MergePy $mergeArgs 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-StageOk "Merged chronicle written to $MergedFile"
} else {
    Write-StageFail "Merge failed (exit code $exitCode)"
    if ($Verbose) {
        Write-Host "  Output: $result" -ForegroundColor DarkGray
    }
    Write-Error "Merge failed. Aborting."
    exit 3
}

# ---------------------------------------------------------------------------
# Stage 4: Categorisation (optional)
# ---------------------------------------------------------------------------
if ($SkipCategorize) {
    Write-Host ""
    Write-Host ("=" * 72) -ForegroundColor Cyan
    Write-Host "  Stage 4: Categorisation - SKIPPED (-SkipCategorize)" -ForegroundColor Yellow
    Write-Host ("=" * 72) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Pipeline complete. Output:" -ForegroundColor Green
    Write-Host "  Normalised files: $NormalisedDir/"
    Write-Host "  Merged chronicle: $MergedFile"
    exit 0
}

Write-StageHeader 4 "Categorisation - $CategorizePy"

$TaggedFile = "$OutputDirAbs/chronicle_tagged.md"
$configArgs = ""
if ($Config) {
    if (-not (Test-Path $Config)) {
        Write-Error "Config file not found: $Config"
        exit 4
    }
    $configArgs = "--config $Config"
}
$verboseFlag = if ($Verbose) { "--verbose" } else { "" }

$catArgs = @("--input", $MergedFile, "--output", $TaggedFile, "--sidecar")
if ($Config) { $catArgs += @("--config", $Config) }
if ($Verbose) { $catArgs += "--verbose" }
$result = & python.exe $CategorizePy $catArgs 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-StageOk "Tagged chronicle written to $TaggedFile"
} else {
    Write-StageFail "Categorisation failed (exit code $exitCode)"
    if ($Verbose) {
        Write-Host "  Output: $result" -ForegroundColor DarkGray
    }
    Write-Error "Categorisation failed. Aborting."
    exit 4
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host ("=" * 72) -ForegroundColor Cyan
Write-Host "  Pipeline Complete" -ForegroundColor Green
Write-Host ("=" * 72) -ForegroundColor Cyan
Write-Host ""
Write-Host "  Input directory:  $InputDirAbs"
Write-Host "  Output directory: $OutputDirAbs"
Write-Host ""
Write-Host "  Files ingested:   $IngestCount"
Write-Host "  Merge conflicts:  keep-both (all variants preserved)"
Write-Host ""
Write-Host "  Output files:"
Write-Host "    Normalised:     $NormalisedDir/"
Write-Host "    Merged:         $MergedFile"
Write-Host "    Tagged:         $TaggedFile"
Write-Host "    Sidecar JSON:   $([System.IO.Path]::ChangeExtension($TaggedFile, '.tagged.json'))"
Write-Host "    Duplicates:     $([System.IO.Path]::ChangeExtension($MergedFile, '.duplicates.json'))"
Write-Host ""
exit 0
