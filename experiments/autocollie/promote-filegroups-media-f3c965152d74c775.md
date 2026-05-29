# Promote REJECTED — `f3c965152d74c775` on `filegroups/media`

Generated 2026-05-27T00:45:41Z

AUC regressed at full-train: 0.9959 -> 0.9941

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9966)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f3c965152d74c775` | `1b59d29ee9688b38` | `04b7d07052468a33` |
| PR AUC | 0.9966 | 0.9949 | 0.9951 |
| ROC AUC | 0.9959 | 0.9938 | 0.9941 |
| F1 | 0.9519 | 0.9474 | 0.9474 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9959 -> 0.9941
