# Promote REJECTED — `7360ec684c546a48` on `filetypes/java`

Generated 2026-05-27T05:39:50Z

AUC regressed at full-train: 0.9977 -> 0.8466

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.2292)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `7360ec684c546a48` | `d8f9f48cf5af3a5a` | `ea0b4052ac2a8f28` |
| PR AUC | 0.2292 | 0.3728 | 0.4766 |
| ROC AUC | 0.9977 | 0.9559 | 0.8466 |
| F1 | 0.4000 | 0.5000 | 0.5714 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9977 -> 0.8466
