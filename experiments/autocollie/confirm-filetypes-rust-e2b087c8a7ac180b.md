# Confirm PASS — e2b087c8a7ac180b on `filetypes/rust`

Cycle `20260525T212742-confirm-e2b087c8a7ac180b` — 2026-05-25T21:27:42Z

PR_AUC held across 3 seeds (orig 0.9000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e2b087c8a7ac180b` | `d9e9561146532c9f` | `d9e9561146532c9f` | `d9e9561146532c9f` |
| PR AUC | 0.9000 | 0.9074 | 0.6479 | 0.9280 |
| ROC AUC | 0.9855 | 0.9888 | 0.9563 | 0.9902 |
| Recall@3FPM | — | 0.3846 | 0.0000 | 0.5385 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e2b087c8a7ac180b
```
