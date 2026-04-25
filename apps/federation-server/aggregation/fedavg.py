"""FedAvg — Weighted Federated Averaging.

Reference: McMahan, H. B., et al. "Communication-Efficient Learning
of Deep Networks from Decentralized Data." AISTATS 2017.
"""

import numpy as np


def compute_fedavg(
    deltas: list[np.ndarray],
    weights: list[float] | None = None,
) -> np.ndarray:
    """Weighted average of model weight deltas.

    Args:
        deltas: List of weight delta vectors from participating banks.
        weights: Trust-based weights for each delta (defaults to equal weight).

    Returns:
        Aggregated global model update vector.
    """
    if not deltas:
        return np.array([])

    if weights is None:
        weights = [1.0] * len(deltas)

    total_weight = sum(weights)
    if total_weight < 1e-9:
        return np.zeros_like(deltas[0])

    stacked = np.stack(deltas)
    w = np.array(weights) / total_weight
    return np.average(stacked, axis=0, weights=w)
