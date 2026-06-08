# Confirm FAIL — ea68f28b6cae3378 on `filetypes/python`

Cycle `20260608T182257-confirm-ea68f28b6cae3378` — 2026-06-08T18:22:57Z

averaged ensemble PR_AUC regressed: 0.8711 -> 0.8377 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ea68f28b6cae3378` | `27801332902d4955` | `27801332902d4955` | `27801332902d4955` |
| PR AUC | 0.8711 | 0.8377 | 0.8308 | 0.8325 |
| ROC AUC | 0.9161 | 0.9390 | 0.9301 | 0.9337 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
