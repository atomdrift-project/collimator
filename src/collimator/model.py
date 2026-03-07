"""MLP model for binary malware classification."""

from __future__ import annotations

import torch
import torch.nn as nn


class MalwareClassifier(nn.Module):
    """Feed-forward network for malware detection from cleave features.

    Architecture:
        Input(N) → Linear(256) → BN → ReLU → Drop(0.3)
                 → Linear(128) → BN → ReLU → Drop(0.3)
                 → Linear(64)  → BN → ReLU → Drop(0.2)
                 → Linear(1)   → Sigmoid
    """

    def __init__(self, n_features: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Return raw logits. Apply sigmoid externally for probabilities."""
        return self.net(x)
