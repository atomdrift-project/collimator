# Promote REJECTED — `a03d38247305ae9e` on `filetypes/rust`

Generated 2026-07-18T13:54:37Z

AUC regressed at full-train: 0.9677 -> 0.9657

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.8095)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a03d38247305ae9e` | `370a4f6745d56aa6` | `df101ff14a1b0776` |
| PR AUC | 0.8095 | 0.8443 | 0.8316 |
| ROC AUC | 0.9677 | 0.9633 | 0.9657 |
| F1 | 0.7391 | 0.8000 | 0.8000 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9677 -> 0.9657
