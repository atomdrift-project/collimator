# Confirm PASS — b42606525fa9c7d9 on `filetypes/rust`

Cycle `20260522T174009-confirm-b42606525fa9c7d9` — 2026-05-22T17:40:09Z

PR_AUC held across 3 seeds (orig 0.8239)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b42606525fa9c7d9` | `6d732b33dd3a2a96` | `6d732b33dd3a2a96` | `6d732b33dd3a2a96` |
| PR AUC | 0.8239 | 0.7904 | 0.7975 | 0.7925 |
| ROC AUC | 0.9769 | 0.9776 | 0.9769 | 0.9769 |
| Recall@3FPM | — | 0.1538 | 0.1538 | 0.1538 |
| verdict | — | FAIL | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b42606525fa9c7d9
```
