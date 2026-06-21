# Promote REJECTED — `d86b22aa9130ad30` on `filetypes/text`

Generated 2026-06-17T17:47:20Z

AUC regressed at full-train: 0.9695 -> 0.9684

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9414)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d86b22aa9130ad30` | `1de03061afc23afc` | `492f9542645dc533` |
| PR AUC | 0.9414 | 0.9386 | 0.9398 |
| ROC AUC | 0.9695 | 0.9679 | 0.9684 |
| F1 | 0.8364 | 0.8571 | 0.8889 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9695 -> 0.9684
