# Confirm PASS — 16e8d40169c5ce40 on `filetypes/php`

Cycle `20260615T062035-confirm-16e8d40169c5ce40` — 2026-06-15T06:20:35Z

PR_AUC held across 3 seeds (orig 0.9949)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `16e8d40169c5ce40` | `58c36edec367cc1f` | `58c36edec367cc1f` | `58c36edec367cc1f` |
| PR AUC | 0.9949 | 0.9961 | 0.9955 | 0.9956 |
| ROC AUC | 0.9977 | 0.9985 | 0.9979 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=16e8d40169c5ce40
```
