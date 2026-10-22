"""
Script to verify that all 16 scenarios produce exact expected ground truth outcomes.
"""
import json
import os
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_EXE = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
MANIFEST_PATH = os.path.join(BASE_DIR, "scenarios", "scenario_manifest.json")

def verify_all():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    report_file = os.path.join(BASE_DIR, ".report.json")
    results = {}
    
    for sc in manifest:
        sc_id = sc["scenario_id"]
        target_abs = os.path.join(BASE_DIR, sc["target_file"])
        mutant_abs = os.path.join(BASE_DIR, sc["mutant_file"])
        backup_abs = target_abs + ".orig"
        
        shutil.copy2(target_abs, backup_abs)
        try:
            shutil.copy2(mutant_abs, target_abs)
            cmd = [
                PYTHON_EXE, "-m", "pytest", "tests",
                f"--json-report-file={report_file}",
                "--json-report", "-q"
            ]
            run_res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
            with open(report_file, "r", encoding="utf-8") as rf:
                rep = json.load(rf)
            
            failed_tests = [t["nodeid"].replace("\\", "/") for t in rep.get("tests", []) if t["outcome"] == "failed"]
            passed_tests = [t["nodeid"].replace("\\", "/") for t in rep.get("tests", []) if t["outcome"] == "passed"]
            expected_failed = sc["expected_failing_tests"]
            
            if set(failed_tests) != set(expected_failed):
                raise AssertionError(
                    f"Scenario {sc_id} outcome mismatch!\n"
                    f"Observed failed: {failed_tests}\n"
                    f"Expected failed: {expected_failed}\n"
                    f"Pytest stdout: {run_res.stdout}\n"
                    f"Pytest stderr: {run_res.stderr}"
                )
            
            results[sc_id] = {
                "has_fault": sc["has_fault"],
                "fault_id": sc["fault_id"],
                "total_passed": len(passed_tests),
                "total_failed": len(failed_tests),
                "failed_tests": failed_tests
            }
            print(f"[{sc_id}] OK - has_fault={sc['has_fault']}, detected_failures={failed_tests}")
        finally:
            if os.path.exists(backup_abs):
                shutil.move(backup_abs, target_abs)
            if os.path.exists(report_file):
                os.remove(report_file)

    print("\n>>> ALL 16 SCENARIOS GROUND TRUTH EMPIRICALLY CONFIRMED! <<<")
    return results

if __name__ == "__main__":
    verify_all()
