# Confirm FAIL — bcbadf3afbe9bd0b on `filetypes/java`

Cycle `20260723T050430-confirm-bcbadf3afbe9bd0b` — 2026-07-23T05:04:30Z

averaged ensemble PR_AUC regressed: 0.9583 -> 0.9461 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bcbadf3afbe9bd0b` | `214f3491217bfa3d` | `214f3491217bfa3d` | `214f3491217bfa3d` |
| PR AUC | 0.9583 | 0.9452 | 0.9399 | 0.9408 |
| ROC AUC | 0.9951 | 0.9931 | 0.9918 | 0.9926 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
