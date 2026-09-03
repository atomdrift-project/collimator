# Confirm FAIL — eb3cb9b2669c7be1 on `filetypes/java`

Cycle `20260825T214619-confirm-eb3cb9b2669c7be1` — 2026-08-25T21:46:19Z

averaged ensemble PR_AUC regressed: 0.8077 -> 0.7167 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eb3cb9b2669c7be1` | `459dbeaaea882eee` | `459dbeaaea882eee` | `459dbeaaea882eee` |
| PR AUC | 0.8077 | 0.7108 | 0.6941 | 0.7092 |
| ROC AUC | 0.9779 | 0.9747 | 0.9798 | 0.9771 |
| Recall@L50 | — | 0.2414 | 0.2500 | 0.2004 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
