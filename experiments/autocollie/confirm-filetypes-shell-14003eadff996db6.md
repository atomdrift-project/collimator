# Confirm PASS — 14003eadff996db6 on `filetypes/shell`

Cycle `20260618T015040-confirm-14003eadff996db6` — 2026-06-18T01:50:40Z

PR_AUC held across 3 seeds (orig 0.9973)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `14003eadff996db6` | `36fd72f6bc4de2e3` | `36fd72f6bc4de2e3` | `36fd72f6bc4de2e3` |
| PR AUC | 0.9973 | 0.9974 | 0.9974 | 0.9976 |
| ROC AUC | 0.9974 | 0.9974 | 0.9974 | 0.9976 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=14003eadff996db6
```
