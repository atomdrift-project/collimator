# Confirm PASS — 3a89ec450e58da37 on `filetypes/rust`

Cycle `20260607T010436-confirm-3a89ec450e58da37` — 2026-06-07T01:04:36Z

PR_AUC held across 3 seeds (orig 0.9009)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3a89ec450e58da37` | `75c15019d4b23481` | `75c15019d4b23481` | `75c15019d4b23481` |
| PR AUC | 0.9009 | 0.8438 | 0.9098 | 0.9151 |
| ROC AUC | 0.9920 | 0.9863 | 0.9924 | 0.9944 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3a89ec450e58da37
```
