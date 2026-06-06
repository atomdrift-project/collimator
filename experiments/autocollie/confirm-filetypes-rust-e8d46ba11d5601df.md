# Confirm FAIL — e8d46ba11d5601df on `filetypes/rust`

Cycle `20260606T180643-confirm-e8d46ba11d5601df` — 2026-06-06T18:06:43Z

averaged ensemble PR_AUC regressed: 0.1110 -> 0.0934 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e8d46ba11d5601df` | `a4845e112f76ea10` | `a4845e112f76ea10` | `a4845e112f76ea10` |
| PR AUC | 0.1110 | 0.0883 | 0.0862 | 0.0825 |
| ROC AUC | 0.7316 | 0.4544 | 0.5040 | 0.5117 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
