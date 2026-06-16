# Confirm PASS — cc774fe31cf482ee on `filetypes/csharp`

Cycle `20260616T095437-confirm-cc774fe31cf482ee` — 2026-06-16T09:54:37Z

PR_AUC held across 3 seeds (orig 0.9841)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cc774fe31cf482ee` | `b13a91b40b09ecf4` | `b13a91b40b09ecf4` | `b13a91b40b09ecf4` |
| PR AUC | 0.9841 | 0.9906 | 0.9888 | 0.9900 |
| ROC AUC | 0.9910 | 0.9944 | 0.9933 | 0.9937 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cc774fe31cf482ee
```
