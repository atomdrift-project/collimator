# Promote REJECTED — `d48e6f193c53a02d` on `filetypes/package.json`

Generated 2026-07-04T13:52:42Z

AUC regressed at full-train: 0.9970 -> 0.9954

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9966)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d48e6f193c53a02d` | `76c5e23773dc1db1` | `87213bb109d46e8f` |
| PR AUC | 0.9966 | 0.9957 | 0.9957 |
| ROC AUC | 0.9970 | 0.9954 | 0.9954 |
| F1 | 0.9776 | 0.9908 | 0.9910 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9970 -> 0.9954
