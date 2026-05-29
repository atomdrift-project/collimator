# Confirm PASS — 45add3c8678a165e on `filetypes/go`

Cycle `20260525T160312-confirm-45add3c8678a165e` — 2026-05-25T16:03:12Z

PR_AUC held across 3 seeds (orig 0.9655)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `45add3c8678a165e` | `ad1cd7f52220d064` | `ad1cd7f52220d064` | `ad1cd7f52220d064` |
| PR AUC | 0.9655 | 0.9638 | 0.9641 | 0.9635 |
| ROC AUC | 0.9883 | 0.9880 | 0.9881 | 0.9876 |
| Recall@3FPM | — | 0.5904 | 0.4819 | 0.5241 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=45add3c8678a165e
```
