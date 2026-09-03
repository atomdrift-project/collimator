# Confirm FAIL — f8571b4670562ea6 on `filetypes/json`

Cycle `20260821T132809-confirm-f8571b4670562ea6` — 2026-08-21T13:28:09Z

averaged ensemble PR_AUC regressed: 0.1844 -> 0.1291 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f8571b4670562ea6` | `badf4abe568595e2` | `badf4abe568595e2` | `badf4abe568595e2` |
| PR AUC | 0.1844 | 0.0746 | 0.0674 | 0.1282 |
| ROC AUC | 0.7552 | 0.7610 | 0.7190 | 0.7606 |
| Recall@L50 | — | 0.1386 | 0.1386 | 0.1386 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
