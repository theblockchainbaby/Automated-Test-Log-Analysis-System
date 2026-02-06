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

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src import generate_logs, data_processing, error_extraction
from src import pattern_detection, anomaly_detection, trend_analysis
from src import dashboard, report_generator


def banner(text):
    print(f"\n{'#' * 60}")
    print(f"  {text}")
    print(f"{'#' * 60}")


def main():
    parser = argparse.ArgumentParser(description="Automated Test Log Analysis System")
    parser.add_argument("--skip-gen", action="store_true",
                        help="Skip log generation, use existing data/test_logs.csv")
    args = parser.parse_args()

    data_path = os.path.join(PROJECT_ROOT, "data", "test_logs.csv")
    plots_dir = os.path.join(PROJECT_ROOT, "output", "plots")
    report_path = os.path.join(PROJECT_ROOT, "output", "reports", "analysis_report.txt")

    t_start = time.time()

    # --- Step 1: Generate test logs ---
    if not args.skip_gen:
        banner("STEP 1: Generating Simulated Test Logs")
        generate_logs.generate(data_path)
    else:
        banner("STEP 1: Skipping Generation (using existing data)")
        if not os.path.exists(data_path):
            print(f"ERROR: {data_path} not found. Run without --skip-gen first.")
            sys.exit(1)

    # --- Step 2: Data processing & cleaning ---
    banner("STEP 2: Data Processing & Cleaning")
    df, cleaning_report = data_processing.process(data_path)

    # --- Step 3: Error extraction & classification ---
    banner("STEP 3: Error Extraction & Failure Classification")
    failures, err_summary, cat_summary = error_extraction.analyze(df)
    print("\nError Code Summary (top 10):")
    print(err_summary.head(10).to_string(index=False))
    print("\nFailure Category Summary:")
    print(cat_summary.to_string(index=False))

    # --- Step 4: Pattern detection ---
    banner("STEP 4: Pattern Detection & Correlation Analysis")
    patterns = pattern_detection.analyze(df)
    print("\nCorrelations with Failure:")
    print(patterns["correlations"].to_string(index=False))

    # --- Step 5: Anomaly detection ---
    banner("STEP 5: Anomaly Detection")
    anomaly_results = anomaly_detection.analyze(df, failures)

    # --- Step 6: Trend analysis ---
    banner("STEP 6: Trend Analysis")
    trends = trend_analysis.analyze(df)

    # --- Step 7: Dashboard ---
    banner("STEP 7: Generating Dashboard Visualizations")
    dashboard.generate_all(
        df, err_summary, cat_summary, patterns, anomaly_results, trends, plots_dir
    )

    # --- Step 8: Report ---
    banner("STEP 8: Generating Summary Report")
    report_text = report_generator.generate_report(
        df, cleaning_report, failures, err_summary, cat_summary,
        patterns, anomaly_results, trends, report_path
    )

    elapsed = time.time() - t_start
    banner("ANALYSIS COMPLETE")
    print(f"\n  Time elapsed : {elapsed:.1f}s")
    print(f"  Plots        : {plots_dir}/")
    print(f"  Report       : {report_path}")
    print(f"\n  Summary:")
    # Print just the executive summary section
    for line in report_text.split("\n"):
        if "EXECUTIVE SUMMARY" in line:
            printing = True
        if "DATA QUALITY" in line:
            break
        if "printing" in dir() and printing:
            print(f"  {line}")
    print()


if __name__ == "__main__":
    main()
