# Promote REJECTED — `031999071f35bb21` on `filetypes/python`

Generated 2026-06-08T18:26:02Z

AUC regressed at full-train: 0.9991 -> 0.9955

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9990)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `031999071f35bb21` | `92817fa0b92c8d20` | `0d9f7892d14dc0e7` |
| PR AUC | 0.9990 | 0.9945 | 0.9945 |
| ROC AUC | 0.9991 | 0.9956 | 0.9955 |
| F1 | 0.9836 | 0.9637 | 0.9666 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9991 -> 0.9955
