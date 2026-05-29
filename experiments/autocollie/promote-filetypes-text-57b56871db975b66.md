# Promote REJECTED — `57b56871db975b66` on `filetypes/text`

Generated 2026-05-27T01:52:45Z

PR_AUC regressed at full-train: 0.9691 -> 0.9593

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9691)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `57b56871db975b66` | `d7f5b5f653854a33` | `88dd8066afbdcd2e` |
| PR AUC | 0.9691 | 0.9717 | 0.9593 |
| ROC AUC | 0.9851 | 0.9872 | 0.9817 |
| F1 | 0.8800 | 0.9130 | 0.8936 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9691 -> 0.9593
