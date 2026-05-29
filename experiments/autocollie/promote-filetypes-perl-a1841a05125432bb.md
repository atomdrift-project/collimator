# Promote REJECTED — `a1841a05125432bb` on `filetypes/perl`

Generated 2026-05-26T19:46:26Z

PR_AUC regressed at full-train: 1.0000 -> 0.9940

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a1841a05125432bb` | `cfae70c0175e470d` | `48f9f972da41a591` |
| PR AUC | 1.0000 | 0.9959 | 0.9940 |
| ROC AUC | 1.0000 | 0.9996 | 0.9994 |
| F1 | 0.9375 | 0.9756 | 0.9756 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 1.0000 -> 0.9940
