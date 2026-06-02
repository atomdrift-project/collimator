# Promote REJECTED — `485629e58079417a` on `filetypes/jpeg`

Generated 2026-06-02T02:58:40Z

PR_AUC regressed at full-train: 0.9692 -> 0.9579

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9692)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `485629e58079417a` | `b35c23bdf8c1b4db` | `20400618d663ca5e` |
| PR AUC | 0.9692 | 0.9700 | 0.9579 |
| ROC AUC | 0.9832 | 0.9840 | 0.9777 |
| F1 | 0.8438 | 0.9000 | 0.8889 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9692 -> 0.9579
