# Confirm FAIL — 6e57e827c40fd5ec on `filetypes/go`

Cycle `20260705T180747-confirm-6e57e827c40fd5ec` — 2026-07-05T18:07:47Z

averaged ensemble PR_AUC regressed: 0.4334 -> 0.2839 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6e57e827c40fd5ec` | `1e1ef3ea7dfd3015` | `1e1ef3ea7dfd3015` | `1e1ef3ea7dfd3015` |
| PR AUC | 0.4334 | 0.2799 | 0.2849 | 0.2736 |
| ROC AUC | 0.7006 | 0.6618 | 0.6650 | 0.6494 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
