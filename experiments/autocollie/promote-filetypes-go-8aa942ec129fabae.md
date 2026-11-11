# Promote REJECTED — `8aa942ec129fabae` on `filetypes/go`

Generated 2026-11-06T01:27:34Z

PR_AUC regressed at full-train: 0.9305 -> 0.9002

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9305 -> 0.9415; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `8aa942ec129fabae` | `2aa1669fa8474cc1` | `a0ff58a37058849d` |
| PR AUC | 0.9305 | 0.9415 | 0.9002 |
| ROC AUC | 0.9741 | 0.9804 | 0.9785 |
| F1 | 0.8678 | 0.9052 | 0.8738 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9305 -> 0.9002
