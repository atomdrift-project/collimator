"""Generate an extraction parity fixture for one azoth route.

Used by litmus's `tests/extraction_parity.rs` to verify bit-identical
feature extraction across the new feature families (kv:, symbol:, textenc:,
…) that the v17 specs introduced.

Pulls diverse reports from the hopper DB, extracts features with the route's
spec via the same code path collimator uses at training time, and writes
`extraction_fixture.json` next to the route's `feature_spec.json`.
"""
import argparse
import os
import sys
from pathlib import Path

# Re-use the collimator helpers; this file lives alongside scripts/ in the
# collimator repo, so the package import resolves once we add src/ to path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Enable every feature group that *could* land in a spec. `_assign` no-ops on
# missing-from-spec features, so over-enabling at fixture-gen time only
# matters for code-path coverage — the spec itself decides what survives.
# Without this, runtime env defaults (BLINDFOLD=1, ATTACK_FEATURES off, …)
# silently skip the gated agg/crit/symbol/textenc/kv branches and produce
# zeros that diverge from the trained spec's expectations.
for var in [
    "COLLIMATOR_ATTACK_FEATURES",
    "COLLIMATOR_ATTACK_CODE_NGRAMS",
    "COLLIMATOR_ATTACK_NGRAMS",
    "COLLIMATOR_CRIT_CATEGORY_NGRAMS",
    "COLLIMATOR_TAXONOMY_FEATURES",
    "COLLIMATOR_OBJECTIVE_TRIGRAMS",
    "COLLIMATOR_SUSPICIOUS_TRIGRAMS",
    "COLLIMATOR_EMBER_LITE_FEATURES",
    "COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES",
    "COLLIMATOR_FORMAT_HINTS",
    "COLLIMATOR_FILETYPE_INTERACTIONS",
    "COLLIMATOR_FILE_SEVERITY_DISTRIBUTION",
    "COLLIMATOR_HOSTILE_DEPTH_WEIGHT",
    "COLLIMATOR_HOSTILE_ESCALATION_FEATURES",
    "COLLIMATOR_HOSTILE_FINDING_DENSITY",
    "COLLIMATOR_HOSTILE_WEIGHTED_DENSITY",
    "COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY",
    "COLLIMATOR_SCORE_WEIGHTED_TRAITS",
    "COLLIMATOR_SOFT_PRESENCE",
    "COLLIMATOR_REPETITION_PENALTY_FEATURES",
    "COLLIMATOR_SILENT_PACKER_SIGNAL",
    "COLLIMATOR_OVERLAY_SIGNAL",
    "COLLIMATOR_TEXT_METRICS_FULL",
    "COLLIMATOR_TEXT_ENCODING_FEATURES",
    "COLLIMATOR_EXTENDED_METRICS",
    "COLLIMATOR_METRIC_RATIO_FEATURES",
    "COLLIMATOR_SIZE_NORMALIZED_METRICS",
    "COLLIMATOR_NONSTANDARD_SECTION_SIGNAL",
    "COLLIMATOR_PE_FORMAT_FLAGS",
    "COLLIMATOR_PE_TEMPORAL_ANOMALY",
    "COLLIMATOR_AIR_GAP_SIGNAL",
    "COLLIMATOR_ANACHRONISTIC_INJECTION",
    "COLLIMATOR_CODE_ENTROPY_SPIKE",
    "COLLIMATOR_FOREIGN_BINARY_SIGNAL",
    "COLLIMATOR_EXTENSION_MISMATCH_SIGNAL",
    "COLLIMATOR_EXTREME_FEATURES",
    "COLLIMATOR_MTIME_KURTOSIS",
    "COLLIMATOR_STRUCT_FILE_RISK_COVERAGE",
    "COLLIMATOR_CONFIDENCE_WEIGHTED_NGRAMS",
    "COLLIMATOR_TIERED_CRIT_BIGRAMS",
    "COLLIMATOR_TIERED_CRIT_TRIGRAMS",
    "COLLIMATOR_TIERED_CRIT_QUADGRAMS",
    "COLLIMATOR_SYMBOL_VOCAB",
    "COLLIMATOR_SYMBOL_BIGRAMS",
    "COLLIMATOR_SYMBOL_TRIGRAMS",
    "COLLIMATOR_KV_VOCAB",
    "COLLIMATOR_MBC_ID_VOCAB",
    "COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS",
    "COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE",
]:
    os.environ.setdefault(var, "1")
# Blindfold is on by default at training; the runtime default also leaves it
# on, so keep filetype:* features suppressed for parity with the trained
# extractor.
os.environ.setdefault("COLLIMATOR_BLINDFOLD", "1")

from collimator import features  # noqa: E402
from collimator.__main__ import (  # noqa: E402
    _gather_diverse_fixture_reports,
    generate_extraction_fixture,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--route",
        required=True,
        help="Route relative to model root, e.g. 'filetypes/go' or 'filetypes/csharp'.",
    )
    parser.add_argument(
        "--model-root",
        default="out/models/azoth",
        help="Path to the azoth model root (default: out/models/azoth).",
    )
    parser.add_argument(
        "--db",
        default="postgres://hopper@localhost:5432/hopper",
        help="Hopper DB DSN.",
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=20,
        help="Sample count target (post-diversity gathering may exceed this).",
    )
    args = parser.parse_args()

    spec_path = Path(args.model_root) / args.route / "feature_spec.json"
    if not spec_path.is_file():
        sys.exit(f"error: spec not found: {spec_path}")

    spec = features.FeatureSpec.load(spec_path)
    reports = _gather_diverse_fixture_reports(args.db)
    if not reports:
        sys.exit("error: no reports gathered from DB")
    reports = reports[: args.n_samples]

    # `model=None` skips the e2e prediction/standardization fields — fine for
    # extraction-only parity. The route's per-route LightGBM .txt models live
    # in `models/seed_*.txt`, which the XGBoost-oriented loader can't read.
    generate_extraction_fixture(
        reports,
        spec,
        out_dir=spec_path.parent,
        n_samples=len(reports),
        model=None,
    )


if __name__ == "__main__":
    main()
