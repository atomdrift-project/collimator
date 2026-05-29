# Promote REJECTED — `bf193423d4373393` on `filetypes/batch`

Generated 2026-05-26T22:29:57Z

AUC regressed at full-train: 0.9982 -> 0.9968

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9998)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `bf193423d4373393` | `0f2f5fd66767d23a` | `eaeff7e6ce6a25f6` |
| PR AUC | 0.9998 | 0.9996 | 0.9996 |
| ROC AUC | 0.9982 | 0.9963 | 0.9968 |
| F1 | 0.9850 | 0.9871 | 0.9896 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9982 -> 0.9968
