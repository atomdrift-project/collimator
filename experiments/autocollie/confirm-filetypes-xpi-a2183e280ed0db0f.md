# Confirm FAIL — a2183e280ed0db0f on `filetypes/xpi`

Cycle `20261112T202535-confirm-a2183e280ed0db0f` — 2026-11-12T20:25:35Z

averaged ensemble PR_AUC regressed: 0.9283 -> 0.8969 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a2183e280ed0db0f` | `b4183fb83adbc9f1` | `b4183fb83adbc9f1` | `b4183fb83adbc9f1` |
| PR AUC | 0.9283 | 0.9468 | 0.8676 | 0.8517 |
| ROC AUC | 0.9992 | 0.9993 | 0.9982 | 0.9983 |
| Recall@L50 | — | 0.5556 | 0.3333 | 0.2222 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
