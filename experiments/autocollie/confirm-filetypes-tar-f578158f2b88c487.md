# Confirm FAIL — f578158f2b88c487 on `filetypes/tar`

Cycle `20261030T133136-confirm-f578158f2b88c487` — 2026-10-30T13:31:36Z

averaged ensemble PR_AUC regressed: 0.9614 -> 0.9544 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f578158f2b88c487` | `87d3f667140c8539` | `87d3f667140c8539` | `87d3f667140c8539` |
| PR AUC | 0.9614 | 0.9482 | 0.9213 | 0.9581 |
| ROC AUC | 0.9877 | 0.9845 | 0.9775 | 0.9880 |
| Recall@L50 | — | 0.6212 | 0.5606 | 0.6288 |
| verdict | — | FAIL | FAIL | PASS |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
