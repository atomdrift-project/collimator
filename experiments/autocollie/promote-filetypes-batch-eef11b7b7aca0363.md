# Promote REJECTED — `eef11b7b7aca0363` on `filetypes/batch`

Generated 2026-06-06T20:36:08Z

AUC regressed at full-train: 0.9983 -> 0.9962

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9998)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `eef11b7b7aca0363` | `73ac840846a92651` | `a34b35cbe7497a50` |
| PR AUC | 0.9998 | 0.9997 | 0.9997 |
| ROC AUC | 0.9983 | 0.9956 | 0.9962 |
| F1 | 0.9890 | 0.9916 | 0.9930 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9983 -> 0.9962
