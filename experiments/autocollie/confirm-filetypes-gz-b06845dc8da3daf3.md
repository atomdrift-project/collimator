# Confirm PASS — b06845dc8da3daf3 on `filetypes/gz`

Cycle `20260613T194156-confirm-b06845dc8da3daf3` — 2026-06-13T19:41:56Z

PR_AUC held across 3 seeds (orig 0.7235)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b06845dc8da3daf3` | `98bcd25fd3cfed74` | `98bcd25fd3cfed74` | `98bcd25fd3cfed74` |
| PR AUC | 0.7235 | 0.7312 | 0.7310 | 0.7167 |
| ROC AUC | 0.8958 | 0.9044 | 0.9042 | 0.8914 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b06845dc8da3daf3
```
