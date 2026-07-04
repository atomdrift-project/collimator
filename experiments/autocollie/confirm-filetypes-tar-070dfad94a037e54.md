# Confirm FAIL — 070dfad94a037e54 on `filetypes/tar`

Cycle `20260704T172703-confirm-070dfad94a037e54` — 2026-07-04T17:27:03Z

averaged ensemble PR_AUC regressed: 0.9863 -> 0.9403 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `070dfad94a037e54` | `6d297949322d11db` | `6d297949322d11db` | `6d297949322d11db` |
| PR AUC | 0.9863 | 0.9406 | 0.9414 | 0.9369 |
| ROC AUC | 0.9952 | 0.9671 | 0.9682 | 0.9630 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
