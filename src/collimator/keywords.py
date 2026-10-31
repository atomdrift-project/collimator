"""Keyword search settings and label-safe, per-fit vocabulary selection.

Candidate discovery uses document frequency without labels. Supervised ranking
is delayed until each model fit, after holdout/CV splitting. Unselected columns
are constant zero during fitting, so tree models cannot split on them; the
shared feature layout remains usable by every seed and by existing runtimes.
"""
import os

import numpy as np
import scipy.sparse as sp

SOURCES = {
    "ruleword": "RULE",
    "descword": "DESCRIPTION",
    "fullword": "FULL_RULE",
    "ruletextword": "RULE_DESCRIPTION",
    "contextword": "CONTEXT",
}
METHODS = ("frequency", "balanced_mi")


def settings_from_env():
    """Resolve source overrides; zero/`inherit` use the shared setting."""
    method = os.getenv("COLLIMATOR_KEYWORD_SELECTION", "frequency")
    if method not in METHODS:
        raise ValueError(f"invalid keyword selection: {method}")
    cap = max(0, int(os.getenv("COLLIMATOR_KEYWORD_VOCAB_MAX", "10000")))
    floor = max(1, int(os.getenv("COLLIMATOR_KEYWORD_MIN_FREQ", "5")))
    candidate_cap = int(os.getenv("COLLIMATOR_KEYWORD_CANDIDATE_MAX", "100000"))
    if candidate_cap < 1:
        raise ValueError("keyword candidate maximum must be positive")
    settings = {}
    for source, prefix in SOURCES.items():
        source_cap = int(os.getenv(f"COLLIMATOR_{prefix}_KEYWORD_VOCAB_MAX", "0"))
        source_floor = int(os.getenv(f"COLLIMATOR_{prefix}_KEYWORD_MIN_FREQ", "0"))
        source_method = os.getenv(f"COLLIMATOR_{prefix}_KEYWORD_SELECTION", "inherit")
        if source_cap < 0 or source_floor < 0:
            raise ValueError(f"negative keyword override for {source}")
        if source_method not in (*METHODS, "inherit"):
            raise ValueError(f"invalid keyword selection for {source}: {source_method}")
        settings[source] = dict(selection=method if source_method == "inherit" else source_method,
                                vocab_max=source_cap or cap, min_freq=source_floor or floor,
                                candidate_max=max(candidate_cap, source_cap or cap))
    return settings


def balanced_information(malware, benign, n_malware, n_benign):
    """Smoothed Bernoulli mutual information with equal class priors, in nats."""
    pm = (np.asarray(malware, dtype=float) + .5) / (n_malware + 1)
    pb = (np.asarray(benign, dtype=float) + .5) / (n_benign + 1)
    mean = (pm + pb) / 2
    return .5 * (pm * np.log(pm / mean) + (1-pm) * np.log((1-pm)/(1-mean))
                 + pb * np.log(pb / mean) + (1-pb) * np.log((1-pb)/(1-mean)))


def select_for_fit(matrix, labels, feature_names, settings=None):
    """Mask supervised keyword candidates using ONLY this fit's rows/labels.

    Frequency-only vocabularies retain their historical discovery behavior.
    Zeroing (rather than deleting) keeps shared native/ONNX feature indices
    stable. Neither the input matrix nor the caller's labels are mutated.
    """
    settings = settings if settings is not None else settings_from_env()
    supervised = {source: cfg for source, cfg in settings.items() if cfg["selection"] == "balanced_mi"}
    if not supervised:
        return matrix, {}
    if feature_names is None:
        raise ValueError("class-aware keyword selection requires feature names")
    if len(feature_names) != matrix.shape[1] or len(labels) != matrix.shape[0]:
        raise ValueError("keyword selection matrix/label/layout mismatch")
    labels = np.asarray(labels)
    if not np.isin(labels, [0, 1]).all():
        raise ValueError("keyword selection requires binary labels")
    keep = np.ones(matrix.shape[1], dtype=bool)
    stats = {}
    totals = [int(np.sum(labels == label)) for label in (0, 1)]
    for source, cfg in supervised.items():
        columns = np.array([i for i, name in enumerate(feature_names) if name.startswith(source + ":")], dtype=int)
        if not len(columns):
            continue
        block = matrix[:, columns] != 0
        counts = [np.asarray(block[labels == label].sum(axis=0)).ravel() for label in (0, 1)]
        support = counts[0] + counts[1]
        fallback = min(totals) == 0
        score = support if fallback else balanced_information(counts[1], counts[0], totals[1], totals[0])
        eligible = np.flatnonzero(support >= cfg["min_freq"])
        ranked = sorted(eligible, key=lambda i: (-float(score[i]), feature_names[columns[i]]))
        selected = columns[ranked[:cfg["vocab_max"]]]
        keep[columns] = False
        keep[selected] = True
        stats[source] = dict(**cfg, candidates=len(columns), eligible=len(eligible), selected=len(selected),
                             fitting_goodware=totals[0], fitting_malware=totals[1],
                             fallback="frequency_single_class" if fallback else None)
    if keep.all():
        return matrix, stats
    if sp.issparse(matrix):
        masked = matrix.multiply(keep).tocsr()
        masked.eliminate_zeros()
    else:
        masked = np.array(matrix, copy=True)
        masked[:, ~keep] = 0
    return masked, stats
