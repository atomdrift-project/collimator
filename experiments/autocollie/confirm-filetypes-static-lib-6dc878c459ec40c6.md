# Confirm FAIL — 6dc878c459ec40c6 on `filetypes/static-lib`

Cycle `20261029T125315-confirm-6dc878c459ec40c6` — 2026-10-29T12:53:15Z

confirmation measured L25 recall regressed: 0.33077 -> 0.31538

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6dc878c459ec40c6` | `eeb5fe926bfe18b6` | `eeb5fe926bfe18b6` | `eeb5fe926bfe18b6` |
| PR AUC | 0.7575 | 0.7627 | 0.7497 | 0.7739 |
| ROC AUC | 0.9452 | 0.9458 | 0.9381 | 0.9451 |
| Recall@L50 | — | 0.2115 | 0.2385 | 0.2269 |
| verdict | — | PASS | FAIL | PASS |

## Disposition

This spec did not survive multi-seed reseeding (2/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
