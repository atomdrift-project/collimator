# Promote REJECTED — `93efc52980318a92` on `filetypes/c`

Generated 2026-10-30T23:19:54Z

PR_AUC regressed at full-train: 0.9424 -> 0.8806

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9424 -> 0.9498; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `93efc52980318a92` | `fa87f90ab8f48ceb` | `7adcc19aae1dfef1` |
| PR AUC | 0.9424 | 0.9498 | 0.8806 |
| ROC AUC | 0.9783 | 0.9811 | 0.9799 |
| F1 | 0.8434 | 0.8730 | 0.8267 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9424 -> 0.8806
