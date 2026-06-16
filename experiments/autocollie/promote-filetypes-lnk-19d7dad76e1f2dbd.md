# Promote REJECTED — `19d7dad76e1f2dbd` on `filetypes/lnk`

Generated 2026-06-16T05:06:36Z

AUC regressed at full-train: 0.9890 -> 0.9877

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9977)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `19d7dad76e1f2dbd` | `c2dbadd11d5768ed` | `0016754bcff0007b` |
| PR AUC | 0.9977 | 0.9975 | 0.9974 |
| ROC AUC | 0.9890 | 0.9882 | 0.9877 |
| F1 | 0.9269 | 0.9853 | 0.9845 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9890 -> 0.9877
