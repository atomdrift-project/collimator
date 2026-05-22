# Promote REJECTED — `bc55dc627e7f9421` on `filetypes/package.json`

Generated 2026-05-22T16:47:47Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-bc55dc627e7f9421 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9997)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `bc55dc627e7f9421` | `5bd13df6024a9637` | `8d81c697aab0f197` |
| PR AUC | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9994 | 0.9993 | 0.9994 |
| F1 | 0.9958 | 0.9965 | 0.9945 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-bc55dc627e7f9421 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
