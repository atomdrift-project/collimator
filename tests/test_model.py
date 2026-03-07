"""Tests for the MLP model architecture."""

import torch

from collimator.model import MalwareClassifier


def test_forward_shape() -> None:
    model = MalwareClassifier(n_features=100)
    x = torch.randn(8, 100)
    out = model(x)
    assert out.shape == (8, 1)


def test_output_range() -> None:
    """Sigmoid of logits should be in [0, 1]."""
    model = MalwareClassifier(n_features=50)
    x = torch.randn(32, 50)
    probs = torch.sigmoid(model(x))
    assert probs.min() >= 0.0
    assert probs.max() <= 1.0


def test_single_sample() -> None:
    """Model should handle batch size 1."""
    model = MalwareClassifier(n_features=20)
    model.eval()
    x = torch.randn(1, 20)
    out = model(x)
    assert out.shape == (1, 1)


def test_deterministic_eval() -> None:
    """Same input should produce same output in eval mode."""
    model = MalwareClassifier(n_features=30)
    model.eval()
    x = torch.randn(4, 30)
    out1 = model(x)
    out2 = model(x)
    assert torch.allclose(out1, out2)
