# Promote REJECTED — `6324791d9c8bc111` on `filetypes/vbs`

Generated 2026-05-25T20:33:16Z

AUC regressed at full-train: 0.9989 -> 0.9783

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9993)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `6324791d9c8bc111` | `ef97db65071dbdc2` | `e87ddbb11f06e806` |
| PR AUC | 0.9993 | 0.9957 | 0.9956 |
| ROC AUC | 0.9989 | 0.9783 | 0.9783 |
| F1 | 0.9764 | 0.9890 | 0.9901 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9989 -> 0.9783
