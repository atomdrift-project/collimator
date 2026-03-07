# collimator

PyTorch training pipeline for malware detection. Takes labeled samples from a [cyclotron](https://codeberg.org/atomdrift/cyclotron) database and produces an ONNX model consumable by Rust inference code.

Part of the [atomdrift](https://codeberg.org/atomdrift) toolchain:

- **cleave** -- static analyzer that decomposes binaries and source into traits and findings
- **cyclotron** -- LLM-driven pipeline that builds a labeled sample database using cleave
- **collimator** -- trains a neural network on cyclotron's output (this project)
- **litmus** -- Rust inference engine that runs the trained model in production

## Quick start

```
make train DB=/path/to/cyclotron.db
```

This reads the database, extracts features, trains a model with 5-fold cross-validation, and writes everything to `out/`.

### Prerequisites

- Python 3.11+
- A cyclotron database with labeled samples (status `good` and `bad`)

Dependencies are installed automatically into a virtualenv on first run.

## How it works

### Input: cyclotron database

Cyclotron scans binaries with cleave and stores the full JSON analysis report in SQLite. Each sample has a status that progresses through a state machine. Collimator uses only **terminal statuses** for clean labels:

| Status | Label | Meaning |
|--------|-------|---------|
| `bad` | 1 | Confirmed malware -- cleave detects hostile/suspicious traits |
| `good` | 0 | Confirmed benign -- no false positives from cleave |

All intermediate statuses (`bad-review`, `bad-reversed`, `good-review`, etc.) are skipped. This ensures the model trains on high-confidence labels only.

### Feature extraction

Each sample's cleave `AnalysisReport` JSON is converted to a fixed-size numeric vector. The feature groups:

| Group | Features | Encoding |
|-------|----------|----------|
| Taxonomy | Two slots per prefix (top 200 by frequency) | Max criticality ordinal + log1p(count) |
| Criticality histogram | 6 slots | Count of findings at each level |
| Criticality ratios | 3 slots | Hostile, suspicious, above-notable fractions |
| Criticality weighted | 2 slots | Confidence-weighted hostile + suspicious scores |
| Confidence stats | 4 slots | Mean, max, min, stddev confidence |
| Behavior summary | 4 slots | ATT&CK + MBC unique counts and total refs |
| Evidence methods | One slot per method | Count of evidence items per method type |
| String types | One slot per type + 3 ratios | Count per type + suspicious/encoded/network ratios |
| Section metrics | 5 slots | Count, avg/max entropy, W+X sections, max size |
| Metrics passthrough | All numeric metric fields | Log-scaled counts, raw ratios/entropy |
| File type | One slot per type | One-hot (elf, macho, pe, python, etc.) |
| Aggregate stats | 9 slots | Finding count, risk, strings, imports, size, depth, per-crit counts |
| Finding behavior | 4 slots | ID diversity, avg match count, evidence density |

**Taxonomy-based feature encoding.** Rather than creating one feature per unique finding ID (which explodes to hundreds of thousands with large corpora), collimator decomposes every finding into its `/`-delimited taxonomy hierarchy and encodes each level with criticality + count:

```
objectives/anti-analysis/timing::ast  ->  taxon_crit + taxon_count for:
  objectives/anti-analysis/timing       (leaf, after stripping ::variant)
  objectives/anti-analysis              (parent)
  objectives                            (root)
```

Each taxonomy prefix gets two features: the **max criticality ordinal** (0-5) seen across any matching finding, and the **log1p(count)** of contributing findings. The vocabulary is capped at the top 200 most frequent prefixes across the corpus.

This design:

1. **Keeps the feature vector small.** ~700-800 total features with every feature carrying signal, vs thousands of dead sparse features.
2. **Generalizes across file types.** The specific leaf rules differ between ELF, PE, and Python, but the taxonomy categories (`net/`, `crypto/`, `objectives/anti-analysis/`) are shared. A model trained on ELF malware can recognize `objectives/anti-analysis` patterns in JavaScript.
3. **Captures aggregate signal.** Five different `net/*` findings in one sample is suspicious even if no individual finding is rare. The `taxon_count:net` feature captures this.

The vocabulary (which taxonomy prefixes, evidence methods, string types, metric fields, and file types exist) is built from the training corpus and exported as `feature_spec.json` alongside the model. This is the contract between training and inference.

### Model architecture

Three-layer MLP with batch normalization and dropout:

```
Input(N) -> Linear(256) -> BN -> ReLU -> Dropout(0.3)
         -> Linear(128) -> BN -> ReLU -> Dropout(0.3)
         -> Linear(64)  -> BN -> ReLU -> Dropout(0.2)
         -> Linear(1)   -> Sigmoid -> P(malware)
```

Class imbalance is handled via **focal loss** with dynamic alpha, which focuses training on hard-to-classify examples by downweighting well-classified majority-class samples. Training uses AdamW with cosine annealing and early stopping on validation loss.

### Explainability

SHAP (KernelExplainer) computes per-feature importance across the dataset. The output tells you which findings, metrics, and behavioral properties the model relies on most. This is critical for validating that the model learned real signals rather than dataset artifacts.

## Usage

### Train a model

```
make train DB=/path/to/cyclotron.db
```

Output in `out/`:

```
out/
  model.onnx            ONNX model for Rust inference
  model.pt              PyTorch state dict for SHAP / retraining
  feature_spec.json     Vocabulary and feature layout
  evaluation.json       Metrics, optimal threshold, confusion matrix
  shap_importance.json  Top 50 features by SHAP value
```

### Evaluate against a database

Test an existing model against a (potentially different) database:

```
make evaluate DB=/path/to/other.db
```

Requires `onnxruntime` (`pip install onnxruntime`).

### Run SHAP analysis

Generate or regenerate SHAP feature importance:

```
make explain DB=/path/to/cyclotron.db
```

### Inspect a single sample

Look at a specific sample's feature vector, prediction, and per-feature SHAP breakdown:

```
make inspect DB=/path/to/cyclotron.db SAMPLE=a1b2c3d4
```

`SAMPLE` can be a SHA256 prefix. Output shows:
- The prediction score and classification
- All non-zero features sorted by magnitude
- Per-feature SHAP values showing exactly what pushed the prediction toward malware or benign

### Find misclassifications

Show false positives and false negatives with their scores:

```
make errors DB=/path/to/cyclotron.db
```

Useful after training to understand where the model struggles. Combine with `inspect` to drill into individual failures.

### Analyze trait false positives

Show per-trait prevalence across malware and benign samples:

```bash
make traits DB=/path/to/cyclotron.db
```

This is especially useful for hostile trait IDs. By default the report shows exact hostile findings with their benign sample count, malware sample count, precision, prevalence, and lift, ranked so noisy traits rise to the top.

### Scan a live file

Run cleave on any file and score it with the trained model, with full SHAP breakdown:

```
make scan FILE=/path/to/suspicious_binary
```

This runs `cleave --format=json` on the file, extracts features, scores with the model, and shows the per-feature SHAP breakdown. Optionally pass `DB=` to provide background samples for more accurate SHAP values.

To use a specific cleave binary:

```
make scan FILE=/path/to/binary CLEAVE=/usr/local/bin/cleave
```

### Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DB` | (required for most) | Path to cyclotron SQLite database |
| `OUT_DIR` | `out` | Output directory |
| `SAMPLE` | (required for inspect) | SHA256 or prefix of sample |
| `FILE` | (required for scan) | Path to file to scan |
| `CLEAVE` | `cleave` | Path to cleave binary |

### All targets

```
make train DB=...                  Train model and export to out/
make evaluate DB=...               Evaluate existing model against a database
make explain DB=...                SHAP feature importance analysis
make inspect DB=... SAMPLE=<sha>   Inspect one sample (features + SHAP)
make errors DB=...                 Show misclassified samples
make traits DB=...                 Show trait-level prevalence / false-positive stats
make scan FILE=/path/to/binary     Score a live file via cleave + model
make test                          Run tests
make lint                          Run ruff + mypy
make venv                          Create virtual environment
make clean                         Remove out/, venv, and caches
```

## Output files

### `model.onnx`

The trained model in ONNX format. Single input tensor `features` of shape `[batch_size, N]`, single output tensor `probability` of shape `[batch_size, 1]` in range [0, 1].

To run inference, construct a feature vector using the same vocabulary and ordering described in `feature_spec.json`, then run the ONNX model. In Rust, use the [ort](https://crates.io/crates/ort) crate.

### `feature_spec.json`

The contract between training and inference. Structure:

```json
{
  "version": 9,
  "taxonomy_vocab": ["objectives", "objectives/command-and-control", "micro-behaviors", ...],
  "evidence_vocab": ["header", "hex", "import_symbol", "magic", "raw", "string", "symbol", ...],
  "string_type_vocab": ["Base64", "Const", "ShellCmd", "Url", ...],
  "metric_vocab": ["binary:code_entropy", "binary:file_size", "text:char_entropy", ...],
  "filetype_vocab": ["elf", "javascript", "macho", "pe", "python", ...],
  "feature_names": ["taxon_crit:objectives", "taxon_count:objectives", ...,
                     "crit_count:hostile", ..., "metrics:binary_file_size", ...],
  "total_features": 769
}
```

**For Rust implementers:** `feature_names` defines the exact order of the feature vector. To construct a feature vector at inference time:

1. Run cleave on the target file to get an `AnalysisReport`.
2. Allocate a zero vector of length `total_features`.
3. For each finding, strip any `::variant` suffix from its ID, then split on `/` to get all ancestor prefixes (including the leaf). For example, `objectives/anti-analysis/timing::ast` produces `["objectives", "objectives/anti-analysis", "objectives/anti-analysis/timing"]`. For each prefix in `taxonomy_vocab`, accumulate the max criticality ordinal (filtered=0, component=1, baseline=2, notable=3, suspicious=4, hostile=5) and the log1p of the count of contributing findings.
4. Fill the criticality histogram, ratios, weighted scores, confidence stats, behavior summary, evidence counts, string type counts, section metrics, metrics passthrough, file type, aggregate stats, and finding behavior features following the `feature_names` ordering.
5. Apply z-score standardization using the `feature_means` and `feature_stds` arrays (if present).
6. Pass the vector to the ONNX model.

The `feature_names` array is the source of truth for slot ordering. Each name has a prefix indicating its group (`taxon_crit:`, `taxon_count:`, `crit_count:`, `crit_ratio:`, `crit_weighted:`, `conf:`, `behavior:`, `evidence:`, `string_type:`, `string_ratio:`, `sections:`, `metrics:`, `filetype:`, `agg:`, `finding:`).

### `evaluation.json`

Training metrics for the model:

```json
{
  "metrics": {
    "accuracy": 0.999,
    "precision": 0.989,
    "recall": 0.936,
    "f1": 0.962,
    "roc_auc": 0.981,
    "avg_precision": 0.973
  },
  "optimal_threshold": 0.396,
  "confusion_matrix": [[TN, FP], [FN, TP]],
  "class_distribution": {"benign": 51432, "malware": 627},
  "fold_metrics": [{"roc_auc": 0.998, "f1": 0.945, ...}, ...],
  "n_features": 769
}
```

The `optimal_threshold` maximizes F1 on holdout data. For production use, you may want to tune this based on your tolerance for false positives vs. false negatives. A lower threshold catches more malware but flags more benign files.

### `shap_importance.json`

Global feature importance from SHAP analysis:

```json
{
  "top_features": [
    {"name": "string_type:Import", "importance": 0.003},
    {"name": "crit_weighted:suspicious", "importance": 0.001},
    ...
  ],
  "useless_feature_count": 767,
  "total_features": 769
}
```

Use this to validate the model is learning meaningful signals. Features like `crit_weighted:suspicious`, `taxon_crit:objectives/lateral-movement`, and `metrics:binary_high_complexity_functions` indicate the model is learning real behavioral patterns.

## Project structure

```
src/collimator/
  __main__.py     CLI entry point (train, evaluate, explain subcommands)
  data.py         SQLite loader -- reads cyclotron DB, filters terminal statuses
  features.py     cleave JSON -> fixed-size feature vector
  model.py        MLP architecture definition
  train.py        Training loop with focal loss and stratified K-fold CV
  export.py       ONNX export and validation
  explain.py      SHAP feature importance
  inspect.py      Single sample inspection, error analysis, live scanning
  traits.py       Trait-level false positive diagnostics
tests/
  test_data.py       Data loading from SQLite
  test_features.py   Feature extraction correctness
  test_model.py      Model architecture and output range
  test_traits.py     Trait statistics
```

## License

Apache-2.0
