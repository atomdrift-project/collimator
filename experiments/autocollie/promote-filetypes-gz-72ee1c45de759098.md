# Promote REJECTED — `72ee1c45de759098` on `filetypes/gz`

Generated 2026-05-22T17:34:27Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-gz-72ee1c45de759098 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `72ee1c45de759098` | `d75378540711b47e` | `c0b602e180ec5bb1` |
| PR AUC | 0.9988 | 0.9989 | 0.9988 |
| ROC AUC | 0.9985 | 0.9986 | 0.9985 |
| F1 | 0.9774 | 0.9956 | 0.9956 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-gz-72ee1c45de759098 lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
