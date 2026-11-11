# Confirm FAIL — c45a9d762fc22bac on `filetypes/chrome_manifest`

Cycle `20261106T012102-confirm-c45a9d762fc22bac` — 2026-11-06T01:21:02Z

averaged ensemble PR_AUC regressed: 0.9889 -> 0.9798 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c45a9d762fc22bac` | `883d0a55039a3307` | `883d0a55039a3307` | `883d0a55039a3307` |
| PR AUC | 0.9889 | 0.9889 | 0.9514 | 0.9300 |
| ROC AUC | 0.9992 | 0.9992 | 0.9942 | 0.9933 |
| Recall@L50 | — | 0.8889 | 0.8889 | 0.7778 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
