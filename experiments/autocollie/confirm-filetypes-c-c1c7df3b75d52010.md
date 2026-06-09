# Confirm PASS — c1c7df3b75d52010 on `filetypes/c`

Cycle `20260608T184640-confirm-c1c7df3b75d52010` — 2026-06-08T18:46:40Z

PR_AUC held across 3 seeds (orig 0.9862)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c1c7df3b75d52010` | `859430e0d3bf1a20` | `859430e0d3bf1a20` | `859430e0d3bf1a20` |
| PR AUC | 0.9862 | 0.9862 | 0.9861 | 0.9865 |
| ROC AUC | 0.9939 | 0.9937 | 0.9938 | 0.9937 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c1c7df3b75d52010
```
