# collimator

PyTorch training pipeline for malware detection. Takes labeled samples from a [cyclotron](https://codeberg.org/atomdrift/cyclotron) database and produces an ONNX model for Rust inference.

Part of the [atomdrift](https://codeberg.org/atomdrift) toolchain: **cleave** (static analysis) → **cyclotron** (labeling pipeline) → **collimator** (training) → **litmus** (inference).

## Quick start

```
make train DB=/path/to/cyclotron.db
```

Reads the database, extracts features, trains with 5-fold cross-validation, and writes `model.onnx`, `feature_spec.json`, `evaluation.json`, and `shap_importance.json` to `out/`. Python 3.11+ required; dependencies are installed into a virtualenv automatically.

## How it works

Collimator extracts a ~770-feature numeric vector from each cleave `AnalysisReport`. Features include taxonomy-based criticality encodings (top 200 prefixes), criticality histograms/ratios, confidence stats, ATT&CK/MBC behavior counts, evidence methods, string types, section metrics, binary metrics, and file type. The taxonomy design generalizes across file types — a model trained on ELF malware recognizes the same `objectives/anti-analysis` patterns in JavaScript.

The model is a three-layer MLP (256→128→64) with batch norm, dropout, and focal loss for class imbalance. Training uses AdamW with cosine annealing and early stopping. SHAP analysis validates learned signals.

## Make targets

```
make train    DB=...                 Train and export model
make evaluate DB=...                 Evaluate existing model against a database
make explain  DB=...                 SHAP feature importance analysis
make inspect  DB=... SAMPLE=<sha>    Inspect one sample (features + SHAP)
make errors   DB=...                 Show misclassified samples
make traits   DB=...                 Per-trait false-positive diagnostics
make scan     FILE=... [CLEAVE=...]  Score a live file via cleave + model
make test                            Run tests
make lint                            Run ruff + mypy
```

## License

Apache-2.0
