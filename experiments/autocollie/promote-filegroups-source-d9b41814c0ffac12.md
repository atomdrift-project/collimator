# Promote REJECTED — `d9b41814c0ffac12` on `filegroups/source`

Generated 2026-06-28T12:54:29Z

AUC regressed at full-train: 0.9983 -> 0.9965

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9991)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d9b41814c0ffac12` | `1eba2caf8d8eaca6` | `12a722e2da8303c0` |
| PR AUC | 0.9991 | 0.9961 | 0.9961 |
| ROC AUC | 0.9983 | 0.9965 | 0.9965 |
| F1 | 0.9834 | 0.9676 | 0.9619 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9983 -> 0.9965
