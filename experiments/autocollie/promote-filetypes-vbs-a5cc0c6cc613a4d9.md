# Promote REJECTED — `a5cc0c6cc613a4d9` on `filetypes/vbs`

Generated 2026-06-13T01:21:38Z

AUC regressed at full-train: 0.9930 -> 0.9918

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9980)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a5cc0c6cc613a4d9` | `691cc4f89efc4bb0` | `f2c8755a03b95c0b` |
| PR AUC | 0.9980 | 0.9976 | 0.9977 |
| ROC AUC | 0.9930 | 0.9914 | 0.9918 |
| F1 | 0.9554 | 0.9758 | 0.9722 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9930 -> 0.9918
