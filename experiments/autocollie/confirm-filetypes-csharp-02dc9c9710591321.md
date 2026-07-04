# Confirm FAIL — 02dc9c9710591321 on `filetypes/csharp`

Cycle `20260704T154120-confirm-02dc9c9710591321` — 2026-07-04T15:41:20Z

averaged ensemble PR_AUC regressed: 0.5009 -> 0.4802 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `02dc9c9710591321` | `5eb1e3875bd55291` | `5eb1e3875bd55291` | `5eb1e3875bd55291` |
| PR AUC | 0.5009 | 0.4911 | 0.4545 | 0.4986 |
| ROC AUC | 0.8648 | 0.8752 | 0.8532 | 0.8881 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | PASS |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
