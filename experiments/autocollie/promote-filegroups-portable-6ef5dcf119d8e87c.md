# Promote REJECTED — `6ef5dcf119d8e87c` on `filegroups/portable`

Generated 2026-05-08T20:43:42Z

confirm did not hold: averaged ensemble F1 regressed: 0.9852 -> 0.9728 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble F1 regressed: 0.9852 -> 0.9728 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `6ef5dcf119d8e87c` | `acae07e2f8b688d9` | `—` |
| F1 | 0.9852 | 0.9728 | — |
| ROC AUC | 0.9954 | 0.9953 | — |
| AP | — | — | — |
| recall@3 FP/M (screen) | 0.3593 | 0.4551 | — |
| recall@FP=0 (full-train) | — | — | — |
| recall@FP=5 (full-train) | — | — | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble F1 regressed: 0.9852 -> 0.9728 (tol 0.0050, K=3)
