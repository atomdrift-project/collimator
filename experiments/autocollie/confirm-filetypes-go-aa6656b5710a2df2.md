# Confirm PASS — aa6656b5710a2df2 on `filetypes/go`

Cycle `20260602T002347-confirm-aa6656b5710a2df2` — 2026-06-02T00:23:47Z

PR_AUC held across 3 seeds (orig 0.9595)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `aa6656b5710a2df2` | `3cc49154b488066b` | `3cc49154b488066b` | `3cc49154b488066b` |
| PR AUC | 0.9595 | 0.9538 | 0.9520 | 0.9549 |
| ROC AUC | 0.9852 | 0.9866 | 0.9859 | 0.9866 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=aa6656b5710a2df2
```
