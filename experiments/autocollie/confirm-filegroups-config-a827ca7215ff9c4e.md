# Confirm FAIL — a827ca7215ff9c4e on `filegroups/config`

Cycle `20260703T043102-confirm-a827ca7215ff9c4e` — 2026-07-03T04:31:02Z

averaged ensemble PR_AUC regressed: 0.9020 -> 0.8228 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a827ca7215ff9c4e` | `642d8716dff488c1` | `642d8716dff488c1` | `642d8716dff488c1` |
| PR AUC | 0.9020 | 0.8227 | 0.8243 | 0.8225 |
| ROC AUC | 0.9242 | 0.9087 | 0.9180 | 0.9151 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
