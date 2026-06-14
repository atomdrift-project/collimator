# Confirm PASS — b292c800cbbb875c on `filetypes/pe`

Cycle `20260613T212910-confirm-b292c800cbbb875c` — 2026-06-13T21:29:10Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b292c800cbbb875c` | `23b3c31e9ad13c0a` | `23b3c31e9ad13c0a` | `23b3c31e9ad13c0a` |
| PR AUC | 0.9988 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9989 | 0.9994 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b292c800cbbb875c
```
