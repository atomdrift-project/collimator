# Promote REJECTED — `0601cc794c837c97` on `filetypes/java_class`

Generated 2026-05-26T19:20:58Z

AUC regressed at full-train: 1.0000 -> 0.9990

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0601cc794c837c97` | `7c0bc9aeafb27952` | `5799f98b6e2cd663` |
| PR AUC | 1.0000 | 0.9960 | 0.9958 |
| ROC AUC | 1.0000 | 0.9990 | 0.9990 |
| F1 | 0.9844 | 0.9770 | 0.9770 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9990
