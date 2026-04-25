"""Three-layer gradient anomaly detection per PRD §11.1.

Layer 1 — Statistical Norm Check (z-score > 3.5 → flag)
Layer 2 — Cosine Similarity vs Round Mean (cos_sim < -0.3 → sign_flip, < 0.1 → low_cosine)
Layer 3 — Historical Deviation per Bank (deviation > 4σ → flag)

Final anomaly score = max(all layer scores)
Decision:
    > 0.8 → REJECT, log poisoning event, write to chain
    > 0.4 → FLAG for manual review, reduce trust
    ≤ 0.4 → ACCEPT
"""

import numpy as np

from poisoning.history_tracker import HistoryTracker

_tracker = HistoryTracker(max_rounds=10)


def _layer1_norm_check(gradient: np.ndarray, all_norms: list[float]) -> tuple[float, str]:
    """Layer 1: Statistical norm outlier detection."""
    norm = float(np.linalg.norm(gradient))

    if len(all_norms) < 2:
        return 0.0, ''

    mean_norm = np.mean(all_norms)
    std_norm = np.std(all_norms) + 1e-9
    z_score = abs(norm - mean_norm) / std_norm

    if z_score > 3.5:
        return min(1.0, z_score / 5.0), 'gradient_norm_outlier'
    return z_score / 7.0, ''


def _layer2_cosine_similarity(gradient: np.ndarray, mean_gradient: np.ndarray) -> tuple[float, str]:
    """Layer 2: Cosine similarity vs round mean gradient."""
    grad_norm = float(np.linalg.norm(gradient))
    mean_norm = float(np.linalg.norm(mean_gradient))

    if grad_norm < 1e-9 or mean_norm < 1e-9:
        return 0.0, ''

    cos_sim = float(np.dot(gradient, mean_gradient) / (grad_norm * mean_norm))

    if cos_sim < -0.3:
        return 0.95, 'sign_flip_suspected'
    if cos_sim < 0.1:
        return 0.5, 'low_cosine_similarity'
    return max(0.0, (1.0 - cos_sim) * 0.3), ''


def _layer3_historical_deviation(gradient: np.ndarray, bank_id: str) -> tuple[float, str]:
    """Layer 3: Historical deviation from per-bank gradient norm history."""
    current_norm = float(np.linalg.norm(gradient))
    history = _tracker.values(bank_id)

    if len(history) < 3:
        return 0.0, ''

    hist_mean = np.mean(history)
    hist_std = np.std(history) + 1e-9
    deviation = abs(current_norm - hist_mean) / hist_std

    if deviation > 4.0:
        return min(1.0, deviation / 5.0), 'historical_deviation'
    return deviation / 8.0, ''


def detect_gradient_anomaly(
    gradient: np.ndarray | list,
    bank_id: str = 'unknown',
    all_gradients: list[np.ndarray] | None = None,
) -> dict:
    """Run 3-layer anomaly detection on a gradient.

    Args:
        gradient: The gradient vector to check.
        bank_id: ID of the submitting bank.
        all_gradients: All gradients submitted in this round (for round-level stats).

    Returns:
        Dict with anomaly_score, decision, flags, and per-layer scores.
    """
    if isinstance(gradient, list):
        gradient = np.array(gradient, dtype=np.float64)

    # NaN/Inf guard — reject immediately if gradient contains non-finite values
    if not np.all(np.isfinite(gradient)):
        return {
            'anomaly_score': 1.0,
            'decision': 'reject',
            'flags': ['non_finite_gradient'],
            'layer_scores': {'norm_check': 1.0, 'cosine_similarity': 1.0, 'historical_deviation': 1.0},
        }

    # Gather layer inputs
    if all_gradients:
        all_norms = [float(np.linalg.norm(g)) for g in all_gradients]
        mean_gradient = np.mean(np.stack(all_gradients), axis=0)
    else:
        all_norms = []
        mean_gradient = gradient

    # Run all three layers
    score_l1, flag_l1 = _layer1_norm_check(gradient, all_norms)
    score_l2, flag_l2 = _layer2_cosine_similarity(gradient, mean_gradient)
    score_l3, flag_l3 = _layer3_historical_deviation(gradient, bank_id)

    # Record norm for history
    _tracker.record(bank_id, float(np.linalg.norm(gradient)))

    # Final score = max of all layers
    anomaly_score = max(score_l1, score_l2, score_l3)

    flags = [f for f in [flag_l1, flag_l2, flag_l3] if f]

    if anomaly_score > 0.8:
        decision = 'reject'
    elif anomaly_score > 0.4:
        decision = 'flag'
    else:
        decision = 'accept'

    return {
        'anomaly_score': round(anomaly_score, 6),
        'decision': decision,
        'flags': flags,
        'layer_scores': {
            'norm_check': round(score_l1, 6),
            'cosine_similarity': round(score_l2, 6),
            'historical_deviation': round(score_l3, 6),
        },
    }
