# Confirm PASS — 284bc2bdb81795f1 on `filetypes/pkg-info`

Cycle `20260615T055921-confirm-284bc2bdb81795f1` — 2026-06-15T05:59:21Z

PR_AUC held across 3 seeds (orig 0.9971)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `284bc2bdb81795f1` | `f4f7d497d808d9bd` | `f4f7d497d808d9bd` | `f4f7d497d808d9bd` |
| PR AUC | 0.9971 | 0.9971 | 0.9977 | 0.9950 |
| ROC AUC | 0.9859 | 0.9863 | 0.9920 | 0.9793 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=284bc2bdb81795f1
```
