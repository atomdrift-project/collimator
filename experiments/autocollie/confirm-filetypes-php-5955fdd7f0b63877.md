# Confirm FAIL — 5955fdd7f0b63877 on `filetypes/php`

Cycle `20260704T154136-confirm-5955fdd7f0b63877` — 2026-07-04T15:41:36Z

averaged ensemble PR_AUC regressed: 0.8574 -> 0.7828 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5955fdd7f0b63877` | `77c5fb2829f310fb` | `77c5fb2829f310fb` | `77c5fb2829f310fb` |
| PR AUC | 0.8574 | 0.7691 | 0.7727 | 0.7830 |
| ROC AUC | 0.9490 | 0.9170 | 0.9249 | 0.9350 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
