# Confirm PASS — d8f75ffa5f30d974 on `filetypes/chrome_manifest`

Cycle `20261102T194655-confirm-d8f75ffa5f30d974` — 2026-11-02T19:46:55Z

averaged 3-seed ensemble PR_AUC held: 0.9253 -> 0.9354; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d8f75ffa5f30d974` | `256ee9cd515f0131` | `256ee9cd515f0131` | `256ee9cd515f0131` |
| PR AUC | 0.9253 | 0.9341 | 0.9381 | 0.9174 |
| ROC AUC | 0.9925 | 0.9942 | 0.9942 | 0.9908 |
| Recall@L50 | — | 0.6667 | 0.7778 | 0.7778 |
| verdict | — | PASS | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d8f75ffa5f30d974
```
