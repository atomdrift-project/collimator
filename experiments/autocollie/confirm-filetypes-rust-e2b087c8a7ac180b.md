# Confirm PASS — e2b087c8a7ac180b on `filetypes/rust`

Cycle `20260602T013227-confirm-e2b087c8a7ac180b` — 2026-06-02T01:32:27Z

PR_AUC held across 3 seeds (orig 0.9000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e2b087c8a7ac180b` | `cd549ad2bbc24588` | `cd549ad2bbc24588` | `cd549ad2bbc24588` |
| PR AUC | 0.9000 | 0.8913 | 0.8869 | 0.9075 |
| ROC AUC | 0.9855 | 0.9877 | 0.9877 | 0.9913 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e2b087c8a7ac180b
```
