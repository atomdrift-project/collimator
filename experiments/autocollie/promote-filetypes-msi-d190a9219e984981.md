# Promote REJECTED — `d190a9219e984981` on `filetypes/msi`

Generated 2026-05-26T22:00:56Z

AUC regressed at full-train: 0.9990 -> 0.9967

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d190a9219e984981` | `09c905a98a4b427f` | `332c8f7a1940ad88` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9990 | 0.9970 | 0.9967 |
| F1 | 0.9928 | 0.9967 | 0.9967 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9990 -> 0.9967
