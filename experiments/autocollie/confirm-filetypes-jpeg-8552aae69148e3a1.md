# Confirm PASS — 8552aae69148e3a1 on `filetypes/jpeg`

Cycle `20260628T101633-confirm-8552aae69148e3a1` — 2026-06-28T10:16:33Z

PR_AUC held across 3 seeds (orig 0.9822)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8552aae69148e3a1` | `8afe35b99f1e2d56` | `8afe35b99f1e2d56` | `8afe35b99f1e2d56` |
| PR AUC | 0.9822 | 0.9866 | 0.9897 | 0.9892 |
| ROC AUC | 0.9888 | 0.9926 | 0.9945 | 0.9941 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8552aae69148e3a1
```
