# Confirm FAIL — 49e1116027ab8aa4 on `filetypes/png`

Cycle `20260527T004425-confirm-49e1116027ab8aa4` — 2026-05-27T00:44:25Z

averaged ensemble PR_AUC regressed: 0.9870 -> 0.9818 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `49e1116027ab8aa4` | `4b96b7a8b14b64ae` | `4b96b7a8b14b64ae` | `4b96b7a8b14b64ae` |
| PR AUC | 0.9870 | 0.9698 | 0.9698 | 0.9822 |
| ROC AUC | 0.9753 | 0.9606 | 0.9505 | 0.9650 |
| Recall@3FPM | — | 0.9231 | 0.9231 | 0.9231 |
| verdict | — | FAIL | FAIL | PASS |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
