# Confirm FAIL — 0b784ab9ed7c2000 on `filegroups/portable`

Cycle `20260804T235420-confirm-0b784ab9ed7c2000` — 2026-08-04T23:54:20Z

averaged ensemble PR_AUC regressed: 0.8725 -> 0.7925 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0b784ab9ed7c2000` | `0cefed44bc723903` | `0cefed44bc723903` | `0cefed44bc723903` |
| PR AUC | 0.8725 | 0.7824 | 0.7851 | 0.7968 |
| ROC AUC | 0.9168 | 0.9356 | 0.9015 | 0.9438 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
