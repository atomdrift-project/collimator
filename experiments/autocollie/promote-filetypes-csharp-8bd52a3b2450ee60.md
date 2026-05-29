# Promote REJECTED — `8bd52a3b2450ee60` on `filetypes/csharp`

Generated 2026-05-27T00:30:32Z

AUC regressed at full-train: 0.9937 -> 0.9924

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9882)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `8bd52a3b2450ee60` | `97935a46ec8491ad` | `fc7af0a57ad94bad` |
| PR AUC | 0.9882 | 0.9869 | 0.9864 |
| ROC AUC | 0.9937 | 0.9930 | 0.9924 |
| F1 | 0.9565 | 0.8974 | 0.9032 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9937 -> 0.9924
