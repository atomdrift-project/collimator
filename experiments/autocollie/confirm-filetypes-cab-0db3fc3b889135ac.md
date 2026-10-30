# Confirm FAIL — 0db3fc3b889135ac on `filetypes/cab`

Cycle `20261029T025721-confirm-0db3fc3b889135ac` — 2026-10-29T02:57:21Z

confirmation measured L25 recall regressed: 0.99065 -> 0.98131

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0db3fc3b889135ac` | `efc145c14e6cfe91` | `efc145c14e6cfe91` | `efc145c14e6cfe91` |
| PR AUC | 0.9992 | 0.9979 | 0.9978 | 0.9991 |
| ROC AUC | 0.9935 | 0.9853 | 0.9838 | 0.9928 |
| Recall@L50 | — | 0.8692 | 0.8505 | 0.9533 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
