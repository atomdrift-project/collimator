# Confirm PASS — cbc26bd8623393a1 on `filetypes/zip`

Cycle `20260805T005457-confirm-cbc26bd8623393a1` — 2026-08-05T00:54:57Z

PR_AUC held across 3 seeds (orig 0.9931)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cbc26bd8623393a1` | `7afed0b387e737f4` | `7afed0b387e737f4` | `7afed0b387e737f4` |
| PR AUC | 0.9931 | 0.9962 | 0.9964 | 0.9964 |
| ROC AUC | 0.9803 | 0.9859 | 0.9866 | 0.9865 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cbc26bd8623393a1
```
