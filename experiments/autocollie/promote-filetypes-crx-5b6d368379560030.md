# Promote REJECTED — `5b6d368379560030` on `filetypes/crx`

Generated 2026-06-28T08:48:19Z

AUC regressed at full-train: 0.9966 -> 0.9939

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9966)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5b6d368379560030` | `b34be1bcd88e24ce` | `a7fad3b252ea532a` |
| PR AUC | 0.9966 | 0.9948 | 0.9939 |
| ROC AUC | 0.9966 | 0.9947 | 0.9939 |
| F1 | 0.9091 | 0.9405 | 0.9349 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9966 -> 0.9939
