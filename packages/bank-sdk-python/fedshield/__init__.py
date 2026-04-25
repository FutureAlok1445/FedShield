"""FedShield SDK — Bank-side integration package for federated fraud intelligence."""

from .client import FedShieldClient
from .trainer import LocalTrainer
from .features import FeatureExtractor
from .privacy import apply_dp_noise, gaussian_noise_sigma

__all__ = [
    'FedShieldClient',
    'LocalTrainer',
    'FeatureExtractor',
    'apply_dp_noise',
    'gaussian_noise_sigma',
]
