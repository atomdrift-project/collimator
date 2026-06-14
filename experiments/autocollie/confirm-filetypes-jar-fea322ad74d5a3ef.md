# Confirm PASS — fea322ad74d5a3ef on `filetypes/jar`

Cycle `20260613T023531-confirm-fea322ad74d5a3ef` — 2026-06-13T02:35:31Z

PR_AUC held across 3 seeds (orig 0.9896)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fea322ad74d5a3ef` | `e3945b9c03bb9218` | `e3945b9c03bb9218` | `e3945b9c03bb9218` |
| PR AUC | 0.9896 | 0.9930 | 0.9916 | 0.9898 |
| ROC AUC | 0.9771 | 0.9844 | 0.9816 | 0.9778 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fea322ad74d5a3ef
```
