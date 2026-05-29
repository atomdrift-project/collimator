# Confirm FAIL — fd64b5f83279b6ae on `filetypes/plist`

Cycle `20260525T210101-confirm-fd64b5f83279b6ae` — 2026-05-25T21:01:01Z

averaged ensemble PR_AUC regressed: 0.9849 -> 0.9586 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fd64b5f83279b6ae` | `75f463461fc6231c` | `75f463461fc6231c` | `75f463461fc6231c` |
| PR AUC | 0.9849 | 0.9575 | 0.9530 | 0.9566 |
| ROC AUC | 0.9985 | 0.9955 | 0.9949 | 0.9954 |
| Recall@3FPM | — | 0.7302 | 0.7302 | 0.8254 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
