# Confirm PASS — e0a55f7cf41757bc on `filetypes/go`

Cycle `20260607T010448-confirm-e0a55f7cf41757bc` — 2026-06-07T01:04:48Z

PR_AUC held across 3 seeds (orig 0.9439)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e0a55f7cf41757bc` | `45ef4487cf204baa` | `45ef4487cf204baa` | `45ef4487cf204baa` |
| PR AUC | 0.9439 | 0.9401 | 0.9430 | 0.9478 |
| ROC AUC | 0.9862 | 0.9846 | 0.9849 | 0.9862 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e0a55f7cf41757bc
```
