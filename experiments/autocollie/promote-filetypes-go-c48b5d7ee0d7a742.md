# Promote REJECTED — `c48b5d7ee0d7a742` on `filetypes/go`

Generated 2026-06-28T13:50:58Z

AUC regressed at full-train: 0.9763 -> 0.9733

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9247)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c48b5d7ee0d7a742` | `87299b065570518e` | `91495e9e727bdd3f` |
| PR AUC | 0.9247 | 0.9249 | 0.9250 |
| ROC AUC | 0.9763 | 0.9726 | 0.9733 |
| F1 | 0.8364 | 0.8438 | 0.8433 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9763 -> 0.9733
