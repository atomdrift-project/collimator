# Confirm FAIL — 4f430bd91e98b123 on `filetypes/dmg`

Cycle `20261102T190349-confirm-4f430bd91e98b123` — 2026-11-02T19:03:49Z

averaged ensemble PR_AUC regressed: 0.9573 -> 0.9063 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4f430bd91e98b123` | `d87c870dede70b15` | `d87c870dede70b15` | `d87c870dede70b15` |
| PR AUC | 0.9573 | 0.9430 | 0.9063 | 0.9124 |
| ROC AUC | 0.9913 | 0.9891 | 0.9848 | 0.9826 |
| Recall@L50 | — | 0.5000 | 0.3000 | 0.4000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
