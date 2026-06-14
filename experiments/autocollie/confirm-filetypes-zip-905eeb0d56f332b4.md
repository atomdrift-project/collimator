# Confirm PASS — 905eeb0d56f332b4 on `filetypes/zip`

Cycle `20260613T183915-confirm-905eeb0d56f332b4` — 2026-06-13T18:39:15Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `905eeb0d56f332b4` | `0daa1b7daef2f8ac` | `0daa1b7daef2f8ac` | `0daa1b7daef2f8ac` |
| PR AUC | 0.9996 | 0.9995 | 0.9994 | 0.9995 |
| ROC AUC | 0.9960 | 0.9956 | 0.9950 | 0.9958 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=905eeb0d56f332b4
```
