# Confirm FAIL — a6c6adf9e94e1c8d on `filetypes/applescript`

Cycle `20261110T195814-confirm-a6c6adf9e94e1c8d` — 2026-11-10T19:58:14Z

confirmation measured L25 recall regressed: 0.61538 -> 0.53846

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a6c6adf9e94e1c8d` | `7a2f039954d7dd12` | `7a2f039954d7dd12` | `7a2f039954d7dd12` |
| PR AUC | 0.8831 | 0.8710 | 0.8831 | 0.8825 |
| ROC AUC | 0.9460 | 0.9541 | 0.9610 | 0.9599 |
| Recall@L50 | — | 0.5385 | 0.5385 | 0.5385 |
| verdict | — | FAIL | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (2/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
