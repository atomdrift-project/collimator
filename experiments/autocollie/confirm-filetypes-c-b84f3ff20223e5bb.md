# Confirm PASS — b84f3ff20223e5bb on `filetypes/c`

Cycle `20260602T005253-confirm-b84f3ff20223e5bb` — 2026-06-02T00:52:53Z

PR_AUC held across 3 seeds (orig 0.9902)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b84f3ff20223e5bb` | `503aa69a1f66fee6` | `503aa69a1f66fee6` | `503aa69a1f66fee6` |
| PR AUC | 0.9902 | 0.9881 | 0.9893 | 0.9885 |
| ROC AUC | 0.9951 | 0.9943 | 0.9950 | 0.9944 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b84f3ff20223e5bb
```
