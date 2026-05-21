# Confirm FAIL — d7e3f1d4907fbddb on `filetypes/pdf`

Cycle `20260520T065532-confirm-d7e3f1d4907fbddb` — 2026-05-20T06:55:32Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9942 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d7e3f1d4907fbddb` | `6b9389fca30b7949` | `6b9389fca30b7949` | `6b9389fca30b7949` |
| PR AUC | 1.0000 | 0.9942 | 0.9942 | 0.9942 |
| ROC AUC | 0.9991 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
