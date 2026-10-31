# Confirm FAIL — 2cc1209cbc6bc200 on `filetypes/crx`

Cycle `20261031T000433-confirm-2cc1209cbc6bc200` — 2026-10-31T00:04:33Z

averaged ensemble PR_AUC regressed: 0.8697 -> 0.8611 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2cc1209cbc6bc200` | `5d74d5c25583e66b` | `5d74d5c25583e66b` | `5d74d5c25583e66b` |
| PR AUC | 0.8697 | 0.8603 | 0.8673 | 0.8369 |
| ROC AUC | 0.9813 | 0.9798 | 0.9808 | 0.9786 |
| Recall@L50 | — | 0.2699 | 0.2393 | 0.0920 |
| verdict | — | FAIL | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
