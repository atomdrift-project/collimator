# Confirm FAIL — ba504233ab76f55b on `filetypes/java`

Cycle `20260821T130943-confirm-ba504233ab76f55b` — 2026-08-21T13:09:43Z

averaged ensemble PR_AUC regressed: 0.8112 -> 0.7489 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ba504233ab76f55b` | `c272c3e8ba29018f` | `c272c3e8ba29018f` | `c272c3e8ba29018f` |
| PR AUC | 0.8112 | 0.7330 | 0.7273 | 0.7428 |
| ROC AUC | 0.9781 | 0.9770 | 0.9795 | 0.9793 |
| Recall@L50 | — | 0.2284 | 0.2737 | 0.2694 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
