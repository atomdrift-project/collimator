# Promote REJECTED — `e2b087c8a7ac180b` on `filetypes/rust`

Generated 2026-05-25T21:27:48Z

PR_AUC regressed at full-train: 0.9000 -> 0.8929

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e2b087c8a7ac180b` | `d9e9561146532c9f` | `e0db81e47b6af3e6` |
| PR AUC | 0.9000 | 0.9074 | 0.8929 |
| ROC AUC | 0.9855 | 0.9888 | 0.9881 |
| F1 | 0.7200 | 0.7879 | 0.8387 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9000 -> 0.8929
