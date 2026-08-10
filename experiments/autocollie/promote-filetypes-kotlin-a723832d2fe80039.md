# Promote REJECTED — `a723832d2fe80039` on `filetypes/kotlin`

Generated 2026-08-04T23:06:23Z

AUC regressed at full-train: 0.9836 -> 0.9823

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9764)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a723832d2fe80039` | `67a37b083eb06646` | `9ab823ffbff8a79c` |
| PR AUC | 0.9764 | 0.9730 | 0.9739 |
| ROC AUC | 0.9836 | 0.9818 | 0.9823 |
| F1 | 0.9059 | 0.9056 | 0.9065 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9836 -> 0.9823
