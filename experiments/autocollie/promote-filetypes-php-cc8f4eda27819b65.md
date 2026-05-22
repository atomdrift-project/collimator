# Promote REJECTED — `cc8f4eda27819b65` on `filetypes/php`

Generated 2026-05-22T17:28:57Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-php-cc8f4eda27819b65 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9945)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `cc8f4eda27819b65` | `6878437e86f19818` | `ddedd694775fa963` |
| PR AUC | 0.9945 | 0.9938 | 0.9940 |
| ROC AUC | 0.9973 | 0.9970 | 0.9972 |
| F1 | 0.9771 | 0.9851 | 0.9818 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-php-cc8f4eda27819b65 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
