# Promote REJECTED — `09e3314e33835065` on `filegroups/documents`

Generated 2026-05-23T20:05:34Z

AUC regressed at full-train: 0.9985 -> 0.9704

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `09e3314e33835065` | `3685bacbeac831ad` | `93b36e99833ca7f2` |
| PR AUC | 1.0000 | 0.9996 | 0.9996 |
| ROC AUC | 0.9985 | 0.9672 | 0.9704 |
| F1 | 0.9868 | 0.9965 | 0.9965 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9985 -> 0.9704
