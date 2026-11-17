# Confirm FAIL — 042ec83d854868b5 on `filetypes/ico`

Cycle `20261112T122137-confirm-042ec83d854868b5` — 2026-11-12T12:21:37Z

confirmation measured L25 recall regressed: 1.00000 -> 0.95833

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `042ec83d854868b5` | `2f0bff94c090095f` | `2f0bff94c090095f` | `2f0bff94c090095f` |
| PR AUC | 1.0000 | 0.9940 | 0.9954 | 0.9968 |
| ROC AUC | 1.0000 | 0.9986 | 0.9990 | 0.9993 |
| Recall@L50 | — | 0.9583 | 0.9583 | 0.9583 |
| verdict | — | FAIL | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (2/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
