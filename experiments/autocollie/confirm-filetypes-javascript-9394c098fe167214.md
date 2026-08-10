# Confirm FAIL — 9394c098fe167214 on `filetypes/javascript`

Cycle `20260805T015957-confirm-9394c098fe167214` — 2026-08-05T01:59:57Z

averaged ensemble PR_AUC regressed: 0.9847 -> 0.9664 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9394c098fe167214` | `385222f3fbee6c16` | `385222f3fbee6c16` | `385222f3fbee6c16` |
| PR AUC | 0.9847 | 0.9656 | 0.9659 | 0.9645 |
| ROC AUC | 0.9779 | 0.9879 | 0.9879 | 0.9875 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
