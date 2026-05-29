# Confirm FAIL — 38e9e3b35b273d4e on `filetypes/php`

Cycle `20260526T215229-confirm-38e9e3b35b273d4e` — 2026-05-26T21:52:29Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9928 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `38e9e3b35b273d4e` | `d10c99a69047ca29` | `d10c99a69047ca29` | `d10c99a69047ca29` |
| PR AUC | 1.0000 | 0.9922 | 0.9928 | 0.9930 |
| ROC AUC | 1.0000 | 0.9967 | 0.9968 | 0.9965 |
| Recall@3FPM | — | 0.1507 | 0.1963 | 0.2603 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
