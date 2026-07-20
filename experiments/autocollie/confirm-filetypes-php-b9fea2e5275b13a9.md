# Confirm PASS — b9fea2e5275b13a9 on `filetypes/php`

Cycle `20260713T042209-confirm-b9fea2e5275b13a9` — 2026-07-13T04:22:09Z

PR_AUC held across 3 seeds (orig 0.9842)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b9fea2e5275b13a9` | `87ed664c77561c6b` | `87ed664c77561c6b` | `87ed664c77561c6b` |
| PR AUC | 0.9842 | 0.9818 | 0.9851 | 0.9848 |
| ROC AUC | 0.9957 | 0.9949 | 0.9960 | 0.9957 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b9fea2e5275b13a9
```
