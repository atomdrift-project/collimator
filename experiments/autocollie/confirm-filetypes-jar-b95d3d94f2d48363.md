# Confirm FAIL — b95d3d94f2d48363 on `filetypes/jar`

Cycle `20261110T195346-confirm-b95d3d94f2d48363` — 2026-11-10T19:53:46Z

confirmation measured L25 recall regressed: 0.85317 -> 0.84921

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b95d3d94f2d48363` | `214b724a1fc4b2ce` | `214b724a1fc4b2ce` | `214b724a1fc4b2ce` |
| PR AUC | 0.9875 | 0.9869 | 0.9850 | 0.9882 |
| ROC AUC | 0.9981 | 0.9977 | 0.9976 | 0.9979 |
| Recall@L50 | — | 0.8512 | 0.8393 | 0.8591 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
