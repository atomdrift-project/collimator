# Confirm FAIL — 067ffa69373bbf8f on `filetypes/xml`

Cycle `20260703T025719-confirm-067ffa69373bbf8f` — 2026-07-03T02:57:19Z

averaged ensemble PR_AUC regressed: 0.2407 -> 0.0621 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `067ffa69373bbf8f` | `874bab574b259c01` | `874bab574b259c01` | `874bab574b259c01` |
| PR AUC | 0.2407 | 0.0464 | 0.0555 | 0.0555 |
| ROC AUC | 0.5997 | 0.5234 | 0.5240 | 0.5233 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
