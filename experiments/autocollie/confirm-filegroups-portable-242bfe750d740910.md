# Confirm FAIL — 242bfe750d740910 on `filegroups/portable`

Cycle `20260628T120812-confirm-242bfe750d740910` — 2026-06-28T12:08:12Z

averaged ensemble PR_AUC regressed: 0.9228 -> 0.7083 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `242bfe750d740910` | `e6a84e21273fd6a6` | `e6a84e21273fd6a6` | `e6a84e21273fd6a6` |
| PR AUC | 0.9228 | 0.7744 | 0.0027 | 0.2202 |
| ROC AUC | 0.9746 | 0.8898 | 0.1103 | 0.8839 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
