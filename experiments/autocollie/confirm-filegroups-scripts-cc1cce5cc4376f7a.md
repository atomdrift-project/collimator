# Confirm FAIL — cc1cce5cc4376f7a on `filegroups/scripts`

Cycle `20260705T183139-confirm-cc1cce5cc4376f7a` — 2026-07-05T18:31:39Z

averaged ensemble PR_AUC regressed: 0.9529 -> 0.8210 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cc1cce5cc4376f7a` | `74af2a32bd5f2797` | `74af2a32bd5f2797` | `74af2a32bd5f2797` |
| PR AUC | 0.9529 | 0.8203 | 0.8195 | 0.8239 |
| ROC AUC | 0.9542 | 0.9578 | 0.9584 | 0.9586 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
