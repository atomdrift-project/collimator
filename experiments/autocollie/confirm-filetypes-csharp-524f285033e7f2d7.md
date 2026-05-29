# Confirm FAIL — 524f285033e7f2d7 on `filetypes/csharp`

Cycle `20260525T204015-confirm-524f285033e7f2d7` — 2026-05-25T20:40:15Z

averaged ensemble PR_AUC regressed: 0.9982 -> 0.9870 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `524f285033e7f2d7` | `02355608a6d46635` | `02355608a6d46635` | `02355608a6d46635` |
| PR AUC | 0.9982 | 0.9867 | 0.9859 | 0.9871 |
| ROC AUC | 1.0000 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.7149 | 0.6561 | 0.6833 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
