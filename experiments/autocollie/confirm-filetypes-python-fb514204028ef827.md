# Confirm FAIL — fb514204028ef827 on `filetypes/python`

Cycle `20260826T231411-confirm-fb514204028ef827` — 2026-08-26T23:14:11Z

averaged ensemble PR_AUC regressed: 0.9600 -> 0.8947 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fb514204028ef827` | `322a458f1f35cd33` | `322a458f1f35cd33` | `322a458f1f35cd33` |
| PR AUC | 0.9600 | 0.8921 | 0.8885 | 0.8911 |
| ROC AUC | 0.9794 | 0.9780 | 0.9779 | 0.9788 |
| Recall@L50 | — | 0.5238 | 0.5443 | 0.5121 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
