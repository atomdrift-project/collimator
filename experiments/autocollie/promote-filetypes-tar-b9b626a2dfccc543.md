# Promote REJECTED — `b9b626a2dfccc543` on `filetypes/tar`

Generated 2026-05-15T06:43:14Z

AUC regressed at full-train: 1.0000 -> 0.9989

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b9b626a2dfccc543` | `9800d79fbe956d65` | `54fcf051bd8e0353` |
| PR AUC | 1.0000 | 1.0000 | 0.9999 |
| ROC AUC | 1.0000 | 1.0000 | 0.9989 |
| F1 | 0.9895 | 1.0000 | 0.9932 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9989
