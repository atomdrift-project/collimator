# Promote REJECTED — `9071b393c5cb8e3b` on `filetypes/powershell`

Generated 2026-06-06T15:12:51Z

AUC regressed at full-train: 0.9894 -> 0.9882

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9955)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9071b393c5cb8e3b` | `6f6354df0865d361` | `1a046125366e7524` |
| PR AUC | 0.9955 | 0.9949 | 0.9950 |
| ROC AUC | 0.9894 | 0.9880 | 0.9882 |
| F1 | 0.9686 | 0.9401 | 0.9387 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9894 -> 0.9882
