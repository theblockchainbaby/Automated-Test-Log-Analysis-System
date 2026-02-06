"""
Simulated Test Log Generator
Generates realistic semiconductor test log data with controlled failure patterns.
"""

import csv
import random
import os
from datetime import datetime, timedelta

# --- Configuration ---
NUM_DEVICES = 10_000
NUM_BATCHES = 25
DEVICES_PER_BATCH = NUM_DEVICES // NUM_BATCHES
BASE_FAILURE_RATE = 0.018  # 1.8% overall target

TEST_TYPES = [
    "Timing_Check", "Voltage_Sweep", "Burn_In", "Stress_Test",
    "Data_Integrity", "Frequency_Scan", "Leakage_Test", "Power_Cycle",
]

ERROR_CODES = {
    "Timing_Check":    ["ERR_T01", "ERR_T02", "ERR_T03"],
    "Voltage_Sweep":   ["ERR_V01", "ERR_V02"],
    "Burn_In":         ["ERR_B01", "ERR_B02", "ERR_B03"],
    "Stress_Test":     ["ERR_S01", "ERR_S02"],
    "Data_Integrity":  ["ERR_D01", "ERR_D02"],
    "Frequency_Scan":  ["ERR_F01", "ERR_F02"],
    "Leakage_Test":    ["ERR_L01", "ERR_L02"],
    "Power_Cycle":     ["ERR_P01", "ERR_P02"],
}

ANOMALOUS_BATCH = 17  # This batch will have ~4x failure rate
HIGH_TEMP_THRESHOLD = 80  # Failures increase above this


def _failure_probability(batch_id, temperature, voltage, test_name):
    """Compute failure probability based on environmental conditions."""
    prob = BASE_FAILURE_RATE

    # Batch anomaly: Batch_17 has elevated failure rate
    if batch_id == ANOMALOUS_BATCH:
        prob *= 4.0

    # Temperature correlation: failure rises sharply above 80°C
    if temperature > HIGH_TEMP_THRESHOLD:
        excess = temperature - HIGH_TEMP_THRESHOLD
        prob += excess * 0.002  # +0.2% per degree above 80

    # Voltage edge effects
    if voltage < 0.85 or voltage > 1.25:
        prob *= 1.5

    # Timing_Check is the most failure-prone test
    if test_name == "Timing_Check":
        prob *= 1.8
    elif test_name == "Burn_In":
        prob *= 1.3

    return min(prob, 0.30)  # cap at 30%


def _add_corruption(row, rng):
    """Randomly corrupt a small fraction of rows to simulate messy data."""
    roll = rng.random()
    if roll < 0.002:
        row["Temperature"] = ""  # missing value
    elif roll < 0.004:
        row["Voltage"] = "N/A"
    elif roll < 0.006:
        row["Execution_Time"] = "-1"  # nonsensical negative
    elif roll < 0.007:
        row["Voltage"] = "9999"  # clearly out of range
    elif roll < 0.008:
        row["Temperature"] = "-999"  # clearly out of range
    return row


def generate(output_path, seed=42):
    """Generate the full test log CSV."""
    rng = random.Random(seed)
    start_time = datetime(2025, 1, 1, 6, 0, 0)
    rows = []

    for batch_id in range(1, NUM_BATCHES + 1):
        for device_idx in range(DEVICES_PER_BATCH):
            device_id = f"DEV_{batch_id:03d}_{device_idx:04d}"
            # Each device runs a random subset of tests
            tests_to_run = rng.sample(TEST_TYPES, k=rng.randint(3, len(TEST_TYPES)))

            for test_name in tests_to_run:
                temperature = round(rng.gauss(65, 18), 1)
                temperature = max(20, min(120, temperature))
                voltage = round(rng.gauss(1.05, 0.12), 3)
                voltage = max(0.7, min(1.4, voltage))
                frequency = round(rng.gauss(2.4, 0.3), 2)
                frequency = max(1.0, min(3.5, frequency))
                exec_time = round(abs(rng.gauss(150, 40)), 1)

                prob = _failure_probability(batch_id, temperature, voltage, test_name)
                result = "FAIL" if rng.random() < prob else "PASS"
                error_code = (
                    rng.choice(ERROR_CODES[test_name]) if result == "FAIL" else ""
                )

                timestamp = start_time + timedelta(
                    seconds=rng.randint(0, 90 * 86400)  # spread over ~90 days
                )

                row = {
                    "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "Device_ID": device_id,
                    "Batch_ID": f"Batch_{batch_id:02d}",
                    "Test_Name": test_name,
                    "Voltage": str(voltage),
                    "Temperature": str(temperature),
                    "Frequency": str(frequency),
                    "Result": result,
                    "Error_Code": error_code,
                    "Execution_Time": str(exec_time),
                }
                row = _add_corruption(row, rng)
                rows.append(row)

    # Shuffle to simulate real-world arrival order
    rng.shuffle(rows)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fieldnames = [
        "Timestamp", "Device_ID", "Batch_ID", "Test_Name",
        "Voltage", "Temperature", "Frequency", "Result",
        "Error_Code", "Execution_Time",
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows):,} test records → {output_path}")
    return output_path


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generate(os.path.join(project_root, "data", "test_logs.csv"))
