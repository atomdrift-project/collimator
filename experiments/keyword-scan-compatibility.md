# Keyword configuration compatibility with Scan — 2026-10-31

Scan's ABI 23 feature reader supports all five keyword sources per model:
relative rule IDs (`ruleword`), descriptions (`descword`), full rule IDs
(`fullword`), pooled descriptions plus full IDs (`ruletextword`), and decoded
context (`contextword`). Context remains independent of the pooled source.

Frequency or supervised vocabulary selection happens during training. Scan
loads the saved `keyword_vocabs`, `feature_names`, explicit `base_feature_abi`,
and ONNX models. It does not repeat mutual-information selection or need the
training labels. The retained candidate columns in a supervised-selection
spec are intentional; discarded columns have no tree splits.

The PE candidate uses balanced-MI descriptions (5,000), balanced-MI relative
IDs (1,000), and frequency context (1,000), each with document support five.
The saved four-seed confirmation layout has 44,221 input columns. This is
the actual experimental model layout, including retained candidate columns,
not a newly trained approximation of its settings.

All eight exported experimental bundles pass all 304 report comparisons. The
largest Scan/native-Python probability difference is `1.19e-7`; the PE winner's
maximum is `8.94e-8`. Scan's library suite passes 777 tests, with four optional
tests skipped.

## Recurring cross-repository integration gate

`make test-scan-parity` runs `scripts/check_scan_parity.py` and is a prerequisite
of `make test`. It generates references from the current Python implementation,
discovers 187 base columns, trains and exports tiny two-seed LightGBM models,
then invokes Scan's actual extractor and model loader. It covers the baseline,
all 31 keyword combinations, and a standardized variant: 33 bundles × 17
reports = 561 comparisons. No database or experiment models are required.
The sibling Scan checkout and its Cargo dependencies must be available; the
Cargo invocation is locked and offline. Override its path with `SCAN_DIR`.

This gate found and fixed two runtime discrepancies:

- Promoting a binary `f32` confidence directly to `f64` differed from the
  decimal JSON that Python reads. It dropped `0.65` at the inclusion boundary
  and changed weighted feature values enough to take different tree branches.
  Scan now reconstructs the serialized decimal, caching distinct values per
  file. A regression checks the real Cleave encoder as well as the boundary.
- Legacy base ABIs emitted zero archive depth/parent features in Scan while
  Python populated them. Scan now uses absolute depth and parent presence for
  those ABIs; the separate relative-depth behavior remains unchanged.

Deliberately corrupting a reference feature and a reference probability each
caused the integration check to fail, as required.

An optional existing leaf bundle can be checked with its exact saved training
environment. This stages only its feature spec and ONNX members, comparing raw
model probabilities before calibration or routing:

```sh
make test-scan-parity PARITY_BUNDLE=/path/to/azoth/filetypes/pe \
  PARITY_CONFIG=/path/to/that-training-run/inputs.json
```

`PARITY_CONFIG` accepts a config/manifest with a `feature_env` object or that
object itself. It must describe the model being checked, not an assumed default.
In particular, the **existing** `../azoth/filetypes/pe` bundle fails when paired
with its saved accepted configuration: that config disables symbols, yet the
spec contains `symbol:CreateProcessW` and the ONNX members contain 10,104 symbol
splits in total. The fixture gets Python `0` versus Scan `1` for that column.
This is an unresolved saved-configuration inconsistency in the existing bundle;
the gate intentionally reports it. No existing bundle or accepted config was
rewritten to make this check pass. The experimental PE bundles pass with the
feature environments saved in their own `inputs.json`.

## Regression coverage

`scripts/keyword_combination_parity_fixture.py` generates 279 Python reference
cases: all 31 nonempty subsets of the five sources, across nine report cases.
Scan's `src/features/keywords.rs` checks both direct extraction and the shared
parse used across models. Cases include reversed column ordering, pruned
columns, duplicate words, missing descriptions, low-confidence findings,
legacy slash IDs, separate context windows, absent context, current byte-text
and legacy Z85 context, and normalized schema-7 display text.

`scripts/keyword_scan_model_fixtures.py` exports eight actual trained bundles
(26 seed models): the four-seed PE winner, separate description/ID sources,
relative IDs, descriptions, full hierarchy, pooled description/full hierarchy,
context alone, and the Mach-O pooled-plus-context experiment. These provide
both frequency-selected and balanced-MI-selected vocabularies.

Each bundle is checked on 29 real development reports (14 PE and 15 Mach-O)
and nine synthetic edge cases, for 304 bundle/report comparisons. The real
reports include both labels, score quantiles, and high-scoring goodware and
low-scoring malware. They are a runtime compatibility fixture, not a new
accuracy evaluation or a new holdout.

The saved database rows include older report schemas. The fixture generator
converts their field aliases and schema-7 display text to Scan's current typed
input, asserting exact equality of the complete Python feature vector before
and after alias conversion for every model. A separate, audited step represents
each archived single-file row as a current standalone report: it clears inherited
archive placement and renders confidences as the shortest `f32` decimals that
Cleave emits. This changes reference columns in 25 cases per bundle; column
names and maximum changes are recorded in `archive_to_current_input_changes`.
Consequently these runtime probabilities are **not** a replay of the original
archived-row scores. This does not add an importer for old database JSON to
Scan. Legacy Z85 context is exercised directly through Scan's typed decoder.

The opt-in `scan/tests/keyword_bundle_parity.rs` compares all extracted feature
columns and the ensemble probabilities against Python. Feature tolerance is
`max(1e-6, abs(expected) * 1e-5)`; probability tolerance is `1e-5`.

## Reproduction

From the collimator checkout, with the original experiment artifacts present:

```sh
.venv/bin/python scripts/keyword_combination_parity_fixture.py /tmp/keyword_combinations_parity.json
cmp /tmp/keyword_combinations_parity.json ../scan/src/features/keyword_combinations_parity.json
# Only needed for a new capture; fetch refuses to replace an existing capture.
.venv/bin/python scripts/keyword_scan_model_fixtures.py fetch
.venv/bin/python scripts/keyword_scan_model_fixtures.py build
KEYWORD_BUNDLE_CASES="$PWD/out/experiments/keyword-scan-parity/bundle_cases.json" \
  cargo test --manifest-path ../scan/Cargo.toml --locked --offline \
  --test keyword_bundle_parity -- --ignored --nocapture
cargo test --manifest-path ../scan/Cargo.toml --locked --offline --lib
make test-scan-parity
```

Large reports, exported bundles, vectors and the Python/ONNX audit remain in
`out/experiments/keyword-scan-parity/`. The small all-combinations fixture is
stored with Scan's unit tests so it runs without the corpus or trained models.

## Nightly and autocollie status

At the operator's request, the confirmed PE keyword settings are now adopted
in `model-configs/filetypes/pe.json`, the shared defaults for the next nightly
training run and autocollie proposals/replays. The configuration records the
sample confirmation evidence separately from its previous deployment provenance.
The next trained bundle still follows the normal validation and publishing gates.

The shared importance allowlist now permits `source:*` for all five keyword
families. These entries only affect enabled keyword sources; they preserve the
base-feature filter and let each training run discover its vocabulary subject
to the configured support/candidate/selection budgets. They never become literal
model columns. This reproduces the research runner's append-keywords policy
without freezing its sampled vocabulary into a production allowlist.

The specialist trainer now restores the route's feature environment for every
seed fit, as well as discovery/extraction. Otherwise balanced-MI overrides would
be lost when the extraction context exits. Tests exercise the current PE config,
normal vocabulary discovery, and selection during multiple seed fits. Autocollie's
actual loader, knob validation, replay environment, and prompt were also checked
against the updated config. No nightly job or model publication was triggered.

Nightly checkpoint identities now include the per-model configuration files
and their referenced allowlists. Changing these defaults invalidates old stage
receipts even when the command, Python code, and pinned corpus are unchanged.
