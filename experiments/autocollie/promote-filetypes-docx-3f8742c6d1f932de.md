# Promote REJECTED — `3f8742c6d1f932de` on `filetypes/docx`

Generated 2026-05-25T20:14:20Z

AUC regressed at full-train: 1.0000 -> 0.9830

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3f8742c6d1f932de` | `32153ddbbb99a2c5` | `0f6b5a778af0b931` |
| PR AUC | 1.0000 | 0.9970 | 0.9970 |
| ROC AUC | 1.0000 | 0.9830 | 0.9830 |
| F1 | 0.9848 | 0.9956 | 0.9956 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9830
