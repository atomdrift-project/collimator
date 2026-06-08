# Promote REJECTED — `67a2ca64c96a750c` on `filetypes/java`

Generated 2026-06-08T10:25:59Z

AUC regressed at full-train: 0.9607 -> 0.9571

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9605)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `67a2ca64c96a750c` | `24562e9be4af75ed` | `909044ab6dc75813` |
| PR AUC | 0.9605 | 0.9656 | 0.9642 |
| ROC AUC | 0.9607 | 0.9560 | 0.9571 |
| F1 | 0.9231 | 0.9524 | 0.9302 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9607 -> 0.9571
