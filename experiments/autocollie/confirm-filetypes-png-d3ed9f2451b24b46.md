# Confirm FAIL — d3ed9f2451b24b46 on `filetypes/png`

Cycle `20260527T004428-confirm-d3ed9f2451b24b46` — 2026-05-27T00:44:28Z

averaged ensemble PR_AUC regressed: 0.9866 -> 0.9791 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d3ed9f2451b24b46` | `16943d4ef61d244e` | `16943d4ef61d244e` | `16943d4ef61d244e` |
| PR AUC | 0.9866 | 0.9698 | 0.9698 | 0.9794 |
| ROC AUC | 0.9746 | 0.9606 | 0.9505 | 0.9571 |
| Recall@3FPM | — | 0.9231 | 0.9231 | 0.9231 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
