# Confirm PASS — 08add01b4df8bc9a on `filetypes/zst`

Cycle `20260526T190503-confirm-08add01b4df8bc9a` — 2026-05-26T19:05:03Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `08add01b4df8bc9a` | `219fc21bf8d3c510` | `219fc21bf8d3c510` | `219fc21bf8d3c510` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=08add01b4df8bc9a
```
