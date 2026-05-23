# Promote REJECTED — `963342a82ee48369` on `filegroups/documents`

Generated 2026-05-23T17:49:38Z

AUC regressed at full-train: 0.9986 -> 0.9879

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `963342a82ee48369` | `d3120a4dd6bc9f6b` | `159bcd16eef2f1d5` |
| PR AUC | 1.0000 | 0.9986 | 0.9999 |
| ROC AUC | 0.9986 | 0.8989 | 0.9879 |
| F1 | 0.9973 | 0.9965 | 0.9965 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9986 -> 0.9879
