# Confirm FAIL — 7bfd642f07afca82 on `filetypes/plist`

Cycle `20260608T092939-confirm-7bfd642f07afca82` — 2026-06-08T09:29:39Z

averaged ensemble PR_AUC regressed: 0.2830 -> 0.2429 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7bfd642f07afca82` | `fd98f5b36c8d36e4` | `fd98f5b36c8d36e4` | `fd98f5b36c8d36e4` |
| PR AUC | 0.2830 | 0.2189 | 0.2445 | 0.1914 |
| ROC AUC | 0.8184 | 0.7815 | 0.8051 | 0.7568 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
