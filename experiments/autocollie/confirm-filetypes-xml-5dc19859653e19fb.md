# Confirm FAIL — 5dc19859653e19fb on `filetypes/xml`

Cycle `20261106T011611-confirm-5dc19859653e19fb` — 2026-11-06T01:16:11Z

confirmation measured L25 recall regressed: 0.55584 -> 0.47273

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5dc19859653e19fb` | `51673cd5a698716f` | `51673cd5a698716f` | `51673cd5a698716f` |
| PR AUC | 0.9580 | 0.9566 | 0.9617 | 0.9647 |
| ROC AUC | 0.9964 | 0.9961 | 0.9963 | 0.9967 |
| Recall@L50 | — | 0.2182 | 0.4857 | 0.3273 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
