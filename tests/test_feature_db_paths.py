"""Regression tests for DB-local feature helpers.

The previous version of this file tested removed APIs:
  - data.load_split_assignments
  - data.stream_raw_reports
  - data.stream_partitioned_raw_reports
  - features.build_vocab_mixed_from_db
  - features.extract_partitioned_stream
  - the split_assignments= parameter of stream_partitioned_metadata_grouped

Those tests were removed during the v16 refactor. Coverage for the DB
partitioning → vocab build → extraction pipeline lives in:
  - tests/test_data_splits.py (canonical_sha256 partitioning)
  - tests/test_experiment.py  (sample_partitioned_reports determinism)
  - litmus/tests/extraction_parity.rs (byte-for-byte cross-language parity)
"""
