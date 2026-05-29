# Confirm PASS — 7525cf2eee9fd2b2 on `filetypes/javascript`

Cycle `20260528T041436-confirm-7525cf2eee9fd2b2` — 2026-05-28T04:14:36Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7525cf2eee9fd2b2` | `3ce4e2b195e5b80c` | `3ce4e2b195e5b80c` | `3ce4e2b195e5b80c` |
| PR AUC | 0.9989 | 0.9995 | 0.9995 | 0.9995 |
| ROC AUC | 0.9984 | 0.9993 | 0.9994 | 0.9993 |
| Recall@3FPM | — | 0.8648 | 0.8690 | 0.8632 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7525cf2eee9fd2b2
```
