# Promote REJECTED — `a60654ac3a45bf43` on `filetypes/ooxml`

Generated 2026-10-29T12:52:10Z

confirm did not hold: confirmation measured L25 recall regressed: 0.35919 -> 0.35896

## Gates

- **Confirm** (different seed, original profile): **FAIL** — confirmation measured L25 recall regressed: 0.35919 -> 0.35896
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a60654ac3a45bf43` | `b43ea356dfb9c63a` | `—` |
| PR AUC | 0.9810 | 0.9814 | — |
| ROC AUC | 0.8632 | 0.8631 | — |
| F1 | 0.5292 | 0.9592 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: confirmation measured L25 recall regressed: 0.35919 -> 0.35896
