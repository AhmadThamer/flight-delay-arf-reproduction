# Airlines ARF reproduction materials

This package accompanies Ahmad Thamer Habib's individual AI508 Assignment 2 report. It contains six completed evaluations: ARF Moderate and ARF Fast, each with learner seeds 1, 2 and 3. Each run processed all 539,383 records using tenfold prequential cross-validation and ten trees per forest. The original paper used 100 trees per forest, so this is a partial reproduction.

## Contents and provenance

- `analysis/source/`: preserved uploaded four-run ZIP, seed-one CSV tables extracted from console output, and the original seed-one console text.
- `evidence/repeat-runs/`: convenience extraction of the same repeat ZIP, including original CSVs, command files, Java arguments and console logs.
- `analysis/analyze_results.py`: standard-library validation and final summary calculations.
- `analysis/plot_six_runs.py`: updated plots and checkpoint statistics from all six preserved streams.
- `analysis/exploratory_analysis.py`: full-precision paired t-test, conditional confidence interval, and descriptive gains above the majority baseline. These calculations do not establish superiority across datasets.
- `figures/`: three-seed stream progression with sample-SD shading, and individual seed accuracies. These replace earlier seed-one-only plots.
- `RunSeededARF.java`: launcher that sets the ARF learner seed through MOA's API without changing the classifier algorithm.
- `run-repeat-experiments.ps1`: original script used for the four additional runs, seeds 2 and 3.
- `run-all-experiments.ps1`: expanded reproduction runner, default seeds 1, 2 and 3. It has not generated new research results for this report.
- `report/`: corrected final report, FlightDelay_AhmadHabib.docx; this replaces the earlier draft.

Original pilot and failed-run files on the student's computer are not complete evaluations and are excluded from summary calculations. The extracted seed-one tables have less command/log metadata than seeds 2 and 3; their preserved console text records the reported numerical evidence. This provenance distinction is retained in the report.

## Dataset

Original authors' repository: https://github.com/hmgomes/AdaptiveRandomForest

Dataset archive: https://github.com/hmgomes/AdaptiveRandomForest/raw/master/AIRL.arff.zip

Extract `airlines.arff` into `data/`. Preserve its existing record order. Do not normalize, shuffle, balance or otherwise transform it for this reproduction.

Expected SHA256:

`C7683A90B40C2CABB1DDC950413DA8EFA231C058327B8C95511C40AF13516C14`

An independent download from the authors' repository matched this checksum on 20 November 2026. File inspection found 539,383 records, seven predictors, 299,119 class-zero records and 240,264 class-one records. No `?` missing-value markers were found. The delay threshold in operational minutes is not independently established by this file inspection.

PowerShell verification:

```powershell
Get-FileHash .\data\airlines.arff -Algorithm SHA256
```

## Software and hardware

Historical experiments used Windows, PowerShell through VS Code, Oracle 64-bit Java 18.0.2.1, MOA 24.07.0, sizeofag 1.1.0 and `-Xmx4g`. Hardware: Ryzen 7 4800H, eight cores/16 logical processors, approximately 15.4 GB usable RAM. ARF's installed numberOfJobs default was one. Four GiB is the Java heap ceiling, not measured peak memory. More memory than this may be needed for the JVM and operating system together.

Pinned MOA release: https://github.com/Waikato/moa/releases/tag/2024.07.0

Download and extract the release under `moa/`, keeping the included MOA and sizeofag JARs. Use a JDK with Java source-file launching support; the reported experiments used Java 18. Confirm `java -version` before running. This package does not redistribute Java, MOA or the dataset. External software remains subject to its own licence.

## Repeat all six experiments

1. Extract this package into the project folder, alongside `data/` and `moa/`.
2. Confirm the dataset checksum and Java version.
3. In the project PowerShell terminal run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-all-experiments.ps1
```

The runner launches both settings for seeds 1, 2 and 3 sequentially and writes a new timestamped results folder. Existing evidence is preserved. It checks full record counts, 54 result rows, and task-failure messages. The original `run-repeat-experiments.ps1` runs only seeds 2 and 3 and is preserved to show the historical procedure.

Evaluation: `EvaluatePrequentialCV`, ten folds (`-w 10`), Cross-Validation (`-a 0`), task seed 1 (`-r 1`), `BasicClassificationPerformanceEvaluator`, limit 539383 and sample frequency 10000. ARF: ten trees, default Poisson parameter 6, grace period 50, split confidence 0.01, 60% feature subspace (four predictors), weighted voting and background learning enabled. Moderate warning/drift thresholds: 0.0001/0.00001. Fast: 0.01/0.001. Learner seed is assigned by the Java helper, separately from task seed. Exact command/JVM records are saved per run. The original data and MOA code, rather than a new classifier implementation, provide the research computation.

## Rebuild the existing analysis without rerunning MOA

From the extracted package:

```powershell
python .\analysis\analyze_results.py
python -m pip install -r .\requirements-plotting.txt
python .\analysis\plot_six_runs.py
```

The first command uses Python's standard library only. The second installs the plotting dependency if needed; no Python package version affected the original Java classifier runs. The scripts rebuild summaries and figures from the preserved six-run source evidence, not from newly generated timestamped runs. To analyse new experiments, supply their source files deliberately and preserve their provenance separately.

Means and sample SDs use three final seed scores per setting; SD is not a confidence interval. The raw MOA fold-level `[err]` columns are not used as between-seed SDs. CPU seconds are evaluation CPU time, not elapsed time or prediction latency. RAM-hours are retained as raw output but are not validated peak-memory estimates. The report retains a qualified exploratory paired t-test on three learner-seed pairs. It does not establish general superiority across datasets, exact reproduction, or deployment readiness.

## Submission checks

Replace the shared-folder-link placeholder in Section 8 of the report. Upload the complete extracted materials to the chosen shared repository/folder and ensure the marker can access it. A private download link to this ZIP alone is not a substitute for checking access. Review the individual reflection and AI disclosure so that they accurately describe the student's own work and understanding.

The corrected final report replaces the earlier draft and contains approximately 4,800 words before references, including front matter and tables. Check the module's precise word-count convention before final submission. Presentation and individual viva preparation are separate deliverables.

## Acknowledgements

Research paper: Gomes et al. (2017), Adaptive random forests for evolving data stream classification, DOI https://doi.org/10.1007/s10994-017-5642-8.

MOA and the original authors' repository provide the algorithm, stream evaluation and dataset access. ChatGPT assisted with commands, launcher code, debugging, validation, analysis, plots and report drafting. The six research evaluations were performed on the student's computer. No new evaluations were run to assemble this package.

## Rebuild the retained exploratory statistics

After running the main analysis script, run:

```powershell
python -m pip install -r .\requirements-analysis.txt
python .\analysis\exploratory_analysis.py
```

This writes `analysis/exploratory_statistics.json` from the six preserved full-precision final accuracies. It includes the paired t statistic, two-sided p-value, conditional confidence interval, baseline-gain ratios, and calculation limits. Three pairs are insufficient to assess the t-test assumptions reliably. No additional research runs are performed.
