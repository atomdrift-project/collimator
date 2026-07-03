# Confirm FAIL — 2d974a57ea62b1cf on `filetypes/javascript`

Cycle `20260703T043200-confirm-2d974a57ea62b1cf` — 2026-07-03T04:32:00Z

averaged ensemble PR_AUC regressed: 0.9836 -> 0.9424 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2d974a57ea62b1cf` | `584ad2cfc5ea3abc` | `584ad2cfc5ea3abc` | `584ad2cfc5ea3abc` |
| PR AUC | 0.9836 | 0.9419 | 0.9425 | 0.9406 |
| ROC AUC | 0.9774 | 0.9732 | 0.9739 | 0.9701 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
