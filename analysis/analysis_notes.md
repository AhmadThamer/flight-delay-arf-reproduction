# Validated Airlines reproduction results

All six runs processed 539,383 records each. Each contains 54 reporting points. The four newly uploaded runs have matching task commands, Java arguments, learner seeds, detector thresholds and summaries. Their logs contain no task-failure or out-of-memory messages.

## Results across three learner seeds

| Measure | Moderate | Fast |
| --- | --- | --- |
| Accuracy, mean (%) | 63.573460 | 63.740502 |
| Accuracy, sample SD (percentage points) | 0.015343 | 0.022309 |
| Evaluation CPU time, mean (seconds) | 2149.770833 | 2263.447917 |
| Evaluation CPU time, sample SD (seconds) | 26.974042 | 31.051417 |
| Kappa M, mean (%) | 18.223544 | 18.598550 |
| Kappa Temporal, mean (%) | 13.164402 | 13.562607 |
| Paper accuracy, 100 trees (%) | 66.26 | 66.48 |
| Shortfall from paper (percentage points) | 2.686540 | 2.739498 |

Fast exceeded Moderate accuracy in all three paired seeds, by a mean of 0.167043 percentage points. Its mean evaluation CPU cost was 5.287870% higher. These are descriptive findings for one dataset and three seeds; no significance or general superiority claim is made. The reported SDs are computed across learner-seed runs using n-1, not MOA's fold-level [err] columns. Three seeds do not provide ten or thirty independent datasets.

## Provenance and limits

The original seed-one CSVs were extracted from the user's previously uploaded console tables; copies of those console outputs are retained. The source repeat ZIP is preserved unchanged and contains the user's original four CSVs, logs, commands, Java argument records and summary. Learner seed one is the installed default; seed two and three were set through the Java helper. Repeat-run argument files confirm MOA 24.07.0 and sizeofag 1.1.0. The helper changes seed assignment through MOA's API and leaves the experiment task otherwise unchanged. Small synthetic-stream checks previously matched native seed-one accuracy; these checks are not Airlines research results.

Each forest has 10 trees; the original Table 2 used 100 trees. The difference in forest size and software means this remains a partial reproduction. The common ordering Fast > Moderate is reproduced across the three tested seeds, while absolute paper accuracies are not matched. The entire gap cannot be attributed to tree count without a controlled size experiment. CPU seconds are evaluation CPU time, not elapsed wall time or production prediction latency. Runs occurred sequentially and on different sessions; their timing spread is not a controlled benchmark of hardware variability. RAM-hours are retained in raw CSVs but are not validated estimates of peak memory.

## Completed scope

The revised report describes three completed learner seeds per setting, with learner seed distinct from task seed. No 20-tree experiments have been performed. Updated plots use all six preserved streams; checkpoint_statistics.csv stores the plotted means and sample standard deviations. The expanded runner supports future reproduction of all six runs and has not produced additional research results for this report.

## Recalculating the summaries

Run `python analyze_results.py` in the extracted package. This uses the Python standard library and regenerates all_six_runs.csv, summary_statistics.csv, paired_differences.csv and validation.txt. No experiment is rerun and no new predictions are generated. The research results originate from the user's MOA experiments. ChatGPT assisted with validation, calculations and documentation.

The consolidated package README provides dataset access, checksum, software versions, setup instructions and runner usage. The research launcher and updated figures are included in the same package.
