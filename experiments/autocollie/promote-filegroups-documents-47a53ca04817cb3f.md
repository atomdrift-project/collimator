# Promote REJECTED — `47a53ca04817cb3f` on `filegroups/documents`

Generated 2026-05-22T16:55:11Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filegroups-documents-47a53ca04817cb3f lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `47a53ca04817cb3f` | `2da06d3766024655` | `b453af4963e3aef2` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9986 | 0.9979 | 0.9979 |
| F1 | 0.9956 | 0.9976 | 0.9976 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filegroups-documents-47a53ca04817cb3f lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
