# Confirm FAIL — c1023bbc64c3cf39 on `general`

Cycle `20260608T161023-confirm-c1023bbc64c3cf39` — 2026-06-08T16:10:23Z

averaged ensemble PR_AUC regressed: 0.9757 -> 0.9532 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c1023bbc64c3cf39` | `a5f205d4f99c8b82` | `a5f205d4f99c8b82` | `a5f205d4f99c8b82` |
| PR AUC | 0.9757 | 0.9528 | 0.9534 | 0.9510 |
| ROC AUC | 0.9706 | 0.9616 | 0.9613 | 0.9592 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
