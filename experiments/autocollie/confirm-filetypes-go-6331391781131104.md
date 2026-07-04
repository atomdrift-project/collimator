# Confirm FAIL — 6331391781131104 on `filetypes/go`

Cycle `20260704T114322-confirm-6331391781131104` — 2026-07-04T11:43:22Z

averaged ensemble PR_AUC regressed: 0.9623 -> 0.9075 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6331391781131104` | `842bca558ac8120c` | `842bca558ac8120c` | `842bca558ac8120c` |
| PR AUC | 0.9623 | 0.9046 | 0.9042 | 0.9047 |
| ROC AUC | 0.9865 | 0.9660 | 0.9665 | 0.9654 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
