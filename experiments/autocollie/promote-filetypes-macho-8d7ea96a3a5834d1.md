# Promote REJECTED — `8d7ea96a3a5834d1` on `filetypes/macho`

Generated 2026-11-02T19:06:55Z

PR_AUC regressed at full-train: 0.9881 -> 0.9807

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9881 -> 0.9896; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `8d7ea96a3a5834d1` | `721d9dd5e82d351e` | `ddf3f80e46a60506` |
| PR AUC | 0.9881 | 0.9896 | 0.9807 |
| ROC AUC | 0.9988 | 0.9989 | 0.9977 |
| F1 | 0.9441 | 0.9563 | 0.9412 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9881 -> 0.9807
