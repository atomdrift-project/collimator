# Confirm FAIL — 412c0bd9419cb5bc on `filetypes/png`

Cycle `20261030T133448-confirm-412c0bd9419cb5bc` — 2026-10-30T13:34:48Z

averaged ensemble PR_AUC regressed: 0.3524 -> 0.1501 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `412c0bd9419cb5bc` | `9911355d8e3b2a34` | `9911355d8e3b2a34` | `9911355d8e3b2a34` |
| PR AUC | 0.3524 | 0.1307 | 0.2572 | 0.1233 |
| ROC AUC | 0.7973 | 0.2869 | 0.6804 | 0.2985 |
| Recall@L50 | — | 0.0676 | 0.0656 | 0.0656 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
