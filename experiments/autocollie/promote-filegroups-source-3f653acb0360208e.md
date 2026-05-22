# Promote REJECTED — `3f653acb0360208e` on `filegroups/source`

Generated 2026-05-22T17:36:39Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filegroups-source-3f653acb0360208e lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3f653acb0360208e` | `1eef94903660b7de` | `b3a4411046ba50b2` |
| PR AUC | 0.9988 | 0.9987 | 0.9988 |
| ROC AUC | 0.9981 | 0.9980 | 0.9981 |
| F1 | 0.9788 | 0.9774 | 0.9776 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filegroups-source-3f653acb0360208e lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
