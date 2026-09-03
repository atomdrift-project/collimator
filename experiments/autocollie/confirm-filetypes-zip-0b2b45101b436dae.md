# Confirm PASS — 0b2b45101b436dae on `filetypes/zip`

Cycle `20260825T214648-confirm-0b2b45101b436dae` — 2026-08-25T21:46:48Z

PR_AUC held across 3 seeds (orig 0.9919)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0b2b45101b436dae` | `ac4c632828934d43` | `ac4c632828934d43` | `ac4c632828934d43` |
| PR AUC | 0.9919 | 0.9955 | 0.9954 | 0.9947 |
| ROC AUC | 0.9802 | 0.9859 | 0.9855 | 0.9836 |
| Recall@L50 | — | 0.4849 | 0.4118 | 0.3202 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0b2b45101b436dae
```
