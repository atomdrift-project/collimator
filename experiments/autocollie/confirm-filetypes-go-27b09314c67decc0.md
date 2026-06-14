# Confirm FAIL — 27b09314c67decc0 on `filetypes/go`

Cycle `20260613T192533-confirm-27b09314c67decc0` — 2026-06-13T19:25:33Z

averaged ensemble PR_AUC regressed: 0.9442 -> 0.9231 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `27b09314c67decc0` | `ade17936f884ed8f` | `ade17936f884ed8f` | `ade17936f884ed8f` |
| PR AUC | 0.9442 | 0.9210 | 0.9181 | 0.9177 |
| ROC AUC | 0.9858 | 0.9766 | 0.9762 | 0.9737 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
