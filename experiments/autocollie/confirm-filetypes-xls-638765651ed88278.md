# Confirm PASS — 638765651ed88278 on `filetypes/xls`

Cycle `20260526T180232-confirm-638765651ed88278` — 2026-05-26T18:02:32Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `638765651ed88278` | `3fc986025213e79f` | `3fc986025213e79f` | `3fc986025213e79f` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9996 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.9864 | 0.9887 | 0.9879 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=638765651ed88278
```
