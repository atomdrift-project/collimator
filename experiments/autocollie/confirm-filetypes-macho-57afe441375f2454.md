# Confirm PASS — 57afe441375f2454 on `filetypes/macho`

Cycle `20260613T015423-confirm-57afe441375f2454` — 2026-06-13T01:54:23Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `57afe441375f2454` | `3a43262b8e43504e` | `3a43262b8e43504e` | `3a43262b8e43504e` |
| PR AUC | 0.9968 | 0.9972 | 0.9961 | 0.9957 |
| ROC AUC | 0.9993 | 0.9994 | 0.9991 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=57afe441375f2454
```
