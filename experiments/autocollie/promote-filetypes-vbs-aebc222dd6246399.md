# Promote REJECTED — `aebc222dd6246399` on `filetypes/vbs`

Generated 2026-05-26T22:29:28Z

AUC regressed at full-train: 0.9985 -> 0.9806

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9991)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `aebc222dd6246399` | `4a328a326e164d66` | `92e784f47bedfe25` |
| PR AUC | 0.9991 | 0.9961 | 0.9964 |
| ROC AUC | 0.9985 | 0.9789 | 0.9806 |
| F1 | 0.9688 | 0.9857 | 0.9868 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9985 -> 0.9806
