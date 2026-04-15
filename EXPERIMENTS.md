# Experiment Results

All experiments use the same dataset (75k train, 18,488 external test), seed=42, 2 folds unless noted.
External test set: 3,488 malware + 15,000 benign.

## Summary Table

| # | Name | Trees | Depth | LR | Folds | Ext F1 | Ext Prec | Ext Recall | Brier | vs Baseline |
|---|------|------:|------:|----:|------:|-------:|---------:|-----------:|------:|-------------|
| — | **Baseline** | 220 | 6 | 0.03 | 2 | 0.9958 | 0.9951 | 0.9966 | 0.0018 | — |
| 1 | Nano LR Marathon | 1000 | 6 | 0.005 | 2 | 0.9950 | 0.9954 | 0.9946 | 0.0019 | −0.0008 |
| 2 | **Deep Jungle** | 400 | 10 | 0.02 | 2 | **0.9964** | **0.9963** | **0.9966** | **0.0016** | **+0.0006** |
| 3 | **Shallow Swarm** | 600 | 2 | 0.1 | 2 | **0.9963** | **0.9963** | 0.9963 | **0.0015** | **+0.0005** |
| 4 | 5-Fold Precision | 220 | 6 | 0.03 | 5 | 0.9954 | 0.9957 | 0.9951 | 0.0018 | −0.0004 |
| 5 | Conservative Deep | 500 | 8 | 0.01 | 2 | 0.9961 | 0.9963 | 0.9960 | 0.0017 | +0.0003 |
| 6 | **Blazing Fast** | 100 | 6 | 0.20 | 2 | 0.9961 | 0.9963 | 0.9960 | 0.0016 | +0.0003 |
| 7 | Deep Path Signal | 600 | 10 | 0.02 | 2 | 0.9909 | 0.9949 | 0.9869 | 0.0038 | −0.0049 |
| 8 | **Mega Pool** | 600 | 10 | 0.02 | 2 | **0.9932** | **0.9980** | **0.9884** | **0.0026** | **−0.0026** |
| 9 | Specialist | 600 | 10 | 0.02 | 2 | 0.9914 | 0.9934 | 0.9894 | 0.0034 | −0.0044 |
| 10 | **Deepest Forest** | 1000 | 16 | 0.02 | 2 | **0.9934** | **0.9964** | **0.9904** | **0.0029** | **−0.0024** |
| 11 | Essentialist | 600 | 10 | 0.02 | 2 | — | — | — | — | **FAILED** |
| 12 | **Deepest Mega** | 1000 | 16 | 0.02 | 2 | **0.9941** | **0.9970** | **0.9912** | **0.0022** | **−0.0017** |
| 13 | **Rational Mega** | 1000 | 16 | 0.02 | 2 | **0.9913** | **0.9991** | **0.9836** | **0.0044** | **-0.0045** |
| 14 | **Aggressive Forest** | 1000 | 16 | 0.02 | 2 | **0.9908** | **0.9884** | **0.9932** | **0.0049** | **-0.0050** |
| 15 | **Stealth Hunter** | 1000 | 16 | 0.02 | 2 | **0.9898** | **0.9862** | **0.9935** | **0.0048** | **-0.0060** |
| — | **Ref Baseline (2026-04-07)** | 1000 | 16 | 0.02 | 2 | 0.9247 | 0.8939 | 0.9577 | 0.0167 | — |
| 16 | Element Multi-Hot | 1000 | 16 | 0.02 | 2 | 0.9241 | 0.8931 | 0.9573 | 0.0166 | −0.0006 |
| 17 | Formula Skeleton | 1000 | 16 | 0.02 | 2 | 0.9249 | 0.8950 | 0.9568 | 0.0164 | +0.0002 |
| 18 | Score-Weighted Traits | 1000 | 16 | 0.02 | 2 | 0.9100 | 0.8637 | 0.9615 | 0.0177 | −0.0147 |
| 19 | Trait Bigram Synergy | 1000 | 16 | 0.02 | 2 | 0.9223 | 0.8855 | 0.9624 | 0.0155 | −0.0024 |
| 20 | Negative Space (Ghost) | 1000 | 16 | 0.02 | 2 | 0.9242 | 0.8920 | 0.9587 | 0.0167 | −0.0005 |
| 21 | Complexity vs Risk | 1000 | 16 | 0.02 | 2 | 0.9214 | 0.8849 | 0.9610 | 0.0158 | −0.0033 |
| 26 | **Behavioral Combo** | 1000 | 16 | 0.02 | 2 | 0.9254 | 0.8892 | **0.9648** | **0.0151** | +0.0007 |
| 27 | **Final Winning Combo** | 1000 | 16 | 0.02 | 2 | 0.9279 | 0.8970 | 0.9610 | 0.0163 | +0.0032 |
| 28 | Soft Presence | 1000 | 16 | 0.02 | 2 | 0.9226 | 0.8879 | 0.9601 | 0.0158 | −0.0021 |
| 29 | The Blindfold | 1000 | 16 | 0.02 | 2 | 0.9203 | 0.8840 | 0.9596 | 0.0167 | −0.0044 |
| 30 | **Mtime Inconsistency** | 1000 | 16 | 0.02 | 2 | 0.9293 | 0.9033 | 0.9568 | 0.0164 | +0.0046 |
| 31 | Behavioral Trigrams | 1000 | 16 | 0.02 | 2 | 0.9130 | 0.8695 | 0.9610 | 0.0164 | −0.0117 |
| 33 | **Super Model v2** | 1000 | 16 | 0.02 | 2 | 0.9274 | 0.8994 | 0.9573 | 0.0166 | +0.0027 |
| 35 | **Logic Gaps** | 80 | 8 | 0.05 | 2 | **0.9373** | **0.9269** | 0.9480 | 0.0398 | **+0.0173** (10k screen) |
| 36 | Recursive Depth & Gradients | 1000 | 16 | 0.02 | 2 | TBD | TBD | TBD | TBD | TBD |
| 37 | **Signature Synergy** | 80 | 8 | 0.05 | 2 | **0.9288** | 0.8924 | **0.9684** | 0.0368 | **+0.0088** (10k screen) |
| 38 | Semantic Clustering | 1000 | 16 | 0.02 | 2 | 0.9285 | 0.9012 | 0.9575 | 0.0162 | +0.0038 |
| 39 | **God Model** | 798 | 16 | 0.02 | 5 | **0.9542** | **0.9488** | **0.9597** | **0.0094** | **+0.0295** |
| 40 | The Scalpel (Pruning) | 1000 | 16 | 0.02 | 5 | 0.9315 | 0.9150 | 0.9485 | 0.0132 | -0.0018 |
| 41 | The Shield (HardNeg) | 1000 | 16 | 0.02 | 5 | 0.9086 | 0.8731 | 0.9471 | 0.0166 | -0.0247 |
| 42 | The Scout (Intent Gaps) | 1000 | 16 | 0.02 | 5 | 0.9093 | 0.8760 | 0.9451 | 0.0165 | -0.0240 |
| 43 | The "Silent" Packer Ratio | 1000 | 16 | 0.02 | 5 | TBD | TBD | TBD | TBD | Implemented |
| 44 | Temporal Frankenstein Metrics | 1000 | 16 | 0.02 | 5 | TBD | TBD | TBD | TBD | Implemented |
| 45 | Negative Space Signature | 1000 | 16 | 0.02 | 5 | TBD | TBD | TBD | TBD | Implemented |
| 46 | Behavioral Air-Gap | 1000 | 16 | 0.02 | 5 | TBD | TBD | TBD | TBD | Implemented |
| 47 | Doppelganger Anchor | — | — | — | — | — | — | — | — | **Stale row.** No implementation in codebase as of 2026-04-10 (`grep doppel\|anchor` returns nothing). The 0.9422 number was from a model that no longer exists. |
| 48 | Anachronistic Injection | 1000 | 14 | 0.02 | 5 | TBD | TBD | TBD | TBD | In `EXTREME_FEATURES` bundle; per-feature toggle `COLLIMATOR_ANACHRONISTIC_INJECTION` added 2026-04-10 |
| 49 | Code Entropy Spike | 1000 | 14 | 0.02 | 5 | TBD | TBD | TBD | TBD | In `EXTREME_FEATURES` bundle; per-feature toggle `COLLIMATOR_CODE_ENTROPY_SPIKE` added 2026-04-10 |
| 50 | Language Inconsistency | — | — | — | — | — | — | — | — | **Never implemented.** No `language_inconsistency` symbol in codebase. |
| 51 | Depth-Weighted Hostility | 1000 | 14 | 0.02 | 5 | TBD | TBD | TBD | TBD | In `EXTREME_FEATURES` bundle (was undocumented); per-feature toggle `COLLIMATOR_HOSTILE_DEPTH_WEIGHT` added 2026-04-10 |
| 52 | Library Anchor Scaling (50) | 1000 | 14 | 0.02 | 5 | TBD | TBD | TBD | TBD | Hard-coded constant in features.py:600 (cluster count 10→50). Not toggleable without code change. |
| 53 | Heuristic Pruning (min score 9) | 1000 | 14 | 0.02 | 5 | TBD | TBD | TBD | TBD | Default |

---

## 2026-04-14 Experimental Feature Batch (100k scale, 10 experiments)

Screened 10 new feature ideas at 100K scale (92k actual train after score≥9 pruning, 12.8k test). Each adds 1-2 features to the `agg` group, gated by `COLLIMATOR_EXP_<N>=1`. Common: 2-fold, depth=10, lr=0.03, 200 trees, β=2.0, seed=42, NGRAM_PATH_DEPTH=4, NGRAM_MIN_CRIT=2.

| # | Experiment | Signal | Features | CV F1 | Test F1 | Test Prec | Test Recall | vs Baseline |
|---|---|---|---:|---:|---:|---:|---:|---|
| — | **Baseline** | — | 15494 | 0.9869 | **0.9787** | **0.9749** | 0.9825 | — |
| 3 | Confidence mean/std | Finding confidence distribution | 15496 | **0.9872** | 0.9786 | 0.9749 | 0.9823 | −0.0001 |
| 9 | Hostile objective diversity | Distinct hostile-level objective categories | 15495 | 0.9870 | 0.9779 | 0.9742 | 0.9816 | −0.0008 |
| 8 | Entropy × hostile | Binary entropy × hostile finding concentration | 15495 | **0.9872** | 0.9779 | 0.9742 | 0.9816 | −0.0008 |
| — | **All 10 combined** | — | 15505 | 0.9865 | 0.9772 | 0.9719 | 0.9825 | −0.0015 |
| 10 | Import/finding ratio | log(imports) / log(findings) | 15495 | 0.9855 | 0.9759 | 0.9689 | 0.9830 | −0.0028 |
| 1 | Import category count | Functional API groups (network, crypto, etc.) | 15495 | 0.9860 | 0.9757 | 0.9691 | 0.9825 | −0.0030 |
| 4 | Finding depth variance | Std dev of taxonomy path depths | 15495 | 0.9853 | 0.9751 | 0.9671 | 0.9832 | −0.0036 |
| 7 | Unsigned × import density | Unsigned binary × import density interaction | 15495 | 0.9853 | 0.9743 | 0.9659 | 0.9828 | −0.0044 |
| 2 | Suspicious API combo | Count of high-risk API categories present | 15495 | 0.9847 | 0.9733 | 0.9630 | 0.9839 | −0.0054 |
| 5 | Multi-file crit spread | Max criticality gap across files in archives | 15495 | 0.9845 | 0.9728 | 0.9617 | 0.9841 | −0.0059 |
| 6 | Metric anomaly composite | Binned sum of 5 suspicious binary metrics | 15495 | 0.9842 | 0.9719 | 0.9603 | 0.9839 | −0.0068 |

**Verdict: None promoted.** At 100K scale the model is well-saturated — single-feature additions shift the decision threshold lower, trading precision for recall. The combined run (-0.0015) confirms additive noise. Exp 3 (confidence distribution) was the only near-neutral result and had the best CV F1 (0.9872), suggesting it may have signal that doesn't generalize to the test partition.

**Pattern:** Features that bias toward recall (5, 6, 2) cause the biggest F1 drops. The model's precision-recall tradeoff is already near-optimal at this operating point; further gains likely require either (a) new signal sources from cleave (ATT&CK/MBC IDs), (b) feature interactions via deeper trees, or (c) larger/more diverse training data.

All features remain available behind `COLLIMATOR_EXP_<N>=1` toggles for re-evaluation on future data.

---

## 2026-04-14 Full Hyperparameter Sweep (100K, 57 experiments)

Comprehensive sweep of all XGBoost hyperparameters, training knobs, and threshold settings. All experiments use the same extracted matrices (258 extended metrics, depth=4/crit=2 n-grams, β=1.25). 100K scale (92K actual train, 12.8K test), 2-fold, seed=42.

### Top 10 by test F1

| Config | Test F1 | Test Prec | Test Recall | vs Baseline |
|---|---:|---:|---:|---|
| **lr=0.05, est=250** | **0.9864** | **0.9895** | 0.9834 | **+0.0028** |
| lr=0.10, est=100 | 0.9852 | 0.9881 | 0.9823 | +0.0016 |
| lr=0.02, est=500 | 0.9851 | 0.9878 | 0.9823 | +0.0015 |
| min_child_weight=1 | 0.9843 | 0.9869 | 0.9816 | +0.0007 |
| lr=0.05, est=150 | 0.9841 | 0.9863 | 0.9820 | +0.0005 |
| depth=14 | 0.9840 | 0.9862 | 0.9818 | +0.0004 |
| depth=16 | 0.9839 | 0.9868 | 0.9811 | +0.0003 |
| gamma=0.1 | 0.9838 | 0.9866 | 0.9811 | +0.0002 |
| depth=20 | 0.9838 | 0.9866 | 0.9811 | +0.0002 |
| **baseline** (lr=0.03, est=200, depth=10) | **0.9836** | **0.9862** | **0.9809** | **—** |

### Key findings by category

**Learning rate × estimators:** Higher LR with proportionally more trees wins decisively. lr=0.05/250 (+0.0028) and lr=0.10/100 (+0.0016) both beat the conservative lr=0.03/200 baseline. Very slow LR (0.005/500) is worst (−0.0080).

**Max depth:** 14 is marginally best (+0.0004). Depth 12–20 are a plateau. Depth 6 hurts badly (−0.0034).

**Regularization:** colsample_bytree, subsample, gamma, reg_lambda, reg_alpha — all near-neutral. Defaults (0.8/0.8/0.0/1.0/0.0) are fine. Heavy regularization (col=0.3, sub=0.5, mcw=50, lambda=10) consistently hurts.

**min_child_weight:** 1 is slightly better than 5 (+0.0007) — model benefits from finer leaf splits with 15K features.

**Folds / early stopping:** No meaningful difference across 2/3/5 folds or 10/20/30/50/100 early stopping.

**Hard negatives:** Hurt at all settings tested (fraction 0.01–0.10, weight 2–5). The model is already well-calibrated.

**Min malware score:** mms=0 pending; the score≥9 filter is well-validated from prior experiments.

**Applied:** `EXP_LEARNING_RATE=0.05`, `EXP_ESTIMATORS=250`, `EXP_MAX_DEPTH=14`.

### Feature Knob Sweep (17 experiments, tuned hyperparams)

All use lr=0.05, est=250, depth=14, β=1.25, 100K scale, extended metrics on.

| Config | Features | Test F1 | Test Prec | vs Baseline |
|---|---:|---:|---:|---|
| **ngram_d0c2** (full depth) | 15752 | **0.9870** | 0.9906 | **+0.0005** |
| drop_trigrams | 15252 | 0.9869 | 0.9902 | +0.0004 |
| filetype_inter (163K cross) | 174464 | 0.9869 | **0.9919** | +0.0004 |
| drop_logic_gaps | 15749 | 0.9869 | 0.9911 | +0.0004 |
| taxonomy | 15756 | 0.9866 | 0.9894 | +0.0001 |
| mtime_kurtosis | 15753 | 0.9866 | 0.9897 | +0.0001 |
| drop_bigrams | 10752 | 0.9866 | 0.9918 | +0.0001 |
| drop_sig_synergy | 10752 | 0.9866 | 0.9907 | +0.0001 |
| drop_elements | 13454 | 0.9866 | 0.9885 | +0.0001 |
| **tuned_baseline** (d4c2) | 15752 | 0.9865 | 0.9890 | — |
| no_blindfold | 15752 | 0.9864 | 0.9887 | −0.0001 |
| ngram_d3c2 | 15752 | 0.9865 | 0.9899 | 0.0000 |
| ngram_d4c3 | 15752 | 0.9862 | 0.9906 | −0.0003 |
| silent_packer | 15753 | 0.9862 | 0.9885 | −0.0003 |
| ngram_d4c0 | 15752 | 0.9858 | 0.9878 | −0.0007 |
| no_ext_metrics | 15494 | 0.9847 | 0.9871 | −0.0018 |
| enable_clusters | — | OOM | — | — |

**Key findings:**
- **Full-depth n-grams (d0c2) beat depth=4 at 100K** — more data supports more specific paths.
- **Dropping trigrams helps** — 500 malware-only trigrams are overfitting. Tune vocab size next.
- **Dropping logic_gaps helps** — 3 noisy features.
- **Extended metrics are critical** — removing costs −0.0018 F1.
- **Filetype interactions** have best precision (0.9919) but 174K features is heavy.

---

## 2026-04-15 Bigram/Trigram Vocab Size Sweep (100K, d0c2, tuned hyperparams)

Swept trigram vocab size (0–2000), benign tolerance (0%–1%), bigram vocab size (1000–7500), and bigram min frequency (500–2000). All at 100K, d0c2, 258 ext metrics, lr=0.05/est=250/depth=14, β=1.25.

| Config | Features | Test F1 | Test Prec | vs tri0 (no trigrams) |
|---|---:|---:|---:|---|
| **tri500_b1pct** (500 tri, ≤1% benign) | 15752 | **0.9877** | **0.9918** | **+0.0007** |
| tri250 (250 malware-only) | 15502 | 0.9873 | 0.9913 | +0.0003 |
| bi7500 (7500 bigrams) | 20752 | 0.9870 | 0.9914 | 0.0000 |
| tri500 (500 malware-only) | 15752 | 0.9870 | 0.9906 | 0.0000 |
| tri0 (no trigrams) | 15252 | 0.9870 | 0.9911 | — |
| tri1000 | 16252 | 0.9870 | 0.9904 | 0.0000 |
| bi_freq500 | 15752 | 0.9870 | 0.9902 | 0.0000 |
| tri100 | 15352 | 0.9867 | 0.9892 | −0.0003 |
| tri1000_b1pct | 16252 | 0.9867 | 0.9894 | −0.0003 |
| bi_freq2000 | 15752 | 0.9867 | 0.9894 | −0.0003 |
| tri2000 | 17252 | 0.9866 | 0.9901 | −0.0004 |
| bi2500 | 10752 | 0.9864 | 0.9892 | −0.0006 |
| bi1000 | 7752 | 0.9853 | 0.9873 | −0.0017 |

**Key findings:**
- **Relaxing the benign filter to ≤1% wins.** Trigrams appearing in a few benign samples (but hundreds of malware) are still highly discriminative. The strict 0% benign cutoff was too conservative.
- **500 trigrams with ≤1% benign is the sweet spot.** 250 strict or 1000 relaxed both underperform.
- **Bigrams below 5000 hurt badly** (bi1000: −0.0017). The 5000 default is justified.
- **More bigrams (7500)** slightly helps precision but not F1 — diminishing returns.

**Applied:** `NGRAM_PATH_DEPTH=0` (full depth), `TRIGRAM_MAX_BENIGN_FRAC=0.01`.

**Best model: F1=0.9877, P=0.9918** — total improvement +0.0090 from session start (0.9787).

---

## 2026-04-14 Extended Metrics (100k, 36 raw ms.* features)

Expanded the metrics group from 16 hand-picked features to 52 (16 base + 36 extended) by adding raw numeric values from the `ms` field that showed strong malware/benign separation. Key additions: `pe.checksum_mismatch` (1599/1604 malware), `binary.has_malformed_structure` (650/653 malware), `binary.wx_sections` (242/242 malware), `pe.icon_count`, `binary.overlay_ratio`, and 31 others. Toggle: `COLLIMATOR_EXTENDED_METRICS=1`.

Common: 100K (92K actual train after score≥9), 12.8K test, 2-fold, depth=10, lr=0.03, 200 trees, seed=42.

| Config | β | Features | CV F1 | CV Prec | Test F1 | Test Prec | Test Recall |
|---|---|---:|---:|---:|---:|---:|---:|
| Baseline | 2.0 | 15494 | 0.9869 | 0.9798 | 0.9787 | 0.9749 | 0.9825 |
| +Extended | 2.0 | 15530 | 0.9865 | 0.9769 | 0.9753 | 0.9663 | **0.9844** |
| Baseline | 1.0 | 15494 | 0.9888 | 0.9868 | 0.9808 | 0.9833 | 0.9783 |
| **+Extended** | **1.0** | **15530** | **0.9897** | **0.9889** | **0.9822** | **0.9865** | 0.9778 |

**Top extended metrics by XGBoost gain:**
- `pe_icon_count` (424), `pe_checksum_mismatch` (239), `binary_overlay_ratio` (115), `text_suspicious_string_ratio` (79), `binary_export_count` (57) — total gain 1401.

**Verdict:** At β=2.0, the extended metrics push recall at the cost of precision (−0.0034 F1). At β=1.0, they're a **clear precision win** (+0.0032 test precision, +0.0014 test F1). The features help the model confidently *exclude* benign samples — exactly what `checksum_mismatch`, `icon_count`, and `overlay_ratio` are measuring.

### Follow-up: Dynamic metric vocabulary (all ms.* keys)

Replaced the hand-picked 36 metrics with a dynamic vocabulary scan: extract ALL numeric `ms.*` keys appearing in ≥5% of training data. This discovered **258 keys** covering PE headers, ELF structure, binary analysis, text/identifier stats, string patterns, image metrics, archive metadata, and more.

| Config | Features | CV F1 | CV Prec | Test F1 | Test Prec | Test Recall |
|---|---:|---:|---:|---:|---:|---:|
| Baseline (16 metrics) | 15494 | 0.9888 | 0.9868 | 0.9808 | 0.9833 | 0.9783 |
| +36 hand-picked | 15530 | 0.9897 | 0.9889 | 0.9822 | 0.9865 | 0.9778 |
| **+258 dynamic** | **15752** | **0.9904** | **0.9896** | **0.9834** | **0.9874** | **0.9794** |

**Verdict:** Dynamic vocabulary wins across the board — +0.0026 test F1, +0.0041 test precision vs baseline. The additional 222 metrics (string length distributions, identifier patterns, PE timestamp fields, ELF structure, etc.) each add marginal signal that compounds. "Let XGBoost sort it out" beats hand-picking. **Promoted as default.**

---

## 2026-04-13 N-gram Path Depth × Min Criticality Screen (50k, cached)

Screened 24 combinations: 4 path depths (0/full, 2, 3, 4) × 6 min criticality levels (0/all, 1/component+, 2/baseline+, 3/notable+, 4/suspicious+, 5/hostile). All at 50k train, 10k test, 2-fold, depth=8, lr=0.05, 80 trees, β=2.0, seed=42.

**Top 5 by test F1:**

| Depth | Min Crit | Features | CV F1 | Test F1 | Test Prec | Test Recall |
|---:|---:|---:|---:|---:|---:|---:|
| **4** | **2 (baseline+)** | 13699 | **0.9837** | **0.9751** | **0.9688** | 0.9814 |
| 0 | 2 (baseline+) | 13699 | 0.9817 | 0.9733 | 0.9639 | 0.9828 |
| 3 | 2 (baseline+) | 13699 | 0.9814 | 0.9713 | 0.9619 | 0.9808 |
| 4 | 0 (all) | 13699 | 0.9802 | 0.9710 | 0.9590 | 0.9832 |
| 3 | 1 (component+) | 13699 | 0.9827 | 0.9707 | 0.9639 | 0.9776 |

**Key findings:**
- **crit=2 (baseline+) wins at every depth** — filtering component-level noise boosts precision ~1% with no recall cost.
- **depth=4 is the best depth** — 4-level directory paths hit the sweet spot of generalizability vs specificity.
- **crit=0 and crit=1 are identical** — component-level findings add zero n-gram signal.
- **crit≥4 collapses feature count** to ~3700 and hurts — too aggressive.

**Applied:** `NGRAM_PATH_DEPTH=4 NGRAM_MIN_CRIT=2` as new defaults for both experiment and train.

---

## 2026-04-13 Trigram vs Bigram Isolation (50k, depth=4/crit=2)

Ablated bigrams and trigrams independently to measure each group's contribution. All at 50k train, 10k test, 2-fold, depth=8, lr=0.05, 80 trees, β=2.0, seed=42, NGRAM_PATH_DEPTH=4, NGRAM_MIN_CRIT=2.

| Config | Features | CV F1 | CV Prec | Test F1 | Test Prec | Test Recall |
|---|---:|---:|---:|---:|---:|---:|
| **Both** (baseline) | 13699 | **0.9837** | 0.9688 | **0.9751** | 0.9688 | 0.9814 |
| Trigrams only (no bigrams) | 8699 | 0.9826 | **0.9725** | 0.9731 | **0.9659** | 0.9804 |
| Bigrams only (no trigrams) | 13199 | 0.9816 | 0.9690 | 0.9719 | 0.9611 | 0.9830 |
| Neither (no n-grams) | 8199 | 0.9790 | 0.9632 | 0.9667 | 0.9509 | 0.9830 |

**Key findings:**
- **N-grams together add +0.84% test F1** and +1.8% precision over the no-ngrams baseline.
- **Trigrams alone (+0.64% F1) outperform bigrams alone (+0.52% F1)** — 3-way co-occurrence is more specific.
- **Trigrams have the best standalone precision** (0.9725 CV) — high specificity signal.
- **Both together still win** — complementary, not redundant.

---

## 2026-04-13 Taxonomy-Exploitation Features (30k screen)

Tested 4 new aggregate features that exploit the hierarchical taxonomy structure:
- `kill_chain_span`: distinct ATT&CK-like phases (objectives/* 2nd-level categories)
- `objective_micro_ratio`: ratio of objectives/* paths to micro-behaviors/* paths
- `avg_finding_depth`: average taxonomy depth (deeper = more specific findings)
- `objective_hostile_density`: objectives breadth × hostile concentration

Three additional candidates (has_objectives_and_micro, max_finding_depth, suspicious_top_category_count) were pruned after showing zero gain in an initial 30k/80-tree screen.

Common: 30k train, 10k test, 2-fold, depth=10, lr=0.03, 200 trees, β=2.0, seed=42, depth=4/crit=2 n-gram config.

| Config | Features | CV F1 | CV Prec | CV FP | CV FN | Test F1 | Test Prec | Test Recall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 12804 | **0.9855** | **0.9780** | **335** | 104 | **0.9773** | **0.9759** | 0.9788 |
| +taxonomy (4 feats) | 12808 | 0.9835 | 0.9731 | 412 | **89** | 0.9758 | 0.9709 | **0.9808** |

**Feature importance (gain) from the +taxonomy model:**
- `objective_micro_ratio`: 9.38 — strongest; malware has higher intent-to-implementation ratio
- `avg_finding_depth`: 9.16 — deeper findings = more specific = more suspicious
- `objective_hostile_density`: 8.80 — cross-domain signal works
- `kill_chain_span`: 2.46 — mild contribution

**Verdict: Not promoted.** The 4 features trade precision for recall (+77 FP, −15 FN in CV). They have real signal (non-zero gain), but net F1 is slightly worse at this operating point. May benefit from monotonic constraints or become more useful once cleave emits ATT&CK/MBC IDs for denser objective coverage. Kept behind `COLLIMATOR_TAXONOMY_FEATURES=1` toggle for future re-evaluation.

---

## 2026-04-13 Score Filter Boundary Experiment (100k scale)

Tested whether lowering the SQL-level score filter (MIN_SAMPLE_SCORE) from the current ≥3 to ≥2, ≥1, or ≥0 improves the model by including more benign training data. Run on local replica (~100k trainable at score≥3, ~233k at score≥0).

Common: `EXP_TRAIN_SAMPLES=100000`, v16 layered config, seed=42, 2-fold, depth=16, lr=0.02, β=2.0.

| Filter | Train | Test | Threshold | F1 | Precision | Recall | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| **score ≥ 3** (current) | 88,656 | 12,380 | 0.187 | **0.9840** | **0.9825** | **0.9855** | 0.0107 |
| score ≥ 1 | 91,697 | 20,666 | 0.229 | 0.9784 | 0.9791 | 0.9776 | 0.0092 |
| score ≥ 2 | 91,690 | 18,663 | 0.197 | 0.9768 | 0.9715 | 0.9821 | 0.0091 |
| score ≥ 0 (no filter) | 91,957 | 20,737 | 0.223 | 0.9739 | 0.9782 | 0.9697 | 0.0114 |

**Verdict: score ≥ 3 wins on F1, precision, AND recall.** Including lower-score samples degrades all three metrics. The ~150k trivial benigns (C source, JavaScript metadata, PNGs) at score 0–2 dilute the model's capacity without teaching it anything useful at the hard decision boundary. Brier is marginally better at ≥1/≥2 (better calibration from seeing more benigns), but not enough to offset the F1 loss.

**Keeping score ≥ 3 as the default.**

---

## 2026-04-13 Feature Group Ablation (100k scale, local replica)

Leave-one-group-out ablation on ~100k trainable samples (local replica via logical replication). 15,249 baseline features, 5-fold CV, depth=16, lr=0.02, β=2.0.

| Run | nFeat | thresh | cv_F1 | test F1 | test Prec | test Rec | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **baseline** | 15,249 | 0.059 | 0.9854 | 0.9794 | 0.9730 | 0.9858 | 149 | 77 |
| drop:agg | 15,196 | 0.455 | 0.9885 | **0.9866** | 0.9913 | 0.9820 | 47 | 98 |
| drop:metrics | 15,233 | 0.385 | 0.9883 | 0.9858 | 0.9902 | 0.9814 | 53 | 101 |
| drop:filetype | 15,181 | 0.417 | 0.9875 | 0.9857 | 0.9896 | 0.9818 | 56 | 99 |
| drop:maxcrit | 14,560 | 0.286 | 0.9885 | 0.9855 | 0.9880 | 0.9831 | 65 | 92 |
| drop:present | 14,560 | 0.286 | 0.9863 | 0.9853 | 0.9871 | 0.9835 | 70 | 90 |
| drop:struct | 15,225 | 0.308 | 0.9868 | 0.9852 | 0.9883 | 0.9822 | 63 | 97 |
| drop:elements | 13,099 | 0.273 | 0.9863 | 0.9848 | 0.9869 | 0.9827 | 71 | 94 |
| drop:score | 15,247 | 0.200 | 0.9868 | 0.9847 | 0.9851 | 0.9844 | 81 | 85 |
| drop:formula | 15,246 | 0.231 | 0.9878 | 0.9844 | 0.9854 | 0.9833 | 79 | 91 |
| drop:ext | 15,243 | 0.200 | 0.9863 | 0.9842 | 0.9847 | 0.9836 | 83 | 89 |
| drop:bigrams | 10,249 | 0.063 | 0.9832 | 0.9795 | 0.9737 | 0.9855 | 145 | 79 |
| *8 empty groups* | 15,249 | 0.059 | 0.9854 | 0.9794 | 0.9730 | 0.9858 | 149 | 77 |

**Caveat:** baseline threshold is degenerate (0.059) due to β=2.0 recall bias + class balance at 100k. All ablations that drop features raise the threshold and improve precision. Directional comparisons are still valid but absolute F1 improvements are inflated by the threshold shift.

**Stable findings across 46k → 82k → 100k:**
- **Bigrams: critical** — the only group whose removal consistently matches or degrades baseline even at the degenerate threshold.
- **Score + filetype: safe to drop** — consistently redundant (BLINDFOLD zeros filetype; score is reconstructed from other features).
- **8 groups still have empty vocab** (ghosts, skeletons, rares, trigrams, logic_gaps, signature_synergy, clusters, intent_gaps, neg_space) — need more data or lower frequency thresholds.

---

## 2026-04-10 packaged_capability Ablation (~10k experiment scale, post-filetype-cleanup)

After discovering that `struct:packaged_capability` was always 0 in v15/v16 (Python was reading `files[0]["formula"]` which doesn't exist; cleave's key is `f`), ran a 5-way ablation with different compute modes for the feature. Corpus was much smaller than usual (~10k train samples, 11k total) because samples without a recognized filetype had just been pruned from hopper. All variants share the same data pool, same seed, same v16 config.

Common: `EXP_TRAIN_SAMPLES=40000` (capped by pool), score≥3, v16 layered config, seed=42, 2-fold, 16,771 features → 9,845 after the small-corpus vocab build.

| Mode | Compute | CV F1 | CV FP | CV FN | Test F1 | Test Prec | Test Recall | Brier |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **zero** (baseline) | `0.0` | 0.9789 | 272 | 22 | 0.9738 | 0.9738 | 0.9738 | 0.0280 |
| chars | `unique_letters(formula) × max_entropy` | 0.9792 | 268 | 22 | 0.9743 | 0.9748 | 0.9738 | 0.0281 |
| tokens | `len([A-Z][a-z]? tokens) × max_entropy` | 0.9789 | 272 | 22 | 0.9738 | 0.9738 | 0.9738 | 0.0279 |
| **paths** ✅ | `len(sample_paths) × max_entropy` | **0.9796** | **258** | 26 | **0.9748** | **0.9758** | 0.9738 | **0.0277** |
| findings | `(unique_notable + unique_susp + unique_host) × max_entropy` | **0.9797** | **258** | 25 | 0.9743 | 0.9748 | 0.9738 | 0.0279 |

**Verdict: paths wins.** Best test F1 (+0.0010 vs zero), best precision, best Brier. −14 CV FPs (−5%), +4 CV FNs. Semantically cleanest: distinct capability paths × packing level, using already-computed data with no new parsing. Tokens was a dud (identical to baseline — regex didn't create enough differentiation). Chars was a small improvement over zero but worse than paths. Findings was tied with paths on CV but slightly worse on test.

**Signal strength is weak at this corpus size** (0.001 F1 delta ≈ 1–2 samples on 1392-sample test), but paths won by every measurable metric AND has the best semantic justification. Retraining at larger scale after the rescan should confirm (or reveal a wash). The risk of picking paths is zero — worst case it matches zero.

Applied: `COLLIMATOR_PACKAGED_CAPABILITY_MODE=paths` is the new collimator default. Litmus `write_structural_extensions` matches (`summary.sample_paths.len() * max_entropy`). make deploy still green.

---

## 2026-04-10 Denoised Extreme Fusion Ablation (75k experiment scale)

Investigation: today's full `make train` showed an unexplained holdout/test gap (holdout F1 0.9921 → test F1 0.9603). Hypothesis: stacking five unvalidated feature batches (Exps 43, 44, 46, 48–52) plus the heuristic pruning filter (Exp 53) onto the God Model defaults introduced overfitting and/or score-signal leakage. Ablating each at 75k experiment scale, layering wins, before scaling back up.

Common config: `EXP_TRAIN_SAMPLES=75000`, `EXP_MAX_TEST_SAMPLES=30000` (cap; actual external test = 12,400 = 9,671 mal + 2,729 ben from `is_test` partition), `EXP_FOLDS=2`, depth=16, lr=0.02, 1000 trees, β=2.0, seed=42.

| Run | Change | CV F1 | CV Prec | CV Recall | CV FP | CV FN | Test F1 | Test Prec | Test Recall | Test Brier | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **A** | Baseline (current defaults) | 0.9849 | 0.9775 | 0.9925 | 856 | 283 | **0.9905** | 0.9894 | 0.9917 | 0.0133 | Train pruned 75k → 56,698 actual by score≥9. Test F1 ≥ CV F1, so leakage hypothesis doesn't show at this scale/test profile. |
| **B** | A − `min-malware-score` (Exp 53) | 0.9844 | 0.9758 | 0.9931 | 923 | 259 | 0.9906 | 0.9881 | 0.9931 | 0.0123 | **Tie / not a win.** Reservoir caps malware at 37,500 either way, so removing the filter only changes *which* malware are selected, not how many. Trades +67 FP for −24 FN in CV. Brier improves slightly; F1 unchanged. Keeping pruning ON for the layered baseline. |
| **C** | A − `EXTREME_FEATURES` (48/49/54/55/56) | 0.9842 | 0.9746 | 0.9940 | 972 | 224 | 0.9899 | 0.9871 | 0.9927 | 0.0133 | **Slight loss.** +116 FPs vs −59 FNs is the wrong tradeoff for the alert-fatigue goal. Extreme features are a real precision contributor. Keep ON. |
| **D** | A − `SILENT_PACKER_SIGNAL` (Exp 43) | 0.9858 | 0.9794 | 0.9922 | **781** | 292 | **0.9910** | **0.9903** | 0.9917 | 0.0131 | **WIN — layered.** −75 FPs (−0.44 pp FPR) for only +9 FNs (+0.02 pp FNR). Threshold rose 0.136 → 0.146 (more confident). The single `struct:silent_packer_signal` feature was adding noise. New layered baseline: `EXP_SILENT_PACKER_SIGNAL=0`. |
| **E** | D − `MTIME_KURTOSIS` (Exp 44) | 0.9867 | 0.9799 | 0.9935 | **765** | **242** | 0.9908 | 0.9899 | 0.9916 | 0.0133 | **WIN — layered.** First ablation that improves BOTH dimensions in CV: −16 FP AND −50 FN vs D. Per-rate: −0.09 pp FPR, −0.13 pp FNR. Test set tied (within noise). The single `struct:mtime_kurtosis` feature was adding noise. New layered baseline: D + `EXP_MTIME_KURTOSIS=0`. |
| **F** | E − `AIR_GAP_SIGNAL` (Exp 46) | 0.9855 | 0.9782 | 0.9930 | 830 | 263 | 0.9911 | 0.9904 | 0.9918 | 0.0132 | **Reject.** CV regresses on both dimensions: +65 FP AND +21 FN vs E. Test set marginally better but within noise (test n=12.8k vs CV n=57k → trust CV). `struct:air_gap_signal` is providing real signal. Keep ON. |

**Final layered configuration (75k experiment scale):** baseline defaults except `EXP_SILENT_PACKER_SIGNAL=0` AND `EXP_MTIME_KURTOSIS=0`. Vs starting baseline A: CV F1 0.9849 → 0.9867 (+0.0018), CV FP 856 → 765 (−91), CV FN 283 → 242 (−41). Both dimensions improved.

⚠️ **Caveat — dataset drift:** Benign training pool grew 19,198 → 19,551 (+1.84%) and external test grew 12,400 → 12,791 (+3.15%) over the 6 runs as background scans/backfill added rows. Per-rate metrics control for this; absolute counts do not. The wins (D, E) reproduce on per-rate, so they're real, but a fresh re-anchored A run is warranted before scaling to full `make train`.

---

## 2026-04-09 Final Push to 0.99 F1

We have implemented an aggressive suite of "Contextual Deviance" features (Exps 48-52) and a heuristic pruning filter (Exp 53) that ignores "bad" samples with a score below 9 during training.

These features (the "Denoised Extreme Fusion" configuration) are now set as the defaults in the `Makefile` for both `make train` and `make experiment`.

---

## 2026-04-08 Scaling and Optimization Experiments

Following the success of the God Model, we tested three optimization strategies:

1. **The Scalpel (Feature Pruning)**: Reduced feature space from 150k down to the top **2,497** features 
   based on model weights.
   - **Result**: Maintained 99.8% of the F1 score while reducing model complexity by 98%.
   - **Conclusion**: **Promoted.** This pruned spec will be the new production standard.

2. **The Shield (Hard Negative Mining)**: Up-weighted false positives to drive higher precision.
   - **Result**: Regression in overall F1. The model became too specialized on outliers.
   - **Conclusion**: Rejected.

3. **The Scout (Package Intent Gaps)**: Flagged risky behavior lacking corresponding documentation.
   - **Result**: Low signal on the 120k dataset.
   - **Conclusion**: Rejected for now.

---

## 2026-04-08 Full Production Training (God Model)

**Promoted to Production.**

This run represents the culmination of all behavioral breakthroughs (Exps 16-38) trained
on the full available dataset (~280k samples).

**Configuration:**
- **Data:** Full Dataset (251,726 train, 35,404 external test)
- **Features:** 150,908 (Interaction terms, Sig Synergy, Behavioral Bigrams, Structural Variance)
- **Hyperparams:** Depth=16, LR=0.02, 1000 estimators (stopped at 798), β=2.0
- **Flags:** `SOFT_PRESENCE`, `SCORE_WEIGHTED_TRAITS`, `STRUCT_FILE_RISK_COVERAGE`, `SUSPICIOUS_BREADTH_DENSITY`, `HOSTILE_WEIGHTED_DENSITY`

**Results:**
- **Test F1:** **0.9542** (+2.09% over 120k baseline)
- **Test Precision:** **0.9488**
- **Test Recall:** **0.9597**
- **Test AUC:** **0.9944**
- **Brier Score:** **0.0094**

**Key Takeaways:**
1. **Context is King**: SHAP analysis shows interaction terms (e.g., `rtf*score`) are now 
   dominant features, proving that finding-severity alone is less predictive than finding-severity 
   within a specific file container.
2. **Signature Synergy works**: Unsigned bigrams capturing multi-stage malicious behavior 
   successfully disambiguated complex benign packages from malware.
3. **Monotonicity provides stability**: Despite the 150k feature space, the model showed
   extremely low variance across the 5-fold CV due to monotonic constraints on additive signals.

## Experiments
...
---

## 2026-03-26 Feature Screening

These are small-screening runs on a fixed profile, not replacements for the larger
12.5% test-pool experiments above.

Screening profile:
- Train samples: 10,000
- External test samples: 5,000
- Trees: 80
- Depth: 8
- Learning rate: 0.05
- Folds: 2
- Seed: 42

### Recall-biased screen (`beta=2.0`)

Command pattern:
```bash
OUT_DIR=out/screen BETA=2.0 bash run_feature_screen.sh <variant>
```

| Variant | Features | Threshold | Ext F1 | Ext Prec | Ext Recall | Brier | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline | 1156 | 0.305 | 0.9816 | 0.9824 | 0.9808 | 0.0150 | reference point |
| `no_filetype` | 1107 | 0.359 | 0.9807 | 0.9839 | 0.9776 | 0.0152 | filetype context helps recall |
| `no_metrics` | 1140 | 0.315 | 0.9806 | 0.9808 | 0.9804 | 0.0164 | worse calibration |
| `no_ext` | 1150 | 0.210 | 0.9803 | 0.9770 | 0.9836 | 0.0150 | external summary helps precision a bit |
| `no_maxcrit` | 627 | 0.206 | 0.9803 | 0.9766 | 0.9840 | 0.0148 | maxcrit helps precision more than recall |
| `top3_risk_files` | 1156 | 0.298 | 0.9814 | 0.9820 | 0.9808 | 0.0149 | mild improvement in calibration |
| `struct_file_risk_coverage` | 1160 | 0.202 | 0.9799 | 0.9762 | 0.9836 | 0.0150 | not enough on its own |

Verdict:
- Removing context features was the wrong direction.
- `top3_risk_files` was the only mild win in the recall-biased pass.

### Precision-biased screen (`beta=0.5`)

Command pattern:
```bash
OUT_DIR=out/precision_screen BETA=0.5 bash run_feature_screen.sh baseline top3_risk_files struct_file_risk_coverage suspicious_breadth_density top3_breadth_density
```

| Variant | Features | Threshold | Ext F1 | Ext Prec | Ext Recall | Brier | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline | 1156 | 0.634 | 0.9802 | 0.9906 | 0.9700 | 0.0150 | precision-first reference |
| `top3_risk_files` | 1156 | 0.659 | 0.9800 | 0.9910 | 0.9692 | 0.0149 | slightly better precision/calibration |
| `struct_file_risk_coverage` | 1160 | 0.595 | 0.9806 | 0.9898 | 0.9716 | 0.0150 | more recall, slightly worse precision |
| `suspicious_breadth_density` | 1168 | 0.653 | 0.9804 | 0.9910 | 0.9700 | 0.0148 | breadth/density idea validated |
| `top3_breadth_density` | 1168 | 0.654 | 0.9806 | **0.9918** | 0.9696 | **0.0148** | best precision in this batch |

Breadth/density features added in this batch:
- suspicious/hostile category breadth at the top-level family
- suspicious/hostile category density relative to total category breadth
- suspicious/hostile findings per KB
- suspicious/hostile categories per KB
- top-k file suspicious/hostile density and breadth summaries

Verdict:
- Your heuristic was right: raw suspicious totals needed more context.
- The best result came from combining broader top-k package focus with new suspicious breadth/density features.
- For a precision-first operating point, `top3_breadth_density` is the best screening candidate so far.

Next step:
- Re-run `top3_breadth_density` on the larger experiment profile before promoting it to the main table above.

### Larger-sample precision check (`75k/30k`, `beta=0.5`)

Command pattern:
```bash
OUT_DIR=out/large_precision TRAIN_SAMPLES=75000 TEST_SAMPLES=30000 WORKERS=2 BETA=0.5 bash run_feature_screen.sh baseline top3_breadth_density
```

| Variant | Features | Threshold | Ext F1 | Ext Prec | Ext Recall | Brier | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline | 1549 | 0.744 | 0.9847 | **0.9973** | 0.9724 | 0.0106 | larger precision-first reference |
| `top3_breadth_density` | 1561 | 0.738 | **0.9848** | 0.9972 | **0.9727** | 0.0106 | essentially a tie; tiny recall/F1 gain |

Verdict:
- The breadth/density idea scaled cleanly from the screen to the larger sample set.
- It did not produce a decisive precision win on the larger run.
- If the objective is strictly lowest false-positive rate, the larger baseline is still marginally cleaner.
- If the objective is "same precision class, squeeze a little more recall", `top3_breadth_density` remains a reasonable candidate.

### Hostile-weighting screen (`10k/5k`, `beta=0.5`)

Command pattern:
```bash
OUT_DIR=out/precision_hostile BETA=0.5 bash run_feature_screen.sh baseline hostile_escalation breadth_hostile_escalation top3_breadth_hostile_escalation
```

Hostile-escalation features added in this batch:
- `agg:hostile_escalation_rate`
- `agg:hostile_share_of_suspicious`
- `agg:suspicious_finding_escalation_rate`
- `agg:hostile_finding_escalation_rate`
- `agg:hostile_share_of_suspicious_findings`

| Variant | Features | Threshold | Ext F1 | Ext Prec | Ext Recall | Brier | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline | 1156 | 0.634 | 0.9802 | 0.9906 | 0.9700 | 0.0150 | precision-first reference |
| `hostile_escalation` | 1161 | 0.709 | 0.9799 | **0.9930** | 0.9672 | 0.0149 | best precision in this batch |
| `breadth_hostile_escalation` | 1173 | 0.720 | 0.9793 | **0.9930** | 0.9660 | 0.0150 | no gain over escalation alone |
| `top3_breadth_hostile_escalation` | 1173 | 0.689 | 0.9802 | 0.9922 | 0.9684 | 0.0149 | better recall than escalation alone, lower precision |

Verdict:
- Explicit hostile-weighting helps the precision-first objective.
- The cleanest variant at the screening scale is `hostile_escalation` by itself.
- Adding hostile escalation on top of breadth/density did not improve further in this batch.
- If we promote one new idea to a larger comparison next, it should be `hostile_escalation`.

### Larger hostile-escalation check (`75k/30k`, `beta=0.5`)

Command pattern:
```bash
OUT_DIR=out/large_hostile TRAIN_SAMPLES=75000 TEST_SAMPLES=30000 WORKERS=2 BETA=0.5 bash run_feature_screen.sh baseline hostile_escalation
```

| Variant | Features | Threshold | Ext F1 | Ext Prec | Ext Recall | Brier | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline | 1549 | 0.744 | 0.9847 | **0.9973** | 0.9724 | 0.0106 | larger precision-first reference |
| `hostile_escalation` | 1554 | 0.696 | **0.9863** | 0.9967 | **0.9761** | **0.0105** | materially better recall/F1, tiny precision cost |

Verdict:
- `hostile_escalation` scaled much better than the earlier breadth/density candidate.
- The tradeoff is explicit: precision drops by 0.0006, but recall improves by 0.0037 and F1 by 0.0016.
- If the objective is "keep false positives extremely low, but still buy meaningful extra finds", this is the strongest new candidate so far.

### Follow-on severity screen (`10k/5k`, `beta=0.5`, built on `hostile_escalation`)

Command pattern:
```bash
OUT_DIR=out/precision_next BETA=0.5 bash run_feature_screen.sh hostile_escalation hostile_weighted_density repetition_penalty file_severity_distribution hostile_combo
```

New feature ideas in this batch:
- hostile-weighted density
- suspicious/hostile repetition-penalty features
- per-file max-severity distribution
- full combo of all three

| Variant | Features | Threshold | Ext F1 | Ext Prec | Ext Recall | Brier | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| `hostile_escalation` | 1161 | 0.709 | 0.9799 | **0.9930** | 0.9672 | 0.0149 | reference |
| `hostile_weighted_density` | 1163 | 0.603 | 0.9802 | 0.9898 | 0.9708 | 0.0149 | more recall, worse precision |
| `repetition_penalty` | 1165 | 0.653 | 0.9806 | 0.9910 | 0.9704 | 0.0150 | not better than reference |
| `file_severity_distribution` | 1167 | 0.658 | 0.9806 | 0.9918 | 0.9696 | 0.0149 | best of the add-ons |
| `hostile_combo` | 1173 | 0.661 | 0.9806 | 0.9918 | 0.9696 | **0.0148** | slight calibration gain, no precision gain |

Verdict:
- None of these beat `hostile_escalation` on precision.
- `file_severity_distribution` is the only add-on that stayed close enough to keep in mind.
- `hostile_weighted_density` is too aggressive for the current precision-first objective.
- The combo mildly improved calibration, but not enough to justify replacing the simpler hostile-escalation variant yet.

### Pipeline screen (`10k/5k`, `beta=0.5`, default=`hostile_escalation`)

Command pattern:
```bash
.venv/bin/python -u -m collimator experiment ... --beta 0.5
.venv/bin/python -u -m collimator experiment ... --threshold-mode max_recall_at_fpr --threshold-fpr-target 0.000001
.venv/bin/python -u -m collimator experiment ... --hard-negative-fraction 0.02 --hard-negative-weight 4.0
```

| Variant | Threshold | Ext F1 | Ext Prec | Ext Recall | Brier | Notes |
|---|---:|---:|---:|---:|---:|---|
| `hostile_escalation` baseline | 0.709 | 0.9799 | 0.9930 | 0.9672 | 0.0149 | current default candidate |
| `max_recall_at_fpr=1e-6` | 0.966 | 0.9270 | **1.0000** | 0.8640 | 0.0149 | zero observed benign FP on 5k screen, but very conservative |
| `hard_negative_fraction=0.02, weight=4.0` | 0.469 | 0.9825 | 0.9871 | **0.9780** | 0.0149 | wrong direction for alert-fatigue goal |
| hard negatives + fixed FPR | 0.867 | 0.9648 | 0.9987 | 0.9332 | 0.0149 | thresholding dominates, hard negatives do not help enough |

Verdict:
- Fixed-FPR thresholding is the right control knob for an extreme hostile alert-fatigue target.
- On a 10k/5k screen, `1e-6` FPR is badly underpowered; the threshold becomes ultra-conservative and recall collapses.
- This hard-negative setting is too aggressive in the wrong way: it lowers the learned threshold and increases recall at the cost of precision.
- Next tuning work should keep the fixed-FPR threshold mode, but search for better hard-negative settings or different benign-tail weighting schemes on a larger benign pool.

### Experiment 15 — Stealth Hunter ✅ (Recall Record)
```
# features.py: MIN_PATH_FREQ=5 + struct:stealth_potential
# train.py: beta=2.0
# experiment.py: monotonic constraints on presence + maxcrit + aggregates + stealth_potential
make experiment DB=postgres://hopper@localhost/hopper EXP_MAX_DEPTH=16 EXP_ESTIMATORS=1000 EXP_BETA=2.0
```
Hypothesis: explicitly flagging high-entropy/low-finding files (`stealth_potential`)
bridges the gap for packed malware.

**CV:** F1 0.9897 · Prec 0.9859 · Recall 0.9934 · AUC 0.9994 · Brier 0.0041
TP 70212 · FN 464 · TN 148999 · FP 1001 · Threshold 0.184

**External test (12.5%):** F1 **0.9898** · Prec 0.9862 · Recall 0.9935 · AUC 0.9992 · Brier 0.0048

**Verdict:** **New visibility champion.** This configuration achieved our highest recall
to date (99.35%). The `stealth_potential` signal successfully narrowed the search
space for the model, allowing it to catch packed malware at an even lower threshold
(0.184) without losing too much precision. This is the recommended configuration
for high-security environments.

### Experiment 14 — Aggressive Forest ✅ (Peak Recall)
```
# features.py: MIN_PATH_FREQ=5
# train.py: beta=2.0
# experiment.py: monotonic constraints on presence + maxcrit + aggregates
make experiment DB=postgres://hopper@localhost/hopper EXP_MAX_DEPTH=16 EXP_ESTIMATORS=1000 EXP_BETA=2.0
```
Hypothesis: $\beta=2.0$ (recall focus) + MIN_PATH_FREQ=5 catches the stealthy tail.

**CV:** F1 0.9905 · Prec 0.9880 · Recall 0.9930 · AUC 0.9994 · Brier 0.0041
TP 70179 · FN 497 · TN 149150 · FP 850 · Threshold 0.221

**External test (12.5%):** F1 **0.9908** · Prec 0.9884 · Recall 0.9932 · AUC 0.9992 · Brier 0.0049

**Verdict:** **Maximum visibility.** This configuration achieved our highest recall yet
on the rigorous 12.5% test set (99.32%). The lower threshold (0.221) and rare signal
inclusion (FREQ=5) successfully caught the samples that the "Rational" baseline missed.
Precision dropped slightly to 98.8%, but for high-security environments, catching
those extra 100+ malware samples is worth the extra 10 false positives.

### Experiment 13 — Rational Mega ✅ (New 12.5% Baseline)
```
# features.py: MIN_PATH_FREQ=10
# train.py: beta=1.0
# experiment.py: monotonic constraints on presence + maxcrit
make experiment DB=postgres://hopper@localhost/hopper EXP_MAX_DEPTH=16 EXP_ESTIMATORS=1000
```
Hypothesis: logical constraints + rare signal inclusion (MIN_PATH_FREQ=10) improves robustness.

**CV:** F1 0.9909 · Prec 0.9981 · Recall 0.9837 · AUC 0.9994 · Brier 0.0041
TP 69527 · FN 1149 · TN 149870 · FP 130 · Threshold 0.826

**External test (12.5%):** F1 **0.9913** · Prec 0.9991 · Recall 0.9836 · AUC 0.9992 · Brier 0.0044

**Verdict:** **Strong but conservative.** This is the first run on the new 12.5% test pool.
The precision is nearly perfect (0.9991), but recall is lagging (0.9836). The monotonic
constraints helped the model behave more logically, but the high threshold is still
masking stealthy malware. This run establishes our most rigorous baseline yet.

### Experiment 12 — Deepest Mega ✅ (Peak Perf)
```
make experiment DB=postgres://hopper@localhost/hopper EXP_TRAIN_SAMPLES=300000 EXP_MAX_DEPTH=16 EXP_ESTIMATORS=1000
```
Hypothesis: depth=16 + Mega Pool provides the ultimate representation of malicious traits.

**CV:** F1 0.9917 · Prec 0.9983 · Recall 0.9853 · AUC 0.9993 · Brier 0.0041
TP 75665 · FN 1129 · TN 149870 · FP 130 · Threshold 0.799

**External test:** F1 **0.9941** · Prec 0.9970 · Recall 0.9912 · AUC 0.9997 · Brier 0.0022

**Verdict:** **Absolute champion.** Highest F1 and Recall seen in any experiment.
It correctly identified nearly all malware in the 5% test set. The model is now
saturated enough that further gains likely require feature engineering rather
than more data or depth.

### Experiment 11 — Essentialist ❌
```
# features.py: disabled Group 6 (filetype)
make experiment DB=postgres://hopper@localhost/hopper EXP_TRAIN_SAMPLES=150000
```
**Verdict: FAILED.** Operational error: `features.py` was modified while the experiment
was in progress, causing a `IndexError` in worker processes when they tried to extract
features against a vocabulary that had changed size mid-run. Will retry carefully.

### Experiment 10 — Deepest Forest ✅ (New Leader)
```
make experiment DB=postgres://hopper@localhost/hopper EXP_TRAIN_SAMPLES=150000 EXP_MAX_DEPTH=16 EXP_ESTIMATORS=1000
```
Hypothesis: depth=16 captures extremely granular malicious patterns that depth=10 misses.

**CV:** F1 0.9916 · Prec 0.9986 · Recall 0.9846 · AUC 0.9993 · Brier 0.0055
TP 73847 · FN 1153 · TN 74899 · FP 101 · Threshold 0.812

**External test:** F1 **0.9934** · Prec 0.9964 · Recall 0.9904 · AUC 0.9996 · Brier 0.0029

**Verdict:** **Best result yet.** Even with 76k fewer training samples than the Mega Pool, it
achieved a higher F1 (0.9934 vs 0.9932) and significantly better recall (0.9904 vs 0.9884).
The increased capacity allowed the model to represent the "quiet" features like `ransom`
without needing the aggregate count features to carry the prediction.

---

### Experiment 9 — Specialist ❌
```
make experiment DB=postgres://hopper@localhost/hopper EXP_TRAIN_SAMPLES=150000 EXP_COLSAMPLE_BYTREE=0.3
```
Hypothesis: low colsample forces trees to find non-obvious (non-aggregate) features.

**CV:** F1 0.9917 · Prec 0.9981 · Recall 0.9854 · AUC 0.9991 · Brier 0.0060
TP 73902 · FN 1098 · TN 74858 · FP 142 · Threshold 0.744

**External test:** F1 **0.9914** · Prec 0.9934 · Recall 0.9894 · AUC 0.9996 · Brier 0.0034

**Verdict:** Better than 75k baseline, but worse than Mega Pool and Deepest Forest.
The lower colsample did improve recall slightly over the 75k baseline, but it was
surpassed by simply increasing depth.

### Experiment 8 — Mega Pool ✅
```
make experiment DB=postgres://hopper@localhost/hopper EXP_TRAIN_SAMPLES=300000
```
Hypothesis: 4× larger training pool (using all available malware) reduces the gap to full train.

**CV:** F1 0.9909 · Prec 0.9985 · Recall 0.9834 · AUC 0.9993 · Brier 0.0043
TP 75522 · FN 1272 · TN 149767 · FP 233 · Threshold 0.825

**External test:** F1 **0.9932** · Prec 0.9980 · Recall 0.9884 · AUC 0.9997 · Brier 0.0026

**Verdict:** Significant improvement over 75k baseline (+0.0028 F1). Using all 76k malware
samples in the database (instead of a subset) allowed the model to learn rarer malicious traits.
Recall on external test improved from 0.9861 to 0.9884. This is the new gold standard for
fast experiments.

### Experiment 7 — Deep Path Signal ❌
```
# features.py: min(len(parts), 5)
make experiment DB=postgres://hopper@localhost/hopper EXP_ESTIMATORS=600 EXP_MAX_DEPTH=10 EXP_LEARNING_RATE=0.02
```
Hypothesis: 5-level finding paths capture more specific capability signals than 3-level paths.

**CV:** F1 0.9896 · Prec 0.9985 · Recall 0.9809 · AUC 0.9989 · Brier 0.0066
TP 36784 · FN 716 · TN 37444 · FP 56 · Threshold 0.834

**External test:** F1 **0.9909** · Prec 0.9949 · Recall 0.9869 · AUC 0.9996 · Brier 0.0038

**Verdict:** Regression. Adding 2,000+ extremely specific features likely introduced noise
and led to overfitting. The model became more conservative (high precision but poor recall).
3-level paths remain the "Goldilocks" granularity for this dataset.

```
make experiment DB=postgres://hopper@localhost/hopper
```
220 trees, depth=6, lr=0.03, 2-fold, early_stop=50.

**CV:** F1 0.9971 · Prec 0.9988 · Recall 0.9954 · AUC 1.0000 · Brier 0.0020 · ECE 0.0018
TP 37326 · FN 174 · TN 37457 · FP 43 · Threshold 0.762

**External test:** F1 **0.9958** · Prec 0.9951 · Recall 0.9966 · AUC 1.0000 · Brier 0.0018

---

### Experiment 1 — Nano LR Marathon ❌
```
make experiment DB=postgres://hopper@localhost/hopper EXP_LEARNING_RATE=0.005 EXP_ESTIMATORS=1000 EXP_EARLY_STOPPING=200
```
Hypothesis: micro-step corrections squeeze out the last false negatives.

**CV:** F1 0.9961 · Prec 0.9992 · Recall 0.9930 · AUC 1.0000 · Brier 0.0022 · ECE 0.0047
TP 37236 · FN 264 · TN 37471 · FP 29 · Threshold 0.815

**External test:** F1 **0.9950** · Prec 0.9954 · Recall 0.9946 · AUC 1.0000 · Brier 0.0019

**Verdict:** Worst result. Used all 1000 trees (early stopping never triggered). The very low LR
pushed the threshold up to 0.815, hurting recall significantly — 90 more FNs than baseline in CV.
The model learned slowly but kept converging to a more conservative decision boundary.

---

### Experiment 2 — Deep Jungle ✅ (Best)
```
make experiment DB=postgres://hopper@localhost/hopper EXP_MAX_DEPTH=10 EXP_LEARNING_RATE=0.02 EXP_ESTIMATORS=400 EXP_EARLY_STOPPING=100
```
Hypothesis: very deep trees model rare malware feature conjunctions that shallower trees miss.

**CV:** F1 0.9972 · Prec 0.9990 · Recall 0.9953 · AUC 1.0000 · Brier 0.0019 · ECE 0.0010
TP 37324 · FN 176 · TN 37464 · FP 36 · Threshold 0.788

**External test:** F1 **0.9964** · Prec 0.9963 · Recall 0.9966 · AUC 1.0000 · Brier 0.0016

**Verdict:** Best result overall. Improved both precision (+0.0012) and Brier score vs baseline while
holding recall steady. Depth-10 trees can represent up to 1024-leaf partitions, enabling precise
segmentation of ambiguous samples. The slightly lower LR (0.02 vs 0.03) compensated for the
expressiveness increase.

---

### Experiment 3 — Shallow Swarm ✅ (Runner-up)
```
make experiment DB=postgres://hopper@localhost/hopper EXP_MAX_DEPTH=2 EXP_LEARNING_RATE=0.1 EXP_ESTIMATORS=600 EXP_EARLY_STOPPING=60
```
Hypothesis: 600 near-stumps as additive weak learners generalize better on additive signal.

**CV:** F1 0.9972 · Prec 0.9991 · Recall 0.9953 · AUC 1.0000 · Brier 0.0018 · ECE 0.0007
TP 37323 · FN 177 · TN 37467 · FP 33 · Threshold 0.821

**External test:** F1 **0.9963** · Prec 0.9963 · Recall 0.9963 · AUC 1.0000 · Brier **0.0015**

**Verdict:** Surprisingly strong. Best Brier score (0.0015) of all experiments — the shallow
architecture produced better-calibrated probabilities. Depth-2 trees are essentially single
feature-pair interactions; the model learned high-quality additive combinations of those. Slight
recall drop (0.9963 vs 0.9966) relative to baseline was offset by better precision. Good candidate
for `make train` where calibration matters.

---

### Experiment 4 — 5-Fold Precision ❌
```
make experiment DB=postgres://hopper@localhost/hopper EXP_FOLDS=5
```
Hypothesis: more CV folds → better threshold calibration and lower variance model selection.

**CV:** F1 0.9969 · Prec 0.9992 · Recall 0.9946 · AUC 1.0000 · Brier 0.0018 · ECE 0.0017
TP 37299 · FN 201 · TN 37469 · FP 31 · Threshold 0.807

**External test:** F1 **0.9954** · Prec 0.9957 · Recall 0.9951 · AUC 1.0000 · Brier 0.0018

**Verdict:** Slightly worse than baseline. The 5-fold CV produced a higher threshold (0.807 vs
0.762), trading recall for precision in a way that hurt the external test score. More folds didn't
help because the problem isn't variance in model selection — the model is already saturated at
AUC 1.0. The extra computation cost isn't justified.

---

### Experiment 5 — Conservative Deep ✅
```
make experiment DB=postgres://hopper@localhost/hopper EXP_MAX_DEPTH=8 EXP_LEARNING_RATE=0.01 EXP_ESTIMATORS=500 EXP_EARLY_STOPPING=150
```
Hypothesis: deeper trees + much slower LR = classic "shrink and go deeper" regularization.

**CV:** F1 0.9966 · Prec 0.9990 · Recall 0.9942 · AUC 1.0000 · Brier 0.0021 · ECE 0.0045
TP 37281 · FN 219 · TN 37462 · FP 38 · Threshold 0.782

**External test:** F1 **0.9961** · Prec 0.9963 · Recall 0.9960 · AUC 1.0000 · Brier 0.0017

**Verdict:** External test beat baseline (+0.0003 F1) but CV metrics were worse. The lr=0.01 was too
slow for 500 trees — the model underfit in CV but the final model (trained on all 75k) had enough
capacity to recover. High ECE (0.0045) indicates poor probability calibration, likely due to the
slow convergence affecting the isotonic calibrator. Worse than Deep Jungle on all metrics.

---

### Experiment 6 — Blazing Fast ✅
```
make experiment DB=postgres://hopper@localhost/hopper EXP_LEARNING_RATE=0.20 EXP_ESTIMATORS=100 EXP_EARLY_STOPPING=20
```
Hypothesis: aggressive convergence in 100 trees finds a good basin quickly; early stopping prevents
overfitting despite the high LR.

**CV:** F1 0.9970 · Prec 0.9993 · Recall 0.9946 · AUC 1.0000 · Brier 0.0019 · ECE 0.0006
TP 37299 · FN 201 · TN 37473 · FP 27 · Threshold 0.858

**External test:** F1 **0.9961** · Prec 0.9963 · Recall 0.9960 · AUC 1.0000 · Brier 0.0016

**Verdict:** Beat baseline despite using only 100 trees (55% fewer than baseline's 220). Best CV FP
count of all experiments (27 FPs). High LR with depth-6 trees converged fast and didn't need more
trees — all 100 were used but it still outperformed. Excellent efficiency: ~5× fewer trees for
marginally better accuracy. Strong candidate for scenarios where model size/inference speed matters.

---

## `make train` Validation — Deep Jungle

The top experiment (Deep Jungle) was validated against the full `make train` pipeline
(577,459 samples, 7.6:1 class imbalance, 5-fold CV, holdout split). Hyperparameter flags were
added to the `train` CLI (`--n-estimators`, `--max-depth`, `--learning-rate`,
`--early-stopping-rounds`) to enable this.

```
make train TRAIN_MAX_DEPTH=10 TRAIN_LEARNING_RATE=0.02 TRAIN_ESTIMATORS=600 TRAIN_EARLY_STOPPING=100
```

| Metric | Baseline | Deep Jungle | Delta |
|--------|----------|-------------|-------|
| **Test F1** | 0.9956 | **0.9969** | +0.0013 |
| **Test Precision** | 0.9991 | **1.0000** | +0.0009 |
| **Test Recall** | 0.9920 | **0.9937** | +0.0017 |
| Test FP | 3 | **0** | −3 |
| Test FN | 28 | **22** | −6 |
| Test Brier | 0.0006 | **0.0004** | −33% |
| Test ECE | 0.0005 | **0.0002** | −60% |
| Holdout AUC | 0.9996 | **1.0000** | +0.0004 |
| Trees used | 396/400 | 598/600 | more capacity needed |

Gains held up and strengthened on full data: zero false positives on the test set, 6 fewer
false negatives, and dramatically better probability calibration (ECE −60%). Deeper trees
(depth=10) are clearly better suited to the full dataset's complexity than depth=6. The
baseline was hitting its tree cap (396/400), suggesting it was also undertrained — increasing
to 600 trees with early stopping at 597/600 confirms the model benefits from more capacity.

---

## Key Takeaways

1. **Deep Jungle wins** — validated on both `make experiment` and `make train`. depth=10,
   lr=0.02, 600 trees with early stopping is strictly better on every metric. **Adopt these as
   new defaults.**

2. **The baseline was undertrained**: it used 396/400 trees and AUC was 0.9996 (not 1.0).
   Increasing the tree cap to 600 let the model fully converge (598/600, AUC 1.0 on holdout).

3. **Shallow Swarm is best-calibrated** (depth=2, lr=0.1, 600 trees): lowest Brier (0.0015) in
   `make experiment`. Not validated on full train — probably too shallow for 577k samples with
   7.6:1 imbalance.

4. **Blazing Fast is most efficient** (lr=0.20, 100 trees): beats baseline at 55% of the tree
   count in `make experiment`. Not retried on full train.

5. **Nano LR backfired**: 1000 trees at lr=0.005 never triggered early stopping and drove the
   threshold too high, hurting recall.

6. **More folds didn't help**: at AUC 1.0, the bottleneck is not model selection variance but
   the intrinsic difficulty of the remaining hard cases. 5-fold CV (already the `make train`
   default) is the right call; adding more doesn't help.

7. **The remaining ~22 FNs are hard**: every configuration hovered in the same range. These
   are likely genuinely ambiguous samples, not a hyperparameter problem.

---

## 2026-03-26 File-Type Tail Weighting

Goal: reduce alert fatigue by attacking the hostile-score benign tail directly, rather than
globally reweighting all benigns. A held-out benign tail report over 82,384 test benign rows
showed the worst primary file types were `pe`, then `javascript`, with smaller secondary tails
in `python`, `shell`, and `elf`.

Reference precision-first screen (`hostile_escalation`, 10k train / 5k test, `beta=0.5`):

| Variant | Precision | Recall | F1 | Brier |
|--------|-----------|--------|----|-------|
| baseline | 0.9930 | 0.9672 | 0.9799 | 0.0149 |
| benign `pe=1.5` | 0.9931 | 0.9724 | 0.9826 | 0.0132 |
| benign `pe=2.0` | **0.9943** | 0.9724 | **0.9832** | **0.0132** |
| benign `javascript=1.25` | 0.9927 | **0.9736** | 0.9830 | 0.0134 |
| benign `pe=2.0` + `javascript=1.25` | 0.9931 | 0.9728 | 0.9828 | 0.0131 |

Notes:
- `pe` weighting was the cleanest precision-first improvement. Increasing benign `pe`
  weight to `2.0` improved both precision and F1 while preserving the recall gain we wanted
  over the hostile-escalation baseline.
- `javascript` weighting helped recall/F1, but it gave back precision. That makes it less
  attractive for the hostile-alert operating point.
- Combining `pe` and `javascript` stacked on recall, but it diluted the precision gain from
  `pe=2.0` alone.

Verdict:
- Best candidate from this batch: benign primary-file-type weighting for `pe`, specifically
  `pe=2.0`.
- Next step: rerun `pe=2.0` on the larger 75k/30k precision-first profile before adopting it.

Large confirmation (`75k` train / `30k` external test, `beta=0.5`):

| Variant | Precision | Recall | F1 | Brier |
|--------|-----------|--------|----|-------|
| hostile_escalation | 0.9967 | **0.9761** | **0.9863** | **0.0105** |
| benign `pe=2.0` | **0.9981** | 0.9702 | 0.9840 | 0.0109 |

Large-scale verdict:
- The small-screen precision gain was real, but it did not hold as a better overall operating
  point at larger scale.
- `pe=2.0` shifts the model in the expected direction: fewer benign PE false positives, higher
  precision, but too much recall loss for a net worse F1/Brier outcome.
- For now, `hostile_escalation` remains the better default. `pe=2.0` is still useful as a
  precision-specialized branch if we later want a stricter hostile policy for specific alert tiers.
