# Confirm FAIL — 79510faeb184368b on `filetypes/dex`

Cycle `20261031T005144-confirm-79510faeb184368b` — 2026-10-31T00:51:44Z

confirmation measured L25 recall regressed: 0.93750 -> 0.87500

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `79510faeb184368b` | `db4a706dd11ff2af` | `db4a706dd11ff2af` | `db4a706dd11ff2af` |
| PR AUC | 0.9511 | 0.9546 | 0.9678 | 0.9830 |
| ROC AUC | 0.9668 | 0.9570 | 0.9805 | 0.9883 |
| Recall@L50 | — | 0.8125 | 0.8125 | 0.9375 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
