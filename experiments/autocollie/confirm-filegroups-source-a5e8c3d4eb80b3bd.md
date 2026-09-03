# Confirm FAIL — a5e8c3d4eb80b3bd on `filegroups/source`

Cycle `20260825T000152-confirm-a5e8c3d4eb80b3bd` — 2026-08-25T00:01:52Z

averaged ensemble PR_AUC regressed: 0.9379 -> 0.6704 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a5e8c3d4eb80b3bd` | `8dae835fd46ed82d` | `8dae835fd46ed82d` | `8dae835fd46ed82d` |
| PR AUC | 0.9379 | 0.6671 | 0.6617 | 0.6668 |
| ROC AUC | 0.9288 | 0.9336 | 0.9236 | 0.9328 |
| Recall@L50 | — | 0.3451 | 0.3397 | 0.3420 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
