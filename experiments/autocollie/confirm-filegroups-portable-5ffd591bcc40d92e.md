# Confirm FAIL — 5ffd591bcc40d92e on `filegroups/portable`

Cycle `20261030T212439-confirm-5ffd591bcc40d92e` — 2026-10-30T21:24:39Z

confirmation measured L25 recall regressed: 0.80488 -> 0.78184

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5ffd591bcc40d92e` | `943755424ae796a9` | `943755424ae796a9` | `943755424ae796a9` |
| PR AUC | 0.9695 | 0.9782 | 0.9668 | 0.9719 |
| ROC AUC | 0.9943 | 0.9962 | 0.9938 | 0.9946 |
| Recall@L50 | — | 0.7642 | 0.7547 | 0.7737 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
