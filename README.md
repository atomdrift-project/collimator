# collimator

[![License](https://img.shields.io/github/license/atomdrift-project/collimator)](LICENSE)

collimator trains and evaluates the routed malware-detection models published as
[Azoth](https://github.com/atomdrift-project/azoth) and consumed by
[Atomdrift Scan](https://github.com/atomdrift-project/scan). It reads labeled
cleave reports from [hopper](https://github.com/atomdrift-project/hopper), trains
a general model plus format specialists, selects routing policies, and stages a
validated ONNX bundle.

This repository is for model developers and operators. To scan files, install
Atomdrift Scan instead.

## What it provides

- General, file-group, and file-type LightGBM models
- Three-seed ensembles for routes where averaging improves stability
- A 42-point false-positive grid from L0 through L25000
- A canonical deployment default of L25, or 0.25 expected false positives per
  million benign files
- Deterministic train/test partitioning and per-route evaluation reports
- ONNX export, bundle validation, and regression gates before publication
- Autonomous experiment search through
  [autocollie](https://github.com/atomdrift-project/autocollie)

The deployed runtime uses raw model probabilities and calibrated operating
thresholds. Training may fit calibrators for evaluation, but current Azoth
bundles intentionally do not ship `calibrator.json` files.

## Requirements

- Python 3.11 or newer
- Make and a C/C++ build toolchain
- A PostgreSQL hopper database containing labeled cleave reports
- Substantial CPU, memory, disk, and time for full-corpus training

The Makefile creates `.venv/` and installs the pinned Python dependencies.

## Quick start

```bash
# Show the maintained targets and required parameters.
make help

# Train the deploy-bound ensemble on the full labeled corpus.
make azoth-full-train DB=postgres://hopper@localhost:5432/hopper

# Use the smaller balanced corpus for iteration.
make azoth-fast-train DB=postgres://hopper@localhost:5432/hopper
```

Successful training builds in an isolated run directory and publishes the
validated bundle under `out/models/azoth/` only after every gate passes.

## Run an experiment

```bash
make experiment \
  EXP_ROUTE=filetypes/python \
  EXP_IDEA=larger-leaves \
  EXP_NUM_LEAVES=128 \
  DB=postgres://hopper@localhost:5432/hopper
```

Experiment records land in `out/experiments/azoth/runs/`. Use a descriptive
`EXP_IDEA`; the JSON record is the durable comparison and audit trail.

To search repeatedly with a local OpenAI-compatible model:

```bash
make autocollie-loop \
  ROUTES=filetypes/python,filetypes/javascript \
  EXPERIMENTS=10 \
  AUTOCOLLIE_DB=postgres://hopper@localhost:5432/hopper
```

Autocollie produces candidates; it does not silently replace the deployed
bundle. Inspect a candidate before staging it:

```bash
make azoth-deploy AZOTH_ROOT=out/models/azoth-candidate-<route>-<key>
```

## Test the resulting bundle

```bash
atomscan --model-dir out/models/azoth suspect.bin
```

## Important paths

| Path | Purpose |
| --- | --- |
| `src/collimator/` | Data access, feature construction, training, thresholds, and export |
| `scripts/` | Routed evaluation, deployment, diagnostics, and regression gates |
| `experiments/` | Human-readable experiment history and methodology |
| `out/experiments/azoth/runs/` | Machine-readable experiment records |
| `out/models/azoth/` | Current validated source bundle |

See [CONTRIBUTING.md](CONTRIBUTING.md) before changing features, partitions, or
deployment gates. Model changes should include the resulting run record and a
clear comparison against the current route.

## License

collimator is available under the [Apache License 2.0](LICENSE).
