# Promote REJECTED — `2d12df1fc1c87c02` on `filetypes/text`

Generated 2026-05-27T01:52:49Z

AUC regressed at full-train: 0.9843 -> 0.9826

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9679)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `2d12df1fc1c87c02` | `79b47489495f6ba7` | `ecba12fe2f376373` |
| PR AUC | 0.9679 | 0.9676 | 0.9638 |
| ROC AUC | 0.9843 | 0.9844 | 0.9826 |
| F1 | 0.8627 | 0.8750 | 0.8750 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9843 -> 0.9826
