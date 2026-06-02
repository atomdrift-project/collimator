# Confirm PASS — 18414b735672d3ba on `filetypes/c`

Cycle `20260602T004039-confirm-18414b735672d3ba` — 2026-06-02T00:40:39Z

PR_AUC held across 3 seeds (orig 0.9913)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `18414b735672d3ba` | `23a48790b1fe7101` | `23a48790b1fe7101` | `23a48790b1fe7101` |
| PR AUC | 0.9913 | 0.9905 | 0.9904 | 0.9894 |
| ROC AUC | 0.9956 | 0.9955 | 0.9955 | 0.9948 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=18414b735672d3ba
```
