# Confirm PASS — f674e3cbd4d8f7fe on `filegroups/native`

Cycle `20260525T173913-confirm-f674e3cbd4d8f7fe` — 2026-05-25T17:39:13Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f674e3cbd4d8f7fe` | `716c3364b8fc39b9` | `716c3364b8fc39b9` | `716c3364b8fc39b9` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 1.0000 | 1.0000 | 0.9999 |
| Recall@3FPM | — | 0.9225 | 0.8914 | 0.8145 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f674e3cbd4d8f7fe
```
