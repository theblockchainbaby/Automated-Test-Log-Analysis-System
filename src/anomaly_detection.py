"""
Anomaly Detection Module
Identifies unusual batches, error spikes, and outlier devices using statistical methods.
"""

import pandas as pd
import numpy as np


def zscore_anomalies(series, threshold=2.5):
    """Return indices where the value exceeds `threshold` standard deviations from mean."""
    mean = series.mean()
    std = series.std()
    if std == 0:
        return pd.Series(False, index=series.index)
    zscores = (series - mean) / std
    return zscores.abs() > threshold, zscores


def detect_anomalous_batches(df, z_threshold=2.5):
    """Find batches with anomalously high failure rates."""
    batch_stats = df.groupby("Batch_ID")["Result"].agg(
        Total="count",
        Failures=lambda x: (x == "FAIL").sum(),
    )
    batch_stats["Failure_Rate"] = batch_stats["Failures"] / batch_stats["Total"]

    is_anomaly, zscores = zscore_anomalies(batch_stats["Failure_Rate"], z_threshold)
    batch_stats["Z_Score"] = zscores.round(3)
    batch_stats["Is_Anomaly"] = is_anomaly

    anomalies = batch_stats[batch_stats["Is_Anomaly"]].copy()
    anomalies["Failure_Rate_Pct"] = (anomalies["Failure_Rate"] * 100).round(2)

    print(f"Batch anomaly detection: {len(anomalies)} anomalous batch(es) found")
    return batch_stats.reset_index(), anomalies.reset_index()


def detect_error_spikes(failures, window_days=7):
    """Detect sudden spikes in daily error counts using a moving average."""
    daily = failures.set_index("Timestamp").resample("D")["Error_Code"].count()
    daily = daily.rename("Daily_Failures")

    moving_avg = daily.rolling(window=window_days, min_periods=1).mean()
    moving_std = daily.rolling(window=window_days, min_periods=1).std().fillna(0)

    upper_bound = moving_avg + 2.5 * moving_std
    spikes = daily[daily > upper_bound]

    result = pd.DataFrame({
        "Daily_Failures": daily,
        "Moving_Avg": moving_avg.round(1),
        "Upper_Bound": upper_bound.round(1),
    })
    result["Is_Spike"] = daily > upper_bound

    spike_count = int(result["Is_Spike"].sum())
    print(f"Error spike detection: {spike_count} spike day(s) found")
    return result, spikes


def detect_outlier_devices(df, z_threshold=3.0):
    """Find devices with unusually high failure counts."""
    device_stats = df.groupby("Device_ID")["Result"].agg(
        Total="count",
        Failures=lambda x: (x == "FAIL").sum(),
    )
    device_stats["Failure_Rate"] = device_stats["Failures"] / device_stats["Total"]

    # Only consider devices with enough tests
    device_stats = device_stats[device_stats["Total"] >= 3]

    is_outlier, zscores = zscore_anomalies(device_stats["Failure_Rate"], z_threshold)
    device_stats["Z_Score"] = zscores.round(3)
    device_stats["Is_Outlier"] = is_outlier

    outliers = device_stats[device_stats["Is_Outlier"]].sort_values(
        "Failure_Rate", ascending=False
    )

    print(f"Outlier device detection: {len(outliers)} outlier device(s) found")
    return device_stats.reset_index(), outliers.reset_index()


def analyze(df, failures):
    """Run all anomaly detection analyses."""
    batch_stats, anomalous_batches = detect_anomalous_batches(df)
    spike_data, spikes = detect_error_spikes(failures)
    device_stats, outlier_devices = detect_outlier_devices(df)

    return {
        "batch_stats": batch_stats,
        "anomalous_batches": anomalous_batches,
        "spike_data": spike_data,
        "spikes": spikes,
        "device_stats": device_stats,
        "outlier_devices": outlier_devices,
    }
