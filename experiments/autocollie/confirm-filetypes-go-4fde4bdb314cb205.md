# Confirm FAIL — 4fde4bdb314cb205 on `filetypes/go`

Cycle `20260704T151306-confirm-4fde4bdb314cb205` — 2026-07-04T15:13:06Z

averaged ensemble PR_AUC regressed: 0.3798 -> 0.2691 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4fde4bdb314cb205` | `54d59c752d46cc8f` | `54d59c752d46cc8f` | `54d59c752d46cc8f` |
| PR AUC | 0.3798 | 0.2784 | 0.2270 | 0.2197 |
| ROC AUC | 0.7020 | 0.6441 | 0.5805 | 0.5736 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
