# Promote REJECTED — `c76e9f9c3465ff0a` on `filetypes/java`

Generated 2026-06-08T12:00:01Z

AUC regressed at full-train: 0.9607 -> 0.9571

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9605)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c76e9f9c3465ff0a` | `d102f792252f6425` | `aa920728976ba01b` |
| PR AUC | 0.9605 | 0.9656 | 0.9642 |
| ROC AUC | 0.9607 | 0.9560 | 0.9571 |
| F1 | 0.9231 | 0.9524 | 0.9302 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9607 -> 0.9571
