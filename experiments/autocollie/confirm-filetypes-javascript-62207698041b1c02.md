# Confirm FAIL — 62207698041b1c02 on `filetypes/javascript`

Cycle `20260825T000438-confirm-62207698041b1c02` — 2026-08-25T00:04:38Z

averaged ensemble PR_AUC regressed: 0.9867 -> 0.9636 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `62207698041b1c02` | `d6c5ec7a5c27ac61` | `d6c5ec7a5c27ac61` | `d6c5ec7a5c27ac61` |
| PR AUC | 0.9867 | 0.9606 | 0.9626 | 0.9636 |
| ROC AUC | 0.9814 | 0.9831 | 0.9854 | 0.9877 |
| Recall@L50 | — | 0.7470 | 0.7927 | 0.7393 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
