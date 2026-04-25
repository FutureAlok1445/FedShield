"""
FedShield — Synthetic Data Generator (PRD §20 Phase 4)

Generates synthetic transaction data for multi-bank simulation.
Produces realistic-looking fraud and legitimate transactions.
"""
import random
from datetime import datetime, timedelta

import numpy as np


class SyntheticDataGenerator:
    """Generate synthetic bank transaction data for federation simulation."""

    CHANNELS = ['upi', 'netbanking', 'card', 'atm']
    HIGH_RISK_MCCS = [6051, 6211, 7995, 5967, 5966]
    LOW_RISK_MCCS = [5411, 5311, 5541, 5812, 5912, 7011, 4111, 5691]

    def __init__(self, fraud_rate: float = 0.02, seed: int | None = None):
        self.fraud_rate = fraud_rate
        self.rng = np.random.default_rng(seed)

    def generate_transactions(self, n: int, bank_id: str = 'bank_001') -> list[dict]:
        """Generate n synthetic transactions with labels."""
        transactions = []
        for i in range(n):
            is_fraud = self.rng.random() < self.fraud_rate
            txn = self._generate_single(is_fraud, bank_id, i)
            transactions.append(txn)
        return transactions

    def generate_feature_matrix(self, n: int) -> tuple[np.ndarray, np.ndarray]:
        """Generate feature matrix X and label vector y for training."""
        X = np.zeros((n, 24))
        y = np.zeros(n)

        for i in range(n):
            is_fraud = self.rng.random() < self.fraud_rate
            y[i] = float(is_fraud)
            X[i] = self._generate_feature_vector(is_fraud)

        return X, y

    def _generate_single(self, is_fraud: bool, bank_id: str, idx: int) -> dict:
        now = datetime.utcnow() - timedelta(hours=self.rng.integers(0, 720))
        amount = self._fraud_amount() if is_fraud else self._legit_amount()
        channel = random.choice(self.CHANNELS)
        mcc = random.choice(self.HIGH_RISK_MCCS if is_fraud and self.rng.random() > 0.4 else self.LOW_RISK_MCCS)

        return {
            'txn_id': f'{bank_id}_txn_{idx:06d}',
            'bank_id': bank_id,
            'amount': round(amount, 2),
            'channel': channel,
            'mcc': mcc,
            'hour_of_day': now.hour,
            'day_of_week': now.weekday(),
            'is_new_device': is_fraud and self.rng.random() > 0.5,
            'is_new_merchant': is_fraud and self.rng.random() > 0.6,
            'ip_country_change': is_fraud and self.rng.random() > 0.8,
            'timestamp': now.isoformat(),
            'is_fraud': is_fraud,
        }

    def _generate_feature_vector(self, is_fraud: bool) -> np.ndarray:
        """Generate 24 feature values."""
        if is_fraud:
            return np.array([
                self.rng.uniform(6, 12),          # amount_log (high)
                self.rng.uniform(2, 6),            # amount_zscore_30d (high)
                self.rng.uniform(0.85, 1.0),       # amount_percentile_acct
                self.rng.integers(3, 15),          # txn_count_1h (suspicious burst)
                self.rng.integers(10, 40),         # txn_count_24h
                self.rng.integers(20, 80),         # txn_count_7d
                self.rng.integers(5, 15),          # unique_merchants_24h
                self.rng.integers(2, 6),           # unique_devices_7d
                self.rng.integers(0, 6),           # hour_of_day (late night)
                self.rng.integers(0, 7),           # day_of_week
                float(self.rng.random() > 0.7),    # is_weekend
                self.rng.uniform(0, 2),            # hours_since_last_txn (very recent)
                self.rng.integers(0, 4),           # channel_encoded
                float(self.rng.random() > 0.4),    # is_new_device
                float(self.rng.random() > 0.5),    # is_new_merchant
                float(self.rng.random() > 0.7),    # ip_country_change
                self.rng.uniform(0.5, 1.0),        # mcc_risk_score
                float(self.rng.random() > 0.4),    # mcc_is_high_risk
                self.rng.uniform(0.001, 0.05),     # account_pagerank
                self.rng.integers(0, 5),           # shared_device_count
                self.rng.uniform(0.05, 0.3),       # merchant_fraud_rate_30d
                self.rng.uniform(0.01, 0.15),      # account_fraud_rate_90d
                float(self.rng.choice(self.HIGH_RISK_MCCS)),
                float(self.rng.random() > 0.8),    # device_country_change
            ])
        else:
            return np.array([
                self.rng.uniform(3, 8),            # amount_log (normal)
                self.rng.uniform(-1, 1),           # amount_zscore_30d (normal)
                self.rng.uniform(0.2, 0.7),        # amount_percentile_acct
                self.rng.integers(0, 3),           # txn_count_1h
                self.rng.integers(1, 8),           # txn_count_24h
                self.rng.integers(3, 20),          # txn_count_7d
                self.rng.integers(1, 5),           # unique_merchants_24h
                self.rng.integers(1, 2),           # unique_devices_7d
                self.rng.integers(8, 22),          # hour_of_day (normal hours)
                self.rng.integers(0, 7),           # day_of_week
                float(self.rng.random() > 0.7),    # is_weekend
                self.rng.uniform(2, 48),           # hours_since_last_txn
                self.rng.integers(0, 4),           # channel_encoded
                0.0,                                # is_new_device
                float(self.rng.random() > 0.85),   # is_new_merchant
                0.0,                                # ip_country_change
                self.rng.uniform(0.0, 0.3),        # mcc_risk_score
                0.0,                                # mcc_is_high_risk
                self.rng.uniform(0.0001, 0.01),    # account_pagerank
                0,                                  # shared_device_count
                self.rng.uniform(0.0, 0.02),       # merchant_fraud_rate_30d
                self.rng.uniform(0.0, 0.01),       # account_fraud_rate_90d
                float(self.rng.choice(self.LOW_RISK_MCCS)),
                0.0,                                # device_country_change
            ])

    def _fraud_amount(self) -> float:
        return float(self.rng.lognormal(mean=9, sigma=1.5))

    def _legit_amount(self) -> float:
        return float(self.rng.lognormal(mean=6, sigma=1.2))


if __name__ == '__main__':
    gen = SyntheticDataGenerator(fraud_rate=0.05, seed=42)
    X, y = gen.generate_feature_matrix(1000)
    print(f'Generated: {len(y)} transactions, {int(y.sum())} fraud ({y.mean()*100:.1f}%)')
    print(f'Feature matrix shape: {X.shape}')
    txns = gen.generate_transactions(5)
    for t in txns:
        print(f'  {t["txn_id"]}: ${t["amount"]:.2f} fraud={t["is_fraud"]}')
