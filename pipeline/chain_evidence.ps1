# Reporting helpers for chain.ps1. Process diagnostics are deliberately excluded.
function New-ChronicleEvidence {
    param([bool]$Verify, [bool]$SkipCategorize, [bool]$SkipIndex)

    $stages = [ordered]@{}
    foreach ($name in @("ingest", "verify", "merge", "categorize", "index")) {
        $stages[$name] = [ordered]@{
            name = $name
            status = "not_run"
            duration_ms = $null
            native_exit_code = $null
            diagnostics = @()
            outputs = @()
        }
    }
    if (-not $Verify) { $stages.verify.status = "skipped" }
    if ($SkipCategorize) { $stages.categorize.status = "skipped" }
    if ($SkipCategorize -or $SkipIndex) { $stages.index.status = "skipped" }

    @{
        schema_version = 1
        run_id = [guid]::NewGuid().ToString()
        started_at = [datetime]::UtcNow.ToString("o")
        finished_at = $null
        exit_code = 1
        status = "failed"
        stages = @($stages.Values)
        ingest_files = [System.Collections.Generic.List[object]]::new()
        merge_inputs = @()
    }
}

function Set-ChronicleStageEvidence {
    param($Stage, $Result)
    $Stage.status = $Result.Status
    $Stage.duration_ms = $Result.DurationMs
    $Stage.native_exit_code = $Result.ExitCode
    if ($Result.FailureKind -in @("native_exit", "launch_error")) {
        $Stage.diagnostics = @([string]$Result.FailureKind)
    }
}

function Get-ChronicleArtifactStamp {
    param([string]$Path)
    try {
        $item = Get-Item -LiteralPath $Path -ErrorAction Stop
        if (-not $item.PSIsContainer) {
            "$($item.LastWriteTimeUtc.Ticks):$($item.Length)"
        }
    } catch {
        # Missing or inaccessible artifacts have no usable stamp.
    }
}

function Read-ChronicleArtifactPrefix {
    param([string]$Path, [int]$Limit, [bool]$WholeFile)
    $reader = [IO.StreamReader]::new($Path, [Text.UTF8Encoding]::new($false, $true))
    try {
        $buffer = New-Object char[] ($Limit + 1)
        $length = $reader.ReadBlock($buffer, 0, $buffer.Length)
        if ($WholeFile -and $length -gt $Limit) { throw "Artifact exceeds read limit" }
        [string]::new($buffer, 0, $length)
    } finally {
        $reader.Dispose()
    }
}

function Get-ChronicleIngestEvidence {
    param($Result, [string]$FileName, [string]$OutputPath, $PreviousOutput, $PreviousManifest)
    $entry = [ordered]@{
        output = "normalised/$FileName"
        status = $Result.Status
        accepted = $null
        rejected = $null
        diagnostics = @()
    }
    if ($Result.FailureKind -in @("native_exit", "launch_error")) {
        $entry.diagnostics += [string]$Result.FailureKind
    }
    if ($Result.FailureKind -eq "launch_error") { return $entry }

    $manifestPath = [IO.Path]::ChangeExtension($OutputPath, ".rejections.json")
    try {
        if ($Result.Status -eq "ok") {
            $stamp = Get-ChronicleArtifactStamp $OutputPath
            if (-not $stamp -or $stamp -eq $PreviousOutput) { throw "No fresh normalized output" }
            $prefix = Read-ChronicleArtifactPrefix $OutputPath 16384 $false
            if ($prefix -notmatch '\A---\r?\n(?<header>[\s\S]*?)\r?\n---\r?\n') {
                throw "Missing normalized front matter"
            }
            $counts = [regex]::Matches($Matches.header, '(?m)^event_count:([^\r\n]*)')
            if ($counts.Count -ne 1 -or $counts[0].Groups[1].Value -notmatch '^ [0-9]+$') {
                throw "Invalid normalized event count"
            }
            $entry.accepted = [long]::Parse($counts[0].Groups[1].Value)
        }

        $manifestStamp = Get-ChronicleArtifactStamp $manifestPath
        if ($manifestStamp -and $manifestStamp -ne $PreviousManifest) {
            $manifest = (Read-ChronicleArtifactPrefix $manifestPath 1048576 $true) |
                ConvertFrom-Json -ErrorAction Stop
            $expectedType = if ($Result.Status -eq "ok") { "partial" } else { "complete" }
            if ($manifest.manifest_type -cne $expectedType -or $manifest.input_file -cne $FileName) {
                throw "Rejection manifest does not describe this input"
            }
            $accepted = $manifest.accepted_event_count
            $rejected = $manifest.rejected_event_count
            if (($accepted -isnot [int] -and $accepted -isnot [long]) -or $accepted -lt 0 -or
                ($rejected -isnot [int] -and $rejected -isnot [long]) -or $rejected -lt 1 -or
                @($manifest.rejected_events).Count -ne $rejected -or
                ($Result.Status -eq "ok" -and $entry.accepted -ne $accepted)) {
                throw "Invalid rejection counts"
            }
            $entry.accepted = $accepted
            $entry.rejected = $rejected
        } elseif ($Result.Status -eq "ok" -and -not $manifestStamp -and
            -not [IO.File]::Exists($manifestPath)) {
            $entry.rejected = 0
        } else {
            throw "No fresh rejection manifest"
        }
    } catch {
        $entry.diagnostics += "metadata_unavailable"
    }
    $entry
}

function Write-ChronicleEvidence {
    param($Evidence, [string]$Path)
    $temporary = "$Path.$($Evidence.run_id).tmp"
    try {
        $json = ConvertTo-Json -InputObject $Evidence -Depth 8 -ErrorAction Stop
        [IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
        [IO.File]::Move($temporary, $Path)
    } finally {
        [IO.File]::Delete($temporary)
    }
}
