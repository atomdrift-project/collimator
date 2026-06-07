# Confirm PASS — 9e3b0b7725ec2ffc on `filetypes/c`

Cycle `20260607T010040-confirm-9e3b0b7725ec2ffc` — 2026-06-07T01:00:40Z

PR_AUC held across 3 seeds (orig 0.9884)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9e3b0b7725ec2ffc` | `39b8f3f53b882790` | `39b8f3f53b882790` | `39b8f3f53b882790` |
| PR AUC | 0.9884 | 0.9886 | 0.9890 | 0.9883 |
| ROC AUC | 0.9951 | 0.9951 | 0.9952 | 0.9946 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9e3b0b7725ec2ffc
```
