"""
Pattern Detection & Correlation Analysis Module
Discovers relationships between failures and environmental conditions.
"""

import pandas as pd
import numpy as np
from scipy import stats


def failure_rate_by_column(df, column, bins=None):
    """Compute failure rate grouped by a column (optionally binned)."""
    work = df.copy()
    if bins is not None:
        work[column + "_bin"] = pd.cut(work[column], bins=bins)
        group_col = column + "_bin"
    else:
        group_col = column

    grouped = work.groupby(group_col)["Result"].agg(
        Total="count",
        Failures=lambda x: (x == "FAIL").sum(),
    )
    grouped["Failure_Rate_Pct"] = (grouped["Failures"] / grouped["Total"] * 100).round(2)
    return grouped.reset_index()


def failure_vs_temperature(df):
    """Failure rate across temperature bins."""
    bins = list(range(20, 130, 10))
    return failure_rate_by_column(df, "Temperature", bins=bins)


def failure_vs_voltage(df):
    """Failure rate across voltage bins."""
    bins = [round(0.7 + i * 0.1, 1) for i in range(9)]
    return failure_rate_by_column(df, "Voltage", bins=bins)


def failure_vs_batch(df):
    """Failure rate per batch."""
    return failure_rate_by_column(df, "Batch_ID")


def failure_vs_test(df):
    """Failure rate per test type."""
    return failure_rate_by_column(df, "Test_Name")


def failure_vs_duration(df):
    """Failure rate across execution time bins."""
    bins = list(range(0, 400, 50))
    return failure_rate_by_column(df, "Execution_Time", bins=bins)


def compute_correlations(df):
    """Point-biserial correlation between numeric features and FAIL outcome."""
    df_work = df.copy()
    df_work["Is_Fail"] = (df_work["Result"] == "FAIL").astype(int)

    numeric_features = ["Temperature", "Voltage", "Frequency", "Execution_Time"]
    results = []

    for feat in numeric_features:
        valid = df_work[[feat, "Is_Fail"]].dropna()
        if len(valid) < 10:
            continue
        corr, pvalue = stats.pointbiserialr(valid["Is_Fail"], valid[feat])
        results.append({
            "Feature": feat,
            "Correlation": round(corr, 4),
            "P_Value": pvalue,
            "Significant": pvalue < 0.05,
            "Strength": (
                "Strong" if abs(corr) > 0.3
                else "Moderate" if abs(corr) > 0.1
                else "Weak"
            ),
        })

    return pd.DataFrame(results)


def analyze(df):
    """Run all pattern detection analyses."""
    patterns = {
        "failure_vs_temperature": failure_vs_temperature(df),
        "failure_vs_voltage": failure_vs_voltage(df),
        "failure_vs_batch": failure_vs_batch(df),
        "failure_vs_test": failure_vs_test(df),
        "failure_vs_duration": failure_vs_duration(df),
        "correlations": compute_correlations(df),
    }
    print("Pattern detection complete: analyzed 5 dimensions + correlations")
    return patterns
