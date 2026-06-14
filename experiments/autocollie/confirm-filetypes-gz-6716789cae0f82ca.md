# Confirm PASS — 6716789cae0f82ca on `filetypes/gz`

Cycle `20260613T193136-confirm-6716789cae0f82ca` — 2026-06-13T19:31:36Z

PR_AUC held across 3 seeds (orig 0.7190)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6716789cae0f82ca` | `6076212ead45d04f` | `6076212ead45d04f` | `6076212ead45d04f` |
| PR AUC | 0.7190 | 0.7324 | 0.7298 | 0.7159 |
| ROC AUC | 0.8396 | 0.9079 | 0.8900 | 0.8922 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6716789cae0f82ca
```
