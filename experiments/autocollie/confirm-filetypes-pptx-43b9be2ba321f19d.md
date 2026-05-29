# Confirm PASS — 43b9be2ba321f19d on `filetypes/pptx`

Cycle `20260527T082307-confirm-43b9be2ba321f19d` — 2026-05-27T08:23:07Z

PR_AUC held across 3 seeds (orig 0.9231)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `43b9be2ba321f19d` | `63f40b50d43afed0` | `63f40b50d43afed0` | `63f40b50d43afed0` |
| PR AUC | 0.9231 | 0.9231 | 0.9231 | 0.9231 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=43b9be2ba321f19d
```
