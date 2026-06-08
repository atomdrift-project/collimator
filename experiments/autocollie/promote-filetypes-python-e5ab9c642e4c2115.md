# Promote REJECTED — `e5ab9c642e4c2115` on `filetypes/python`

Generated 2026-06-08T18:27:47Z

AUC regressed at full-train: 0.9990 -> 0.9955

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9990)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e5ab9c642e4c2115` | `2cde5a0ba94f06b5` | `16b977c30d19c9e7` |
| PR AUC | 0.9990 | 0.9943 | 0.9945 |
| ROC AUC | 0.9990 | 0.9953 | 0.9955 |
| F1 | 0.9853 | 0.9606 | 0.9646 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9990 -> 0.9955
