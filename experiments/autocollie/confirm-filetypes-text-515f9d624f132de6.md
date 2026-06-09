# Confirm FAIL — 515f9d624f132de6 on `filetypes/text`

Cycle `20260609T070308-confirm-515f9d624f132de6` — 2026-06-09T07:03:08Z

averaged ensemble PR_AUC regressed: 0.9466 -> 0.9335 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `515f9d624f132de6` | `712f13145fcbbdd3` | `712f13145fcbbdd3` | `712f13145fcbbdd3` |
| PR AUC | 0.9466 | 0.9188 | 0.9126 | 0.9398 |
| ROC AUC | 0.9726 | 0.9545 | 0.9596 | 0.9710 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
