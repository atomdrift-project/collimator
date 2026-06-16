# Confirm PASS — 19d7dad76e1f2dbd on `filetypes/lnk`

Cycle `20260616T050547-confirm-19d7dad76e1f2dbd` — 2026-06-16T05:05:47Z

PR_AUC held across 3 seeds (orig 0.9977)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `19d7dad76e1f2dbd` | `c2dbadd11d5768ed` | `c2dbadd11d5768ed` | `c2dbadd11d5768ed` |
| PR AUC | 0.9977 | 0.9976 | 0.9977 | 0.9975 |
| ROC AUC | 0.9890 | 0.9885 | 0.9891 | 0.9883 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=19d7dad76e1f2dbd
```
