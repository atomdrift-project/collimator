# Promote REJECTED — `070a7c3bdbfe2122` on `filetypes/package.json`

Generated 2026-11-06T01:31:19Z

confirm did not hold: confirmation measured L25 recall regressed: 0.78233 -> 0.77725

## Gates

- **Confirm** (different seed, original profile): **FAIL** — confirmation measured L25 recall regressed: 0.78233 -> 0.77725
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `070a7c3bdbfe2122` | `e6f9de576bb2d46e` | `—` |
| PR AUC | 0.9984 | 0.9977 | — |
| ROC AUC | 0.9993 | 0.9989 | — |
| F1 | 0.9847 | 0.9890 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: confirmation measured L25 recall regressed: 0.78233 -> 0.77725
