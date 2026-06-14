# Confirm PASS — 12c0f4df43759864 on `filetypes/powershell`

Cycle `20260614T013359-confirm-12c0f4df43759864` — 2026-06-14T01:33:59Z

PR_AUC held across 3 seeds (orig 0.9935)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `12c0f4df43759864` | `5a9eeb5e16c4415d` | `5a9eeb5e16c4415d` | `5a9eeb5e16c4415d` |
| PR AUC | 0.9935 | 0.9930 | 0.9925 | 0.9927 |
| ROC AUC | 0.9843 | 0.9828 | 0.9816 | 0.9823 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=12c0f4df43759864
```
