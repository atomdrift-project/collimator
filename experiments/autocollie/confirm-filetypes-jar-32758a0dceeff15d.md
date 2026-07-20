# Confirm PASS — 32758a0dceeff15d on `filetypes/jar`

Cycle `20260715T080837-confirm-32758a0dceeff15d` — 2026-07-15T08:08:37Z

PR_AUC held across 3 seeds (orig 0.9822)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `32758a0dceeff15d` | `155c6e2c5709a7c5` | `155c6e2c5709a7c5` | `155c6e2c5709a7c5` |
| PR AUC | 0.9822 | 0.9829 | 0.9854 | 0.9822 |
| ROC AUC | 0.9815 | 0.9815 | 0.9851 | 0.9824 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=32758a0dceeff15d
```
