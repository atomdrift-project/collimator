# Confirm PASS — 2bb4b063701f7ea6 on `filetypes/shell`

Cycle `20260628T132307-confirm-2bb4b063701f7ea6` — 2026-06-28T13:23:07Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2bb4b063701f7ea6` | `edd466cbd9ba26cc` | `edd466cbd9ba26cc` | `edd466cbd9ba26cc` |
| PR AUC | 0.9968 | 0.9941 | 0.9936 | 0.9938 |
| ROC AUC | 0.9980 | 0.9955 | 0.9951 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2bb4b063701f7ea6
```
