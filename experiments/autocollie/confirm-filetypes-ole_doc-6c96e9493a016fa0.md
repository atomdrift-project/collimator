# Confirm FAIL — 6c96e9493a016fa0 on `filetypes/ole_doc`

Cycle `20261110T195605-confirm-6c96e9493a016fa0` — 2026-11-10T19:56:05Z

confirmation measured L25 recall regressed: 0.97200 -> 0.95350

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6c96e9493a016fa0` | `e758d87f5745939d` | `e758d87f5745939d` | `e758d87f5745939d` |
| PR AUC | 0.9998 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9995 | 0.9997 | 0.9997 | 0.9997 |
| Recall@L50 | — | 0.9495 | 0.9524 | 0.9440 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
