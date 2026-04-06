"""Regression tests for DB-local feature helpers."""

from __future__ import annotations

import numpy as np

from collimator import data, features
from collimator.demo import create_demo_db


def test_build_vocab_mixed_from_db_matches_stream_vocab(tmp_path) -> None:
    db_path = tmp_path / "demo.db"
    create_demo_db(db_path, n_benign=16, n_malware=16, seed=7)

    splits = data.load_split_assignments(db_path)
    raw_train_row_ids: list[int] = []
    for row_id, _label, is_test, _group_id in data.stream_partitioned_metadata_grouped(
        db_path,
        split_assignments=splits,
    ):
        if not is_test:
            raw_train_row_ids.append(row_id)

    expected = features.build_vocab(
        (report for report, _label in data.stream_raw_reports(
            db_path,
            exclude_test=True,
            split_assignments=splits,
        )),
        n_workers=1,
    )
    actual = features.build_vocab_mixed_from_db(
        db_path,
        raw_train_row_ids,
        [],
        n_workers=1,
    )

    assert actual.presence_vocab == expected.presence_vocab
    assert actual.filetype_vocab == expected.filetype_vocab
    assert actual.feature_names == expected.feature_names


def test_extract_partitioned_from_db_matches_stream_extraction(tmp_path) -> None:
    db_path = tmp_path / "demo.db"
    create_demo_db(db_path, n_benign=16, n_malware=16, seed=7)

    splits = data.load_split_assignments(db_path)
    train_ids_labels: list[tuple[int, int]] = []
    test_ids_labels: list[tuple[int, int]] = []
    for row_id, label, is_test, _group_id in data.stream_partitioned_metadata_grouped(
        db_path,
        split_assignments=splits,
    ):
        if is_test:
            test_ids_labels.append((row_id, label))
        else:
            train_ids_labels.append((row_id, label))

    spec = features.build_vocab_from_db(
        db_path,
        [row_id for row_id, _label in train_ids_labels],
        n_workers=1,
    )
    expected_X_train, expected_y_train, expected_X_test, expected_y_test = features.extract_partitioned_stream(
        data.stream_partitioned_raw_reports(db_path, split_assignments=splits),
        spec,
        n_workers=1,
    )
    actual_X_train, actual_y_train, actual_X_test, actual_y_test = features.extract_partitioned_from_db(
        db_path,
        train_ids_labels,
        test_ids_labels,
        spec,
        n_workers=1,
    )

    np.testing.assert_array_equal(actual_y_train, expected_y_train)
    np.testing.assert_array_equal(actual_y_test, expected_y_test)
    np.testing.assert_array_equal(actual_X_train.toarray(), expected_X_train.toarray())
    np.testing.assert_array_equal(actual_X_test.toarray(), expected_X_test.toarray())
