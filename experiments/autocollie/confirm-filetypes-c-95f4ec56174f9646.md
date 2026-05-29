# Confirm PASS — 95f4ec56174f9646 on `filetypes/c`

Cycle `20260526T033956-confirm-95f4ec56174f9646` — 2026-05-26T03:39:56Z

PR_AUC held across 3 seeds (orig 0.9921)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `95f4ec56174f9646` | `dd49399eea7cbcb9` | `dd49399eea7cbcb9` | `dd49399eea7cbcb9` |
| PR AUC | 0.9921 | 0.9931 | 0.9929 | 0.9935 |
| ROC AUC | 0.9959 | 0.9965 | 0.9963 | 0.9966 |
| Recall@3FPM | — | 0.7824 | 0.7894 | 0.8171 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=95f4ec56174f9646
```
