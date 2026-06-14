# Confirm PASS — 691f89dddbd52f63 on `filetypes/makefile`

Cycle `20260614T151106-confirm-691f89dddbd52f63` — 2026-06-14T15:11:06Z

PR_AUC held across 3 seeds (orig 0.6411)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `691f89dddbd52f63` | `acd86b0a85d264d5` | `acd86b0a85d264d5` | `acd86b0a85d264d5` |
| PR AUC | 0.6411 | 0.6251 | 0.6819 | 0.6267 |
| ROC AUC | 0.8955 | 0.8818 | 0.9045 | 0.8864 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=691f89dddbd52f63
```
