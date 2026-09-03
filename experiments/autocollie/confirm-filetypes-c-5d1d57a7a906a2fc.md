# Confirm FAIL — 5d1d57a7a906a2fc on `filetypes/c`

Cycle `20260827T100211-confirm-5d1d57a7a906a2fc` — 2026-08-27T10:02:11Z

averaged ensemble PR_AUC regressed: 0.7315 -> 0.4128 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5d1d57a7a906a2fc` | `13887a900c37d68f` | `13887a900c37d68f` | `13887a900c37d68f` |
| PR AUC | 0.7315 | 0.4100 | 0.3968 | 0.4065 |
| ROC AUC | 0.8569 | 0.8353 | 0.8624 | 0.8534 |
| Recall@L50 | — | 0.2080 | 0.1961 | 0.2114 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
