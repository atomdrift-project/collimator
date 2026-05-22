# Promote REJECTED — `6322f89cccd1c61e` on `filetypes/python`

Generated 2026-05-22T16:49:07Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-python-6322f89cccd1c61e lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9985)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `6322f89cccd1c61e` | `664104eced8ff8a4` | `780bffce4332d95a` |
| PR AUC | 0.9985 | 0.9984 | 0.9984 |
| ROC AUC | 0.9986 | 0.9986 | 0.9986 |
| F1 | 0.9778 | 0.9820 | 0.9807 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-python-6322f89cccd1c61e lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
