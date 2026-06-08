# Confirm FAIL — e5f8e1a0eed208a1 on `filetypes/rust`

Cycle `20260608T113404-confirm-e5f8e1a0eed208a1` — 2026-06-08T11:34:04Z

averaged ensemble PR_AUC regressed: 0.9130 -> 0.8968 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e5f8e1a0eed208a1` | `4554e40ee1af3c67` | `4554e40ee1af3c67` | `4554e40ee1af3c67` |
| PR AUC | 0.9130 | 0.8802 | 0.8801 | 0.8634 |
| ROC AUC | 0.9893 | 0.9889 | 0.9882 | 0.9832 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
