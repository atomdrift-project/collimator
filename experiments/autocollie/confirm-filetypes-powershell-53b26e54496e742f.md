# Confirm PASS — 53b26e54496e742f on `filetypes/powershell`

Cycle `20260613T184942-confirm-53b26e54496e742f` — 2026-06-13T18:49:42Z

PR_AUC held across 3 seeds (orig 0.9935)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `53b26e54496e742f` | `8dee2228de6bad42` | `8dee2228de6bad42` | `8dee2228de6bad42` |
| PR AUC | 0.9935 | 0.9928 | 0.9928 | 0.9913 |
| ROC AUC | 0.9843 | 0.9825 | 0.9825 | 0.9788 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=53b26e54496e742f
```
