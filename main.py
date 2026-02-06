#!/usr/bin/env python3
"""
Automated Test Log Analysis System
===================================
Main pipeline orchestrator: generates logs, processes data, extracts errors,
detects patterns/anomalies, analyzes trends, generates visualizations & reports.

Usage:
    python main.py              # Generate new data + full analysis
    python main.py --skip-gen   # Re-analyze existing data/test_logs.csv
"""

import os
import sys
import time
import argparse
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

from tqdm import tqdm

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src import generate_logs, data_processing, error_extraction
from src import pattern_detection, anomaly_detection, trend_analysis
from src import dashboard, report_generator


# ── Pipeline step definitions ──────────────────────────────────────
# Each step: (label, function)  — built dynamically in main() based on args

def _step_generate(ctx):
    generate_logs.generate(ctx["data_path"])

def _step_process(ctx):
    df, report = data_processing.process(ctx["data_path"])
    ctx["df"] = df
    ctx["cleaning_report"] = report

def _step_extract(ctx):
    failures, err_summary, cat_summary = error_extraction.analyze(ctx["df"])
    ctx["failures"] = failures
    ctx["err_summary"] = err_summary
    ctx["cat_summary"] = cat_summary

def _step_patterns(ctx):
    ctx["patterns"] = pattern_detection.analyze(ctx["df"])

def _step_anomalies(ctx):
    ctx["anomaly_results"] = anomaly_detection.analyze(ctx["df"], ctx["failures"])

def _step_trends(ctx):
    ctx["trends"] = trend_analysis.analyze(ctx["df"])

def _step_dashboard(ctx):
    dashboard.generate_all(
        ctx["df"], ctx["err_summary"], ctx["cat_summary"],
        ctx["patterns"], ctx["anomaly_results"], ctx["trends"],
        ctx["plots_dir"],
    )

def _step_report(ctx):
    ctx["report_text"] = report_generator.generate_report(
        ctx["df"], ctx["cleaning_report"], ctx["failures"],
        ctx["err_summary"], ctx["cat_summary"], ctx["patterns"],
        ctx["anomaly_results"], ctx["trends"], ctx["report_path"],
    )


def main():
    parser = argparse.ArgumentParser(description="Automated Test Log Analysis System")
    parser.add_argument("--skip-gen", action="store_true",
                        help="Skip log generation, use existing data/test_logs.csv")
    args = parser.parse_args()

    ctx = {
        "data_path":   os.path.join(PROJECT_ROOT, "data", "test_logs.csv"),
        "plots_dir":   os.path.join(PROJECT_ROOT, "output", "plots"),
        "report_path": os.path.join(PROJECT_ROOT, "output", "reports", "analysis_report.txt"),
    }

    # Build step list
    steps = []
    if not args.skip_gen:
        steps.append(("Generating simulated test logs", _step_generate))
    else:
        if not os.path.exists(ctx["data_path"]):
            print(f"ERROR: {ctx['data_path']} not found. Run without --skip-gen first.")
            sys.exit(1)

    steps += [
        ("Processing & cleaning data",             _step_process),
        ("Extracting errors & classifying failures", _step_extract),
        ("Detecting patterns & correlations",       _step_patterns),
        ("Running anomaly detection",               _step_anomalies),
        ("Analyzing trends",                        _step_trends),
        ("Generating dashboard visualizations",     _step_dashboard),
        ("Generating summary report",               _step_report),
    ]

    # ── Run pipeline with live progress bar ────────────────────────
    print()
    print("=" * 60)
    print("  AUTOMATED TEST LOG ANALYSIS SYSTEM")
    print("=" * 60)
    print()

    t_start = time.time()

    progress = tqdm(
        steps,
        bar_format=(
            "  {l_bar}{bar}| {n_fmt}/{total_fmt} "
            "[{elapsed}<{remaining}]"
        ),
        ncols=70,
        colour="green",
    )

    # Suppress sub-module prints so only the progress bar is visible
    devnull = open(os.devnull, "w")
    for label, func in progress:
        progress.set_description(f"  {label:<45}")
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            func(ctx)
        finally:
            sys.stdout = old_stdout
    devnull.close()

    elapsed = time.time() - t_start

    # ── Print results ──────────────────────────────────────────────
    print()
    print("-" * 60)
    print("  RESULTS")
    print("-" * 60)

    df = ctx["df"]
    failures = ctx["failures"]
    err_summary = ctx["err_summary"]
    cat_summary = ctx["cat_summary"]
    patterns = ctx["patterns"]
    anomaly_results = ctx["anomaly_results"]

    total = len(df)
    fail_count = len(failures)
    fail_rate = fail_count / total * 100 if total else 0

    print(f"\n  Total Records  : {total:,}")
    print(f"  Unique Devices : {df['Device_ID'].nunique():,}")
    print(f"  Failure Rate   : {fail_rate:.2f}%")
    print(f"  Rows Cleaned   : {ctx['cleaning_report']['rows_removed']:,}")

    print(f"\n  Top Error Codes:")
    for _, row in err_summary.head(5).iterrows():
        print(f"    {row['Error_Code']:<10} {row['Test_Name']:<18} "
              f"{row['Failure_Category']:<20} Count: {row['Count']}")

    print(f"\n  Failure Categories:")
    for _, row in cat_summary.iterrows():
        pct = row["Count"] / fail_count * 100 if fail_count else 0
        print(f"    {row['Failure_Category']:<22} {row['Count']:>5} ({pct:.1f}%)")

    print(f"\n  Correlations:")
    for _, row in patterns["correlations"].iterrows():
        sig = "*" if row["Significant"] else " "
        print(f"    {row['Feature']:<18} r={row['Correlation']:+.4f}  "
              f"{row['Strength']:<8} {sig}")

    anom = anomaly_results["anomalous_batches"]
    if not anom.empty:
        print(f"\n  Anomalous Batches:")
        for _, row in anom.iterrows():
            print(f"    {row['Batch_ID']} — {row['Failure_Rate_Pct']:.2f}% "
                  f"(Z={row['Z_Score']:.2f})")

    outliers = anomaly_results["outlier_devices"]
    print(f"\n  Outlier Devices : {len(outliers)}")

    print(f"\n  Time Elapsed   : {elapsed:.1f}s")
    print(f"  Plots          : {ctx['plots_dir']}/")
    print(f"  Report         : {ctx['report_path']}")
    print()
    print("=" * 60)
    print("  ANALYSIS COMPLETE")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
