# Confirm FAIL — a002837ef11e6f6b on `filegroups/portable`

Cycle `20260614T200905-confirm-a002837ef11e6f6b` — 2026-06-14T20:09:05Z

averaged ensemble PR_AUC regressed: 0.9224 -> 0.8492 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a002837ef11e6f6b` | `49b7d5a5e104fe3f` | `49b7d5a5e104fe3f` | `49b7d5a5e104fe3f` |
| PR AUC | 0.9224 | 0.8490 | 0.8477 | 0.8483 |
| ROC AUC | 0.9723 | 0.9591 | 0.9389 | 0.9589 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
