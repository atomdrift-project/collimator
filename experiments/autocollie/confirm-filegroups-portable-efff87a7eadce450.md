# Confirm FAIL — efff87a7eadce450 on `filegroups/portable`

Cycle `20260628T121001-confirm-efff87a7eadce450` — 2026-06-28T12:10:01Z

averaged ensemble PR_AUC regressed: 0.9228 -> 0.2202 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `efff87a7eadce450` | `cb428f0a03afa881` | `cb428f0a03afa881` | `cb428f0a03afa881` |
| PR AUC | 0.9228 | 0.2202 | 0.0027 | 0.2202 |
| ROC AUC | 0.9746 | 0.8839 | 0.1103 | 0.8839 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
