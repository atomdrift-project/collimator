# Confirm FAIL — c016aaa41989b9b1 on `filegroups/scripts`

Cycle `20260825T230622-confirm-c016aaa41989b9b1` — 2026-08-25T23:06:22Z

averaged ensemble PR_AUC regressed: 0.9872 -> 0.9434 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c016aaa41989b9b1` | `141670fd030518e9` | `141670fd030518e9` | `141670fd030518e9` |
| PR AUC | 0.9872 | 0.9408 | 0.9490 | 0.9338 |
| ROC AUC | 0.9851 | 0.9889 | 0.9898 | 0.9879 |
| Recall@L50 | — | 0.4212 | 0.4434 | 0.4506 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
