# collimator

`collimator` is a compact, streaming-first malware-classification pipeline built around XGBoost.
It reads labeled samples from a [hopper](https://codeberg.org/atomdrift/hopper) database (PostgreSQL or SQLite), extracts sparse numeric features from cleave reports, trains a calibrated classifier, and exports both XGBoost and ONNX artifacts for downstream inference.

Part of the broader toolchain:

`cleave -> hopper -> collimator -> litmus`

## Goals

This repo is intentionally optimized for four things at once:

- Scientific rigor: threshold tuning is separated from final evaluation, and evaluation artifacts record how the model was trained and scored.
- Performance: the default path is sparse, batched, and streaming-oriented.
- Maintainability: core logic is split across small modules with explicit contracts.
- Clarity: the full pipeline is short enough to read end-to-end.

## Architecture

The core pipeline is:

1. Load labeled samples from `hopper`.
2. Build a feature vocabulary from training samples only.
3. Extract sparse features for train/test streams.
4. Train XGBoost on raw sparse features.
5. Split holdout into calibration and evaluation subsets when feasible.
6. Choose an operating threshold on calibration.
7. Report threshold-free and thresholded metrics on evaluation.
8. Export:
   `model.json`, `model.onnx`, `feature_spec.json`, `evaluation.json`

### Modules

- [`data.py`](/srv/home/t/collimator/src/collimator/data.py): streaming access to labeled samples and deterministic test-bucket assignment
- [`features.py`](/srv/home/t/collimator/src/collimator/features.py): sparse feature extraction and feature-group definitions
- [`train.py`](/srv/home/t/collimator/src/collimator/train.py): model fitting, calibration/evaluation split, metrics
- [`model.py`](/srv/home/t/collimator/src/collimator/model.py): XGBoost creation, device detection, probability inference
- [`export.py`](/srv/home/t/collimator/src/collimator/export.py): ONNX export, ONNX/XGBoost parity, evaluation artifact helpers
- [`thresholds.py`](/srv/home/t/collimator/src/collimator/thresholds.py): operating-point analysis
- [`ablation.py`](/srv/home/t/collimator/src/collimator/ablation.py): leave-one-group-out feature ablations
- [`benchmark.py`](/srv/home/t/collimator/src/collimator/benchmark.py): throughput benchmarking

## Scientific Contract

Out of the box, the pipeline is designed to be methodologically defensible:

- The deterministic test bucket is excluded from training.
- Within training, a holdout split is created when the dataset is large enough.
- That holdout is further split into:
  calibration: choose the decision threshold
  evaluation: report final thresholded metrics
- Threshold-free metrics are also reported:
  `ROC AUC`, `Average Precision`, `Brier`

The saved [`evaluation.json`](/srv/home/t/collimator/out/evaluation.json) artifact includes:

- metrics
- calibration summary:
  `ECE` plus reliability-bin summaries
- chosen threshold
- split summary
- environment metadata
- experiment metadata:
  seed, feature-spec version, worker count, git SHA, train config

## Features

The model uses a fixed sparse feature layout derived from cleave `AnalysisReport` JSON:

- `present:*`: binary path presence
- `maxcrit:*`: maximum criticality per path
- `agg:*`: path breadth and concentration summaries
- `ext:*`: third-party and well-known signal summaries
- `metrics:*`: curated numeric report metrics
- `filetype:*`: file-type one-hot features
- `struct:*`: simple structural anomaly features

Feature groups are explicit so they can be benchmarked and ablated.

## Quick Start

### Virtualenv

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Synthetic demo database

Generate a small self-contained SQLite database that matches the `hopper` schema:

```bash
python -m collimator demo-db --output out/demo.db
```

Or via `make`:

```bash
make demo-db
```

### Train

```bash
python -m collimator train --db postgres://hopper@localhost/hopper --output out
```

Or via `make`:

```bash
make train DB=postgres://hopper@localhost/hopper
```

This writes:

- `out/model.json`
- `out/model.onnx`
- `out/feature_spec.json`
- `out/evaluation.json`
- `out/shap_importance.json`

## Core Workflows

### Train and export

```bash
python -m collimator train --db postgres://hopper@localhost/hopper --output out --seed 42
```

Demo run:

```bash
python -m collimator train --db out/demo.db --output out
```

### Evaluate an exported ONNX model

```bash
python -m collimator evaluate --db postgres://hopper@localhost/hopper --model out/model.onnx --spec out/feature_spec.json
```

### Analyze operating thresholds

```bash
python -m collimator thresholds --db postgres://hopper@localhost/hopper --model out/model.json --spec out/feature_spec.json
```

### Run feature-group ablations

```bash
python -m collimator ablate --db postgres://hopper@localhost/hopper
```

Optional subset:

```bash
python -m collimator ablate --db postgres://hopper@localhost/hopper --groups present metrics struct
```

Save JSON:

```bash
python -m collimator ablate --db postgres://hopper@localhost/hopper --output out/ablation.json
```

### Benchmark throughput

```bash
python -m collimator benchmark --db postgres://hopper@localhost/hopper
```

Reuse an existing model/spec:

```bash
python -m collimator benchmark --db postgres://hopper@localhost/hopper --model out/model.json --spec out/feature_spec.json
```

Save JSON:

```bash
python -m collimator benchmark --db postgres://hopper@localhost/hopper --output out/benchmark.json
```

## Interpreting Outputs

### `evaluation.json`

This is the main experiment record. Use it to answer:

- What split policy was used?
- What threshold was chosen?
- What seed and config produced this model?
- What threshold-free metrics did the model achieve?
- How well calibrated are the predicted probabilities?

### `thresholds`

This command prints two things:

- called-set accuracy tables for hostile/benign decisions
- recommendation tables based on recall/FPR constraints

The held-out test recommendations are the honest operating-point reference.
The full-corpus recommendation table is operationally useful, but it includes training data.

### `ablate`

Each ablation drops one named feature group and retrains the model.
Use this to answer:

- Which feature families matter most?
- Which groups improve ranking metrics vs thresholded metrics?
- Which groups can be removed without much loss?

### `benchmark`

The benchmark command reports:

- vocab-build time
- extraction throughput
- training time
- inference throughput
- feature count and test-set size

It is intentionally simple: the goal is comparability across runs, not a full profiling framework.

## Make Targets

```bash
make train      DB=...                 Train model and export artifacts
make evaluate   DB=...                 Evaluate exported ONNX model
make explain    DB=...                 SHAP feature importance analysis
make inspect    DB=... SAMPLE=<sha>    Inspect one sample
make errors     DB=...                 Show top false positives/negatives
make traits     DB=...                 Trait-level prevalence diagnostics
make thresholds DB=...                 Show threshold tables
make benchmark  DB=...                 Benchmark extraction/training/inference
make ablate     DB=...                 Run feature-group ablations
make demo-db                           Create a small synthetic demo database
make scan       FILE=...               Score a live file via cleave + model
make test                              Run tests
make lint                              Run ruff + mypy
```

## Notes on Performance

- Sparse features are used throughout training.
- Large-corpus evaluation paths are batched.
- Feature extraction defaults to a conservative auto worker count.
- Use `--workers 1` to force single-process execution or `--workers N` to pin parallelism.
- GPU detection reports the device XGBoost can actually use, not just the requested device.

## Notes on Reproducibility

- Training seed is explicit.
- Evaluation artifacts persist experiment metadata.
- Optional dependency groups are declared in [`pyproject.toml`](/srv/home/t/collimator/pyproject.toml).
- The full test suite should pass in a clean venv created from [`requirements.txt`](/srv/home/t/collimator/requirements.txt).

## License

Apache-2.0
