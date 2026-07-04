# Confirm FAIL — c6326a992d099c37 on `filetypes/shell`

Cycle `20260704T172651-confirm-c6326a992d099c37` — 2026-07-04T17:26:51Z

averaged ensemble PR_AUC regressed: 0.9615 -> 0.9539 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c6326a992d099c37` | `40aea7893957041f` | `40aea7893957041f` | `40aea7893957041f` |
| PR AUC | 0.9615 | 0.9531 | 0.9531 | 0.9533 |
| ROC AUC | 0.9782 | 0.9752 | 0.9754 | 0.9760 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
