"""Multi-bank federation simulator.

Simulates N banks (some adversarial) running federated learning rounds.
Validates FLTrust defense against gradient scaling, sign flip, backdoor, and sybil attacks.
"""

import hashlib
import logging

import numpy as np

from sys import path as sys_path
sys_path.insert(0, '../apps/federation-server')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')

FEATURE_DIM = 24


def generate_honest_gradient(seed: int) -> np.ndarray:
    """Generate a gradient from a hypothetical honest bank."""
    rng = np.random.RandomState(seed)
    base = rng.randn(FEATURE_DIM) * 0.1
    base += np.ones(FEATURE_DIM) * 0.05  # Slight positive bias (legitimate learning)
    return base


def generate_attack_gradient(attack_type: str, seed: int) -> np.ndarray:
    """Generate an adversarial gradient."""
    rng = np.random.RandomState(seed)
    honest = generate_honest_gradient(seed + 1000)

    if attack_type == 'gradient_scaling':
        return honest * 50.0
    elif attack_type == 'sign_flip':
        return -honest * 2.0
    elif attack_type == 'backdoor':
        backdoor = rng.randn(FEATURE_DIM) * 0.3
        backdoor[0] = 5.0  # Large perturbation on feature 0
        return honest + backdoor
    elif attack_type == 'sybil':
        # Sybil: many copies of the same biased gradient
        return honest * 0.8 + rng.randn(FEATURE_DIM) * 0.01
    else:
        return honest


def run_simulation(
    num_banks: int = 10,
    num_malicious: int = 2,
    attack_type: str = 'gradient_scaling',
    num_rounds: int = 20,
) -> dict:
    """Run a multi-bank federation simulation.

    Args:
        num_banks: Total participating banks.
        num_malicious: Number of adversarial banks.
        attack_type: One of gradient_scaling, sign_flip, backdoor, sybil.
        num_rounds: Number of federation rounds.

    Returns:
        Simulation results dict.
    """
    results = {
        'config': {
            'num_banks': num_banks,
            'num_malicious': num_malicious,
            'attack_type': attack_type,
            'num_rounds': num_rounds,
        },
        'rounds': [],
        'detections': 0,
        'false_negatives': 0,
    }

    malicious_ids = {f'bank_{i}' for i in range(num_malicious)}

    for round_num in range(1, num_rounds + 1):
        gradients = {}
        for i in range(num_banks):
            bank_id = f'bank_{i}'
            if bank_id in malicious_ids:
                gradients[bank_id] = generate_attack_gradient(attack_type, round_num * 100 + i)
            else:
                gradients[bank_id] = generate_honest_gradient(round_num * 100 + i)

        # Server gradient (from trusted dataset)
        server_gradient = np.ones(FEATURE_DIM, dtype=np.float64) / np.sqrt(FEATURE_DIM)

        # Compute trust scores (simplified inline FLTrust)
        trust_scores = {}
        server_norm = float(np.linalg.norm(server_gradient))
        for bid, grad in gradients.items():
            grad_norm = float(np.linalg.norm(grad))
            if grad_norm < 1e-9:
                trust_scores[bid] = 0.0
            else:
                cos_sim = float(np.dot(server_gradient, grad) / (server_norm * grad_norm))
                trust_scores[bid] = max(0.0, cos_sim)

        round_detections = 0
        for bid in malicious_ids:
            if trust_scores.get(bid, 1.0) < 0.3:
                round_detections += 1
                results['detections'] += 1
            else:
                results['false_negatives'] += 1

        results['rounds'].append({
            'round': round_num,
            'trust_scores': {k: round(v, 4) for k, v in trust_scores.items()},
            'detections': round_detections,
        })

    total_attacks = num_malicious * num_rounds
    results['detection_rate'] = results['detections'] / max(total_attacks, 1)
    results['summary'] = (
        f"Detected {results['detections']}/{total_attacks} attacks "
        f"({results['detection_rate']:.1%} rate) across {num_rounds} rounds."
    )

    logger.info(results['summary'])
    return results


if __name__ == '__main__':
    for attack in ['gradient_scaling', 'sign_flip', 'backdoor', 'sybil']:
        print(f'\n{"="*60}')
        print(f'Attack: {attack}')
        result = run_simulation(num_banks=10, num_malicious=3, attack_type=attack, num_rounds=20)
        print(result['summary'])
