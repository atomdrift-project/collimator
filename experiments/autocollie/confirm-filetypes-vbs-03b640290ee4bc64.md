# Confirm PASS — 03b640290ee4bc64 on `filetypes/vbs`

Cycle `20260628T071610-confirm-03b640290ee4bc64` — 2026-06-28T07:16:10Z

PR_AUC held across 3 seeds (orig 0.9964)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `03b640290ee4bc64` | `cec68563ee360e14` | `cec68563ee360e14` | `cec68563ee360e14` |
| PR AUC | 0.9964 | 0.9964 | 0.9966 | 0.9965 |
| ROC AUC | 0.9865 | 0.9868 | 0.9877 | 0.9873 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=03b640290ee4bc64
```
