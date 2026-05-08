# Experiment History

A chronological topical index of the experiment tranches that produced the
deployed model. Each row links to the original writeup; this page exists so a
new reader doesn't have to read 25 markdowns to get the shape of the work.

The detailed per-tranche logs are kept as the paper trail — not deleted,
because reproducibility matters and PR reviewers periodically need to verify
"yes that idea was tried, here's why it didn't ship."

## How experiments work

Methodology, contracts, and how to run one are in
[`README.md`](README.md). The source-of-truth ledger of every screened idea
with its metrics is [`EXPERIMENTS.md`](EXPERIMENTS.md). Both stay current
because autocollie writes run JSONs under `out/experiments/azoth/runs/` that
the docs reflect.

## Architecture lineage

The deployed routed-ensemble emerged from four overlapping waves:

1. **Single-model exploration** (early 2026-04). One general LightGBM
   classifier; tested feature toggles, hyperparameters, and tree shape.
2. **Per-ecosystem specialists** (mid 2026-04). Hypothesis: PE malware and
   npm supply-chain malware are different; specialists outperform generalists
   on their domain. Confirmed; this became the routed ensemble.
3. **Routing policy + calibration** (2026-04 → 2026-05). Per-route isotonic
   calibration, per-FP/M operating points, multi-seed averaging, stacked
   combiners.
4. **Autonomous search** (2026-05). Autocollie drives the screen → confirm →
   promote ladder; per-route discoveries feed back into `make azoth-train`.

## Tranche index

### Single-model & feature-engineering era

| Writeup | What it tested | Outcome |
|---|---|---|
| [`AZOTH-LIGHT.md`](AZOTH-LIGHT.md) | Lighter training profiles for fast iteration; baseline azoth at 50/400 estimators. | Established the screen-vs-confirm fidelity tiers we still use. |
| [`AZOTH-NGRAMS.md`](AZOTH-NGRAMS.md) | N-gram pool sizing — `{depth, min_freq, min_crit, vocab_max}` sweep. | `tieredbi:` (severity-prefixed notable+ trait bigrams) shipped as default; tier-1 trigrams shipped opt-in. |
| [`AZOTH-OFFICE-KV.md`](AZOTH-OFFICE-KV.md) | KV-shape feature for office-document specialists. | KV vocab shipped; `KV_VOCAB_MAX=5000` is the default. |
| [`AZOTH-AGGRESSIVE.md`](AZOTH-AGGRESSIVE.md) | Higher hard-negative weights + larger leaves for low-FP regimes. | PE specialist runs with `hard_negative_fraction=0.01, weight=12`; survives in `AZOTH_SPECIALIST_TRAIN_OVERRIDE`. |
| [`AZOTH-OPTIMAL.md`](AZOTH-OPTIMAL.md) | Tier-bigram A/B across general + specialists, score-only-gate ablation, weak-filetype retrains. | Bigram defaults firmed up; weak-route retrains identified the routes that needed the family-pool augmentation in `azoth_augment_small_route_policies.py`. |

### Specialist-by-route experiments

| Writeup | Route | Outcome |
|---|---|---|
| [`AZOTH-ELF.md`](AZOTH-ELF.md) | `filetypes/elf` | ELF-specific training profile + native-group features baseline. Shipped. |
| [`AZOTH-SOURCE.md`](AZOTH-SOURCE.md) | `filegroups/source` | Source-language specialist with notable+ bigrams. |
| [`AZOTH-PYTHON-JAVASCRIPT.md`](AZOTH-PYTHON-JAVASCRIPT.md) | `filetypes/python`, `filetypes/javascript` | Per-language n-gram pools. Both became deployed specialists. |
| [`AZOTH-SCRIPT-DETECTION-PYTHON.md`](AZOTH-SCRIPT-DETECTION-PYTHON.md) | `filetypes/python` | Detection-specific tuning (vs. supply-chain detection). |
| [`AZOTH-SCRIPT-DETECTION-JAVASCRIPT.md`](AZOTH-SCRIPT-DETECTION-JAVASCRIPT.md) | `filetypes/javascript` | Same for JS; the deployed `filetypes/javascript` carries this profile. |
| [`AZOTH-SCRIPT-DETECTION-PY-JS.md`](AZOTH-SCRIPT-DETECTION-PY-JS.md) | both, joint | Joint training experiment. Did not outperform per-language specialists; abandoned. |
| [`AZOTH-SCRIPT-DETECTION-SCRIPTS.md`](AZOTH-SCRIPT-DETECTION-SCRIPTS.md) | `filegroups/scripts` | Group-level training across all script languages. |
| [`AZOTH-WEAK-ROUTES.md`](AZOTH-WEAK-ROUTES.md) | small filetypes (msi, pkg-info, vbs, etc.) | Identified routes where own-benign count is too small to resolve a 3 FP/M target; motivated family-pool augmentation. |
| [`AZOTH-WILD.md`](AZOTH-WILD.md) | wide search across filetypes | Tranche of speculative configurations; a handful survived as autocollie seeds. |

### Confirmation, ensemble & calibration

| Writeup | Theme | Outcome |
|---|---|---|
| [`AZOTH-CONFIRMATION.md`](AZOTH-CONFIRMATION.md) | Confirmation methodology — when does screen winner hold under retraining? | Established the seed-search confirm gate that autocollie now uses. |
| [`AZOTH-OVERNIGHT.md`](AZOTH-OVERNIGHT.md) | Overnight tranches, large-scale screens. | Discovered configurations that fed the next day's confirms. |
| [`AZOTH-FILETYPE-NIGHT.md`](AZOTH-FILETYPE-NIGHT.md) | Per-filetype overnight sweeps. | Per-filetype best-config picker now does this systematically via autocollie. |
| [`AZOTH-FILETYPE-MANIFEST-TRANCHE.md`](AZOTH-FILETYPE-MANIFEST-TRANCHE.md) | Manifest-driven sweeps over filetype × idea matrix. | Replaced by autocollie's auto-route loop. |
| [`AZOTH-TAIL-CONTRAST.md`](AZOTH-TAIL-CONTRAST.md) | Distinguishing ambiguous-tail rows from clearly-malicious. | Tail-contrast feature shipped in select specialists. |
| [`AZOTH-TAIL-CONTRAST-SMOKE.md`](AZOTH-TAIL-CONTRAST-SMOKE.md) | Smoke test for the above. | Validated the methodology before the full sweep. |

### Plan documents (now shipped)

| Document | Status |
|---|---|
| [`ENSEMBLE-IMPROVEMENTS-PLAN.md`](ENSEMBLE-IMPROVEMENTS-PLAN.md) | Items B (calibrated combiner shipped to litmus runtime), C (stacked XGB combiner), and A (multi-seed within-route averaging) are all deployed. Item D (per-row OOD-aware weighting) deferred. |
| [`NEXT_EXPERIMENTS.md`](NEXT_EXPERIMENTS.md) | Historical from 2026-04. Item B's "specialists outperform generalist" hypothesis became the routed ensemble. Items A/C either shipped or were superseded by autocollie's per-route discovery. |

## What survived into the deployed model

If you want to see the actual deployed configuration, the shortest path is:

1. The deployed bundle's `MODEL.md` / `ENSEMBLE_MODEL.md` /
   `route_diagnostics.md` (regenerated by `make azoth-deploy` against the
   live deployed root).
2. The per-route `feature_env` and `train_config` carried in the run JSON
   for each route's deployed key, under `out/experiments/azoth/runs/`.
3. `azoth_specialist_suite.py`'s `--autocollie-best-runs-dir` mechanism
   replays exactly those configurations — running it is the most direct way
   to materialize the deployed configuration into a fresh artifact.

The TL;DR: tier-1 bigrams, KV vocab, format hints, taxonomy features,
hostile/escalation density, and per-route hard-negative reweighting all
shipped. Score-only gates were rejected. Joint multi-language script training
was rejected in favor of per-language specialists.
