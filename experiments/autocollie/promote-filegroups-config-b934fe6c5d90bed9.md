# Promote REJECTED — `b934fe6c5d90bed9` on `filegroups/config`

Generated 2026-10-30T21:03:42Z

PR_AUC regressed at full-train: 0.9757 -> 0.9653

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9757 -> 0.9789; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b934fe6c5d90bed9` | `a3beb52955e78629` | `3667d7741c42f678` |
| PR AUC | 0.9757 | 0.9789 | 0.9653 |
| ROC AUC | 0.9812 | 0.9828 | 0.9825 |
| F1 | 0.6483 | 0.9703 | 0.9639 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9757 -> 0.9653
