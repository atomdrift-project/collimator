# Confirm FAIL — 64f68922510f5e25 on `filetypes/rust`

Cycle `20260723T061904-confirm-64f68922510f5e25` — 2026-07-23T06:19:04Z

averaged ensemble PR_AUC regressed: 0.8250 -> 0.7882 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `64f68922510f5e25` | `c6aa273fa58eb810` | `c6aa273fa58eb810` | `c6aa273fa58eb810` |
| PR AUC | 0.8250 | 0.8095 | 0.7390 | 0.7745 |
| ROC AUC | 0.9683 | 0.9728 | 0.9550 | 0.9617 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
