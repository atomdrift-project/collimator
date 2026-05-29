# Confirm PASS — 56858f615390057a on `filetypes/zip`

Cycle `20260526T231522-confirm-56858f615390057a` — 2026-05-26T23:15:22Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `56858f615390057a` | `9d298c7e1afe8506` | `9d298c7e1afe8506` | `9d298c7e1afe8506` |
| PR AUC | 0.9999 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9983 | 0.9959 | 0.9961 | 0.9962 |
| Recall@3FPM | — | 0.6382 | 0.6916 | 0.7112 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=56858f615390057a
```
