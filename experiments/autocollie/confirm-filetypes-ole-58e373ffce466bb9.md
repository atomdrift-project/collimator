# Confirm PASS — 58e373ffce466bb9 on `filetypes/ole`

Cycle `20260628T122744-confirm-58e373ffce466bb9` — 2026-06-28T12:27:44Z

PR_AUC held across 3 seeds (orig 0.9964)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `58e373ffce466bb9` | `850caaecad9dc395` | `850caaecad9dc395` | `850caaecad9dc395` |
| PR AUC | 0.9964 | 0.9967 | 0.9967 | 0.9966 |
| ROC AUC | 0.9890 | 0.9896 | 0.9894 | 0.9890 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=58e373ffce466bb9
```
