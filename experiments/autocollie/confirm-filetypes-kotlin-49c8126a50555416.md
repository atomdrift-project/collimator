# Confirm PASS — 49c8126a50555416 on `filetypes/kotlin`

Cycle `20260825T190807-confirm-49c8126a50555416` — 2026-08-25T19:08:07Z

PR_AUC held across 3 seeds (orig 0.9778)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `49c8126a50555416` | `485b3d2877962745` | `485b3d2877962745` | `485b3d2877962745` |
| PR AUC | 0.9778 | 0.9741 | 0.9769 | 0.9767 |
| ROC AUC | 0.9849 | 0.9821 | 0.9843 | 0.9844 |
| Recall@L50 | — | 0.6455 | 0.6992 | 0.7041 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=49c8126a50555416
```
