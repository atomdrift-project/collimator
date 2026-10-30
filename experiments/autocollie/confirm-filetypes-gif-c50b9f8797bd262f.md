# Confirm FAIL — c50b9f8797bd262f on `filetypes/gif`

Cycle `20261029T034113-confirm-c50b9f8797bd262f` — 2026-10-29T03:41:13Z

confirmation measured L25 recall regressed: 0.92208 -> 0.87013

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c50b9f8797bd262f` | `aae684b1f6865fb2` | `aae684b1f6865fb2` | `aae684b1f6865fb2` |
| PR AUC | 0.9876 | 0.9856 | 0.9854 | 0.9864 |
| ROC AUC | 0.9931 | 0.9925 | 0.9921 | 0.9926 |
| Recall@L50 | — | 0.8182 | 0.8312 | 0.8701 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
