# Confirm FAIL — 7298de301ac1f347 on `filetypes/php`

Cycle `20260608T161025-confirm-7298de301ac1f347` — 2026-06-08T16:10:25Z

averaged ensemble PR_AUC regressed: 0.8494 -> 0.8207 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7298de301ac1f347` | `05b02448b23b2620` | `05b02448b23b2620` | `05b02448b23b2620` |
| PR AUC | 0.8494 | 0.8200 | 0.8206 | 0.8186 |
| ROC AUC | 0.9513 | 0.9431 | 0.9425 | 0.9337 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
