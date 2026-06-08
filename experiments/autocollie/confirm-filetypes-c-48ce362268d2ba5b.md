# Confirm FAIL — 48ce362268d2ba5b on `filetypes/c`

Cycle `20260608T160702-confirm-48ce362268d2ba5b` — 2026-06-08T16:07:02Z

averaged ensemble PR_AUC regressed: 0.6196 -> 0.3838 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `48ce362268d2ba5b` | `11134131520f1d0a` | `11134131520f1d0a` | `11134131520f1d0a` |
| PR AUC | 0.6196 | 0.3835 | 0.3778 | 0.3682 |
| ROC AUC | 0.8432 | 0.8597 | 0.8636 | 0.8638 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
