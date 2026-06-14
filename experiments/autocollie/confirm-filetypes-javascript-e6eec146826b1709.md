# Confirm PASS — e6eec146826b1709 on `filetypes/javascript`

Cycle `20260614T042128-confirm-e6eec146826b1709` — 2026-06-14T04:21:28Z

PR_AUC held across 3 seeds (orig 0.9976)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e6eec146826b1709` | `07a39d62623f6d7f` | `07a39d62623f6d7f` | `07a39d62623f6d7f` |
| PR AUC | 0.9976 | 0.9990 | 0.9990 | 0.9990 |
| ROC AUC | 0.9971 | 0.9987 | 0.9986 | 0.9987 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e6eec146826b1709
```
