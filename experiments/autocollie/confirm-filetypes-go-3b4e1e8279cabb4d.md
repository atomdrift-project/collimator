# Confirm FAIL — 3b4e1e8279cabb4d on `filetypes/go`

Cycle `20260704T114335-confirm-3b4e1e8279cabb4d` — 2026-07-04T11:43:35Z

averaged ensemble PR_AUC regressed: 0.9597 -> 0.9049 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3b4e1e8279cabb4d` | `15004e036a22ac76` | `15004e036a22ac76` | `15004e036a22ac76` |
| PR AUC | 0.9597 | 0.8979 | 0.8955 | 0.9066 |
| ROC AUC | 0.9861 | 0.9619 | 0.9622 | 0.9650 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
