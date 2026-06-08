# Confirm PASS — 1db903d7cb1c968c on `filetypes/rtf`

Cycle `20260608T094735-confirm-1db903d7cb1c968c` — 2026-06-08T09:47:35Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1db903d7cb1c968c` | `8807223fe2e94fd9` | `8807223fe2e94fd9` | `8807223fe2e94fd9` |
| PR AUC | 0.9996 | 0.9996 | 0.9986 | 0.9986 |
| ROC AUC | 0.9968 | 0.9965 | 0.9918 | 0.9917 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1db903d7cb1c968c
```
