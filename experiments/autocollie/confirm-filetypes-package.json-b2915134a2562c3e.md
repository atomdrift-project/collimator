# Confirm PASS — b2915134a2562c3e on `filetypes/package.json`

Cycle `20260514T172108-confirm-b2915134a2562c3e` — 2026-05-14T17:21:08Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b2915134a2562c3e` | `bf57e8739c629fe9` | `bf57e8739c629fe9` | `bf57e8739c629fe9` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9998 | 0.9997 | 0.9997 | 0.9998 |
| Recall@3FPM | — | 0.9821 | 0.9728 | 0.9777 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b2915134a2562c3e
```
