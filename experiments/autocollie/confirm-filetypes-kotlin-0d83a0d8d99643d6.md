# Confirm PASS — 0d83a0d8d99643d6 on `filetypes/kotlin`

Cycle `20260821T131322-confirm-0d83a0d8d99643d6` — 2026-08-21T13:13:22Z

PR_AUC held across 3 seeds (orig 0.9788)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0d83a0d8d99643d6` | `641edfb16bdf8104` | `641edfb16bdf8104` | `641edfb16bdf8104` |
| PR AUC | 0.9788 | 0.9773 | 0.9786 | 0.9786 |
| ROC AUC | 0.9848 | 0.9840 | 0.9848 | 0.9842 |
| Recall@L50 | — | 0.6927 | 0.6809 | 0.7041 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0d83a0d8d99643d6
```
