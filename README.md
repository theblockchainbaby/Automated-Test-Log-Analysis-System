# Automated Test Log Analysis System

An end-to-end pipeline that processes raw semiconductor test output, classifies failure modes, detects anomalies, and generates engineering reports — simulating real-world hardware validation workflows.

## Problem

In semiconductor and hardware companies, every device goes through electrical tests, stress tests, performance validation, and burn-in testing. These produce massive log files. Engineers must quickly determine:
- **What failed?**
- **How often?**
- **Under what conditions?**
- **Is the failure rate rising?**

This system automates that entire workflow.

## Architecture

```
Raw Test Logs → Data Cleaning → Error Extraction → Pattern Detection
                                                  → Anomaly Detection
                                                  → Trend Analysis
                                                  → Dashboard Plots
                                                  → Summary Report
```

## Features

| Module | Description |
|--------|-------------|
| **Log Generator** | Simulates 55,000+ test records across 10,000 devices, 25 batches, 8 test types with realistic failure patterns |
| **Data Processing** | Cleans missing values, out-of-range readings, corrupt entries, and standardizes units |
| **Error Extraction** | Filters failures, maps error codes to 4 categories (Timing, Overcurrent, Data Corruption, Thermal) |
| **Pattern Detection** | Point-biserial correlation between environmental conditions (temperature, voltage, frequency) and failure outcome |
| **Anomaly Detection** | Z-score analysis to flag anomalous batches, error spikes (moving average), and outlier devices |
| **Trend Analysis** | Daily/weekly failure rates, 7-day and 14-day rolling averages, batch-over-batch comparison |
| **Dashboard** | 10 publication-quality plots (heatmaps, bar charts, pie charts, time series, box plots) |
| **Report Generator** | Auto-generated engineering summary with key findings and recommendations |

## Sample Results

| Metric | Value |
|--------|-------|
| Total Records Analyzed | 54,681 |
| Unique Devices | 10,000 |
| Overall Failure Rate | 2.96% |
| Highest Failure Test | Timing_Check (4.72%) |
| Anomalous Batch | Batch_17 (8.70%, Z-Score: 4.55) |
| Temperature Effect | Failure rate jumps to ~8% above 100°C |
| Outlier Devices Detected | 216 |

## Visualizations

The system generates 10 plots:

1. **Failure Heatmap** — Test Type × Batch failure rates
2. **Error Frequency** — Top error codes ranked by count
3. **Failure Categories** — Distribution pie chart
4. **Failure vs Temperature** — Thermal correlation
5. **Failure vs Voltage** — Voltage edge effects
6. **Batch Failure Rate** — Anomalous batches highlighted
7. **Daily Trend** — With rolling averages
8. **Error Spike Timeline** — Moving average bounds
9. **Feature Correlations** — Correlation coefficients
10. **Test Distribution** — Box plot per test type

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run full pipeline (generate data + analyze)
python main.py

# Re-analyze existing data
python main.py --skip-gen
```

Output is saved to:
- `output/plots/` — 10 PNG visualizations
- `output/reports/analysis_report.txt` — Full engineering report

## Tech Stack

- **Python 3.9+**
- **pandas** — Data manipulation and cleaning
- **NumPy** — Numerical computation
- **SciPy** — Statistical correlation analysis
- **matplotlib / seaborn** — Visualization
- **CSV** — Log generation and I/O

## Skills Demonstrated

- Data cleaning and preprocessing of messy engineering data
- Statistical analysis (Z-scores, point-biserial correlation, moving averages)
- Failure mode classification and root cause pattern discovery
- Anomaly detection across production batches
- Automated report generation for engineering teams
- Publication-quality data visualization

## Relevance

This project simulates daily workflows for:
- **Validation Engineers** — Interpreting test results
- **Test Engineers** — Failure categorization
- **Yield Engineers** — Statistical yield analysis
- **Reliability Engineers** — Trend monitoring and anomaly detection
