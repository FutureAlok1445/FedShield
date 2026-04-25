"""
FedShield SDK — Differential Privacy Module (PRD §10.3)

Implements Gaussian mechanism for (ε, δ)-differential privacy.
Applied to model weight deltas before upload.
"""
import math

import numpy as np


def gaussian_noise_sigma(epsilon: float, delta: float, sensitivity: float) -> float:
    """
    Compute noise scale for the Gaussian mechanism.

    σ = sensitivity × √(2 × ln(1.25/δ)) / ε

    Args:
        epsilon: Privacy budget (lower = more private). Bank configures between 0.1–10.
        delta: Probability bound. Standard value: 1e-5 for financial applications.
        sensitivity: Maximum gradient norm (L2 clipping threshold). Default: 1.0.

    Returns:
        Standard deviation of Gaussian noise to add.
    """
    if epsilon <= 0:
        raise ValueError('epsilon must be positive')
    if delta <= 0 or delta >= 1:
        raise ValueError('delta must be in (0, 1)')
    return sensitivity * math.sqrt(2 * math.log(1.25 / delta)) / epsilon


def clip_gradient(gradient: np.ndarray, max_norm: float = 1.0) -> np.ndarray:
    """
    Clip gradient to max L2 norm (sensitivity bound).

    Args:
        gradient: Raw gradient vector.
        max_norm: Maximum allowed L2 norm.

    Returns:
        Clipped gradient.
    """
    norm = float(np.linalg.norm(gradient))
    if norm > max_norm:
        return gradient * (max_norm / norm)
    return gradient


def apply_dp_noise(
    gradient: np.ndarray,
    epsilon: float = 1.0,
    delta: float = 1e-5,
    max_grad_norm: float = 1.0,
) -> np.ndarray:
    """
    Apply (ε, δ)-differential privacy to a gradient vector.

    Steps:
    1. Clip gradient to max_grad_norm (bounds sensitivity)
    2. Compute noise scale σ from Gaussian mechanism
    3. Add calibrated Gaussian noise

    Args:
        gradient: Raw gradient/weight delta vector.
        epsilon: Privacy budget (bank's choice).
        delta: Standard 1e-5 for financial data.
        max_grad_norm: Gradient clipping threshold.

    Returns:
        DP-protected gradient with same shape.
    """
    clipped = clip_gradient(gradient, max_grad_norm)
    sigma = gaussian_noise_sigma(epsilon, delta, max_grad_norm)
    noise = np.random.normal(0, sigma, size=clipped.shape)
    return clipped + noise
