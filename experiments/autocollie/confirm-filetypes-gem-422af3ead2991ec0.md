# Confirm PASS — 422af3ead2991ec0 on `filetypes/gem`

Cycle `20260821T125438-confirm-422af3ead2991ec0` — 2026-08-21T12:54:38Z

PR_AUC held across 3 seeds (orig 0.9883)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `422af3ead2991ec0` | `8f6c979158e45fbf` | `8f6c979158e45fbf` | `8f6c979158e45fbf` |
| PR AUC | 0.9883 | 0.9900 | 0.9894 | 0.9878 |
| ROC AUC | 0.9932 | 0.9955 | 0.9947 | 0.9935 |
| Recall@L50 | — | 0.9633 | 0.9633 | 0.9633 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=422af3ead2991ec0
```
