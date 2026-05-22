# Promote REJECTED — `9684f0d96da27540` on `filetypes/zip`

Generated 2026-05-22T17:10:41Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-zip-9684f0d96da27540 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9998)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9684f0d96da27540` | `06e2493c6559d096` | `6f759c9bf0ca5e2e` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9963 | 0.9965 | 0.9969 |
| F1 | 0.9937 | 0.9941 | 0.9938 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-zip-9684f0d96da27540 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
