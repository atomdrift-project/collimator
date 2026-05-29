# Confirm FAIL — af1f902cd9ad2bf4 on `filetypes/data`

Cycle `20260525T194138-confirm-af1f902cd9ad2bf4` — 2026-05-25T19:41:38Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9939 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `af1f902cd9ad2bf4` | `e570d1ec8dcb90a8` | `e570d1ec8dcb90a8` | `e570d1ec8dcb90a8` |
| PR AUC | 1.0000 | 0.9954 | 0.9872 | 0.9918 |
| ROC AUC | 1.0000 | 0.9998 | 0.9994 | 0.9996 |
| Recall@3FPM | — | 0.9600 | 0.8200 | 0.9200 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
