"""Reproduce the report's exploratory paired t-test and baseline comparisons.

Run from the package root: python analysis/exploratory_analysis.py
Requires scipy, in requirements-analysis.txt. No MOA experiment is rerun.
The t-test is conditional on one fixed dataset and three learner-seed pairs.
"""
import csv
import json
import math
import statistics
from pathlib import Path

from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parent
runs = list(csv.DictReader((ROOT / 'all_six_runs.csv').open()))
lookup = {(r['setting'], int(r['learner_seed'])): r for r in runs}
diffs = [float(lookup['fast', seed]['accuracy_percent']) -
         float(lookup['moderate', seed]['accuracy_percent']) for seed in (1, 2, 3)]
mean = statistics.mean(diffs)
sd = statistics.stdev(diffs)
se = sd / math.sqrt(3)
stat = mean / se
pvalue = 2 * student_t.sf(abs(stat), df=2)
critical = student_t.ppf(.975, df=2)
majority = 100 * 299119 / 539383
baseline_results = {}
for setting, paper in [('moderate', 66.26), ('fast', 66.48)]:
    reproduced = statistics.mean(float(lookup[setting, seed]['accuracy_percent']) for seed in (1, 2, 3))
    baseline_results[setting] = {
        'paper_accuracy_percent': paper,
        'reproduced_accuracy_percent': reproduced,
        'paper_gain_above_majority_pp': paper - majority,
        'reproduced_gain_above_majority_pp': reproduced - majority,
        'published_gain_retained_percent': 100 * (reproduced - majority) / (paper - majority),
    }

result = {
    'n_seed_pairs': 3,
    'paired_differences_pp': diffs,
    'mean_difference_pp': mean,
    'sample_sd_difference_pp': sd,
    'paired_t': stat,
    'degrees_of_freedom': 2,
    'two_sided_p': float(pvalue),
    'conditional_95_percent_ci_pp': [mean - critical * se, mean + critical * se],
    'interpretation': 'Exploratory variation over learner seeds on one fixed dataset; assumptions cannot be assessed reliably with three pairs. This is not a test of superiority across datasets or equivalence with the original paper.',
    'majority_class_share_percent': majority,
    'baseline_comparisons': baseline_results,
    'kappa_m_reconstructed_from_paper_accuracy_and_global_majority_percent':
        100 * (66.26 - majority) / (100 - majority),
    'airlines_original_serial_to_parallel_cpu_ratio': 2745.49 / 361.31,
    'causal_limit': 'Similar retained-gain ratios do not identify the cause of the accuracy shortfalls.',
}
(ROOT / 'exploratory_statistics.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
