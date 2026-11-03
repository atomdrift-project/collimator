# Promote REJECTED — `5ce32696fa36da2b` on `filetypes/c`

Generated 2026-11-02T22:22:41Z

PR_AUC regressed at full-train: 0.9434 -> 0.9006

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9434 -> 0.9420; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5ce32696fa36da2b` | `81f0f458ce64414c` | `81921777072f9ed8` |
| PR AUC | 0.9434 | 0.9420 | 0.9006 |
| ROC AUC | 0.9784 | 0.9774 | 0.9817 |
| F1 | 0.8459 | 0.8599 | 0.8400 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9434 -> 0.9006
