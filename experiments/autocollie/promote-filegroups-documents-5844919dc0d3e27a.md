# Promote REJECTED — `5844919dc0d3e27a` on `filegroups/documents`

Generated 2026-05-21T08:34:45Z

PR_AUC regressed at full-train: 1.0000 -> 0.9945

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5844919dc0d3e27a` | `9971aebc51c9247b` | `599cd8822a9e7ae4` |
| PR AUC | 1.0000 | 1.0000 | 0.9945 |
| ROC AUC | 0.9991 | 0.9986 | 0.5000 |
| F1 | 0.9961 | 0.9981 | 0.9972 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 1.0000 -> 0.9945
