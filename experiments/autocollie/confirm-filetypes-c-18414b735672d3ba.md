# Confirm FAIL — 18414b735672d3ba on `filetypes/c`

Cycle `20260628T140540-confirm-18414b735672d3ba` — 2026-06-28T14:05:40Z

experiment failed: interrupted: context canceled
--- experiment log tail ---
make[2]: *** [Makefile:1889: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-28T14-05-40_20260628T140540-confirm-18414b735672d3ba_c_feat_symbol_bigrams_vocab_expanded_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `18414b735672d3ba` | `` |
| PR AUC | 0.9913 | 0.0000 |
| ROC AUC | 0.9956 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
