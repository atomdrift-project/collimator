# Confirm FAIL — 4ec3a6dba8a3e08f on `filetypes/crate`

Cycle `20261106T014938-confirm-4ec3a6dba8a3e08f` — 2026-11-06T01:49:38Z

averaged ensemble PR_AUC regressed: 0.9341 -> 0.1030 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4ec3a6dba8a3e08f` | `f15413ef90bacf2e` | `f15413ef90bacf2e` | `f15413ef90bacf2e` |
| PR AUC | 0.9341 | 0.0019 | 0.1030 | 0.0020 |
| ROC AUC | 0.9999 | 0.7642 | 0.9132 | 0.7939 |
| Recall@L50 | — | 0.8571 | 0.8571 | 0.8571 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
