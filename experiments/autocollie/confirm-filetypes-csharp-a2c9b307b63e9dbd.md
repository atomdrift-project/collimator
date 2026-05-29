# Confirm FAIL — a2c9b307b63e9dbd on `filetypes/csharp`

Cycle `20260526T231524-confirm-a2c9b307b63e9dbd` — 2026-05-26T23:15:24Z

averaged ensemble PR_AUC regressed: 0.9976 -> 0.9716 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a2c9b307b63e9dbd` | `a84c923d35a2545c` | `a84c923d35a2545c` | `a84c923d35a2545c` |
| PR AUC | 0.9976 | 0.9677 | 0.9700 | 0.9695 |
| ROC AUC | 1.0000 | 0.9979 | 0.9982 | 0.9977 |
| Recall@3FPM | — | 0.7240 | 0.7466 | 0.7466 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
