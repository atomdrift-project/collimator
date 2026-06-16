# Confirm PASS — 8ae51deb2f68609e on `filetypes/rtf`

Cycle `20260616T053735-confirm-8ae51deb2f68609e` — 2026-06-16T05:37:35Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8ae51deb2f68609e` | `61136fbf33ee36ec` | `61136fbf33ee36ec` | `61136fbf33ee36ec` |
| PR AUC | 0.9989 | 0.9989 | 0.9986 | 0.9989 |
| ROC AUC | 0.9926 | 0.9925 | 0.9917 | 0.9926 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8ae51deb2f68609e
```
