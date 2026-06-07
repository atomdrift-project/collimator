# Confirm FAIL — 2757c6c31fd77735 on `filetypes/makefile`

Cycle `20260606T180835-confirm-2757c6c31fd77735` — 2026-06-06T18:08:35Z

averaged ensemble PR_AUC regressed: 0.6667 -> 0.6220 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2757c6c31fd77735` | `1ea28330dd684c2b` | `1ea28330dd684c2b` | `1ea28330dd684c2b` |
| PR AUC | 0.6667 | 0.6220 | 0.6220 | 0.5595 |
| ROC AUC | 0.9167 | 0.9531 | 0.9531 | 0.9375 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
