# Confirm PASS — df39e602555e3bcc on `filetypes/package.json`

Cycle `20260608T024326-confirm-df39e602555e3bcc` — 2026-06-08T02:43:26Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `df39e602555e3bcc` | `e29c91690210e257` | `e29c91690210e257` | `e29c91690210e257` |
| PR AUC | 0.9987 | 0.9989 | 0.9987 | 0.9989 |
| ROC AUC | 0.9978 | 0.9982 | 0.9980 | 0.9984 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=df39e602555e3bcc
```
