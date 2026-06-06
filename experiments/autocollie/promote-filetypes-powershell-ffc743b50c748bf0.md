# Promote REJECTED — `ffc743b50c748bf0` on `filetypes/powershell`

Generated 2026-06-06T15:13:17Z

AUC regressed at full-train: 0.9897 -> 0.9882

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9956)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `ffc743b50c748bf0` | `b10f47550c4e94f4` | `c00b6708e48ba915` |
| PR AUC | 0.9956 | 0.9949 | 0.9950 |
| ROC AUC | 0.9897 | 0.9880 | 0.9882 |
| F1 | 0.9678 | 0.9401 | 0.9387 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9897 -> 0.9882
