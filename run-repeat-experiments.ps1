# Run from FlightDelayARF, or save this file in that folder.
# Four full runs: Moderate/Fast with ARF learner seeds 2 and 3.
# All learner options apart from the seed match the earlier 10-tree runs.
$ErrorActionPreference = 'Stop'
if ($PSScriptRoot) { Set-Location -LiteralPath $PSScriptRoot }

if (-not (Test-Path -LiteralPath '.\data\airlines.arff')) {
    throw 'Save this script inside FlightDelayARF beside the data and moa folders.'
}
if (-not (Test-Path -LiteralPath '.\RunSeededARF.java')) {
    throw 'Extract RunSeededARF.java beside this script before running.'
}
$moaJar = Get-ChildItem .\moa -Recurse -File |
    Where-Object { $_.Name -match '^moa(?:-\d[\d.]*)?\.jar$' } |
    Select-Object -First 1
$agentJar = Get-ChildItem .\moa -Recurse -File |
    Where-Object { $_.Name -match '^sizeofag(?:-[\d.]+)?\.jar$' } |
    Select-Object -First 1
if (-not $moaJar -or -not $agentJar) { throw 'MOA or sizeofag JAR not found.' }
if (-not (Get-Command java -ErrorAction SilentlyContinue)) { throw 'Java not found.' }

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$runFolder = "results/repeats-$stamp"
New-Item -ItemType Directory -Path $runFolder | Out-Null
$javaArguments = @('-Xmx4g', '-cp', $moaJar.FullName,
    "-javaagent:$($agentJar.FullName)", '.\RunSeededARF.java')
$summary = @()
$invariant = [System.Globalization.CultureInfo]::InvariantCulture

foreach ($seed in @(2, 3)) {
    foreach ($setting in @('moderate', 'fast')) {
        if ($setting -eq 'moderate') { $warning = '0.0001'; $drift = '0.00001' }
        else { $warning = '0.01'; $drift = '0.001' }

        $prefix = "$runFolder/full-$setting-seed$seed"
        $csvPath = "$prefix.csv"
        $logPath = "$prefix-console.txt"
        # MOA 24.07 ARF does not expose -r in its CLI options. The Java helper
        # sets the learner seed through setRandomSeed(); task seed stays at 1.
        $task = "EvaluatePrequentialCV -l (meta.AdaptiveRandomForest -s 10 -p (ADWINChangeDetector -a $warning) -x (ADWINChangeDetector -a $drift)) -s (ArffFileStream -f data/airlines.arff) -e BasicClassificationPerformanceEvaluator -w 10 -a 0 -r 1 -i 539383 -f 10000 -d $csvPath"
        $task | Set-Content -LiteralPath "$prefix-command.txt" -Encoding UTF8
        @($javaArguments + @([string]$seed, $task)) | ConvertTo-Json | Set-Content -LiteralPath "$prefix-java-args.json" -Encoding UTF8
        Write-Host "`nRunning $setting, ARF seed $seed ..." -ForegroundColor Cyan

        # MOA normally writes its banner/progress to stderr. Preserve that output
        # without treating the normal banner as a terminating PowerShell error.
        $ErrorActionPreference = 'Continue'
        try {
            & java @javaArguments "$seed" $task 2>&1 |
                ForEach-Object { $_.ToString() } |
                Tee-Object -FilePath $logPath
            $javaExitCode = $LASTEXITCODE
        }
        finally { $ErrorActionPreference = 'Stop' }

        # MOA can report a failed task even with Java exit code 0.
        if ($javaExitCode -ne 0 -or -not (Test-Path -LiteralPath $csvPath)) {
            throw "Java did not complete successfully. Check $logPath"
        }
        if (Select-String -LiteralPath $logPath -Pattern 'Task failed|OutOfMemoryError' -Quiet) {
            throw "MOA reported a failed task. Check $logPath"
        }
        $rows = @(Import-Csv -LiteralPath $csvPath)
        if ($rows.Count -ne 54) {
            throw "Expected 54 result rows; found $($rows.Count). Check $csvPath"
        }
        $last = $rows[-1]
        $processed = [double]::Parse($last.'learning evaluation instances', $invariant)
        if ($processed -ne 539383) { throw "Incomplete stream in $csvPath" }
        $accuracy = [double]::Parse($last.'[avg] classifications correct (percent)', $invariant)
        $cpuSeconds = [double]::Parse($last.'evaluation time (cpu seconds)', $invariant)
        $summary += [PSCustomObject]@{
            Setting = $setting
            ARFSeed = $seed
            TreesPerForest = 10
            Folds = 10
            Records = $processed
            AccuracyPercent = $accuracy
            CPUSeconds = $cpuSeconds
            KappaMPercent = [double]::Parse($last.'[avg] Kappa M Statistic (percent)', $invariant)
            KappaTemporalPercent = [double]::Parse($last.'[avg] Kappa Temporal Statistic (percent)', $invariant)
            ResultFile = $csvPath
        }
        $summary | Export-Csv -LiteralPath "$runFolder/summary.csv" -NoTypeInformation -Encoding UTF8
        Write-Host "Verified: 539,383 records; accuracy $accuracy percent." -ForegroundColor Green
    }
}

Write-Host "`nAll four experiments completed. Results: $runFolder" -ForegroundColor Green
$summary | Format-Table Setting, ARFSeed, AccuracyPercent, CPUSeconds -AutoSize
Compress-Archive -Path "$runFolder/*" -DestinationPath "$runFolder.zip"
Write-Host "Upload this ZIP: $runFolder.zip" -ForegroundColor Green
