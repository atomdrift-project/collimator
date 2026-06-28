# Confirm PASS — c8e6bb662650b5ca on `filetypes/vbs`

Cycle `20260628T104258-confirm-c8e6bb662650b5ca` — 2026-06-28T10:42:58Z

PR_AUC held across 3 seeds (orig 0.9964)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c8e6bb662650b5ca` | `72fb119d3fba440b` | `72fb119d3fba440b` | `72fb119d3fba440b` |
| PR AUC | 0.9964 | 0.9964 | 0.9966 | 0.9965 |
| ROC AUC | 0.9865 | 0.9867 | 0.9875 | 0.9872 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c8e6bb662650b5ca
```
