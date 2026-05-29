# Confirm PASS — c1217b9525fd1b93 on `filetypes/go`

Cycle `20260525T185158-confirm-c1217b9525fd1b93` — 2026-05-25T18:51:58Z

PR_AUC held across 3 seeds (orig 0.9666)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c1217b9525fd1b93` | `5985403ab81f29bf` | `5985403ab81f29bf` | `5985403ab81f29bf` |
| PR AUC | 0.9666 | 0.9672 | 0.9657 | 0.9685 |
| ROC AUC | 0.9886 | 0.9892 | 0.9890 | 0.9894 |
| Recall@3FPM | — | 0.5602 | 0.4880 | 0.5241 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c1217b9525fd1b93
```
