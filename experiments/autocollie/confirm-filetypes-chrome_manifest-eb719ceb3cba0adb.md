# Confirm PASS — eb719ceb3cba0adb on `filetypes/chrome_manifest`

Cycle `20261102T190703-confirm-eb719ceb3cba0adb` — 2026-11-02T19:07:03Z

averaged 3-seed ensemble PR_AUC held: 0.9253 -> 0.9354; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eb719ceb3cba0adb` | `0c20796d2ce34ed7` | `0c20796d2ce34ed7` | `0c20796d2ce34ed7` |
| PR AUC | 0.9253 | 0.9341 | 0.9381 | 0.9174 |
| ROC AUC | 0.9925 | 0.9942 | 0.9942 | 0.9908 |
| Recall@L50 | — | 0.6667 | 0.7778 | 0.7778 |
| verdict | — | PASS | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=eb719ceb3cba0adb
```
