# Confirm PASS — 872d1478afaf40f2 on `filetypes/pptx`

Cycle `20260527T081230-confirm-872d1478afaf40f2` — 2026-05-27T08:12:30Z

PR_AUC held across 3 seeds (orig 0.9231)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `872d1478afaf40f2` | `590d30726e75b5a4` | `590d30726e75b5a4` | `590d30726e75b5a4` |
| PR AUC | 0.9231 | 0.9231 | 0.9231 | 0.9231 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=872d1478afaf40f2
```
