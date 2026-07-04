# Confirm PASS — 0b144894d304ef62 on `filetypes/macho`

Cycle `20260704T135824-confirm-0b144894d304ef62` — 2026-07-04T13:58:24Z

PR_AUC held across 3 seeds (orig 0.9931)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0b144894d304ef62` | `f3fa42be2e10fd1a` | `f3fa42be2e10fd1a` | `f3fa42be2e10fd1a` |
| PR AUC | 0.9931 | 0.9878 | 0.9873 | 0.9883 |
| ROC AUC | 0.9985 | 0.9956 | 0.9951 | 0.9957 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0b144894d304ef62
```
