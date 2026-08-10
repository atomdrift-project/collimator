# Confirm FAIL — ac30fce4c7382951 on `filetypes/python-bytecode`

Cycle `20260804T235532-confirm-ac30fce4c7382951` — 2026-08-04T23:55:32Z

averaged ensemble PR_AUC regressed: 0.8147 -> 0.7308 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ac30fce4c7382951` | `140121cffc2e6d35` | `140121cffc2e6d35` | `140121cffc2e6d35` |
| PR AUC | 0.8147 | 0.7243 | 0.7437 | 0.7149 |
| ROC AUC | 0.9276 | 0.9274 | 0.9376 | 0.9091 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
