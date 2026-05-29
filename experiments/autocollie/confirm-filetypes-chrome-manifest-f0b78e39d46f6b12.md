# Confirm FAIL — f0b78e39d46f6b12 on `filetypes/chrome-manifest`

Cycle `20260527T050700-confirm-f0b78e39d46f6b12` — 2026-05-27T05:07:00Z

averaged ensemble PR_AUC regressed: 0.8444 -> 0.8000 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f0b78e39d46f6b12` | `47b1f3a7b0cacec7` | `47b1f3a7b0cacec7` | `47b1f3a7b0cacec7` |
| PR AUC | 0.8444 | 0.5885 | 0.8833 | 0.5703 |
| ROC AUC | 0.9692 | 0.8744 | 0.9641 | 0.9359 |
| Recall@3FPM | — | 0.0000 | 0.8000 | 0.0000 |
| verdict | — | FAIL | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
