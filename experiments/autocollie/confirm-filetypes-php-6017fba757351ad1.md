# Confirm FAIL — 6017fba757351ad1 on `filetypes/php`

Cycle `20260821T131121-confirm-6017fba757351ad1` — 2026-08-21T13:11:21Z

averaged ensemble PR_AUC regressed: 0.8909 -> 0.8383 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6017fba757351ad1` | `75d208a59044c883` | `75d208a59044c883` | `75d208a59044c883` |
| PR AUC | 0.8909 | 0.8336 | 0.8438 | 0.8297 |
| ROC AUC | 0.9606 | 0.9601 | 0.9654 | 0.9639 |
| Recall@L50 | — | 0.6400 | 0.6769 | 0.6425 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
