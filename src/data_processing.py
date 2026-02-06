"""
Data Processing & Cleaning Module
Reads raw test logs, cleans inconsistent data, standardizes units, removes corrupt entries.
"""

import pandas as pd
import numpy as np


# --- Valid ranges for each numeric column ---
VALID_RANGES = {
    "Voltage": (0.5, 2.0),
    "Temperature": (-40, 150),
    "Frequency": (0.5, 5.0),
    "Execution_Time": (0, 10_000),
}


def load_raw_data(csv_path):
    """Load the raw CSV into a DataFrame."""
    df = pd.read_csv(csv_path, dtype=str)
    print(f"Loaded {len(df):,} raw records from {csv_path}")
    return df


def clean_data(df):
    """Clean and standardize the raw test log DataFrame."""
    initial_count = len(df)
    report = {}

    # 1. Convert numeric columns (coerce invalid → NaN)
    numeric_cols = ["Voltage", "Temperature", "Frequency", "Execution_Time"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 2. Count and drop rows with NaN in critical columns
    missing_mask = df[numeric_cols].isna().any(axis=1)
    report["rows_with_missing_values"] = int(missing_mask.sum())
    df = df.dropna(subset=numeric_cols).copy()

    # 3. Remove out-of-range values
    out_of_range_total = 0
    for col, (lo, hi) in VALID_RANGES.items():
        bad = (df[col] < lo) | (df[col] > hi)
        out_of_range_total += int(bad.sum())
        df = df[~bad]
    report["rows_out_of_range"] = out_of_range_total

    # 4. Parse timestamp
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    bad_ts = df["Timestamp"].isna()
    report["rows_bad_timestamp"] = int(bad_ts.sum())
    df = df[~bad_ts].copy()

    # 5. Standardize Result column
    df["Result"] = df["Result"].str.strip().str.upper()
    valid_results = df["Result"].isin(["PASS", "FAIL"])
    report["rows_invalid_result"] = int((~valid_results).sum())
    df = df[valid_results].copy()

    # 6. Fill missing Error_Code for PASS results
    df["Error_Code"] = df["Error_Code"].fillna("")

    # 7. Sort by timestamp
    df = df.sort_values("Timestamp").reset_index(drop=True)

    report["rows_removed"] = initial_count - len(df)
    report["rows_remaining"] = len(df)

    print(f"Cleaning complete: {report['rows_removed']:,} rows removed, "
          f"{report['rows_remaining']:,} rows remaining")
    return df, report


def process(csv_path):
    """Full processing pipeline: load → clean → return."""
    df = load_raw_data(csv_path)
    df, report = clean_data(df)
    return df, report
