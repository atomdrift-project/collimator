# Promote REJECTED — `766e183dc546441a` on `filetypes/jar`

Generated 2026-06-09T10:59:09Z

AUC regressed at full-train: 0.9871 -> 0.9859

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9942)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `766e183dc546441a` | `faa6e2db72506f18` | `7b959b7c3336c3c8` |
| PR AUC | 0.9942 | 0.9929 | 0.9936 |
| ROC AUC | 0.9871 | 0.9843 | 0.9859 |
| F1 | 0.9335 | 0.9496 | 0.9534 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9871 -> 0.9859
