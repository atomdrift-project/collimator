"""Trait-level diagnostics for finding false positives and strong signals."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .data import Sample, load_samples
from .features import report_files


@dataclass(frozen=True, slots=True)
class TraitStat:
    """Per-trait prevalence statistics across malware and benign samples."""

    trait_id: str
    benign_samples: int
    malware_samples: int
    benign_occurrences: int
    malware_occurrences: int
    benign_rate: float
    malware_rate: float
    precision: float
    lift: float


def compute_trait_stats(
    samples: list[Sample],
    *,
    crit: str | None = "hostile",
    min_samples: int = 1,
) -> list[TraitStat]:
    """Aggregate exact finding IDs across labeled samples."""
    benign_total = sum(1 for sample in samples if sample.label == 0)
    malware_total = len(samples) - benign_total

    benign_sample_counts: dict[str, int] = {}
    malware_sample_counts: dict[str, int] = {}
    benign_occurrence_counts: dict[str, int] = {}
    malware_occurrence_counts: dict[str, int] = {}

    for sample in samples:
        seen: set[str] = set()
        for file_entry in report_files(sample.report):
            for finding in file_entry.get("ts") or []:
                if crit is not None and finding.get("l") != crit:
                    continue
                trait_id = finding.get("i", "")
                if not trait_id:
                    continue

                if sample.label == 1:
                    malware_occurrence_counts[trait_id] = (
                        malware_occurrence_counts.get(trait_id, 0) + 1
                    )
                else:
                    benign_occurrence_counts[trait_id] = (
                        benign_occurrence_counts.get(trait_id, 0) + 1
                    )

                if trait_id in seen:
                    continue
                seen.add(trait_id)
                if sample.label == 1:
                    malware_sample_counts[trait_id] = (
                        malware_sample_counts.get(trait_id, 0) + 1
                    )
                else:
                    benign_sample_counts[trait_id] = (
                        benign_sample_counts.get(trait_id, 0) + 1
                    )

    trait_ids = set(benign_sample_counts) | set(malware_sample_counts)
    stats: list[TraitStat] = []
    for trait_id in trait_ids:
        b_samples = benign_sample_counts.get(trait_id, 0)
        m_samples = malware_sample_counts.get(trait_id, 0)
        total = b_samples + m_samples
        if total < min_samples:
            continue

        b_rate = b_samples / benign_total if benign_total else 0.0
        m_rate = m_samples / malware_total if malware_total else 0.0
        prec = m_samples / total if total else 0.0
        if b_rate > 0:
            lift = m_rate / b_rate
        elif m_rate > 0:
            lift = float("inf")
        else:
            lift = 0.0
        stats.append(TraitStat(
            trait_id=trait_id,
            benign_samples=b_samples,
            malware_samples=m_samples,
            benign_occurrences=benign_occurrence_counts.get(trait_id, 0),
            malware_occurrences=malware_occurrence_counts.get(trait_id, 0),
            benign_rate=b_rate,
            malware_rate=m_rate,
            precision=prec,
            lift=lift,
        ))

    return stats


def _sort_key_precision(s: TraitStat) -> tuple[float, ...]:
    return (s.precision, -(s.benign_samples + s.malware_samples), -s.benign_samples)


def _sort_key_benign(s: TraitStat) -> tuple[float, ...]:
    total_occ = s.benign_occurrences + s.malware_occurrences
    return (-s.benign_samples, s.precision, -total_occ)


def _sort_key_malware(s: TraitStat) -> tuple[float, ...]:
    total = s.benign_samples + s.malware_samples
    return (-s.malware_samples, -s.precision, -total)


def _sort_key_support(s: TraitStat) -> tuple[float, ...]:
    total = s.benign_samples + s.malware_samples
    return (-total, s.precision, -s.malware_samples)


def _sort_key_lift(s: TraitStat) -> tuple[float, ...]:
    total = s.benign_samples + s.malware_samples
    return (-s.lift, -s.precision, -total)


_SORT_KEYS = {
    "precision": _sort_key_precision,
    "benign": _sort_key_benign,
    "malware": _sort_key_malware,
    "support": _sort_key_support,
    "lift": _sort_key_lift,
}


def sort_trait_stats(stats: list[TraitStat], sort_by: str) -> list[TraitStat]:
    """Sort trait statistics for either noisy or strong signals."""
    key_fn = _SORT_KEYS.get(sort_by)
    if key_fn is None:
        raise ValueError(f"unsupported sort: {sort_by}")
    return sorted(stats, key=key_fn)


def save_trait_stats(stats: list[TraitStat], output_path: Path) -> None:
    """Write trait statistics as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump([asdict(stat) for stat in stats], f, indent=2)


def print_trait_stats(stats: list[TraitStat], *, top_n: int) -> None:
    """Print a compact table of trait-level statistics."""
    print("\nTrait statistics:")
    print(
        f"{'Trait ID':<70} {'Benign':>6} {'Mal':>6} {'Prec':>7} "
        f"{'BRate':>7} {'MRate':>7} {'Lift':>8}"
    )
    for stat in stats[:top_n]:
        lift = "inf" if stat.lift == float("inf") else f"{stat.lift:.2f}"
        print(
            f"{stat.trait_id[:70]:<70} "
            f"{stat.benign_samples:>6d} {stat.malware_samples:>6d} "
            f"{stat.precision:>7.3f} {stat.benign_rate:>7.3f} "
            f"{stat.malware_rate:>7.3f} {lift:>8}"
        )


def analyze_traits(
    db_path: Path,
    *,
    crit: str | None = "hostile",
    min_samples: int = 1,
    sort_by: str = "precision",
    top_n: int = 50,
    output_path: Path | None = None,
    limit: int = 50_000,
) -> list[TraitStat]:
    """Load a DB, compute trait statistics, print a report, optionally save."""
    samples = load_samples(db_path, limit=limit)
    stats = compute_trait_stats(samples, crit=crit, min_samples=min_samples)
    stats = sort_trait_stats(stats, sort_by)
    print_trait_stats(stats, top_n=top_n)
    if output_path is not None:
        save_trait_stats(stats, output_path)
        print(f"\nSaved trait statistics to {output_path}")
    return stats
