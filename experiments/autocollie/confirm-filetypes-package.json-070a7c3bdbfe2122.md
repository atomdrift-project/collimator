# Confirm FAIL — 070a7c3bdbfe2122 on `filetypes/package.json`

Cycle `20261106T013048-confirm-070a7c3bdbfe2122` — 2026-11-06T01:30:48Z

confirmation measured L25 recall regressed: 0.78233 -> 0.77725

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `070a7c3bdbfe2122` | `e6f9de576bb2d46e` | `e6f9de576bb2d46e` | `e6f9de576bb2d46e` |
| PR AUC | 0.9984 | 0.9983 | 0.9971 | 0.9972 |
| ROC AUC | 0.9993 | 0.9993 | 0.9985 | 0.9987 |
| Recall@L50 | — | 0.7262 | 0.7410 | 0.6096 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
