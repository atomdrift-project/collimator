# Promote REJECTED — `02e6aac4fca061d0` on `filetypes/lnk`

Generated 2026-05-22T16:55:26Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-02e6aac4fca061d0 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `02e6aac4fca061d0` | `2d9564967a5c9d5c` | `06d781a562bc7f81` |
| PR AUC | 0.9988 | 0.9988 | 0.9989 |
| ROC AUC | 0.9855 | 0.9844 | 0.9858 |
| F1 | 0.9843 | 0.9843 | 0.9843 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-02e6aac4fca061d0 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
