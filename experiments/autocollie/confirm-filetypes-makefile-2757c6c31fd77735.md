# Confirm FAIL — 2757c6c31fd77735 on `filetypes/makefile`

Cycle `20260525T212748-confirm-2757c6c31fd77735` — 2026-05-25T21:27:48Z

averaged ensemble PR_AUC regressed: 0.6667 -> 0.4500 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2757c6c31fd77735` | `617871a1732faf37` | `617871a1732faf37` | `617871a1732faf37` |
| PR AUC | 0.6667 | 0.3667 | 0.4500 | 0.4500 |
| ROC AUC | 0.9167 | 0.8958 | 0.9167 | 0.9167 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
