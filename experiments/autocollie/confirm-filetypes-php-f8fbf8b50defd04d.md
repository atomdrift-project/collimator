# Confirm FAIL — f8fbf8b50defd04d on `filetypes/php`

Cycle `20260526T215225-confirm-f8fbf8b50defd04d` — 2026-05-26T21:52:25Z

averaged ensemble PR_AUC regressed: 0.9999 -> 0.9918 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f8fbf8b50defd04d` | `4d39c5df717db1b7` | `4d39c5df717db1b7` | `4d39c5df717db1b7` |
| PR AUC | 0.9999 | 0.9900 | 0.9932 | 0.9924 |
| ROC AUC | 0.9999 | 0.9963 | 0.9967 | 0.9964 |
| Recall@3FPM | — | 0.0662 | 0.2306 | 0.1963 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
