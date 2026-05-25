# Confirm PASS — 0cdfb1f35ac5ce69 on `filetypes/zip`

Cycle `20260524T170128-confirm-0cdfb1f35ac5ce69` — 2026-05-24T17:01:28Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0cdfb1f35ac5ce69` | `5203f042ed178a57` | `5203f042ed178a57` | `5203f042ed178a57` |
| PR AUC | 0.9998 | 0.9997 | 0.9998 | 0.9997 |
| ROC AUC | 0.9959 | 0.9958 | 0.9958 | 0.9956 |
| Recall@3FPM | — | 0.6800 | 0.6867 | 0.6913 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0cdfb1f35ac5ce69
```
