# Confirm FAIL — d62a17cb2a946f57 on `filetypes/lua`

Cycle `20260527T051753-confirm-d62a17cb2a946f57` — 2026-05-27T05:17:53Z

averaged ensemble PR_AUC regressed: 0.7088 -> 0.6838 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d62a17cb2a946f57` | `81db5a5f8e1f0f05` | `81db5a5f8e1f0f05` | `81db5a5f8e1f0f05` |
| PR AUC | 0.7088 | 0.5446 | 0.6630 | 0.6493 |
| ROC AUC | 0.8370 | 0.8043 | 0.8370 | 0.7935 |
| Recall@3FPM | — | 0.2500 | 0.2500 | 0.5000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
