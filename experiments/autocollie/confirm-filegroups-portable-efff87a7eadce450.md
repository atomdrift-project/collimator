# Confirm FAIL — efff87a7eadce450 on `filegroups/portable`

Cycle `20260614T200842-confirm-efff87a7eadce450` — 2026-06-14T20:08:42Z

averaged ensemble PR_AUC regressed: 0.9228 -> 0.8460 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `efff87a7eadce450` | `e2271a206735dbe6` | `e2271a206735dbe6` | `e2271a206735dbe6` |
| PR AUC | 0.9228 | 0.8389 | 0.8464 | 0.8427 |
| ROC AUC | 0.9746 | 0.8825 | 0.9381 | 0.9249 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
