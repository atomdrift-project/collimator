# Confirm FAIL — 42d71f81ecd742a1 on `filetypes/rust`

Cycle `20260527T053154-confirm-42d71f81ecd742a1` — 2026-05-27T05:31:54Z

averaged ensemble PR_AUC regressed: 0.9279 -> 0.9062 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `42d71f81ecd742a1` | `5a040aa7d322bbf7` | `5a040aa7d322bbf7` | `5a040aa7d322bbf7` |
| PR AUC | 0.9279 | 0.9130 | 0.8117 | 0.8855 |
| ROC AUC | 0.9909 | 0.9902 | 0.9818 | 0.9874 |
| Recall@3FPM | — | 0.3846 | 0.0769 | 0.3846 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
