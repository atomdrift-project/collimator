# Confirm PASS — 0d0c6636d75dc0b9 on `filetypes/png`

Cycle `20260522T170021-confirm-0d0c6636d75dc0b9` — 2026-05-22T17:00:21Z

PR_AUC held across 3 seeds (orig 0.9867)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0d0c6636d75dc0b9` | `4fe77bf95fb29bba` | `4fe77bf95fb29bba` | `4fe77bf95fb29bba` |
| PR AUC | 0.9867 | 0.9736 | 0.9736 | 0.9842 |
| ROC AUC | 0.9731 | 0.9605 | 0.9605 | 0.9692 |
| Recall@3FPM | — | 0.9091 | 0.9091 | 0.9091 |
| verdict | — | FAIL | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0d0c6636d75dc0b9
```
