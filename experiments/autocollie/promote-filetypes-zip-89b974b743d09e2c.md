# Promote REJECTED — `89b974b743d09e2c` on `filetypes/zip`

Generated 2026-05-26T23:09:58Z

AUC regressed at full-train: 0.9982 -> 0.9965

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `89b974b743d09e2c` | `9a58400e04407d76` | `0b3a7dd6eb49a141` |
| PR AUC | 0.9999 | 0.9998 | 0.9998 |
| ROC AUC | 0.9982 | 0.9964 | 0.9965 |
| F1 | 0.9883 | 0.9955 | 0.9959 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9982 -> 0.9965
