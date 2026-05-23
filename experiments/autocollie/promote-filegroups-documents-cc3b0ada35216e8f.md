# Promote REJECTED — `cc3b0ada35216e8f` on `filegroups/documents`

Generated 2026-05-23T21:04:41Z

AUC regressed at full-train: 0.9985 -> 0.9704

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `cc3b0ada35216e8f` | `7dbbba1731b53f20` | `77138f0b8b476f6e` |
| PR AUC | 1.0000 | 0.9996 | 0.9996 |
| ROC AUC | 0.9985 | 0.9672 | 0.9704 |
| F1 | 0.9868 | 0.9965 | 0.9965 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9985 -> 0.9704
