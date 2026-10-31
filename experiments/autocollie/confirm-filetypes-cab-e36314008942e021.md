# Confirm FAIL — e36314008942e021 on `filetypes/cab`

Cycle `20261030T231529-confirm-e36314008942e021` — 2026-10-30T23:15:29Z

confirmation measured L25 recall regressed: 0.99065 -> 0.98131

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e36314008942e021` | `903d315b601f3c58` | `903d315b601f3c58` | `903d315b601f3c58` |
| PR AUC | 0.9995 | 0.9986 | 0.9977 | 0.9990 |
| ROC AUC | 0.9957 | 0.9885 | 0.9827 | 0.9914 |
| Recall@L50 | — | 0.8785 | 0.8411 | 0.9346 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
