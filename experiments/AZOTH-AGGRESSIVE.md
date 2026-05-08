# Azoth Aggressive Experiments

Created: 2026-05-06

Script:

```sh
scripts/run_azoth_aggressive_tranche.sh
```

Purpose: test high-risk, high-upside feature spaces for Azoth without relaxing
promotion discipline. Isolated sampled metrics are only screening evidence.
Promotion requires routed full-corpus improvement under the same FP budget.

Profile:

- Serial execution.
- Default probe: 150k train / 40k external / 180 trees / 64 workers.
- PE probe cap: 80k train / 25k external / 120 trees unless overridden.
- Large filegroups (`scripts`, `native`) cap: 110k train / 30k external /
  150 trees unless overridden.
- Filetype and filegroup routes train with score filter disabled.

The 20 aggressive ideas:

1. `general_hsn8_tax_format_no_score`: global scoreless deep H/S/N trigrams
   plus taxonomy and format hints.
2. `general_static_tax_hardtail`: global EMBER-lite/static + taxonomy +
   format hints with hard-negative tail weighting.
3. `general_sparse_regularized_tail`: global precision-biased sparse,
   regularized LightGBM with hard-negative weighting.
4. `general_deep_recall_beta2`: global recall-biased deep n-grams and beta=2.
5. `general_scoreless_objective_attack`: global scoreless objective/ATT&CK
   count features with strict benign trigram cap.
6. `js_scoreless_hsn10_ultradeep`: JavaScript scoreless severity trigrams to
   depth 10, very large vocab.
7. `js_objective_attack_static_tail`: JavaScript objective/ATT&CK features
   with taxonomy/format hints and hard-negative tail.
8. `js_no_presence_ngrams_only`: JavaScript n-gram-only style model with
   presence/maxcrit/score removed.
9. `py_promoted_plus_hardtail`: promoted Python tax-density recipe plus
   hard-negative tail.
10. `py_scoreless_hsn_tax`: Python scoreless deep H/S/N trigrams plus taxonomy.
11. `py_struct_metrics_only_tail`: Python structural/metrics-only stress test.
12. `scripts_scoreless_objective_attack`: scripts group scoreless
   objective/ATT&CK route.
13. `scripts_hsn10_hardtail`: scripts group depth-10 severity trigrams with
   hard-negative tail.
14. `scripts_low_leaf_precision`: scripts group precision-biased low-leaf,
   regularized hard-tail model.
15. `macho_static_tax_hardtail`: Mach-O EMBER-lite/static + taxonomy with
   aggressive hard-tail weighting.
16. `macho_scoreless_hsn8`: Mach-O scoreless deep H/S/N n-gram model.
17. `pe_static_tax_scoreless_small`: PE scoreless static/taxonomy probe with
   PE-sized cap.
18. `pe_precision_tiny_leaf_tail`: PE precision-biased tiny-leaf hard-tail.
19. `native_static_hsn_hardtail`: native group static + taxonomy + H/S/N
   trigrams with hard-tail weighting.
20. `source_formula_density_tax`: source group taxonomy/density/objective
   route with deep path n-grams.

Outcome log:

- 2026-05-06: tranche defined. Run command:
  `scripts/run_azoth_aggressive_tranche.sh`. Use `RUN_LIMIT`/`RUN_SKIP` to
  run or resume in chunks.
- 2026-05-06: first bounded chunk (`RUN_LIMIT=3`) completed.
  `general_hsn8_tax_format_no_score` (`773c7b9c4d173b8c`) was the only
  promising local result: external F1 0.9956, precision 0.9938, recall
  0.9974, AUC 0.9998, AP 0.9998, Brier 0.0037; holdout F1 0.9963. It is
  expensive at 150k: 42,495 features, 449M nonzeros, 1034s. Needs routed
  full-corpus confirmation before any promotion.
- 2026-05-06: `general_static_tax_hardtail` (`c8c61dd12c9120d9`) underperformed
  locally: external F1 0.9938, precision 0.9919, recall 0.9957, AUC 0.9998,
  Brier 0.0048. Runtime 1894s. Do not pursue unless there is a specific
  route-level reason.
- 2026-05-06: `general_sparse_regularized_tail` (`5b23d2b450ceb55f`)
  underperformed locally: external F1 0.9907, precision 0.9937, recall
  0.9878, AUC 0.9995, Brier 0.0080. Reject for now.
- 2026-05-06: routed confirmation rejected `general_hsn8_tax_format_no_score`.
  Confirmation root: `out/models/azoth-confirm-general-773c`. The candidate
  required refreshing current-corpus route scores for scripts, native, PE, and
  Python. On snapshot `688111954` (2,890,513 rows; 559,418 malware;
  2,331,095 benign), routed global metrics were weak: L3 hostile recall
  0.472806 at 6 FP (2.57 FP/M), L5 hostile recall 0.502588 at 11 FP
  (4.72 FP/M), and L9 hostile recall 0.515146 at 20 FP (8.58 FP/M). Do not
  promote despite strong sampled metrics; the sampled split was misleading for
  the deployed FP-budget objective.
- 2026-05-06: resumed bounded chunk (`RUN_SKIP=3 RUN_LIMIT=3`,
  100k/30k/150) completed. `general_deep_recall_beta2`
  (`0c294a827f290b7f`) underperformed: external F1 0.9902, precision 0.9830,
  recall 0.9976, AUC 0.9994, AP 0.9993, Brier 0.0068. Reject for now.
- 2026-05-06: `general_scoreless_objective_attack`
  (`367f6ce346f37935`) also underperformed: external F1 0.9913, precision
  0.9885, recall 0.9941, AUC 0.9994, AP 0.9993, Brier 0.0068. Reject for
  now.
- 2026-05-06: `js_scoreless_hsn10_ultradeep` (`89bcfaab5466c232`) is
  promising as a JavaScript specialist screen: external F1 0.9959, precision
  0.9949, recall 0.9968, AUC 0.9998, AP 0.9997, Brier 0.0022. Current
  deployed JavaScript model card benchmark is F1 0.9778, so this deserves
  routed full-corpus confirmation before promotion.
- 2026-05-06: next bounded chunk (`RUN_SKIP=6 RUN_LIMIT=3`, 100k/30k/150)
  completed. `js_objective_attack_static_tail` (`e5ebd13824f37c35`) is the
  strongest JavaScript screen so far: external F1 0.9972, precision 0.9985,
  recall 0.9959, AUC 0.9999, AP 0.9998, Brier 0.0014, with only 18,601
  features. Prefer this over `js_scoreless_hsn10_ultradeep` for routed
  confirmation.
- 2026-05-06: `js_no_presence_ngrams_only` (`7fce9e7afa80b4d0`) is strong but
  trails the objective/static-tail JS recipe: external F1 0.9960, precision
  0.9963, recall 0.9957, AUC 0.9998, AP 0.9997, Brier 0.0023. Keep as backup,
  not first confirmation target.
- 2026-05-06: `py_promoted_plus_hardtail` (`c4374fc768e1e716`) improved sampled
  Python F1 versus the deployed model card (0.9903 vs 0.9835): external
  precision 0.9855, recall 0.9951, AUC 0.9997, AP 0.9990, Brier 0.0016.
  Worth routed confirmation after the stronger JavaScript candidate.
- 2026-05-06: next bounded chunk (`RUN_SKIP=9 RUN_LIMIT=3`, 100k/30k/150)
  completed. `py_scoreless_hsn_tax` (`e627cce284113418`) was close but behind
  the Python hard-tail candidate: external F1 0.9894, precision 0.9843, recall
  0.9945, AUC 0.9995, AP 0.9987, Brier 0.0022. Reject for now.
- 2026-05-06: `py_struct_metrics_only_tail` (`e3629d17007ee50c`) confirmed that
  structural/metric features alone lose too much Python signal: external F1
  0.9869, precision 0.9866, recall 0.9872, AUC 0.9997, AP 0.9982, Brier
  0.0023. Useful ablation result; reject as a deployable recipe.
- 2026-05-06: `scripts_scoreless_objective_attack` (`2257818be6f47a12`) is a
  strong scripts-filegroup screen: external F1 0.9966, precision 0.9955,
  recall 0.9976, AUC 0.9998, AP 0.9998, Brier 0.0023. Current deployed
  scripts model card benchmark is F1 0.9849, so route confirmation is
  warranted.
- 2026-05-06: next bounded chunk (`RUN_SKIP=12 RUN_LIMIT=3`, 100k/30k/150)
  completed. `scripts_hsn10_hardtail` (`56ff6ea327743220`) was slower and
  weaker than the simpler scripts objective candidate: external F1 0.9940,
  precision 0.9964, recall 0.9915, AUC 0.9996, AP 0.9996, Brier 0.0038.
  Reject for now.
- 2026-05-06: `scripts_low_leaf_precision` (`5aade5844231db77`) also trailed
  the scripts objective candidate: external F1 0.9922, precision 0.9969,
  recall 0.9875, AUC 0.9994, AP 0.9995, Brier 0.0051. Reject for now.
- 2026-05-06: `macho_static_tax_hardtail` (`1362d77caa3e0faa`) was roughly
  flat versus deployed Mach-O sampled F1 (0.9834 vs 0.9831) and hit degenerate
  isotonic calibration on the small holdout. Do not promote without a larger
  Mach-O confirmation set or a clearer route-level win.
- 2026-05-06: next bounded chunk (`RUN_SKIP=15 RUN_LIMIT=3`, 100k/30k/150)
  completed. `macho_scoreless_hsn8` (`1ba5ec8e906c67fd`) improved sampled F1
  to 0.9900 with precision 0.9933, recall 0.9867, AUC 0.9999, AP 0.9994,
  Brier 0.0043, but again had degenerate isotonic calibration on the tiny
  holdout. It is a possible Mach-O follow-up only if we build a larger
  confirmation/evaluation pool.
- 2026-05-06: `pe_static_tax_scoreless_small` (`781fae16ec255c78`) was
  effectively flat against deployed PE sampled F1 (0.9948): external precision
  0.9956, recall 0.9941, AUC 0.9998, AP 0.9998, Brier 0.0036. No promotion
  case.
- 2026-05-06: `pe_precision_tiny_leaf_tail` (`b617aadaaae3b7cd`) was also
  flat: external F1 0.9951, precision 0.9951, recall 0.9950, AUC 0.9998, AP
  0.9998, Brier 0.0044. It may be directionally better than PE static/tax, but
  the difference is too small for promotion without routed confirmation.
- 2026-05-06: final bounded chunk (`RUN_SKIP=18 RUN_LIMIT=2`, 100k/30k/150)
  completed. `native_static_hsn_hardtail` (`fb94e178f2ecee97`) was strong in
  isolation but weaker than the deployed native model card F1 (0.9961 vs
  0.9984): precision 0.9955, recall 0.9968, AUC 0.9998, AP 0.9998, Brier
  0.0031. Reject for now.
- 2026-05-06: `source_formula_density_tax` (`b5af19645438cce3`) is the largest
  sampled specialist/filegroup win in this tranche: external F1 0.9939,
  precision 0.9908, recall 0.9969, AUC 0.9999, AP 0.9988, Brier 0.0010, versus
  deployed source model card F1 0.6615. It had degenerate isotonic calibration,
  so do not promote blindly, but route confirmation should be high priority.

Runtime note:

- The first general scoreless deep-H/S/N idea is confirmation-scale at 150k.
  For the rest of this tranche, prefer smaller chunks and consider lowering
  general runs to 100k/30k/150 trees unless confirming a likely winner.
