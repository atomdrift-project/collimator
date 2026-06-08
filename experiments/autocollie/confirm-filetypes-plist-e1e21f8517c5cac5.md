# Confirm FAIL — e1e21f8517c5cac5 on `filetypes/plist`

Cycle `20260608T060126-confirm-e1e21f8517c5cac5` — 2026-06-08T06:01:26Z

averaged ensemble PR_AUC regressed: 0.2819 -> 0.2404 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e1e21f8517c5cac5` | `05769e496dee32a3` | `05769e496dee32a3` | `05769e496dee32a3` |
| PR AUC | 0.2819 | 0.2237 | 0.2630 | 0.1371 |
| ROC AUC | 0.8021 | 0.7865 | 0.8202 | 0.6298 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
