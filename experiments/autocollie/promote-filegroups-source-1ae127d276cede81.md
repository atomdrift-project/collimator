# Promote REJECTED — `1ae127d276cede81` on `filegroups/source`

Generated 2026-11-12T20:39:35Z

PR_AUC regressed at full-train: 0.9828 -> 0.9696

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9828 -> 0.9895; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `1ae127d276cede81` | `e61a09d820415883` | `af40b2ba272c4002` |
| PR AUC | 0.9828 | 0.9895 | 0.9696 |
| ROC AUC | 0.9810 | 0.9891 | 0.9873 |
| F1 | 0.9378 | 0.9496 | 0.9321 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9828 -> 0.9696
