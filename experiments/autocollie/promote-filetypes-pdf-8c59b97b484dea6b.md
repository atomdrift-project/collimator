# Promote REJECTED — `8c59b97b484dea6b` on `filetypes/pdf`

Generated 2026-06-01T12:58:34Z

AUC regressed at full-train: 0.9992 -> 0.9948

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `8c59b97b484dea6b` | `3098726c5f4d31d3` | `c56c3cffc9d6c45d` |
| PR AUC | 1.0000 | 0.9999 | 0.9999 |
| ROC AUC | 0.9992 | 0.9950 | 0.9948 |
| F1 | 0.9967 | 0.9954 | 0.9954 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9992 -> 0.9948
