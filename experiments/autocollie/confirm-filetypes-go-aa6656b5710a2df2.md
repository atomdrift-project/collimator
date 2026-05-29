# Confirm PASS — aa6656b5710a2df2 on `filetypes/go`

Cycle `20260528T045103-confirm-aa6656b5710a2df2` — 2026-05-28T04:51:03Z

PR_AUC held across 3 seeds (orig 0.9595)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `aa6656b5710a2df2` | `c1c0dac7ef592ecf` | `c1c0dac7ef592ecf` | `c1c0dac7ef592ecf` |
| PR AUC | 0.9595 | 0.9583 | 0.9549 | 0.9568 |
| ROC AUC | 0.9852 | 0.9856 | 0.9845 | 0.9838 |
| Recall@3FPM | — | 0.4821 | 0.5595 | 0.5893 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=aa6656b5710a2df2
```
