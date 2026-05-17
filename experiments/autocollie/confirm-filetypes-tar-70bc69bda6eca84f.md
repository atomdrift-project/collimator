# Confirm PASS — 70bc69bda6eca84f on `filetypes/tar`

Cycle `20260514T152822-confirm-70bc69bda6eca84f` — 2026-05-14T15:28:22Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `70bc69bda6eca84f` | `b82c5799fe251638` | `b82c5799fe251638` | `b82c5799fe251638` |
| PR AUC | 0.9999 | 0.9997 | 1.0000 | 0.9991 |
| ROC AUC | 0.9984 | 0.9968 | 1.0000 | 0.9899 |
| Recall@3FPM | — | 0.9793 | 1.0000 | 0.9793 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=70bc69bda6eca84f
```
