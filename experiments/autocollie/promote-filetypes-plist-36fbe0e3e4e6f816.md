# Promote REJECTED — `36fbe0e3e4e6f816` on `filetypes/plist`

Generated 2026-10-30T19:16:54Z

confirm did not hold: confirmation measured L25 recall regressed: 0.49057 -> 0.39623

## Gates

- **Confirm** (different seed, original profile): **FAIL** — confirmation measured L25 recall regressed: 0.49057 -> 0.39623
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `36fbe0e3e4e6f816` | `6b72a4f22084c0ca` | `—` |
| PR AUC | 0.8053 | 0.8434 | — |
| ROC AUC | 0.9985 | 0.9969 | — |
| F1 | 0.6622 | 0.7840 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: confirmation measured L25 recall regressed: 0.49057 -> 0.39623
