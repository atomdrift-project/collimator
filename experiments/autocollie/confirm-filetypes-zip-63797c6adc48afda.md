# Confirm PASS — 63797c6adc48afda on `filetypes/zip`

Cycle `20260601T152644-confirm-63797c6adc48afda` — 2026-06-01T15:26:44Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `63797c6adc48afda` | `7bc3d410e1797d60` | `7bc3d410e1797d60` | `7bc3d410e1797d60` |
| PR AUC | 0.9997 | 0.9996 | 0.9996 | 0.9996 |
| ROC AUC | 0.9964 | 0.9948 | 0.9950 | 0.9950 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=63797c6adc48afda
```
