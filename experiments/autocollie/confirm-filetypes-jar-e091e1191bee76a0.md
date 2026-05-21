# Confirm PASS — e091e1191bee76a0 on `filetypes/jar`

Cycle `20260521T042213-confirm-e091e1191bee76a0` — 2026-05-21T04:22:13Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e091e1191bee76a0` | `ea71b95e3315b3c4` | `ea71b95e3315b3c4` | `ea71b95e3315b3c4` |
| PR AUC | 0.9988 | 0.9973 | 0.9980 | 0.9981 |
| ROC AUC | 0.9977 | 0.9947 | 0.9963 | 0.9965 |
| Recall@3FPM | — | 0.8824 | 0.8824 | 0.8824 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e091e1191bee76a0
```
