# Confirm PASS — f16563158733e06f on `filetypes/powershell`

Cycle `20260614T211936-confirm-f16563158733e06f` — 2026-06-14T21:19:36Z

PR_AUC held across 3 seeds (orig 0.9953)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f16563158733e06f` | `8241f915d8ef99f8` | `8241f915d8ef99f8` | `8241f915d8ef99f8` |
| PR AUC | 0.9953 | 0.9956 | 0.9955 | 0.9951 |
| ROC AUC | 0.9883 | 0.9893 | 0.9890 | 0.9879 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f16563158733e06f
```
