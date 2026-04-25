"""
FedShield — Attack Simulator (PRD §11.2)

Class-based attack implementations for demo/testing:
- GradientScalingAttack: 10x gradient amplification
- SignFlipAttack: Negates gradient direction
- BackdoorAttack: Targets specific features
- SybilAttack: Coordinated multi-identity poisoning
"""
import numpy as np


class GradientScalingAttack:
    """Multiplies gradient by 10x — caught by norm outlier layer."""

    def __init__(self, scale: float = 10.0):
        self.scale = scale

    def poison(self, gradient: np.ndarray) -> np.ndarray:
        return gradient * self.scale


class SignFlipAttack:
    """Negates gradient completely — caught by cosine similarity layer."""

    def poison(self, gradient: np.ndarray) -> np.ndarray:
        return -gradient


class BackdoorAttack:
    """Adds a specific pattern to make model ignore certain features."""

    def __init__(self, target_feature_idx: int = 0, multiplier: float = 5.0):
        self.target_feature_idx = target_feature_idx
        self.multiplier = multiplier

    def poison(self, gradient: np.ndarray) -> np.ndarray:
        poisoned = gradient.copy()
        poisoned[self.target_feature_idx] = -abs(gradient[self.target_feature_idx]) * self.multiplier
        return poisoned


class SybilAttack:
    """Multiple fake bank identities submitting coordinated poisoned updates."""

    def __init__(self, n_sybils: int = 3):
        self.n_sybils = n_sybils
        self.sign_flip = SignFlipAttack()

    def generate_updates(self, base_gradient: np.ndarray) -> list[np.ndarray]:
        return [self.sign_flip.poison(base_gradient) for _ in range(self.n_sybils)]


if __name__ == '__main__':
    # Demo: test all attack types
    np.random.seed(42)
    gradient = np.random.randn(24)
    print(f'Original gradient norm: {np.linalg.norm(gradient):.4f}')

    attacks = {
        'gradient_scaling': GradientScalingAttack(),
        'sign_flip': SignFlipAttack(),
        'backdoor': BackdoorAttack(target_feature_idx=5),
        'sybil': SybilAttack(n_sybils=3),
    }

    for name, attack in attacks.items():
        if name == 'sybil':
            updates = attack.generate_updates(gradient)
            print(f'{name}: {len(updates)} sybil updates, norms: {[f"{np.linalg.norm(u):.4f}" for u in updates]}')
        else:
            poisoned = attack.poison(gradient)
            cos_sim = np.dot(gradient, poisoned) / (np.linalg.norm(gradient) * np.linalg.norm(poisoned) + 1e-9)
            print(f'{name}: norm={np.linalg.norm(poisoned):.4f}, cos_sim={cos_sim:.4f}')
