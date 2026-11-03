# Confirm FAIL — d81d94290be9815a on `filetypes/crx`

Cycle `20261102T220738-confirm-d81d94290be9815a` — 2026-11-02T22:07:38Z

averaged ensemble PR_AUC regressed: 0.8720 -> 0.8288 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d81d94290be9815a` | `3de901d8c7886ee3` | `3de901d8c7886ee3` | `3de901d8c7886ee3` |
| PR AUC | 0.8720 | 0.8544 | 0.7914 | 0.8162 |
| ROC AUC | 0.9793 | 0.9782 | 0.9754 | 0.9750 |
| Recall@L50 | — | 0.2331 | 0.0920 | 0.0613 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
