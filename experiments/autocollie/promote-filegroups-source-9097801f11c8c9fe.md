# Promote REJECTED — `9097801f11c8c9fe` on `filegroups/source`

Generated 2026-10-30T21:40:52Z

PR_AUC regressed at full-train: 0.9865 -> 0.9659

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9865 -> 0.9869; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9097801f11c8c9fe` | `d1bf268e35cd2960` | `099310b4118a6d97` |
| PR AUC | 0.9865 | 0.9869 | 0.9659 |
| ROC AUC | 0.9858 | 0.9859 | 0.9858 |
| F1 | 0.9394 | 0.9420 | 0.9234 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9865 -> 0.9659
