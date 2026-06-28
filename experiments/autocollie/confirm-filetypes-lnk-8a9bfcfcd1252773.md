# Confirm PASS — 8a9bfcfcd1252773 on `filetypes/lnk`

Cycle `20260627T121246-confirm-8a9bfcfcd1252773` — 2026-06-27T12:12:46Z

PR_AUC held across 3 seeds (orig 0.9953)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8a9bfcfcd1252773` | `6ee0ee378058328b` | `6ee0ee378058328b` | `6ee0ee378058328b` |
| PR AUC | 0.9953 | 0.9954 | 0.9957 | 0.9960 |
| ROC AUC | 0.9793 | 0.9794 | 0.9809 | 0.9817 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8a9bfcfcd1252773
```
