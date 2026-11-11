# Confirm FAIL — 592cfada4a242fa8 on `filetypes/tar`

Cycle `20261106T195327-confirm-592cfada4a242fa8` — 2026-11-06T19:53:27Z

confirmation measured L25 recall regressed: 0.75000 -> 0.72727

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `592cfada4a242fa8` | `ddffbf6a58ba59d5` | `ddffbf6a58ba59d5` | `ddffbf6a58ba59d5` |
| PR AUC | 0.9580 | 0.9465 | 0.9548 | 0.9609 |
| ROC AUC | 0.9864 | 0.9831 | 0.9868 | 0.9877 |
| Recall@L50 | — | 0.6667 | 0.6136 | 0.6364 |
| verdict | — | FAIL | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (2/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
