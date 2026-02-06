"""
Error Extraction & Failure Classification Module
Filters failures, counts error types, classifies failure categories.
"""

import pandas as pd


# --- Error code → failure category mapping ---
FAILURE_CATEGORIES = {
    # Timing failures
    "ERR_T01": "Timing Failure",
    "ERR_T02": "Timing Failure",
    "ERR_T03": "Timing Failure",
    # Overcurrent / voltage
    "ERR_V01": "Overcurrent",
    "ERR_V02": "Overcurrent",
    # Burn-in / thermal
    "ERR_B01": "Thermal Issue",
    "ERR_B02": "Thermal Issue",
    "ERR_B03": "Data Corruption",
    # Stress
    "ERR_S01": "Thermal Issue",
    "ERR_S02": "Data Corruption",
    # Data integrity
    "ERR_D01": "Data Corruption",
    "ERR_D02": "Data Corruption",
    # Frequency
    "ERR_F01": "Timing Failure",
    "ERR_F02": "Overcurrent",
    # Leakage
    "ERR_L01": "Overcurrent",
    "ERR_L02": "Thermal Issue",
    # Power cycle
    "ERR_P01": "Data Corruption",
    "ERR_P02": "Overcurrent",
}


def extract_failures(df):
    """Filter the DataFrame to only FAIL rows."""
    failures = df[df["Result"] == "FAIL"].copy()
    print(f"Extracted {len(failures):,} failure records out of {len(df):,} total")
    return failures


def classify_failures(failures):
    """Add a Failure_Category column based on error code mapping."""
    failures = failures.copy()
    failures["Failure_Category"] = failures["Error_Code"].map(FAILURE_CATEGORIES)
    failures["Failure_Category"] = failures["Failure_Category"].fillna("Unknown")
    return failures


def error_summary(failures):
    """Produce a summary table: Error_Code × count, avg temp, avg voltage, test type."""
    if failures.empty:
        return pd.DataFrame()

    summary = (
        failures.groupby(["Error_Code", "Test_Name", "Failure_Category"])
        .agg(
            Count=("Error_Code", "size"),
            Avg_Temperature=("Temperature", "mean"),
            Avg_Voltage=("Voltage", "mean"),
            Avg_Execution_Time=("Execution_Time", "mean"),
        )
        .reset_index()
        .sort_values("Count", ascending=False)
    )
    summary["Avg_Temperature"] = summary["Avg_Temperature"].round(1)
    summary["Avg_Voltage"] = summary["Avg_Voltage"].round(3)
    summary["Avg_Execution_Time"] = summary["Avg_Execution_Time"].round(1)
    return summary


def category_summary(failures):
    """Summarize failure counts by category."""
    if failures.empty:
        return pd.DataFrame()

    return (
        failures.groupby("Failure_Category")
        .agg(
            Count=("Failure_Category", "size"),
            Unique_Error_Codes=("Error_Code", "nunique"),
            Avg_Temperature=("Temperature", lambda x: round(x.mean(), 1)),
            Avg_Voltage=("Voltage", lambda x: round(x.mean(), 3)),
        )
        .reset_index()
        .sort_values("Count", ascending=False)
    )


def analyze(df):
    """Full error extraction pipeline."""
    failures = extract_failures(df)
    failures = classify_failures(failures)
    err_summary = error_summary(failures)
    cat_summary = category_summary(failures)
    return failures, err_summary, cat_summary
