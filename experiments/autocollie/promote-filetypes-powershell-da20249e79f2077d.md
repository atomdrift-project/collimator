# Promote REJECTED — `da20249e79f2077d` on `filetypes/powershell`

Generated 2026-05-22T17:28:20Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-powershell-da20249e79f2077d lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9987)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `da20249e79f2077d` | `9039d25b71f17135` | `9589dfb4d5af1193` |
| PR AUC | 0.9987 | 0.9979 | 0.9983 |
| ROC AUC | 0.9967 | 0.9949 | 0.9957 |
| F1 | 0.9520 | 0.9841 | 0.9822 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-powershell-da20249e79f2077d lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
