"""FLTrust Byzantine-robust trust scoring.

Reference: Cao, X., et al. "FLTrust: Byzantine-robust Federated Learning
via Trust Bootstrapping." NDSS 2021.

Unlike mean-gradient anchoring, FLTrust uses a small trusted dataset held
by the server to generate a reference gradient.  Trust score for each bank
is ReLU(cosine_similarity(bank_gradient, server_gradient)).
"""

import numpy as np


def compute_trust_scores(
    server_gradient: np.ndarray,
    bank_gradients: dict[str, np.ndarray],
) -> dict[str, float]:
    """Compute per-bank trust scores using cosine similarity with server root gradient.

    Args:
        server_gradient: Reference gradient computed on server's trusted dataset.
        bank_gradients: Mapping of bank_id → gradient vector.

    Returns:
        Mapping of bank_id → trust score in [0.0, 1.0].
    """
    if server_gradient is None or len(bank_gradients) == 0:
        return {}

    server_norm = float(np.linalg.norm(server_gradient))
    if server_norm < 1e-9:
        return {bank_id: 0.0 for bank_id in bank_gradients}

    scores: dict[str, float] = {}
    for bank_id, grad in bank_gradients.items():
        grad_norm = float(np.linalg.norm(grad))
        if grad_norm < 1e-9:
            scores[bank_id] = 0.0
            continue

        cos_sim = float(np.dot(server_gradient, grad) / (server_norm * grad_norm))
        # ReLU: if gradient opposes server direction, trust = 0
        scores[bank_id] = max(0.0, round(cos_sim, 6))

    return scores


def fltrust_aggregate(
    server_gradient: np.ndarray,
    bank_gradients: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, float]]:
    """Run full FLTrust: compute trust scores and produce weighted aggregation.

    Returns:
        (aggregated_gradient, trust_scores)
    """
    trust_scores = compute_trust_scores(server_gradient, bank_gradients)

    total_trust = sum(trust_scores.values())
    if total_trust < 1e-9:
        return np.zeros_like(server_gradient), trust_scores

    dim = len(server_gradient)
    aggregated = np.zeros(dim)

    for bank_id, grad in bank_gradients.items():
        ts = trust_scores.get(bank_id, 0.0)
        if ts > 0:
            # Normalize bank gradient to unit length, scale by trust score
            grad_norm = float(np.linalg.norm(grad))
            if grad_norm > 1e-9:
                normalized = grad / grad_norm * float(np.linalg.norm(server_gradient))
                aggregated += ts * normalized

    aggregated /= total_trust
    return aggregated, trust_scores
