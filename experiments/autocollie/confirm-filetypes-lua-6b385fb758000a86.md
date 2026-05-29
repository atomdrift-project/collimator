# Confirm FAIL — 6b385fb758000a86 on `filetypes/lua`

Cycle `20260525T212106-confirm-6b385fb758000a86` — 2026-05-25T21:21:06Z

averaged ensemble PR_AUC regressed: 0.8026 -> 0.6756 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6b385fb758000a86` | `2a36fc54193bb00e` | `2a36fc54193bb00e` | `2a36fc54193bb00e` |
| PR AUC | 0.8026 | 0.6667 | 0.7542 | 0.6811 |
| ROC AUC | 0.8370 | 0.8478 | 0.8696 | 0.8804 |
| Recall@3FPM | — | 0.2500 | 0.5000 | 0.2500 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
