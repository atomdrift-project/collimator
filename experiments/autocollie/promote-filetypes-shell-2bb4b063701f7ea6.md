# Promote REJECTED — `2bb4b063701f7ea6` on `filetypes/shell`

Generated 2026-06-28T13:23:47Z

AUC regressed at full-train: 0.9980 -> 0.9957

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9968)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `2bb4b063701f7ea6` | `edd466cbd9ba26cc` | `536dd65304a17473` |
| PR AUC | 0.9968 | 0.9941 | 0.9943 |
| ROC AUC | 0.9980 | 0.9955 | 0.9957 |
| F1 | 0.9621 | 0.9608 | 0.9650 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9980 -> 0.9957
