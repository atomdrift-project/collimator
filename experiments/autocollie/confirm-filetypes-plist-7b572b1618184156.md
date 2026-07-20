# Confirm FAIL — 7b572b1618184156 on `filetypes/plist`

Cycle `20260709T121021-confirm-7b572b1618184156` — 2026-07-09T12:10:21Z

averaged ensemble PR_AUC regressed: 0.9444 -> 0.8524 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7b572b1618184156` | `69e50c816c1d55c3` | `69e50c816c1d55c3` | `69e50c816c1d55c3` |
| PR AUC | 0.9444 | 0.8644 | 0.8333 | 0.8690 |
| ROC AUC | 0.9963 | 0.9852 | 0.9790 | 0.9901 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
