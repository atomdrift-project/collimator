# Confirm FAIL — d91795f4123a5485 on `filetypes/rust`

Cycle `20260705T160019-confirm-d91795f4123a5485` — 2026-07-05T16:00:19Z

averaged ensemble PR_AUC regressed: 0.1634 -> 0.0800 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d91795f4123a5485` | `66b81fcc11e37c62` | `66b81fcc11e37c62` | `66b81fcc11e37c62` |
| PR AUC | 0.1634 | 0.0140 | 0.0180 | 0.1067 |
| ROC AUC | 0.7536 | 0.5619 | 0.5377 | 0.7575 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
