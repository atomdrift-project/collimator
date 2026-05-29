# Confirm FAIL — 330cc4779fb1aac7 on `filetypes/ruby`

Cycle `20260526T191505-confirm-330cc4779fb1aac7` — 2026-05-26T19:15:05Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9460 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `330cc4779fb1aac7` | `5e1f538ea3d28630` | `5e1f538ea3d28630` | `5e1f538ea3d28630` |
| PR AUC | 1.0000 | 0.9060 | 0.9460 | 0.9093 |
| ROC AUC | 1.0000 | 0.9972 | 0.9977 | 0.9954 |
| Recall@3FPM | — | 0.3333 | 0.6667 | 0.5556 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
