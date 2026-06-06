# Confirm FAIL — f7ca53206add1f32 on `filetypes/rust`

Cycle `20260606T180631-confirm-f7ca53206add1f32` — 2026-06-06T18:06:31Z

averaged ensemble PR_AUC regressed: 0.1106 -> 0.0928 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f7ca53206add1f32` | `67426080ff0b1855` | `67426080ff0b1855` | `67426080ff0b1855` |
| PR AUC | 0.1106 | 0.0884 | 0.0862 | 0.0825 |
| ROC AUC | 0.7308 | 0.4550 | 0.5040 | 0.5117 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
