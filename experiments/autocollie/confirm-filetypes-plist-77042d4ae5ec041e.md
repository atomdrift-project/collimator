# Confirm FAIL — 77042d4ae5ec041e on `filetypes/plist`

Cycle `20260608T161650-confirm-77042d4ae5ec041e` — 2026-06-08T16:16:50Z

averaged ensemble PR_AUC regressed: 0.2830 -> 0.2414 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `77042d4ae5ec041e` | `3ef697405fd78346` | `3ef697405fd78346` | `3ef697405fd78346` |
| PR AUC | 0.2830 | 0.2209 | 0.2445 | 0.1914 |
| ROC AUC | 0.8184 | 0.7923 | 0.8051 | 0.7568 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
