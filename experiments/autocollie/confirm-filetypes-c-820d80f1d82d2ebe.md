# Confirm PASS — 820d80f1d82d2ebe on `filetypes/c`

Cycle `20260601T150751-confirm-820d80f1d82d2ebe` — 2026-06-01T15:07:51Z

PR_AUC held across 3 seeds (orig 0.9889)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `820d80f1d82d2ebe` | `00231550e86045cc` | `00231550e86045cc` | `00231550e86045cc` |
| PR AUC | 0.9889 | 0.9848 | 0.9853 | 0.9844 |
| ROC AUC | 0.9940 | 0.9924 | 0.9927 | 0.9918 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=820d80f1d82d2ebe
```
