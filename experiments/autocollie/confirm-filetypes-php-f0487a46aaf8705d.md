# Confirm PASS — f0487a46aaf8705d on `filetypes/php`

Cycle `20260609T095409-confirm-f0487a46aaf8705d` — 2026-06-09T09:54:09Z

PR_AUC held across 3 seeds (orig 0.9943)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f0487a46aaf8705d` | `00c7c477afccd9db` | `00c7c477afccd9db` | `00c7c477afccd9db` |
| PR AUC | 0.9943 | 0.9946 | 0.9944 | 0.9948 |
| ROC AUC | 0.9969 | 0.9972 | 0.9969 | 0.9973 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f0487a46aaf8705d
```
