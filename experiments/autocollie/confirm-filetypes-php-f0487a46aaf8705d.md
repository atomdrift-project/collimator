# Confirm PASS — f0487a46aaf8705d on `filetypes/php`

Cycle `20260613T201044-confirm-f0487a46aaf8705d` — 2026-06-13T20:10:44Z

PR_AUC held across 3 seeds (orig 0.9943)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f0487a46aaf8705d` | `c1ef02cdf9899427` | `c1ef02cdf9899427` | `c1ef02cdf9899427` |
| PR AUC | 0.9943 | 0.9939 | 0.9927 | 0.9933 |
| ROC AUC | 0.9969 | 0.9971 | 0.9960 | 0.9964 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f0487a46aaf8705d
```
