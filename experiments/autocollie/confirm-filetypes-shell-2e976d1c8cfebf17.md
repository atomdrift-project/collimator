# Confirm FAIL — 2e976d1c8cfebf17 on `filetypes/shell`

Cycle `20260703T064932-confirm-2e976d1c8cfebf17` — 2026-07-03T06:49:32Z

averaged ensemble PR_AUC regressed: 0.9616 -> 0.9540 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2e976d1c8cfebf17` | `e2dac6b5c8f1c15f` | `e2dac6b5c8f1c15f` | `e2dac6b5c8f1c15f` |
| PR AUC | 0.9616 | 0.9531 | 0.9533 | 0.9530 |
| ROC AUC | 0.9784 | 0.9765 | 0.9767 | 0.9755 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
