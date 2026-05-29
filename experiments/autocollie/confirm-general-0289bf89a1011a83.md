# Confirm PASS — 0289bf89a1011a83 on `general`

Cycle `20260527T031723-confirm-0289bf89a1011a83` — 2026-05-27T03:17:23Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0289bf89a1011a83` | `57a6c7593efdf4cc` | `57a6c7593efdf4cc` | `57a6c7593efdf4cc` |
| PR AUC | 0.9988 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9988 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.5593 | 0.7232 | 0.6749 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0289bf89a1011a83
```
