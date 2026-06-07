# Confirm PASS — 63797c6adc48afda on `filetypes/zip`

Cycle `20260606T140950-confirm-63797c6adc48afda` — 2026-06-06T14:09:50Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `63797c6adc48afda` | `d2ac5eab009654b9` | `d2ac5eab009654b9` | `d2ac5eab009654b9` |
| PR AUC | 0.9997 | 0.9996 | 0.9995 | 0.9996 |
| ROC AUC | 0.9964 | 0.9955 | 0.9954 | 0.9961 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=63797c6adc48afda
```
