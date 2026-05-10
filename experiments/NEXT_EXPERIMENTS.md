# Next Experiments

Designed 2026-04-15. Current best: F1=0.9906 test, 0.9927 holdout.
Data: 106K trainable rows. MBC/ATT&CK data incoming via cleave `m`/`a` fields.

## Ready to run now

### Exp A: Feature pruning + more capacity
SHAP shows ~14K of 15.5K features contribute <0.001 importance.
Prune to top N features by SHAP gain, then train deeper.
- A1: Top 2000 features, 1500 trees, depth=18
- A2: Top 1000 features, 2000 trees, depth=20
- A3: Top 500 features, 2000 trees, depth=20
Hypothesis: removing noise lets the model specialize on hard cases.

### Exp B: Per-ecosystem models
PE malware and npm supply-chain malware are fundamentally different.
- B1: Train PE-only model (file_type=pe)
- B2: Train package-only model (file_type in javascript,python,ruby,go,rust,shell)
- B3: Evaluate each on their own test sets vs the unified model
Hypothesis: specialists outperform generalist on their own domain.

### Exp C: Import API features
The `is` field has rich import data we don't use (except indirectly via metrics).
- C1: import_count as a raw feature (already in extended metrics)
- C2: Top-100 most common import names as multi-hot features
- C3: Import functional categories (network, crypto, process_inject, etc.)
Hypothesis: import patterns add signal orthogonal to finding paths.

### Exp D: Confidence-weighted n-grams
Current bigrams/trigrams are binary (0/1). Weight by average confidence
of the component findings instead.
- D1: Confidence-weighted bigrams (replace 1.0 with avg confidence)
- D2: Confidence-weighted trigrams
Hypothesis: high-confidence co-occurrences are more discriminative.

### Exp E: Adversarial FP training
Use the 45 test FP samples as hard negative examples in a second
training pass. Or add synthetic "known-benign" features.
- E1: Train with hard_negative_fraction=0.05, targeting installer/crypto FPs
- E2: Add "is_installer" and "has_crypto_library" synthetic features
Hypothesis: explicitly teaching what benign-but-complex looks like.

## Ready when MBC/ATT&CK data arrives

### Exp F: ATT&CK technique features
New `a` field in findings. T-codes map to kill chain phases.
- F1: ATT&CK technique presence (multi-hot over unique T-codes)
- F2: ATT&CK tactic count (how many kill chain phases covered)
- F3: ATT&CK technique bigrams (co-occurring techniques)
Hypothesis: ATT&CK provides a standardized attack vocabulary.

### Exp G: MBC behavior features
New `m` field in findings. MBC IDs describe malware behavior.
- G1: MBC ID presence (multi-hot)
- G2: MBC behavior category count
Hypothesis: MBC captures implementation-level behavior patterns.

## Methodological roadmap

### Family-aware split audit
The current train/dev/test partition keys on `canonical_sha256` last byte
(`src/collimator/data.py`). Archive-level duplication is prevented (an
archive and its inner files share `canonical_sha256`), but
**campaign/family-level correlation is not**: same actor, same packer,
same dropper produces different content hashes that can land on opposite
sides of the split. Reported metrics may therefore be optimistic against
truly held-out malware.

Reliable family labels do not exist in hopper yet. The plan once test
data regeneration lands is to treat the `Sample.formula` field as an
informal content-cluster hash and:

1. For each test sample, count near-duplicates in train by formula match.
   Report the distribution.
2. If the leakage rate is non-trivial, switch to a formula-stratified
   partition (group by formula, assign each formula group to one
   partition) instead of byte-level hashing.

Until this is feasible, document the limitation explicitly in any paper
or model card: "metrics reflect content-deduplicated splitting only;
campaign-level generalization is not measured."

### Temporal evaluation
Filesystem `mtime` is when the file was packed/written, not when the
sample entered the corpus, so it isn't usable for temporal split. Once
hopper logs an ingest timestamp on insert and enough months have
accumulated, time-blocked evaluation (train ≤ T1, dev T1–T2, test > T2)
becomes feasible and should be reported alongside random-split metrics.
