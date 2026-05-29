# Confirm PASS — a49e841c745e660c on `filetypes/makefile`

Cycle `20260527T060737-confirm-a49e841c745e660c` — 2026-05-27T06:07:37Z

PR_AUC held across 3 seeds (orig 0.3333)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a49e841c745e660c` | `5aaf48e2d7600211` | `5aaf48e2d7600211` | `5aaf48e2d7600211` |
| PR AUC | 0.3333 | 0.4500 | 0.4500 | 0.4167 |
| ROC AUC | 0.8750 | 0.9167 | 0.9167 | 0.9167 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a49e841c745e660c
```
