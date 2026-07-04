# Promote REJECTED — `04f53a576111ba93` on `filegroups/source`

Generated 2026-07-04T08:10:01Z

AUC regressed at full-train: 0.9982 -> 0.9966

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9990)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `04f53a576111ba93` | `66538b89b739a2bb` | `5dec98b2bf086aa0` |
| PR AUC | 0.9990 | 0.9961 | 0.9962 |
| ROC AUC | 0.9982 | 0.9965 | 0.9966 |
| F1 | 0.9832 | 0.9681 | 0.9669 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9982 -> 0.9966
