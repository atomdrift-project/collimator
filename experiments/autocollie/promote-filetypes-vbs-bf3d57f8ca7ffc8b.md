# Promote REJECTED — `bf3d57f8ca7ffc8b` on `filetypes/vbs`

Generated 2026-05-22T17:23:16Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-bf3d57f8ca7ffc8b lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9979)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `bf3d57f8ca7ffc8b` | `2d1bd72d1a70409f` | `92a3b5ae5ec1bf49` |
| PR AUC | 0.9979 | 0.9980 | 0.9981 |
| ROC AUC | 0.9853 | 0.9863 | 0.9867 |
| F1 | 0.9846 | 0.9885 | 0.9885 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-bf3d57f8ca7ffc8b lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
