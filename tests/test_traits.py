"""Tests for trait-level diagnostics."""

from collimator.data import Sample
from collimator.traits import compute_trait_stats, sort_trait_stats


def _sample(sha: str, label: int, findings: list[dict]) -> Sample:
    return Sample(
        row_id=0,
        sha256=sha,
        path=f"/tmp/{sha}",
        label=label,
        report={
            "version": "3",
            "files": [{
                "id": 0,
                "path": f"/tmp/{sha}",
                "depth": 0,
                "file_type": "elf",
                "sha256": sha,
                "size": 1024,
                "findings": findings,
                "structure": [],
                "strings": [],
            }],
            "summary": {"files_analyzed": 1, "duration_ms": 1, "tools": []},
        },
    )


def test_compute_trait_stats_hostile_only() -> None:
    samples = [
        _sample("m1", 1, [
            {"id": "trait/a", "crit": "hostile"},
            {"id": "trait/a", "crit": "hostile"},
            {"id": "trait/b", "crit": "suspicious"},
        ]),
        _sample("b1", 0, [
            {"id": "trait/a", "crit": "hostile"},
            {"id": "trait/c", "crit": "hostile"},
        ]),
    ]

    stats = compute_trait_stats(samples, crit="hostile")
    by_id = {stat.trait_id: stat for stat in stats}

    assert set(by_id) == {"trait/a", "trait/c"}
    assert by_id["trait/a"].malware_samples == 1
    assert by_id["trait/a"].benign_samples == 1
    assert by_id["trait/a"].malware_occurrences == 2
    assert by_id["trait/a"].benign_occurrences == 1
    assert by_id["trait/a"].precision == 0.5
    assert by_id["trait/c"].malware_samples == 0
    assert by_id["trait/c"].benign_samples == 1


def test_compute_trait_stats_any_crit() -> None:
    samples = [
        _sample("m1", 1, [{"id": "trait/a", "crit": "suspicious"}]),
        _sample("b1", 0, [{"id": "trait/a", "crit": "suspicious"}]),
    ]

    stats = compute_trait_stats(samples, crit=None)

    assert len(stats) == 1
    assert stats[0].trait_id == "trait/a"


def test_sort_trait_stats_precision_surfaces_noisy_traits() -> None:
    samples = [
        _sample("m1", 1, [{"id": "trait/good", "crit": "hostile"}]),
        _sample("m2", 1, [{"id": "trait/good", "crit": "hostile"}]),
        _sample("b1", 0, [{"id": "trait/noisy", "crit": "hostile"}]),
        _sample("m3", 1, [{"id": "trait/noisy", "crit": "hostile"}]),
    ]

    stats = compute_trait_stats(samples, crit="hostile")
    sorted_stats = sort_trait_stats(stats, "precision")

    assert sorted_stats[0].trait_id == "trait/noisy"
    assert sorted_stats[-1].trait_id == "trait/good"
