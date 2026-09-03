# Confirm FAIL — 33ae1bf11394fe2c on `filegroups/portable`

Cycle `20260825T230537-confirm-33ae1bf11394fe2c` — 2026-08-25T23:05:37Z

averaged ensemble PR_AUC regressed: 0.8834 -> 0.7911 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `33ae1bf11394fe2c` | `c0236d3a203b37cc` | `c0236d3a203b37cc` | `c0236d3a203b37cc` |
| PR AUC | 0.8834 | 0.7850 | 0.7836 | 0.7845 |
| ROC AUC | 0.9432 | 0.9112 | 0.9023 | 0.9458 |
| Recall@L50 | — | 0.6859 | 0.6776 | 0.6694 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
