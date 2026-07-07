# Confirm PASS — c186ffa5b85ca757 on `filetypes/csharp`

Cycle `20260705T174835-confirm-c186ffa5b85ca757` — 2026-07-05T17:48:35Z

PR_AUC held across 3 seeds (orig 0.4577)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c186ffa5b85ca757` | `8b8543c7614fa879` | `8b8543c7614fa879` | `8b8543c7614fa879` |
| PR AUC | 0.4577 | 0.4519 | 0.5120 | 0.5065 |
| ROC AUC | 0.8492 | 0.8528 | 0.8672 | 0.8680 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c186ffa5b85ca757
```
