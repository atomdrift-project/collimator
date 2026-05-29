# Confirm FAIL — acf757f53ad896f2 on `filetypes/php`

Cycle `20260526T184555-confirm-acf757f53ad896f2` — 2026-05-26T18:45:55Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9911 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `acf757f53ad896f2` | `390998bf60b185c1` | `390998bf60b185c1` | `390998bf60b185c1` |
| PR AUC | 1.0000 | 0.9879 | 0.9926 | 0.9911 |
| ROC AUC | 1.0000 | 0.9968 | 0.9972 | 0.9969 |
| Recall@3FPM | — | 0.0160 | 0.1210 | 0.0753 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
