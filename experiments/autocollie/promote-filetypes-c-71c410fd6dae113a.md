# Promote REJECTED — `71c410fd6dae113a` on `filetypes/c`

Generated 2026-05-22T17:11:13Z

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-c-71c410fd6dae113a lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9922)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `71c410fd6dae113a` | `6b5e8ecc60f38fd9` | `3a7e740cf830507c` |
| PR AUC | 0.9922 | 0.9923 | 0.9922 |
| ROC AUC | 0.9959 | 0.9959 | 0.9959 |
| F1 | 0.9352 | 0.9566 | 0.9342 |

## Disposition

This spec did not survive the promotion ladder.

candidate baseline is stale: candidate /home/t/collimator/out/models/azoth-candidate-filetypes-c-71c410fd6dae113a lacks baseline sentinel (.autocollie_baseline_snapshot_id) — cannot verify freshness. Re-stage from a fresh promote.
