# Confirm FAIL — 3639896e9723ddf0 on `filetypes/rust`

Cycle `20260527T053534-confirm-3639896e9723ddf0` — 2026-05-27T05:35:34Z

averaged ensemble PR_AUC regressed: 0.9101 -> 0.8908 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3639896e9723ddf0` | `989d5321a83b00ab` | `989d5321a83b00ab` | `989d5321a83b00ab` |
| PR AUC | 0.9101 | 0.9020 | 0.6254 | 0.9307 |
| ROC AUC | 0.9898 | 0.9881 | 0.9545 | 0.9909 |
| Recall@3FPM | — | 0.3846 | 0.0769 | 0.5385 |
| verdict | — | FAIL | FAIL | PASS |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
