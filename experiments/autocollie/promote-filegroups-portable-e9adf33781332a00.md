# Promote REJECTED — `e9adf33781332a00` on `filegroups/portable`

Generated 2026-05-22T16:41:20Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filegroups-portable-e9adf33781332a00 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9961)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e9adf33781332a00` | `60603d5829b59f05` | `8899525cd6580542` |
| PR AUC | 0.9961 | 0.9965 | 0.9961 |
| ROC AUC | 0.9990 | 0.9992 | 0.9991 |
| F1 | 0.9375 | 0.9740 | 0.9740 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filegroups-portable-e9adf33781332a00 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
