"""
Trend Analysis Module
Tracks failure rates over time — daily, rolling averages, and batch comparisons.
"""

import pandas as pd
import numpy as np


def daily_failure_rate(df):
    """Compute daily failure count and failure percentage."""
    df_work = df.copy()
    df_work["Date"] = df_work["Timestamp"].dt.date

    daily = df_work.groupby("Date")["Result"].agg(
        Total="count",
        Failures=lambda x: (x == "FAIL").sum(),
    )
    daily["Failure_Rate_Pct"] = (daily["Failures"] / daily["Total"] * 100).round(2)
    daily.index = pd.to_datetime(daily.index)
    return daily


def rolling_failure_rate(daily_df, window=7):
    """Compute rolling average failure rate."""
    rolling = daily_df["Failure_Rate_Pct"].rolling(window=window, min_periods=1).mean()
    return rolling.round(2).rename(f"Rolling_{window}d_Pct")


def weekly_failure_rate(df):
    """Compute weekly failure rate."""
    df_work = df.copy()
    df_work["Week"] = df_work["Timestamp"].dt.isocalendar().week.astype(int)
    df_work["Year"] = df_work["Timestamp"].dt.isocalendar().year.astype(int)

    weekly = df_work.groupby(["Year", "Week"])["Result"].agg(
        Total="count",
        Failures=lambda x: (x == "FAIL").sum(),
    )
    weekly["Failure_Rate_Pct"] = (weekly["Failures"] / weekly["Total"] * 100).round(2)
    return weekly


def batch_comparison(df):
    """Compare failure rates across batches, ordered by batch ID."""
    batch = df.groupby("Batch_ID")["Result"].agg(
        Total="count",
        Failures=lambda x: (x == "FAIL").sum(),
    )
    batch["Failure_Rate_Pct"] = (batch["Failures"] / batch["Total"] * 100).round(2)
    return batch.sort_index()


def failure_trend_by_test(df):
    """Compute weekly failure rate per test type."""
    df_work = df.copy()
    df_work["Week"] = df_work["Timestamp"].dt.isocalendar().week.astype(int)

    result = []
    for test in df_work["Test_Name"].unique():
        test_df = df_work[df_work["Test_Name"] == test]
        weekly = test_df.groupby("Week")["Result"].agg(
            Total="count",
            Failures=lambda x: (x == "FAIL").sum(),
        )
        weekly["Failure_Rate_Pct"] = (weekly["Failures"] / weekly["Total"] * 100).round(2)
        weekly["Test_Name"] = test
        result.append(weekly.reset_index())

    return pd.concat(result, ignore_index=True) if result else pd.DataFrame()


def analyze(df):
    """Run all trend analyses."""
    daily = daily_failure_rate(df)
    rolling_7 = rolling_failure_rate(daily, window=7)
    rolling_14 = rolling_failure_rate(daily, window=14)
    weekly = weekly_failure_rate(df)
    batch = batch_comparison(df)
    by_test = failure_trend_by_test(df)

    trends = {
        "daily": daily,
        "rolling_7d": rolling_7,
        "rolling_14d": rolling_14,
        "weekly": weekly,
        "batch_comparison": batch,
        "by_test": by_test,
    }
    print("Trend analysis complete")
    return trends
