# Confirm PASS — f8d001ce7e89fd43 on `filetypes/powershell`

Cycle `20260713T085218-confirm-f8d001ce7e89fd43` — 2026-07-13T08:52:18Z

PR_AUC held across 3 seeds (orig 0.9985)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f8d001ce7e89fd43` | `5fe122a2a0680bf9` | `5fe122a2a0680bf9` | `5fe122a2a0680bf9` |
| PR AUC | 0.9985 | 0.9987 | 0.9987 | 0.9985 |
| ROC AUC | 0.9948 | 0.9956 | 0.9954 | 0.9948 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f8d001ce7e89fd43
```
