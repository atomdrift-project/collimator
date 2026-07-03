# Confirm PASS — 06ba4c8a340d6c3c on `filetypes/xlsx`

Cycle `20260703T065042-confirm-06ba4c8a340d6c3c` — 2026-07-03T06:50:42Z

PR_AUC held across 3 seeds (orig 0.9852)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `06ba4c8a340d6c3c` | `f480f28a9d8264db` | `f480f28a9d8264db` | `f480f28a9d8264db` |
| PR AUC | 0.9852 | 0.9758 | 0.9816 | 0.9852 |
| ROC AUC | 0.7261 | 0.6542 | 0.7003 | 0.7561 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=06ba4c8a340d6c3c
```
