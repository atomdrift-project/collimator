# Promote REJECTED — `e67b060e5bcc3a6a` on `filegroups/scripts`

Generated 2026-07-04T08:38:13Z

AUC regressed at full-train: 0.9977 -> 0.9955

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9979)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e67b060e5bcc3a6a` | `d082d95ae7ab28d4` | `8662ae5f138e559d` |
| PR AUC | 0.9979 | 0.9939 | 0.9945 |
| ROC AUC | 0.9977 | 0.9951 | 0.9955 |
| F1 | 0.9725 | 0.9553 | 0.9531 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9977 -> 0.9955
