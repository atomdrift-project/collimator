# Confirm PASS — 777c99e1705ab45b on `filetypes/crx`

Cycle `20260702T233049-confirm-777c99e1705ab45b` — 2026-07-02T23:30:49Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `777c99e1705ab45b` | `263aacfba8ef4813` | `263aacfba8ef4813` | `263aacfba8ef4813` |
| PR AUC | 0.9966 | 0.9956 | 0.9957 | 0.9949 |
| ROC AUC | 0.9966 | 0.9958 | 0.9957 | 0.9950 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=777c99e1705ab45b
```
