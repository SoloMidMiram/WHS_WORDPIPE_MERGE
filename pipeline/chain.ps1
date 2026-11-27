<#
.SYNOPSIS
    Chronicle pipeline: ingest -> verify -> merge -> categorize -> index

.DESCRIPTION
    One-command wrapper for the chronicle pipeline. Runs all stages in sequence
    with error handling and logging.

.PARAMETER InputDir
    Directory containing raw .md files (required).

.PARAMETER OutputDir
    Directory for output files (required; created if missing).

.PARAMETER ThemesConfig
    Theme config file for categorize.py (JSON or YAML). Optional.

.PARAMETER IndexConfig
    Index config file for index.py (JSON). Optional.

.PARAMETER Verify
    Switch: run verify_ingest.py before merging.

.PARAMETER SkipCategorize
    Switch: stop after merge (skip categorisation and indexing).

.PARAMETER SkipIndex
    Switch: stop after categorise (skip index generation).

.PARAMETER NoLinkRegistry
    Switch: skip link registry generation in index.py.

.PARAMETER SourceCoverage
    Switch: pass source_coverage.md to index.py for manifest generation.

.PARAMETER Verbose
    Switch: enable debug logging in all stages.

.EXAMPLE
    .\chain.ps1 -InputDir raw/ -OutputDir output/

.EXAMPLE
    .\chain.ps1 -InputDir raw/ -OutputDir output/ -Verify -ThemesConfig themes.yaml

.EXAMPLE
    .\chain.ps1 -InputDir raw/ -OutputDir output/ -SkipCategorize

.EXAMPLE
    .\chain.ps1 -InputDir raw/ -OutputDir output/ -IndexConfig index_config.json -NoLinkRegistry

.NOTES
    Exit codes:
      0 - All stages completed successfully
      1 - Ingestion stage failed
      2 - Verification stage failed (only with -Verify)
      3 - Merge stage failed
      4 - Categorisation stage failed
      5 - Index generation failed
#>

param(
    [string]$InputDir,
    [string]$OutputDir,
    [string]$ThemesConfig,
    [string]$IndexConfig,
    [switch]$Verify,
    [switch]$SkipCategorize,
    [switch]$SkipIndex,
    [switch]$NoLinkRegistry,
    [switch]$SourceCoverage,
    [switch]$AllowPartialIngest,
    [switch]$Verbose,
    [double]$StageTimeoutSeconds
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path "$ScriptDir/.."
$IngestPy = "$ScriptDir/ingest.py"
$VerifyPy = "$ScriptDir/verify_ingest.py"
$MergePy = "$ScriptDir/merge.py"
$CategorizePy = "$ScriptDir/categorize.py"
$IndexPy = "$ScriptDir/index.py"
$ExecutePy = "$ScriptDir/execute_stage.py"
$HasStageTimeout = $PSBoundParameters.ContainsKey("StageTimeoutSeconds")

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
function Show-Help {
    @"
chain.ps1 - Chronicle pipeline: ingest -> verify -> merge -> categorize -> index

Usage:
  .\chain.ps1 -InputDir <dir> -OutputDir <dir> [options]

Required:
  -InputDir <dir>   Directory containing raw .md files
  -OutputDir <dir>  Directory for output files (created if missing)

Options:
  -ThemesConfig <file>  Theme config for categorize.py (JSON or YAML)
  -IndexConfig <file>   Index config for index.py (JSON)
  -Verify               Run verify_ingest.py before merging
  -SkipCategorize       Stop after merge (skip categorisation and indexing)
  -SkipIndex            Stop after categorise (skip index generation)
  -NoLinkRegistry       Skip link registry generation in index.py
  -SourceCoverage       Pass source_coverage.md to index.py
  -AllowPartialIngest    Continue pipeline when some (not all) files fail to ingest
  -StageTimeoutSeconds <seconds>  Optional positive deadline per native stage
  -Verbose              Enable debug logging in all stages

Exit codes:
  0  All stages completed successfully
  1  Ingestion failed
  2  Verification failed (only with -Verify)
  3  Merge failed
  4  Categorisation failed
  5  Index generation failed

Examples:
  .\chain.ps1 -InputDir raw/ -OutputDir output/
  .\chain.ps1 -InputDir raw/ -OutputDir output/ -Verify -ThemesConfig themes.yaml
  .\chain.ps1 -InputDir raw/ -OutputDir output/ -SkipCategorize
  .\chain.ps1 -InputDir raw/ -OutputDir output/ -IndexConfig index_config.json -NoLinkRegistry
"@
    exit 0
}

if (-not $InputDir -and -not $OutputDir) {
    Show-Help
}
if ($HasStageTimeout -and ($StageTimeoutSeconds -le 0 -or
        [double]::IsNaN($StageTimeoutSeconds) -or [double]::IsInfinity($StageTimeoutSeconds))) {
    Write-Error "StageTimeoutSeconds must be finite and positive"
    exit 1
}

# chain.ps1 signals failures via exit codes, not thrown errors. Keep
# Write-Error non-terminating so each abort message is followed by exit N
# even under a caller's $ErrorActionPreference = "Stop".
$ErrorActionPreference = "Continue"

# ---------------------------------------------------------------------------
# Stage helpers
# ---------------------------------------------------------------------------
function Invoke-ChronicleStage {
    param([string]$StageName, [string]$ScriptPath, [string[]]$Arguments)

    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $status = "failed"
    $failureKind = "launch_error"
    $exitCode = $null
    $diagnostics = @()
    $previousExitCode = $global:LASTEXITCODE
    $terminal = $null
    $bridgeStarted = $false
    $script:executionCount++
    $evidenceRef = "exec-01/$($evidence.run_id)/$($script:executionCount).json"
    $script:activeExecutionRef = $evidenceRef
    $evidencePath = Join-Path $OutputDirAbs $evidenceRef
    $requestPath = "$evidencePath.request"
    $responsePath = "$evidencePath.response"
    $bridge = $null

    try {
        $pythonName = if ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) { "python.exe" } else { "python" }
        $python = Get-Command -Name $pythonName -CommandType Application -TotalCount 1 -ErrorAction Stop
        # Keep native stderr diagnostic-only in Windows PowerShell and PowerShell 7.
        $ErrorActionPreference = "Continue"
        $PSNativeCommandUseErrorActionPreference = $false
        $global:LASTEXITCODE = $null
        $request = @{
            evidence = $evidencePath; response = $responsePath
            argv = @($python.Source, $ScriptPath) + $Arguments
            timeout = $(if ($HasStageTimeout) { $StageTimeoutSeconds } else { $null })
        }
        [IO.File]::WriteAllText($requestPath, (ConvertTo-Json -InputObject $request -Compress),
            [Text.UTF8Encoding]::new($false))
        $startInfo = [Diagnostics.ProcessStartInfo]::new($python.Source)
        $startInfo.UseShellExecute = $false
        if ($null -ne $startInfo.PSObject.Properties["ArgumentList"]) {
            $startInfo.ArgumentList.Add($ExecutePy)
            $startInfo.ArgumentList.Add($requestPath)
        } else {
            $startInfo.Arguments = '"{0}" "{1}"' -f $ExecutePy, $requestPath
        }
        # Native command pipelines stop their child on Ctrl+C. Wait on the
        # bridge directly so it can handle the console signal and publish.
        $bridge = [Diagnostics.Process]::Start($startInfo)
        $bridgeStarted = $true
        $bridge.WaitForExit()
        if ($bridge.ExitCode -ne 0 -or -not [IO.File]::Exists($responsePath)) {
            throw "Bounded execution bridge did not return a terminal record"
        }
        # JSON escaping can expand both 1 MiB streams by up to sixfold.
        if ([IO.FileInfo]::new($responsePath).Length -gt 13MB) {
            throw "Bounded execution bridge response exceeded its limit"
        }
        $terminal = [IO.File]::ReadAllText($responsePath, [Text.UTF8Encoding]::new($false, $true)) |
            ConvertFrom-Json -ErrorAction Stop
        if ($terminal.schema -cne "exec-01-v1") { throw "Unknown execution evidence schema" }
        $exitCode = $terminal.native_exit_code
        $diagnostics = @($terminal.stdout_text, $terminal.stderr_text, $terminal.detail) |
            Where-Object { $_ }
        if ($env:WORDPIPE_ORIGIN_QUALIFICATION -and -not $Verbose -and
            $terminal.outcome -eq "native_failure" -and $terminal.stderr_text -match '(?m)^CI-01: [^\r\n]+') {
            Write-Host $Matches[0]
        }
        if ($terminal.outcome -eq "success") {
            $status = "ok"
            $failureKind = $null
        } elseif ($terminal.outcome -eq "native_failure") {
            $failureKind = "native_exit"
        } elseif ($terminal.outcome -ne "launch_failure") {
            $failureKind = $terminal.outcome
        }
    } catch {
        $diagnostics += $_
        if ($bridgeStarted) { $failureKind = "cleanup_failure" }
        if (-not [IO.File]::Exists($evidencePath)) {
            $fallbackOutcome = if ($bridgeStarted) { "cleanup_failure" } else { "launch_failure" }
            $fallbackCleanup = if ($bridgeStarted) { "unverified" } else { "not_started" }
            $fallback = @{
                schema = "exec-01-v1"; outcome = $fallbackOutcome; trigger = $fallbackOutcome
                native_exit_code = $null; exit_code = 125; elapsed_seconds = $timer.Elapsed.TotalSeconds
                stdout = $null; stderr = $null; cleanup = $fallbackCleanup
                detail = "PowerShell execution bridge unavailable"; exited_process_records = $null
            }
            try {
                $stream = [IO.File]::Open($evidencePath, [IO.FileMode]::CreateNew)
                try {
                    $bytes = [Text.Encoding]::UTF8.GetBytes((ConvertTo-Json -InputObject $fallback -Compress))
                    $stream.Write($bytes, 0, $bytes.Length)
                } finally { $stream.Dispose() }
            } catch { $evidenceRef = $null }
        }
    } finally {
        if ($bridge) { $bridge.Dispose() }
        [IO.File]::Delete($requestPath)
        [IO.File]::Delete($responsePath)
        $global:LASTEXITCODE = $previousExitCode
        $timer.Stop()
    }

    [pscustomobject]@{
        Stage       = $StageName
        Status      = $status
        FailureKind = $failureKind
        ExitCode    = $exitCode
        Diagnostics = $diagnostics
        DurationMs  = $timer.ElapsedMilliseconds
        ExecutionEvidence = $evidenceRef
    }
}

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
# Validate input directory
# ---------------------------------------------------------------------------
. "$ScriptDir/chain_evidence.ps1"
$evidence = New-ChronicleEvidence $Verify.IsPresent $SkipCategorize.IsPresent $SkipIndex.IsPresent
$ingestStage, $verifyStage, $mergeStage, $categorizeStage, $indexStage = $evidence.stages
$activeStage = $ingestStage
$runExitCode = 1
$lock = $null
$summaryPath = $null
$executionCount = 0
$activeExecutionRef = $null

try {
    try {
        if (-not (Test-Path -LiteralPath $OutputDir -PathType Container -ErrorAction Stop)) {
            New-Item -ItemType Directory -Path $OutputDir -Force -ErrorAction Stop | Out-Null
            if (-not (Test-Path -LiteralPath $OutputDir -PathType Container -ErrorAction Stop)) {
                throw "Output path is not a directory: $OutputDir"
            }
        }
        $OutputDirAbs = (Resolve-Path -LiteralPath $OutputDir -ErrorAction Stop).Path
        $lockPath = Join-Path $OutputDirAbs ".chronicle-run.lock"
        $lock = [IO.FileStream]::new($lockPath, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite,
            [IO.FileShare]::None, 4096, [IO.FileOptions]::DeleteOnClose)
        $path = Join-Path $OutputDirAbs "run.json"
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $prior = (Read-ChronicleArtifactPrefix $path 1048576 $true) | ConvertFrom-Json -ErrorAction Stop
            if ($prior.status -in @("ok", "partial") -and $prior.exit_code -eq 0) {
                throw "Output directory contains a successful run. Use a fresh OutputDir."
            }
        }
        [IO.File]::Delete($path)
        $summaryPath = $path
        [IO.Directory]::CreateDirectory((Join-Path $OutputDirAbs "exec-01/$($evidence.run_id)")) | Out-Null

        if (-not (Test-Path -LiteralPath $InputDir -PathType Container -ErrorAction Stop)) {
            throw "Input directory does not exist: $InputDir"
        }
        $InputDirAbs = (Resolve-Path -LiteralPath $InputDir -ErrorAction Stop).Path
    } catch {
        Write-Error "Ingestion setup failed (input '$InputDir', output '$OutputDir'): $_"
        exit 1
    }

    # ---------------------------------------------------------------------------
    # Validate tool scripts
    # ---------------------------------------------------------------------------
    foreach ($script in @($IngestPy, $MergePy, $CategorizePy)) {
        if (-not (Test-Path $script)) {
            Write-Error "Required script not found: $script"
            $runExitCode = 1
            exit $runExitCode
        }
    }
    if ($Verify -and -not (Test-Path $VerifyPy)) {
        Write-Error "-Verify requested but verify_ingest.py not found: $VerifyPy"
        $runExitCode = 1
        exit $runExitCode
    }
    if (-not $SkipCategorize -and -not $SkipIndex -and -not (Test-Path $IndexPy)) {
        Write-Error "index.py not found: $IndexPy"
        $runExitCode = 1
        exit $runExitCode
    }

    # ---------------------------------------------------------------------------
    # Stage 1: Ingestion
    # ---------------------------------------------------------------------------
    Write-StageHeader 1 "Ingestion - $IngestPy"

    $NormalisedDir = "$OutputDirAbs/normalised"
    try {
        New-Item -ItemType Directory -Path $NormalisedDir -Force -ErrorAction Stop | Out-Null
        if (-not (Test-Path -LiteralPath $NormalisedDir -PathType Container -ErrorAction Stop)) {
            throw "Normalized output path is not a directory: $NormalisedDir"
        }
        $RawFiles = Get-ChildItem -LiteralPath $InputDirAbs -Filter "*.md" -File -ErrorAction Stop
    } catch {
        Write-Error "Ingestion setup failed (input '$InputDirAbs', output '$NormalisedDir'): $_"
        $runExitCode = 1
        exit $runExitCode
    }
    if ($RawFiles.Count -eq 0) {
        Write-Error "No .md files found in $InputDirAbs"
        $runExitCode = 1
        exit $runExitCode
    }

    $IngestCount = 0
    $IngestFailures = 0
    $IngestFiles = @()

    foreach ($rawFile in $RawFiles) {
        $filename = $rawFile.Name
        $outFile = "$NormalisedDir/$filename"
        Write-Host "  Processing: $filename"

        $ingestArgs = @("--input", $rawFile.FullName, "--output", $outFile)
        if ($Verbose) { $ingestArgs += "--verbose" }
        $previousOutput = Get-ChronicleArtifactStamp $outFile
        $previousManifest = Get-ChronicleArtifactStamp ([IO.Path]::ChangeExtension($outFile, ".rejections.json"))
        $result = Invoke-ChronicleStage "Ingestion" $IngestPy $ingestArgs
        $fileEvidence = Get-ChronicleIngestEvidence $result $filename $outFile $previousOutput $previousManifest
        $evidence.ingest_files.Add($fileEvidence)
        $ingestStage.duration_ms = $ingestStage.duration_ms + $result.DurationMs
        if ($result.Status -eq "failed" -and $ingestStage.diagnostics.Count -eq 0) {
            $ingestStage.native_exit_code = $result.ExitCode
            $ingestStage.diagnostics = @($result.FailureKind)
        }

        if ($result.Status -eq "ok") {
            $IngestCount++
            $IngestFiles += $outFile
            $ingestStage.outputs += $fileEvidence.output
            Write-StageOk $filename
        } else {
            $IngestFailures++
            Write-StageFail "$filename ($($result.FailureKind), exit code $($result.ExitCode))"
            if ($Verbose -or $result.FailureKind -eq "launch_error") {
                Write-Host "  Output: $($result.Diagnostics)" -ForegroundColor DarkGray
            }
            if ($result.FailureKind -ne "native_exit") {
                $runExitCode = 1
                exit $runExitCode
            }
        }
    }

    Write-Host ""
    Write-Host "  Ingestion complete: $IngestCount succeeded, $IngestFailures failed"

    if ($IngestFailures -gt 0 -and -not $AllowPartialIngest) {
        Write-Error "One or more files failed to ingest. Aborting. Use -AllowPartialIngest to skip failures."
        $runExitCode = 1
        exit $runExitCode
    }

    if ($IngestCount -eq 0) {
        Write-Error "No files were successfully ingested. Aborting."
        $runExitCode = 1
        exit $runExitCode
    }

    $ingestStage.status = if ($IngestFailures -gt 0) { "partial" } else { "ok" }
    if ($IngestFailures -eq 0) { $ingestStage.native_exit_code = 0 }

    # ---------------------------------------------------------------------------
    # Stage 2: Verification (optional)
    # ---------------------------------------------------------------------------
    if ($Verify) {
        $activeStage = $verifyStage
        Write-StageHeader 2 "Verification - $VerifyPy"

        $verifyArgs = @("--dir", $InputDirAbs, "--ingest", $IngestPy)
        if ($Verbose) { $verifyArgs += "--verbose" }
        $result = Invoke-ChronicleStage "Verification" $VerifyPy $verifyArgs
        Set-ChronicleStageEvidence $verifyStage $result

        if ($result.Status -eq "ok") {
            Write-StageOk "All files verified successfully"
            if ($Verbose) {
                $result.Diagnostics | ForEach-Object { Write-Host $_ -ForegroundColor DarkGray }
            }
        } else {
            Write-StageFail "Verification failed ($($result.FailureKind), exit code $($result.ExitCode))"
            if ($Verbose -or $result.FailureKind -eq "launch_error") {
                Write-Host "  Output: $($result.Diagnostics)" -ForegroundColor DarkGray
            }
            Write-Error "Verification failed. Aborting."
            $runExitCode = 2
            exit $runExitCode
        }
    }

    # ---------------------------------------------------------------------------
    # Stage 3: Merge
    # ---------------------------------------------------------------------------
    $activeStage = $mergeStage
    Write-StageHeader 3 "Merge - $MergePy"

    $MergedFile = "$OutputDirAbs/merged.md"
    $mergeArgs = @("--inputs") + $IngestFiles + @("--output", $MergedFile, "--conflict-mode", "keep-both")
    if ($Verbose) { $mergeArgs += "--verbose" }
    if ($SourceCoverage) { $mergeArgs += "--source-coverage" }
    $evidence.merge_inputs = @($ingestStage.outputs)
    $result = Invoke-ChronicleStage "Merge" $MergePy $mergeArgs
    Set-ChronicleStageEvidence $mergeStage $result

    if ($result.Status -eq "ok") {
        $mergeStage.outputs = @("merged.md", "merged.duplicates.json")
        if ($SourceCoverage) { $mergeStage.outputs += "merged.source_coverage.md" }
        Write-StageOk "Merged chronicle written to $MergedFile"
    } else {
        Write-StageFail "Merge failed ($($result.FailureKind), exit code $($result.ExitCode))"
        if ($Verbose -or $result.FailureKind -eq "launch_error") {
            Write-Host "  Output: $($result.Diagnostics)" -ForegroundColor DarkGray
        }
        Write-Error "Merge failed. Aborting."
        $runExitCode = 3
        exit $runExitCode
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
        $runExitCode = 0
        exit $runExitCode
    }

    $activeStage = $categorizeStage
    Write-StageHeader 4 "Categorisation - $CategorizePy"

    $TaggedFile = "$OutputDirAbs/chronicle_tagged.md"
    $sidecarName = "chronicle_tagged.tagged.json"
    $sidecarPath = Join-Path $OutputDirAbs $sidecarName
    $catArgs = @("--input", $MergedFile, "--output", $TaggedFile, "--sidecar")
    if ($ThemesConfig) {
        if (-not (Test-Path $ThemesConfig)) {
            Write-Error "Theme config file not found: $ThemesConfig"
            $runExitCode = 4
            exit $runExitCode
        }
        $catArgs += @("--config", $ThemesConfig)
    }
    if ($Verbose) { $catArgs += "--verbose" }
    $previousSidecar = Get-ChronicleArtifactStamp $sidecarPath
    $result = Invoke-ChronicleStage "Categorisation" $CategorizePy $catArgs
    Set-ChronicleStageEvidence $categorizeStage $result

    if ($result.Status -eq "ok") {
        $categorizeStage.outputs = @("chronicle_tagged.md")
        $sidecarStamp = Get-ChronicleArtifactStamp $sidecarPath
        if ($sidecarStamp -and $sidecarStamp -ne $previousSidecar) {
            $categorizeStage.outputs += $sidecarName
        }
        Write-StageOk "Tagged chronicle written to $TaggedFile"
    } else {
        Write-StageFail "Categorisation failed ($($result.FailureKind), exit code $($result.ExitCode))"
        if ($Verbose -or $result.FailureKind -eq "launch_error") {
            Write-Host "  Output: $($result.Diagnostics)" -ForegroundColor DarkGray
        }
        Write-Error "Categorisation failed. Aborting."
        $runExitCode = 4
        exit $runExitCode
    }

    # ---------------------------------------------------------------------------
    # Stage 5: Index Generation (optional)
    # ---------------------------------------------------------------------------
    if ($SkipIndex) {
        Write-Host ""
        Write-Host ("=" * 72) -ForegroundColor Cyan
        Write-Host "  Stage 5: Index Generation - SKIPPED (-SkipIndex)" -ForegroundColor Yellow
        Write-Host ("=" * 72) -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Pipeline complete. Output:" -ForegroundColor Green
        Write-Host "  Normalised files: $NormalisedDir/"
        Write-Host "  Merged chronicle: $MergedFile"
        Write-Host "  Tagged chronicle: $TaggedFile"
        if ($sidecarName -in $categorizeStage.outputs) { Write-Host "  Sidecar JSON:    $sidecarPath" }
        Write-Host "  Duplicates:      $([System.IO.Path]::ChangeExtension($MergedFile, '.duplicates.json'))"
        $runExitCode = 0
        exit $runExitCode
    }

    $activeStage = $indexStage
    Write-StageHeader 5 "Index Generation - $IndexPy"

    $AppendixDir = "$OutputDirAbs/appendix"
    $indexArgs = @("--input", $TaggedFile, "--merged", $MergedFile, "--output-dir", $AppendixDir)
    if ($IndexConfig) {
        if (-not (Test-Path $IndexConfig)) {
            Write-Error "Index config file not found: $IndexConfig"
            $runExitCode = 5
            exit $runExitCode
        }
        $indexArgs += @("--config", $IndexConfig)
    }
    if ($NoLinkRegistry) {
        $indexArgs += "--no-link-registry"
    }
    if ($SourceCoverage) {
        $sourceCoverageFile = "$OutputDirAbs/merged.source_coverage.md"
        if (Test-Path $sourceCoverageFile) {
            $indexArgs += @("--source-coverage", $sourceCoverageFile)
        } else {
            Write-Host "  [WARN] Source coverage file not found: $sourceCoverageFile" -ForegroundColor Yellow
        }
    }
    if ($Verbose) { $indexArgs += "--verbose" }
    $registryName = "appendix/link_registry.md"
    $registryPath = Join-Path $OutputDirAbs $registryName
    $requiredIndex = @("appendix/event_index.md", "appendix/theme_index.md", "appendix/source_manifest.md")
    $optionalIndex = @($registryName, "appendix/chronicle_tagged_anchored.md")
    $previousIndex = @{}
    foreach ($name in ($requiredIndex + $optionalIndex)) {
        $previousIndex[$name] = Get-ChronicleArtifactStamp (Join-Path $OutputDirAbs $name)
    }
    $result = Invoke-ChronicleStage "Index generation" $IndexPy $indexArgs
    Set-ChronicleStageEvidence $indexStage $result

    if ($result.Status -eq "ok") {
        foreach ($name in $requiredIndex) {
            $stamp = Get-ChronicleArtifactStamp (Join-Path $OutputDirAbs $name)
            if (-not $stamp -or $stamp -eq $previousIndex[$name]) {
                $indexStage.status = "failed"
                $indexStage.diagnostics = @("missing_or_stale_index_artifact")
                Write-Error "Index generation did not publish a fresh $name."
                $runExitCode = 5
                exit $runExitCode
            }
        }
        $indexStage.outputs = $requiredIndex
        foreach ($name in $optionalIndex) {
            $stamp = Get-ChronicleArtifactStamp (Join-Path $OutputDirAbs $name)
            if ($stamp -and $stamp -ne $previousIndex[$name]) {
                $indexStage.outputs += $name
            }
        }
        Write-StageOk "Appendix indices written to $AppendixDir"
    } else {
        Write-StageFail "Index generation failed ($($result.FailureKind), exit code $($result.ExitCode))"
        if ($Verbose -or $result.FailureKind -eq "launch_error") {
            Write-Host "  Output: $($result.Diagnostics)" -ForegroundColor DarkGray
        }
        Write-Error "Index generation failed. Aborting."
        $runExitCode = 5
        exit $runExitCode
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
    if ($sidecarName -in $categorizeStage.outputs) { Write-Host "    Sidecar JSON:   $sidecarPath" }
    Write-Host "    Duplicates:     $([System.IO.Path]::ChangeExtension($MergedFile, '.duplicates.json'))"
    Write-Host "    Appendix:       $AppendixDir/"
    Write-Host "      Event index:  $AppendixDir/event_index.md"
    Write-Host "      Theme index:  $AppendixDir/theme_index.md"
    Write-Host "      Manifest:     $AppendixDir/source_manifest.md"
    if ($registryName -in $indexStage.outputs) {
        Write-Host "      Link registry: $registryPath"
    }
    Write-Host ""
    $runExitCode = 0
    exit $runExitCode
} finally {
    try {
        if ($summaryPath) {
            if ($runExitCode -ne 0 -and $activeExecutionRef) {
                $lastExecutionPath = Join-Path $OutputDirAbs $activeExecutionRef
                if ([IO.File]::Exists($lastExecutionPath)) {
                    $lastExecution = (Read-ChronicleArtifactPrefix $lastExecutionPath 16384 $true) |
                        ConvertFrom-Json -ErrorAction Stop
                    if ($lastExecution.trigger -eq "cancelled") {
                        $activeStage.status = "failed"
                        $activeStage.native_exit_code = $lastExecution.native_exit_code
                        $activeStage.diagnostics = @("cancelled")
                        $activeStage.execution_evidence = $activeExecutionRef
                    }
                }
            }
            if ($runExitCode -ne 0 -and $activeStage.status -ne "failed") {
                $activeStage.status = "failed"
                if ($activeStage.diagnostics.Count -eq 0) {
                    $activeStage.diagnostics = @("stage_setup_error")
                }
            }
            $evidence.finished_at = [datetime]::UtcNow.ToString("o")
            $evidence.exit_code = $runExitCode
            $evidence.status = if ($runExitCode -ne 0) { "failed" }
                elseif ($ingestStage.status -eq "partial") { "partial" }
                else { "ok" }
            Write-ChronicleEvidence $evidence $summaryPath
        }
    } catch {
        Write-Error "Could not publish Chronicle run evidence: $summaryPath"
        if ($runExitCode -eq 0) { $runExitCode = 1 }
    } finally {
        if ($lock) { $lock.Dispose() }
    }
    exit $runExitCode
}
