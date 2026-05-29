# Promote REJECTED — `1547b4e8d80f09a8` on `filetypes/msi`

Generated 2026-05-25T20:23:49Z

AUC regressed at full-train: 1.0000 -> 0.9973

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `1547b4e8d80f09a8` | `d359ca514f554c0a` | `afe8e45711262e8b` |
| PR AUC | 1.0000 | 0.9999 | 0.9999 |
| ROC AUC | 1.0000 | 0.9970 | 0.9973 |
| F1 | 1.0000 | 0.9950 | 0.9967 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9973
