"""Validate six Airlines streams and summarize three learner seeds per setting.

Run python analyze_results.py from the extracted package. Standard library only.
Seed-one CSV tables were previously extracted from uploaded console output.
Seeds two and three come from the user's original repeat-run ZIP.
"""
import csv
import io
import json
import math
import statistics
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = {
    "accuracy_percent": "[avg] classifications correct (percent)",
    "cpu_seconds": "evaluation time (cpu seconds)",
    "kappa_m_percent": "[avg] Kappa M Statistic (percent)",
    "kappa_temporal_percent": "[avg] Kappa Temporal Statistic (percent)",
}
PAPER = {"moderate": 66.26, "fast": 66.48}
EXPECTED = list(range(10000, 539383, 10000)) + [539383]


def decode(raw):
    return raw.decode("utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")


def write_csv(name, rows):
    with (ROOT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    runs = []
    checks = []
    archive = ROOT / "source/repeats-20261119-183637-313.zip"
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None, "Archive integrity failed"
        supplied_summary = list(csv.DictReader(io.StringIO(decode(z.read("summary.csv")))))
        for setting in ("moderate", "fast"):
            for seed in (1, 2, 3):
                stem = f"full-{setting}-seed{seed}"
                if seed == 1:
                    text = (ROOT / f"source/{stem}.csv").read_text(encoding="utf-8-sig")
                else:
                    text = decode(z.read(stem + ".csv"))
                    log = decode(z.read(stem + "-console.txt"))
                    assert f"ARF learner seed set through MOA API: {seed}" in log
                    assert not any(s in log for s in ("Task failed", "OutOfMemoryError", "Exception in thread"))
                    args = json.loads(decode(z.read(stem + "-java-args.json")))
                    command = decode(z.read(stem + "-command.txt")).strip()
                    assert args[-2] == str(seed) and args[0] == "-Xmx4g"
                    assert args[-1] == command
                    assert "-w 10 -a 0 -r 1 -i 539383 -f 10000" in command
                    assert "meta.AdaptiveRandomForest -s 10 -p" in command
                    thresholds = ("0.0001", "0.00001") if setting == "moderate" else ("0.01", "0.001")
                    assert f"-p (ADWINChangeDetector -a {thresholds[0]}) -x (ADWINChangeDetector -a {thresholds[1]})" in command
                rows = list(csv.DictReader(io.StringIO(text)))
                assert len(rows) == 54
                assert [int(float(r["learning evaluation instances"])) for r in rows] == EXPECTED
                assert all(int(float(r["[avg] classified instances"])) == EXPECTED[i] for i, r in enumerate(rows))
                assert all(math.isfinite(float(v)) for r in rows for v in r.values())
                assert all(float(rows[i][FIELDS["cpu_seconds"]]) >= float(rows[i - 1][FIELDS["cpu_seconds"]]) for i in range(1, 54))
                run = {"setting": setting, "learner_seed": seed, "records": 539383, "trees_per_forest": 10, "folds": 10}
                run.update({name: float(rows[-1][field]) for name, field in FIELDS.items()})
                if seed != 1:
                    original = next(r for r in supplied_summary if r["Setting"] == setting and int(r["ARFSeed"]) == seed)
                    assert math.isclose(float(original["AccuracyPercent"]), run["accuracy_percent"], abs_tol=1e-10)
                    assert math.isclose(float(original["CPUSeconds"]), run["cpu_seconds"], abs_tol=1e-10)
                runs.append(run)
                checks.append(f"PASS {setting} learner seed {seed}: 54 points; final record 539383; numeric values finite; CPU time monotonic.")

    summary = []
    for setting in ("moderate", "fast"):
        subset = [r for r in runs if r["setting"] == setting]
        row = {"setting": setting, "n_runs": len(subset)}
        for field in FIELDS:
            values = [r[field] for r in subset]
            row[field + "_mean"] = statistics.mean(values)
            row[field + "_sample_sd"] = statistics.stdev(values)
        row["paper_accuracy_percent_100_trees"] = PAPER[setting]
        row["accuracy_shortfall_from_paper_pp"] = PAPER[setting] - row["accuracy_percent_mean"]
        summary.append(row)
    paired = []
    for seed in (1, 2, 3):
        fast = next(r for r in runs if r["setting"] == "fast" and r["learner_seed"] == seed)
        moderate = next(r for r in runs if r["setting"] == "moderate" and r["learner_seed"] == seed)
        paired.append({"learner_seed": seed, "fast_minus_moderate_accuracy_pp": fast["accuracy_percent"] - moderate["accuracy_percent"], "fast_minus_moderate_cpu_seconds": fast["cpu_seconds"] - moderate["cpu_seconds"]})
    write_csv("all_six_runs.csv", runs)
    write_csv("summary_statistics.csv", summary)
    write_csv("paired_differences.csv", paired)
    (ROOT / "validation.txt").write_text("\n".join(checks) + "\nPASS new-run logs, learner seeds, JVM arguments, task commands, detector thresholds, and uploaded summary agree.\n", encoding="utf-8")
    print(json.dumps({"runs": runs, "summary": summary, "paired": paired}, indent=2))


if __name__ == "__main__":
    main()
