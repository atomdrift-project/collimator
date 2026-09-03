# Confirm FAIL — fbec14a35cd48426 on `filetypes/python-bytecode`

Cycle `20260825T000108-confirm-fbec14a35cd48426` — 2026-08-25T00:01:08Z

averaged ensemble PR_AUC regressed: 0.7998 -> 0.6982 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fbec14a35cd48426` | `1949985d0920257f` | `1949985d0920257f` | `1949985d0920257f` |
| PR AUC | 0.7998 | 0.6928 | 0.7092 | 0.7056 |
| ROC AUC | 0.9403 | 0.9410 | 0.9242 | 0.9354 |
| Recall@L50 | — | 0.6638 | 0.6638 | 0.6594 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
