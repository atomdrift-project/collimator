# Confirm PASS — ca80ff7fae74687c on `filetypes/lnk`

Cycle `20260608T081345-confirm-ca80ff7fae74687c` — 2026-06-08T08:13:45Z

PR_AUC held across 3 seeds (orig 0.9961)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ca80ff7fae74687c` | `3a190741c1bf45a8` | `3a190741c1bf45a8` | `3a190741c1bf45a8` |
| PR AUC | 0.9961 | 0.9957 | 0.9962 | 0.9963 |
| ROC AUC | 0.9824 | 0.9808 | 0.9831 | 0.9842 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ca80ff7fae74687c
```
