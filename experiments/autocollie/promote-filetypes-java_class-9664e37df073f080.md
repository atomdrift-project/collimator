# Promote REJECTED — `9664e37df073f080` on `filetypes/java_class`

Generated 2026-05-22T17:16:33Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-9664e37df073f080 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9965)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9664e37df073f080` | `06ede31238ca18dc` | `bb1435c504f60120` |
| PR AUC | 0.9965 | 0.9966 | 0.9965 |
| ROC AUC | 0.9992 | 0.9992 | 0.9992 |
| F1 | 0.9485 | 0.9170 | 0.9209 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-9664e37df073f080 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
