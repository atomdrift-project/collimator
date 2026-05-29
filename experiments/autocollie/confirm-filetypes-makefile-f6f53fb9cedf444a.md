# Confirm PASS — f6f53fb9cedf444a on `filetypes/makefile`

Cycle `20260527T061448-confirm-f6f53fb9cedf444a` — 2026-05-27T06:14:48Z

PR_AUC held across 3 seeds (orig 0.0769)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f6f53fb9cedf444a` | `8fd0d3a6d0d550ce` | `8fd0d3a6d0d550ce` | `8fd0d3a6d0d550ce` |
| PR AUC | 0.0769 | 0.0769 | 0.0769 | 0.0769 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f6f53fb9cedf444a
```
