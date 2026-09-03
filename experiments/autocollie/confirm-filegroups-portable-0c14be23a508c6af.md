# Confirm FAIL — 0c14be23a508c6af on `filegroups/portable`

Cycle `20260824T234523-confirm-0c14be23a508c6af` — 2026-08-24T23:45:23Z

averaged ensemble PR_AUC regressed: 0.8769 -> 0.7929 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0c14be23a508c6af` | `68956494ad12a5c6` | `68956494ad12a5c6` | `68956494ad12a5c6` |
| PR AUC | 0.8769 | 0.7935 | 0.7908 | 0.7724 |
| ROC AUC | 0.9437 | 0.9334 | 0.9309 | 0.9263 |
| Recall@L50 | — | 0.6823 | 0.6781 | 0.6754 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
