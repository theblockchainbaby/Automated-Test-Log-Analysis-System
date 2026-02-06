"""
Dashboard & Visualization Module
Generates publication-quality plots for failure analysis.
"""

import os
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import pandas as pd


# --- Style setup ---
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
COLORS = sns.color_palette("Set2", 10)
FIG_DPI = 150


def _save(fig, output_dir, name):
    path = os.path.join(output_dir, f"{name}.png")
    fig.savefig(path, dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Saved plot → {path}")


def plot_failure_heatmap(df, output_dir):
    """Heatmap of failure rate: Test_Name × Batch_ID."""
    pivot = df.pivot_table(
        index="Test_Name",
        columns="Batch_ID",
        values="Result",
        aggfunc=lambda x: (x == "FAIL").mean() * 100,
    )
    fig, ax = plt.subplots(figsize=(16, 6))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax,
                linewidths=0.5, cbar_kws={"label": "Failure Rate (%)"})
    ax.set_title("Failure Rate Heatmap: Test Type vs Batch", fontsize=14, fontweight="bold")
    ax.set_xlabel("Batch ID")
    ax.set_ylabel("Test Name")
    plt.xticks(rotation=45, ha="right")
    _save(fig, output_dir, "01_failure_heatmap")


def plot_error_frequency(err_summary, output_dir):
    """Bar chart of error code frequency."""
    if err_summary.empty:
        return
    top = err_summary.head(15)
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(
        top["Error_Code"] + " (" + top["Test_Name"] + ")",
        top["Count"],
        color=COLORS[0],
        edgecolor="gray",
    )
    ax.set_xlabel("Failure Count")
    ax.set_title("Top Error Codes by Frequency", fontsize=14, fontweight="bold")
    ax.invert_yaxis()
    for bar, count in zip(bars, top["Count"]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                str(count), va="center", fontsize=9)
    _save(fig, output_dir, "02_error_frequency")


def plot_failure_category_pie(cat_summary, output_dir):
    """Pie chart of failure categories."""
    if cat_summary.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        cat_summary["Count"],
        labels=cat_summary["Failure_Category"],
        autopct="%1.1f%%",
        colors=COLORS[:len(cat_summary)],
        startangle=140,
        pctdistance=0.85,
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
    ax.set_title("Failure Distribution by Category", fontsize=14, fontweight="bold")
    _save(fig, output_dir, "03_failure_categories")


def plot_failure_vs_temperature(temp_data, output_dir):
    """Bar chart: failure rate vs temperature bins."""
    if temp_data.empty:
        return
    fig, ax = plt.subplots(figsize=(12, 5))
    x_labels = temp_data["Temperature_bin"].astype(str)
    ax.bar(x_labels, temp_data["Failure_Rate_Pct"], color=COLORS[1], edgecolor="gray")
    ax.set_xlabel("Temperature Range (°C)")
    ax.set_ylabel("Failure Rate (%)")
    ax.set_title("Failure Rate vs Temperature", fontsize=14, fontweight="bold")
    plt.xticks(rotation=45, ha="right")
    ax.axhline(y=temp_data["Failure_Rate_Pct"].mean(), color="red",
               linestyle="--", label="Average")
    ax.legend()
    _save(fig, output_dir, "04_failure_vs_temperature")


def plot_failure_vs_voltage(volt_data, output_dir):
    """Bar chart: failure rate vs voltage bins."""
    if volt_data.empty:
        return
    fig, ax = plt.subplots(figsize=(12, 5))
    x_labels = volt_data["Voltage_bin"].astype(str)
    ax.bar(x_labels, volt_data["Failure_Rate_Pct"], color=COLORS[2], edgecolor="gray")
    ax.set_xlabel("Voltage Range (V)")
    ax.set_ylabel("Failure Rate (%)")
    ax.set_title("Failure Rate vs Voltage", fontsize=14, fontweight="bold")
    plt.xticks(rotation=45, ha="right")
    _save(fig, output_dir, "05_failure_vs_voltage")


def plot_batch_failure_rate(batch_data, output_dir):
    """Bar chart: failure rate per batch with anomaly highlighting."""
    if batch_data.empty:
        return
    fig, ax = plt.subplots(figsize=(14, 5))
    mean_rate = batch_data["Failure_Rate_Pct"].mean()
    colors_list = [
        "tomato" if r > mean_rate * 2 else COLORS[3]
        for r in batch_data["Failure_Rate_Pct"]
    ]
    ax.bar(batch_data["Batch_ID"], batch_data["Failure_Rate_Pct"],
           color=colors_list, edgecolor="gray")
    ax.axhline(y=mean_rate, color="red", linestyle="--",
               label=f"Average ({mean_rate:.1f}%)")
    ax.set_xlabel("Batch ID")
    ax.set_ylabel("Failure Rate (%)")
    ax.set_title("Failure Rate by Batch (anomalies in red)", fontsize=14, fontweight="bold")
    ax.legend()
    plt.xticks(rotation=45, ha="right")
    _save(fig, output_dir, "06_batch_failure_rate")


def plot_daily_trend(daily, rolling_7, rolling_14, output_dir):
    """Line chart: daily failure rate with rolling averages."""
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(daily.index, daily["Failure_Rate_Pct"], alpha=0.3, color="gray",
            label="Daily", linewidth=0.8)
    ax.plot(rolling_7.index, rolling_7, color=COLORS[4],
            label="7-day Rolling Avg", linewidth=2)
    ax.plot(rolling_14.index, rolling_14, color=COLORS[5],
            label="14-day Rolling Avg", linewidth=2)
    ax.set_xlabel("Date")
    ax.set_ylabel("Failure Rate (%)")
    ax.set_title("Failure Rate Trend Over Time", fontsize=14, fontweight="bold")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45, ha="right")
    _save(fig, output_dir, "07_daily_trend")


def plot_error_spike_timeline(spike_data, output_dir):
    """Timeline showing daily failure counts with spike markers."""
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.fill_between(spike_data.index, spike_data["Daily_Failures"],
                    alpha=0.3, color=COLORS[0])
    ax.plot(spike_data.index, spike_data["Daily_Failures"],
            color=COLORS[0], linewidth=1, label="Daily Failures")
    ax.plot(spike_data.index, spike_data["Moving_Avg"],
            color="blue", linestyle="--", linewidth=1.5, label="Moving Avg")
    ax.plot(spike_data.index, spike_data["Upper_Bound"],
            color="red", linestyle=":", linewidth=1, label="Upper Bound")
    spikes = spike_data[spike_data["Is_Spike"]]
    if not spikes.empty:
        ax.scatter(spikes.index, spikes["Daily_Failures"],
                   color="red", s=80, zorder=5, label="Spikes")
    ax.set_xlabel("Date")
    ax.set_ylabel("Failure Count")
    ax.set_title("Daily Failure Count with Spike Detection", fontsize=14, fontweight="bold")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.xticks(rotation=45, ha="right")
    _save(fig, output_dir, "08_error_spike_timeline")


def plot_correlation_bars(corr_df, output_dir):
    """Horizontal bar chart of feature correlations with failure."""
    if corr_df.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 4))
    bar_colors = ["tomato" if c > 0 else "steelblue" for c in corr_df["Correlation"]]
    ax.barh(corr_df["Feature"], corr_df["Correlation"], color=bar_colors, edgecolor="gray")
    ax.set_xlabel("Point-Biserial Correlation with Failure")
    ax.set_title("Feature Correlation with Test Failure", fontsize=14, fontweight="bold")
    ax.axvline(x=0, color="black", linewidth=0.8)
    for i, (val, sig) in enumerate(zip(corr_df["Correlation"], corr_df["Significant"])):
        marker = " *" if sig else ""
        ax.text(val + 0.005 if val > 0 else val - 0.005,
                i, f"{val:.3f}{marker}", va="center",
                ha="left" if val > 0 else "right", fontsize=9)
    _save(fig, output_dir, "09_correlations")


def plot_test_failure_distribution(df, output_dir):
    """Box plot of failure rates by test type."""
    device_test = df.groupby(["Device_ID", "Test_Name"])["Result"].agg(
        lambda x: (x == "FAIL").mean() * 100
    ).reset_index()
    device_test.columns = ["Device_ID", "Test_Name", "Failure_Rate_Pct"]

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=device_test, x="Test_Name", y="Failure_Rate_Pct", ax=ax,
                palette="Set2", fliersize=3)
    ax.set_xlabel("Test Name")
    ax.set_ylabel("Failure Rate (%)")
    ax.set_title("Failure Rate Distribution by Test Type", fontsize=14, fontweight="bold")
    plt.xticks(rotation=45, ha="right")
    _save(fig, output_dir, "10_test_failure_distribution")


def generate_all(df, err_summary, cat_summary, patterns, anomalies, trends, output_dir):
    """Generate all dashboard plots."""
    os.makedirs(output_dir, exist_ok=True)
    print("\nGenerating dashboard plots...")

    plot_failure_heatmap(df, output_dir)
    plot_error_frequency(err_summary, output_dir)
    plot_failure_category_pie(cat_summary, output_dir)
    plot_failure_vs_temperature(patterns["failure_vs_temperature"], output_dir)
    plot_failure_vs_voltage(patterns["failure_vs_voltage"], output_dir)
    plot_batch_failure_rate(patterns["failure_vs_batch"], output_dir)
    plot_daily_trend(trends["daily"], trends["rolling_7d"], trends["rolling_14d"], output_dir)
    plot_error_spike_timeline(anomalies["spike_data"], output_dir)
    plot_correlation_bars(patterns["correlations"], output_dir)
    plot_test_failure_distribution(df, output_dir)

    print(f"All 10 plots saved to {output_dir}/")
