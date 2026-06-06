# Confirm PASS — 67b5e0bea23a0d48 on `filetypes/java_class`

Cycle `20260606T141643-confirm-67b5e0bea23a0d48` — 2026-06-06T14:16:43Z

PR_AUC held across 3 seeds (orig 0.9955)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `67b5e0bea23a0d48` | `de4122ac6c7f75f1` | `de4122ac6c7f75f1` | `de4122ac6c7f75f1` |
| PR AUC | 0.9955 | 0.9918 | 0.9888 | 0.9908 |
| ROC AUC | 0.9992 | 0.9985 | 0.9978 | 0.9983 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=67b5e0bea23a0d48
```
