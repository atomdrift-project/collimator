# Confirm FAIL — 340db75650f1214a on `filetypes/text`

Cycle `20260520T202602-confirm-340db75650f1214a` — 2026-05-20T20:26:02Z

averaged ensemble PR_AUC regressed: 0.9666 -> 0.9556 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `340db75650f1214a` | `b356d1be43b39e47` | `b356d1be43b39e47` | `b356d1be43b39e47` |
| PR AUC | 0.9666 | 0.9366 | 0.9671 | 0.9585 |
| ROC AUC | 0.9834 | 0.9703 | 0.9834 | 0.9781 |
| Recall@3FPM | — | 0.5909 | 0.8182 | 0.7727 |
| verdict | — | FAIL | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
