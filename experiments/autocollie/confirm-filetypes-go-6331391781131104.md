# Confirm PASS — 6331391781131104 on `filetypes/go`

Cycle `20260602T010318-confirm-6331391781131104` — 2026-06-02T01:03:18Z

PR_AUC held across 3 seeds (orig 0.9623)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6331391781131104` | `3950329899641e8b` | `3950329899641e8b` | `3950329899641e8b` |
| PR AUC | 0.9623 | 0.9655 | 0.9560 | 0.9575 |
| ROC AUC | 0.9865 | 0.9901 | 0.9876 | 0.9879 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6331391781131104
```
