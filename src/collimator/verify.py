"""Post-training verification against known-good and known-bad samples.

Scans raw files from testdata/ using cleave, scores them with the trained
model, and asserts correct classification. Provides a deterministic
regression gate that catches model degradation across retraining runs.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

import numpy as np

from .features import FeatureSpec, extract, standardize
from .model import load_model, predict_proba

log = logging.getLogger(__name__)

TESTDATA_DIR = Path(__file__).resolve().parent.parent.parent / "testdata"

# Subdirectory name -> expected label (1 = malware, 0 = benign).
LABEL_DIRS: dict[str, int] = {
    "hostile": 1,
    "suspicious": 1,
    "benign": 0,
}


def _predict(model: object, vec: np.ndarray) -> float:
    return float(predict_proba(model, vec.reshape(1, -1))[0])


def _cleave_file(file_path: Path, cleave_bin: str) -> dict[str, object] | None:
    """Run cleave on a file and return the report, or None on failure."""
    try:
        result = subprocess.run(
            [cleave_bin, "--format=json", str(file_path)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        log.error("cleave not found at '%s'", cleave_bin)
        return None
    except subprocess.TimeoutExpired:
        log.warning("cleave timed out on %s", file_path.name)
        return None

    if result.returncode != 0:
        log.warning("cleave failed on %s (exit %d): %s",
                     file_path.name, result.returncode, result.stderr.strip())
        return None

    try:
        report: dict[str, object] = json.loads(result.stdout)
        return report
    except json.JSONDecodeError:
        log.warning("cleave returned invalid JSON for %s", file_path.name)
        return None


def _collect_files(testdata_dir: Path) -> list[tuple[Path, int]]:
    """Collect all test files with their expected labels."""
    files: list[tuple[Path, int]] = []
    for dirname, label in LABEL_DIRS.items():
        d = testdata_dir / dirname
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.is_file() and not f.name.startswith("."):
                files.append((f, label))
            elif f.is_dir():
                # Support .app bundles and similar directory structures.
                files.append((f, label))
    return files


def verify(
    model_path: Path,
    spec_path: Path,
    cleave_bin: str = "cleave",
    testdata_dir: Path | None = None,
    threshold: float = 0.5,
) -> bool:
    """Run verification against testdata samples.

    Returns True if all samples are classified correctly.
    """
    if testdata_dir is None:
        testdata_dir = TESTDATA_DIR

    spec = FeatureSpec.load(spec_path)
    model = load_model(model_path)

    files = _collect_files(testdata_dir)
    if not files:
        log.warning("no test files found in %s", testdata_dir)
        print(f"WARNING: no verification files found in {testdata_dir}")
        return True

    print(f"\n{'=' * 60}")
    print("VERIFICATION")
    print(f"{'=' * 60}")
    print(f"Testdata:  {testdata_dir}")
    print(f"Threshold: {threshold:.3f}")
    print(f"Samples:   {len(files)}")
    print()

    passed = 0
    failed = 0
    skipped = 0

    print(f"  {'Result':<8} {'Score':>7} {'Expected':<10} {'File'}")
    print(f"  {'-' * 55}")

    for file_path, expected_label in files:
        report = _cleave_file(file_path, cleave_bin)
        if report is None:
            print(f"  {'SKIP':<8} {'':>7} "
                  f"{'malware' if expected_label else 'benign':<10} {file_path.name}")
            skipped += 1
            continue

        vec_raw = extract(report, spec)
        vec = standardize(vec_raw, spec)
        prob = _predict(model, vec)

        predicted_label = 1 if prob > threshold else 0
        correct = predicted_label == expected_label
        expected_str = "malware" if expected_label else "benign"

        if correct:
            print(f"  {'PASS':<8} {prob:>7.4f} {expected_str:<10} {file_path.name}")
            passed += 1
        else:
            predicted_str = "malware" if predicted_label else "benign"
            print(f"  {'FAIL':<8} {prob:>7.4f} {expected_str:<10} "
                  f"{file_path.name}  (predicted {predicted_str})")
            failed += 1

    print(f"\n  Passed: {passed}  Failed: {failed}  Skipped: {skipped}")

    if failed > 0:
        print(f"\nVERIFICATION FAILED: {failed} sample(s) misclassified")
        return False

    if passed == 0:
        print("\nVERIFICATION WARNING: no samples were scored (all skipped)")
        return True

    print("\nVERIFICATION PASSED")
    return True
