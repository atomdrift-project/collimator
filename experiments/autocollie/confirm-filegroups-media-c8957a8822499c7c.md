# Confirm PASS — c8957a8822499c7c on `filegroups/media`

Cycle `20260514T191414-confirm-c8957a8822499c7c` — 2026-05-14T19:14:14Z

PR_AUC held across 3 seeds (orig 0.9946)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c8957a8822499c7c` | `e311ec319fad3dfa` | `e311ec319fad3dfa` | `e311ec319fad3dfa` |
| PR AUC | 0.9946 | 0.9918 | 0.9924 | 0.9952 |
| ROC AUC | 0.9935 | 0.9902 | 0.9906 | 0.9945 |
| Recall@3FPM | — | 0.8684 | 0.8947 | 0.8816 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c8957a8822499c7c
```
