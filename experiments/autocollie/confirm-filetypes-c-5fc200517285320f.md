# Confirm PASS — 5fc200517285320f on `filetypes/c`

Cycle `20260526T041841-confirm-5fc200517285320f` — 2026-05-26T04:18:41Z

PR_AUC held across 3 seeds (orig 0.9915)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5fc200517285320f` | `5cb491cb1b771cda` | `5cb491cb1b771cda` | `5cb491cb1b771cda` |
| PR AUC | 0.9915 | 0.9927 | 0.9927 | 0.9932 |
| ROC AUC | 0.9955 | 0.9963 | 0.9961 | 0.9964 |
| Recall@3FPM | — | 0.7847 | 0.8194 | 0.8171 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5fc200517285320f
```
