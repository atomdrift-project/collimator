# Confirm FAIL — 0e86a803364abab2 on `filetypes/rust`

Cycle `20260606T180654-confirm-0e86a803364abab2` — 2026-06-06T18:06:54Z

averaged ensemble PR_AUC regressed: 0.1110 -> 0.0934 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0e86a803364abab2` | `a29bd15e7af5328a` | `a29bd15e7af5328a` | `a29bd15e7af5328a` |
| PR AUC | 0.1110 | 0.0883 | 0.0862 | 0.0825 |
| ROC AUC | 0.7316 | 0.4544 | 0.5040 | 0.5117 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
