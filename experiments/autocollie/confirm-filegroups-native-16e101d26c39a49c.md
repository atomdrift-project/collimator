# Confirm PASS — 16e101d26c39a49c on `filegroups/native`

Cycle `20260608T050753-confirm-16e101d26c39a49c` — 2026-06-08T05:07:53Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `16e101d26c39a49c` | `54fe361d0c81ae4e` | `54fe361d0c81ae4e` | `54fe361d0c81ae4e` |
| PR AUC | 0.9992 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9992 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=16e101d26c39a49c
```
