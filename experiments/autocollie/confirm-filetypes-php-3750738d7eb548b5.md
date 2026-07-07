# Confirm FAIL — 3750738d7eb548b5 on `filetypes/php`

Cycle `20260705T162606-confirm-3750738d7eb548b5` — 2026-07-05T16:26:06Z

averaged ensemble PR_AUC regressed: 0.8463 -> 0.7830 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3750738d7eb548b5` | `12d1cc989c1b28b6` | `12d1cc989c1b28b6` | `12d1cc989c1b28b6` |
| PR AUC | 0.8463 | 0.7827 | 0.7638 | 0.7904 |
| ROC AUC | 0.9370 | 0.9373 | 0.9234 | 0.9422 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
