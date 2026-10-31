# Full rule ID, pooled description, and context keyword screen

## Results

Natural 10% cohorts; two-seed ensembles. Cells are **recall at 0 FP / recall at 1 FP (%)**. These are averaged-probability bundle results, not averages of individual-seed recall.

| File type | Dev malware | Baseline | Relative ID | Description | Full ID | Full + desc separate | Full + desc pooled | Context |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| java_class | 22 | 0.0 / 40.9 | 0.0 / 86.4 | 0.0 / 81.8 | 0.0 / 59.1 | 0.0 / 54.5 | 0.0 / 54.5 | 0.0 / 81.8 |
| go | 135 | 34.8 / 45.2 | 3.7 / 18.5 | 31.1 / 34.8 | 5.9 / 50.4 | 1.5 / 28.9 | 2.2 / 14.8 | 5.2 / 8.1 |
| c | 250 | 40.8 / 54.4 | 37.6 / 44.4 | 49.6 / 50.4 | 43.2 / 50.8 | 46.8 / 48.4 | 36.4 / 48.4 | 51.6 / 53.2 |
| python | 273 | 70.7 / 72.5 | 69.6 / 70.7 | 67.4 / 71.8 | 69.2 / 71.8 | 68.9 / 72.2 | 67.4 / 73.6 | 71.8 / 73.3 |
| javascript | 1832 | 65.6 / 71.4 | 54.0 / 57.6 | 50.8 / 60.1 | 55.1 / 62.6 | 49.6 / 59.4 | 57.9 / 61.5 | 59.3 / 64.7 |

The strongest new follow-up is context for Python: +1.1 percentage points at 0 FP and +0.7 at 1 FP. C context gains 10.8 points at 0 FP but loses 1.2 at 1 FP. Go full-ID words gain 5.2 points at 1 FP but lose 28.9 at 0 FP. Python pooling gains 1.1 points at 1 FP but loses 3.3 at 0 FP. These are operating-point tradeoffs, not universal improvements.

Java’s relative-ID control remains strongest at 1 FP; all Java arms score zero at 0 FP, and the dev set has only 22 malware examples. JavaScript’s baseline wins at both budgets. No model was promoted.

Context availability differs by class. For example, 86.8% of benign Python dev reports have captured context, compared with 41.4% of malware. Validate context on a cohort with comparable capture coverage before promoting. The diagnostic audit decoded 3,659,060 windows across 575,766 selected train/dev reports without errors, including 950 legacy plain-text windows.

The exact selected vocabulary sizes are:

| File type | Full ID | Pooled full ID + description | Context |
|---|---:|---:|---:|
| java_class | 932 | 1196 | 10000 |
| go | 2881 | 3196 | 10000 |
| c | 9169 | 9641 | 10000 |
| python | 10000 | 10000 | 10000 |
| javascript | 7655 | 8843 | 10000 |

Raising the cap alone cannot add full-ID or pooled words for Java, Go, C or JavaScript at the current frequency floor. Python reaches 10k for those sources. Every context source reaches 10k; this first screen does not establish its optimal cap.

All 35 configurations (70 seed fits) passed matched-input and saved-prediction verification. The full per-seed, ensemble, vocabulary-use and cost data are in `out/experiments/keyword-hierarchy-context-10pct-v2/verified_summary.json` and `comparison.csv`; `RESULTS.md` shows individual-seed means and ensembles separately. Python/Scan vector fixtures and 27 actual ONNX bundle predictions passed parity checks.

## Feature contract and reproduction

These are independent, optional additions to the existing feature vector:

| Feature setting | Make setting | Feature columns | Input |
|---|---|---|---|
| `full_rule_keywords` | `EXP_FULL_RULE_KEYWORDS=1` | `fullword:*` | Entire finding ID, including every hierarchy component and its relative ID |
| `rule_description_keywords` | `EXP_RULE_DESCRIPTION_KEYWORDS=1` | `ruletextword:*` | One pooled vocabulary: full finding ID **plus description** |
| `context_keywords` | `EXP_CONTEXT_KEYWORDS=1` | `contextword:*` | Separate vocabulary from decoded file context windows |

Pooling combines only description and full rule ID. Context stays separate.
Autocollie can select any setting per model; all three default off. Existing
`rule_keywords` (relative ID only) and `description_keywords` remain available.
A separate `full_rule_keywords` + `description_keywords` arm distinguishes
pooling from keeping the same two sources in separate columns.
The cap applies per vocabulary: separate sources can add up to 20,000
columns, while the pooled source adds at most 10,000. Inspect actual widths
and costs; this first screen does not hold the total keyword budget equal.

Each vocabulary is learned from both classes in the selected **training**
cohort. Words rank by document frequency, with lexical tie breaking, a 10,000
word cap per source, and minimum frequency five. The tokenizer lowercases,
splits on non-ASCII-alphanumeric characters, and drops single characters and
pure numbers. Features are binary and deduplicate across all findings and
archive members in a report. Trees can learn from presence and absence.

Rule and description sources require eligible, confident findings (at least
0.65 confidence). Missing descriptions add no words while retaining the full
ID and other features. Context reads all captured windows independently of
finding confidence. It excludes locations, notes, and other annotations;
window boundaries cannot join two fragments into a new word. Missing context
contributes zero words. Malformed windows fail explicitly.

The trainer imports all three historical context representations:

- schema 7 `t`: plain text, interpreted as UTF-8;
- legacy `b`: Cleave's Z85 alphabet, including partial trailing groups;
- current `s`: byte text, recovering the original bytes before UTF-8 decoding.

Invalid UTF-8 bytes use replacement characters before tokenization. This
matches Scan's `String::from_utf8_lossy` behavior on decoded context bytes.
Legacy plain-text imports have a parity fixture against equivalent current
windows; Scan's typed report reader itself still expects `s` or `b` windows.

New source specifications use ABI 23 and save the route's exact vocabularies
alongside `base_feature_abi=20`. Scan preserves base feature behavior and
extracts only sources active in that model's surviving columns. Its shared
report parser gathers the union of sources required by the general model and
applicable specialist models. ABI 22 models retain their original description
validation behavior. ABI 23 models treat missing description text as empty.
Azoth stores the ordinary model/spec bundle; no separate vocabulary sidecar or
Azoth code change is needed.

Run the controlled screen:

```sh
.venv/bin/python scripts/keyword_route_controls.py \
  --output out/experiments/keyword-hierarchy-context-10pct-v2 \
  --route-jobs 2 \
  --variants baseline ids descriptions hierarchy hierarchy_descriptions pooled context

.venv/bin/python scripts/summarize_extended_keywords.py \
  out/experiments/keyword-hierarchy-context-10pct-v2
```

The screen uses a natural 10% canonical-group sample for `java_class`, `go`,
`c`, `python`, and `javascript`, seeds 43 and 44, full column sampling, and a
shared read-only PostgreSQL snapshot. Every arm retains all sampled train/dev
rows without score floors or row caps. The existing feature allowlist is
cleared so experimental columns can participate. Locked test data is unused.
The runner verifies identical base features, selected rows, labels and report
revision before comparing each arm. The summarizer rechecks saved predictions,
training settings, and recorded metrics. Individual-seed means and averaged
ensembles are reported separately.

`audit_keyword_context.py` inspects only the saved train/dev IDs in a separate
read-only diagnostic snapshot. Its `context_coverage.json` records availability
by class and partition, encoding counts, decoded size and invalid windows.
Coverage differences can confound context results, so inspect them before
promoting a model. `comparison.csv`, `verified_summary.json`, and `RESULTS.md`
are generated under the experiment output directory. Matrix scoring timings
exclude decoding and feature extraction; they are not end-to-end Scan latency.

The first partial screen under `keyword-hierarchy-context-10pct` was stopped
when the coverage audit discovered schema 7 plain-text windows in Go. Use the
complete `-v2` comparison for conclusions.

To check actual ONNX bundle probabilities against Python after training:

```sh
.venv/bin/python scripts/keyword_bundle_parity_fixture.py \
  out/experiments/keyword-hierarchy-context-10pct-v2 \
  /tmp/keyword-bundle-cases.json

(cd ../scan && KEYWORD_BUNDLE_CASES=/tmp/keyword-bundle-cases.json \
  cargo test --test keyword_bundle_parity -- --ignored)
```

This checks hierarchy, pooled and context bundles against Python on old/new
context encodings, normalized schema 7 imports, missing descriptions, missing
context and pruned source fixtures. The independent small-vector fixtures can
be regenerated with `scripts/extended_keyword_parity_fixture.py`.
Larger source-cap probes can use `--keyword-vocab-max 25000` with a fresh
output directory; a 10,000-word first screen does not establish the best cap
for a new source that reaches it.

The completed screen spans two training code revisions because separate
compatibility edits landed in the shared workspace while it ran. They reorder
a GPU probe for CPU workloads and replace deprecated LightGBM validation
arguments with their current names. The original revision was reconstructed
exactly; both fit implementations produced bit-identical 180-tree models and
dev predictions for each of seeds 43 and 44 on the full cached JavaScript
matrices (147,586 train rows and 24,580 dev rows). The verifier requires the
recorded numerical audit when revisions differ and checks every saved model
uses the audited CPU device. See `training_revision_audit.json` and the saved
before/after source files in `training_revision_sources/`. The feature
extractor revision, input matrices, and training settings stayed consistent.
