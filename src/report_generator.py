"""
Summary Report Generator
Auto-generates a comprehensive engineering analysis report.
"""

import os
from datetime import datetime


def _section(title):
    width = 70
    return f"\n{'=' * width}\n  {title}\n{'=' * width}\n"


def _subsection(title):
    return f"\n--- {title} ---\n"


def generate_report(
    df, cleaning_report, failures, err_summary, cat_summary,
    patterns, anomalies, trends, output_path
):
    """Generate the full text summary report."""
    total_records = len(df)
    total_devices = df["Device_ID"].nunique()
    total_failures = len(failures)
    overall_fail_rate = (total_failures / total_records * 100) if total_records else 0

    lines = []
    lines.append("=" * 70)
    lines.append("  AUTOMATED TEST LOG ANALYSIS REPORT")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)

    # --- Executive Summary ---
    lines.append(_section("EXECUTIVE SUMMARY"))
    lines.append(f"  Total Test Records Analyzed : {total_records:,}")
    lines.append(f"  Unique Devices Tested       : {total_devices:,}")
    lines.append(f"  Total Failures              : {total_failures:,}")
    lines.append(f"  Overall Failure Rate         : {overall_fail_rate:.2f}%")
    lines.append(f"  Date Range                   : "
                 f"{df['Timestamp'].min().strftime('%Y-%m-%d')} to "
                 f"{df['Timestamp'].max().strftime('%Y-%m-%d')}")
    lines.append(f"  Unique Test Types            : {df['Test_Name'].nunique()}")
    lines.append(f"  Unique Batches               : {df['Batch_ID'].nunique()}")

    # --- Data Cleaning Summary ---
    lines.append(_section("DATA QUALITY"))
    lines.append(f"  Rows with missing values     : {cleaning_report.get('rows_with_missing_values', 0):,}")
    lines.append(f"  Rows out of valid range      : {cleaning_report.get('rows_out_of_range', 0):,}")
    lines.append(f"  Rows with bad timestamps     : {cleaning_report.get('rows_bad_timestamp', 0):,}")
    lines.append(f"  Rows with invalid results    : {cleaning_report.get('rows_invalid_result', 0):,}")
    lines.append(f"  Total rows removed           : {cleaning_report.get('rows_removed', 0):,}")
    lines.append(f"  Clean rows remaining         : {cleaning_report.get('rows_remaining', 0):,}")

    # --- Top Error Codes ---
    lines.append(_section("TOP FAILURE ERROR CODES"))
    if not err_summary.empty:
        top = err_summary.head(10)
        lines.append(f"  {'Error Code':<12} {'Test':<18} {'Category':<20} {'Count':>6}  "
                      f"{'Avg Temp':>8}  {'Avg Volt':>8}")
        lines.append("  " + "-" * 80)
        for _, row in top.iterrows():
            lines.append(
                f"  {row['Error_Code']:<12} {row['Test_Name']:<18} "
                f"{row['Failure_Category']:<20} {row['Count']:>6}  "
                f"{row['Avg_Temperature']:>7.1f}°C  {row['Avg_Voltage']:>7.3f}V"
            )

    # --- Failure Categories ---
    lines.append(_section("FAILURE CATEGORY BREAKDOWN"))
    if not cat_summary.empty:
        for _, row in cat_summary.iterrows():
            pct = row["Count"] / total_failures * 100 if total_failures else 0
            lines.append(
                f"  {row['Failure_Category']:<22} : {row['Count']:>5} failures "
                f"({pct:.1f}%)  |  Avg Temp: {row['Avg_Temperature']:.1f}°C  "
                f"Avg Voltage: {row['Avg_Voltage']:.3f}V"
            )

    # --- Highest Failure Test ---
    lines.append(_section("HIGHEST FAILURE TEST"))
    test_rates = patterns["failure_vs_test"]
    if not test_rates.empty:
        worst_test = test_rates.sort_values("Failure_Rate_Pct", ascending=False).iloc[0]
        lines.append(f"  Test Name    : {worst_test['Test_Name']}")
        lines.append(f"  Failure Rate : {worst_test['Failure_Rate_Pct']:.2f}%")
        lines.append(f"  Total Tests  : {worst_test['Total']:,}")
        lines.append(f"  Total Fails  : {worst_test['Failures']:,}")

    # --- Temperature Correlation ---
    lines.append(_section("TEMPERATURE CORRELATION"))
    corr_df = patterns["correlations"]
    if not corr_df.empty:
        temp_corr = corr_df[corr_df["Feature"] == "Temperature"]
        if not temp_corr.empty:
            tc = temp_corr.iloc[0]
            lines.append(f"  Correlation Coefficient : {tc['Correlation']:.4f}")
            lines.append(f"  Strength                : {tc['Strength']}")
            lines.append(f"  Statistically Significant: {'Yes' if tc['Significant'] else 'No'}")

    temp_data = patterns["failure_vs_temperature"]
    if not temp_data.empty:
        high_temp = temp_data[temp_data["Failure_Rate_Pct"] > overall_fail_rate * 1.5]
        if not high_temp.empty:
            lines.append(f"\n  Temperature ranges with elevated failure rates:")
            for _, row in high_temp.iterrows():
                lines.append(f"    {row['Temperature_bin']} : {row['Failure_Rate_Pct']:.2f}%")

    # --- Anomalous Batches ---
    lines.append(_section("ANOMALOUS BATCHES"))
    anom_batches = anomalies["anomalous_batches"]
    if not anom_batches.empty:
        for _, row in anom_batches.iterrows():
            lines.append(
                f"  {row['Batch_ID']} — Failure Rate: {row['Failure_Rate_Pct']:.2f}%  "
                f"(Z-Score: {row['Z_Score']:.2f})"
            )
    else:
        lines.append("  No anomalous batches detected.")

    # --- Error Spikes ---
    lines.append(_section("ERROR SPIKES"))
    spike_data = anomalies["spike_data"]
    spike_days = spike_data[spike_data["Is_Spike"]]
    lines.append(f"  Spike days detected: {len(spike_days)}")
    if not spike_days.empty:
        for date, row in spike_days.head(5).iterrows():
            lines.append(
                f"    {date.strftime('%Y-%m-%d')} : {int(row['Daily_Failures'])} failures "
                f"(bound: {row['Upper_Bound']:.0f})"
            )

    # --- Outlier Devices ---
    lines.append(_section("OUTLIER DEVICES"))
    outliers = anomalies["outlier_devices"]
    lines.append(f"  Outlier devices detected: {len(outliers)}")
    if not outliers.empty:
        for _, row in outliers.head(10).iterrows():
            lines.append(
                f"    {row['Device_ID']} — Failures: {row['Failures']}/{row['Total']} "
                f"({row['Failure_Rate'] * 100:.1f}%)  Z-Score: {row['Z_Score']:.2f}"
            )

    # --- Feature Correlations ---
    lines.append(_section("FEATURE CORRELATIONS WITH FAILURE"))
    if not corr_df.empty:
        lines.append(f"  {'Feature':<18} {'Correlation':>12} {'Strength':<12} {'Significant'}")
        lines.append("  " + "-" * 55)
        for _, row in corr_df.iterrows():
            lines.append(
                f"  {row['Feature']:<18} {row['Correlation']:>12.4f} "
                f"{row['Strength']:<12} {'Yes' if row['Significant'] else 'No'}"
            )

    # --- Batch Comparison ---
    lines.append(_section("BATCH COMPARISON"))
    batch_comp = trends["batch_comparison"]
    if not batch_comp.empty:
        lines.append(f"  {'Batch':<12} {'Total':>7} {'Failures':>9} {'Rate':>8}")
        lines.append("  " + "-" * 40)
        for batch_id, row in batch_comp.iterrows():
            marker = " <<<" if row["Failure_Rate_Pct"] > overall_fail_rate * 2 else ""
            lines.append(
                f"  {batch_id:<12} {row['Total']:>7,} {row['Failures']:>9,} "
                f"{row['Failure_Rate_Pct']:>7.2f}%{marker}"
            )

    # --- Key Findings ---
    lines.append(_section("KEY FINDINGS & RECOMMENDATIONS"))
    lines.append("  1. " + _find_highest_failure_test(patterns))
    lines.append("  2. " + _find_temp_insight(patterns, overall_fail_rate))
    lines.append("  3. " + _find_batch_insight(anomalies))
    lines.append("  4. " + _find_correlation_insight(patterns))
    lines.append("")
    lines.append("=" * 70)
    lines.append("  END OF REPORT")
    lines.append("=" * 70)

    report_text = "\n".join(lines)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report_text)

    print(f"\nReport saved → {output_path}")
    return report_text


def _find_highest_failure_test(patterns):
    test_rates = patterns["failure_vs_test"]
    if test_rates.empty:
        return "No test data available."
    worst = test_rates.sort_values("Failure_Rate_Pct", ascending=False).iloc[0]
    return (f"Highest failure test is '{worst['Test_Name']}' at "
            f"{worst['Failure_Rate_Pct']:.2f}% — recommend targeted root cause analysis.")


def _find_temp_insight(patterns, overall_rate):
    temp = patterns["failure_vs_temperature"]
    if temp.empty:
        return "No temperature data available."
    high_temp = temp[temp["Failure_Rate_Pct"] > overall_rate * 2]
    if high_temp.empty:
        return "No strong temperature correlation observed."
    return (f"Failure rate increases significantly above 80°C — "
            f"recommend thermal mitigation review for high-temperature test conditions.")


def _find_batch_insight(anomalies):
    ab = anomalies["anomalous_batches"]
    if ab.empty:
        return "No anomalous batches detected — batch quality is consistent."
    batch_names = ", ".join(ab["Batch_ID"].tolist())
    return (f"Anomalous batch(es) detected: {batch_names} — "
            f"recommend process investigation for these production lots.")


def _find_correlation_insight(patterns):
    corr = patterns["correlations"]
    if corr.empty:
        return "No correlation data available."
    strong = corr[corr["Strength"] == "Strong"]
    if strong.empty:
        return "No strong feature correlations found with failure outcome."
    feats = ", ".join(strong["Feature"].tolist())
    return f"Strong correlation with failure: {feats} — prioritize monitoring these parameters."
