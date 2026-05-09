# Confirm PASS — 7be6dd3819d84ef9 on `filetypes/package.json`

Cycle `20260508T230809-confirm-7be6dd3819d84ef9` — 2026-05-08T23:08:09Z

F1 held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7be6dd3819d84ef9` | `ca4c6ec658d9b572` | `ca4c6ec658d9b572` | `ca4c6ec658d9b572` |
| F1 | 0.9987 | 0.9981 | 0.9981 | 0.9981 |
| ROC AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 0.9562 | 0.9594 | 0.9594 | 0.9594 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7be6dd3819d84ef9
```
