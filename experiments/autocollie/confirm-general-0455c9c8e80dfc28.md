# Confirm PASS — 0455c9c8e80dfc28 on `general`

Cycle `20260525T090559-confirm-0455c9c8e80dfc28` — 2026-05-25T09:05:59Z

PR_AUC held across 3 seeds (orig 0.9982)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0455c9c8e80dfc28` | `1c3b3831d0898590` | `1c3b3831d0898590` | `1c3b3831d0898590` |
| PR AUC | 0.9982 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9982 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.6457 | 0.6331 | 0.6851 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0455c9c8e80dfc28
```
