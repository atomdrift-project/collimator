# Promote REJECTED — `589b9b4aec45069c` on `filegroups/documents`

Generated 2026-05-20T19:31:23Z

PR_AUC regressed at full-train: 1.0000 -> 0.9945

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `589b9b4aec45069c` | `bb6124eb5d3ce754` | `a082d50b9e2497cd` |
| PR AUC | 1.0000 | 1.0000 | 0.9945 |
| ROC AUC | 0.9991 | 0.9986 | 0.5000 |
| F1 | 0.9949 | 0.9981 | 0.9972 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 1.0000 -> 0.9945
