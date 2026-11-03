"""Controlled group-disjoint holdout intervention for recovery research.

Ordinary TrainConfig does not encode this split protocol. Artifacts produced
with this helper must record training_protocol and must not be promoted as
ordinary recipes. Use one training invocation per process, never threads.
"""
from dataclasses import asdict
from unittest.mock import patch

import numpy as np

from collimator import train as training


def group_holdout_indices(labels, groups, *, fraction, seed):
    """Choose among 32 seeded group splits by class-count balance alone.

    This uses no model scores. Entire canonical groups stay together, even
    when a group contains conflicting labels. The requested fraction applies
    to group count; the fixed search minimizes deviation in each class's row
    fraction. Reject impossible class coverage instead of splitting a group.
    """
    labels, groups = np.asarray(labels), np.asarray(groups)
    if labels.ndim != 1 or groups.ndim != 1 or len(labels) != len(groups):
        raise ValueError('labels and groups must be aligned one-dimensional arrays')
    if not 0 < fraction < 1 or not np.all(np.isin(labels, [0, 1])):
        raise ValueError('binary labels and a fraction strictly between zero and one are required')
    if groups.dtype.kind not in 'US' or np.any(groups == ''):
        raise ValueError('nonempty string group identities are required')
    identities, inverse = np.unique(groups, return_inverse=True)
    count = len(identities)
    holdout_count = int(np.ceil(count * fraction))
    if not 0 < holdout_count < count:
        raise ValueError('not enough distinct groups for a holdout')
    totals = np.bincount(labels.astype(int), minlength=2)
    if np.any(totals < 2):
        raise ValueError('both classes need support on both sides of the holdout')
    by_group = np.stack([np.bincount(inverse, weights=labels == c, minlength=count)
                         for c in (0, 1)], axis=1)
    rng, best = np.random.default_rng(seed), None
    for _ in range(32):
        held_groups = rng.permutation(count)[:holdout_count]
        held_counts = by_group[held_groups].sum(axis=0)
        if np.any(held_counts == 0) or np.any(held_counts == totals):
            continue
        error = float(np.square(held_counts / totals - fraction).sum())
        if best is None or error < best[0]:
            best = error, held_groups
    if best is None:
        raise ValueError('no group-disjoint split with both classes in the fixed 32-draw search')
    held = np.zeros(count, dtype=bool)
    held[best[1]] = True
    mask = held[inverse]
    return np.flatnonzero(~mask), np.flatnonzero(mask)


def train_grouped(X, y, config, groups, *, feature_names=None, sample_file_types=None):
    """Run the ordinary fitting procedure with two explicit grouped splits.

    The scoped patch is restricted to the two known train_test_split calls,
    with exact input checks. CV and no-holdout configurations are rejected.
    This keeps all other model fitting behavior identical in this ablation.
    """
    y, groups = np.asarray(y), np.asarray(groups)
    if config.n_folds >= 2 or config.holdout_fraction <= 0:
        raise ValueError('grouped recovery requires holdout training with CV disabled')
    if min(np.bincount(y.astype(int), minlength=2)) < training.MIN_HOLDOUT_CLASS_SIZE:
        raise ValueError('insufficient class support for the ordinary holdout path')
    fit, holdout = group_holdout_indices(y, groups, fraction=config.holdout_fraction, seed=config.seed)
    calls = [(len(y), y, config.holdout_fraction, (fit, holdout))]
    if min(np.bincount(y[holdout].astype(int), minlength=2)) >= training.MIN_CALIBRATION_CLASS_SIZE:
        calibration_positions, evaluation_positions = group_holdout_indices(
            y[holdout], groups[holdout], fraction=.5, seed=config.seed)
        calls.append((len(holdout), y[holdout], .5, (calibration_positions, evaluation_positions)))
        calibration, evaluation = holdout[calibration_positions], holdout[evaluation_positions]
    else:
        calibration = evaluation = holdout
    observed_calls = []

    def split(indices, *, test_size, stratify, random_state):
        index = len(observed_calls)
        if index >= len(calls):
            raise ValueError('ordinary trainer made an unexpected additional split')
        size, expected_labels, fraction, result = calls[index]
        if (not np.array_equal(indices, np.arange(size))
                or not np.array_equal(stratify, expected_labels)
                or test_size != fraction or random_state != config.seed):
            raise ValueError('ordinary trainer split contract changed')
        observed_calls.append(index)
        return result

    with patch.object(training, 'train_test_split', split):
        result = training.train(X, y, config, feature_names=feature_names,
                                sample_file_types=sample_file_types)
    if len(observed_calls) != len(calls):
        raise ValueError('ordinary trainer did not consume the expected grouped splits')
    result.split_summary = {**result.split_summary, 'holdout_split': 'canonical_group_32_draws',
        'calibration_evaluation_split': 'canonical_group_32_draws' if len(calls)==2 else 'shared_small_holdout'}
    partitions = {'fit':fit, 'calibration':calibration, 'evaluation':evaluation}
    audit = {'config':asdict(config), 'partitions': {
        name:{'rows':len(idx),'malware':int(y[idx].sum()),'groups':len(np.unique(groups[idx]))}
        for name,idx in partitions.items()},
        'fit_calibration_group_overlap':len(np.intersect1d(groups[fit],groups[calibration])),
        'fit_evaluation_group_overlap':len(np.intersect1d(groups[fit],groups[evaluation])),
        'calibration_evaluation_group_overlap':len(np.intersect1d(groups[calibration],groups[evaluation])),
        'shared_small_holdout':len(calls)==1}
    assert audit['fit_calibration_group_overlap'] == audit['fit_evaluation_group_overlap'] == 0
    if len(calls)==2:
        assert audit['calibration_evaluation_group_overlap'] == 0
    return result, audit, partitions
