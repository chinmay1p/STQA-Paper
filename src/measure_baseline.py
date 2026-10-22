"""
Measures baseline execution durations for all 30 tests across multiple runs on the clean codebase.
"""
import json
import os
import subprocess
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_EXE = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "raw", "baseline_test_durations.json")

def measure_baseline(num_runs: int = 5):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    report_file = os.path.join(BASE_DIR, ".report.json")
    durations = {}

    print(f"Measuring clean baseline test durations over {num_runs} repeated runs...")
    for run_idx in range(num_runs):
        cmd = [
            PYTHON_EXE, "-m", "pytest", "tests",
            f"--json-report-file={report_file}",
            "--json-report", "-q"
        ]
        res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
        with open(report_file, "r", encoding="utf-8") as f:
            rep = json.load(f)
        
        for t in rep.get("tests", []):
            node = t["nodeid"].replace("\\", "/")
            call_dur = t.get("call", {}).get("duration", 0.002)
            if node not in durations:
                durations[node] = []
            durations[node].append(call_dur)

    if os.path.exists(report_file):
        os.remove(report_file)

    summary = {}
    for node, durs in durations.items():
        summary[node] = {
            "mean_duration_sec": float(np.mean(durs)),
            "std_duration_sec": float(np.std(durs)),
            "min_duration_sec": float(np.min(durs)),
            "max_duration_sec": float(np.max(durs)),
            "raw_samples": durs
        }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved baseline measurements for {len(summary)} tests to {OUTPUT_PATH}")
    return summary

if __name__ == "__main__":
    measure_baseline()
