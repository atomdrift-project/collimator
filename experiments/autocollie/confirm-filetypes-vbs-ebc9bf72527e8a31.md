# Confirm PASS — ebc9bf72527e8a31 on `filetypes/vbs`

Cycle `20260627T220458-confirm-ebc9bf72527e8a31` — 2026-06-27T22:04:58Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ebc9bf72527e8a31` | `58d74810f5d65570` | `58d74810f5d65570` | `58d74810f5d65570` |
| PR AUC | 0.9968 | 0.9968 | 0.9969 | 0.9966 |
| ROC AUC | 0.9883 | 0.9883 | 0.9887 | 0.9875 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ebc9bf72527e8a31
```
