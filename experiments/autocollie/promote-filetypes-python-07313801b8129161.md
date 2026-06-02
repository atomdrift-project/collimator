# Promote REJECTED — `07313801b8129161` on `filetypes/python`

Generated 2026-06-02T01:25:35Z

AUC regressed at full-train: 0.9993 -> 0.9982

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9992)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `07313801b8129161` | `674abd9208bae962` | `dc8f62d9f3d7cc15` |
| PR AUC | 0.9992 | 0.9975 | 0.9975 |
| ROC AUC | 0.9993 | 0.9981 | 0.9982 |
| F1 | 0.9820 | 0.9712 | 0.9712 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9993 -> 0.9982
