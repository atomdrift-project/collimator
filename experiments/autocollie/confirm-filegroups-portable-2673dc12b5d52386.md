# Confirm FAIL — 2673dc12b5d52386 on `filegroups/portable`

Cycle `20260827T100131-confirm-2673dc12b5d52386` — 2026-08-27T10:01:31Z

averaged ensemble PR_AUC regressed: 0.8502 -> 0.7918 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2673dc12b5d52386` | `22b4c2ed152b86f4` | `22b4c2ed152b86f4` | `22b4c2ed152b86f4` |
| PR AUC | 0.8502 | 0.7832 | 0.7863 | 0.7773 |
| ROC AUC | 0.9091 | 0.9433 | 0.9004 | 0.9206 |
| Recall@L50 | — | 0.6872 | 0.6708 | 0.6845 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
