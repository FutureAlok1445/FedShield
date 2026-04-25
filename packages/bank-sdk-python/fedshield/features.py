"""
FedShield SDK — Feature Extractor (unified with ml/feature_pipeline/extractor.py)

This module re-exports the canonical feature extractor from the ML pipeline
to ensure training and inference use identical feature engineering.

Usage:
    from fedshield.features import FeatureExtractor

    extractor = FeatureExtractor()
    features = extractor.extract(transaction, account_history, graph_stats)
"""
import math
from typing import Any

# Canonical feature names — must match ml/feature_pipeline/extractor.py exactly
FEATURE_NAMES = [
    'amount', 'currency_risk_score', 'mcc', 'mcc_is_high_risk',
    'is_new_device', 'is_new_payee', 'device_fingerprint_hash',
    'ip_country_match', 'geo_distance_km', 'cross_border',
    'txn_count_1h', 'txn_count_24h', 'velocity_ratio_1h',
    'avg_txn_amount_30d', 'amount_zscore_30d',
    'hour_of_day', 'weekend_flag',
    'time_since_last_txn_min', 'failed_attempts_24h',
    'payee_age_days', 'merchant_risk_score',
    'device_country_change', 'channel_risk_score', 'session_duration_sec',
]

HIGH_RISK_MCCS = {5912, 5944, 5999, 7995, 5816, 5817}

FEATURE_DIM = 24


class FeatureExtractor:
    """Extracts the 24-feature vector required by the FedShield model.

    This class mirrors ml/feature_pipeline/extractor.extract_features()
    exactly, ensuring train/inference feature parity.
    """

    def extract(self, txn: dict[str, Any], account_history: dict[str, Any] | None = None,
                graph_stats: dict[str, Any] | None = None) -> list[float]:
        """Extract 24 features matching the canonical pipeline."""
        account_history = account_history or {}
        import numpy as np

        features = np.zeros(FEATURE_DIM, dtype=np.float64)

        features[0] = float(txn.get('amount', 0))
        features[1] = float(txn.get('currency_risk_score', 0.5))
        features[2] = float(txn.get('mcc', 0))
        features[3] = 1.0 if txn.get('mcc', 0) in HIGH_RISK_MCCS else 0.0
        features[4] = 1.0 if txn.get('is_new_device', False) else 0.0
        features[5] = 1.0 if txn.get('is_new_payee', txn.get('is_new_merchant', False)) else 0.0
        features[6] = hash(txn.get('device_fingerprint', '')) % 1000000 / 1000000
        features[7] = 1.0 if txn.get('ip_country', 'IN') == txn.get('billing_country', 'IN') else 0.0
        features[8] = float(txn.get('geo_distance_km', 0))
        features[9] = 1.0 if txn.get('cross_border', False) else 0.0
        features[10] = float(txn.get('txn_count_1h', account_history.get('txn_count_1h', 0)))
        features[11] = float(txn.get('txn_count_24h', account_history.get('txn_count_24h', 0)))
        features[12] = float(txn.get('velocity_ratio_1h', 1.0))
        features[13] = float(txn.get('avg_txn_amount_30d', account_history.get('amount_mean_30d', 0)))
        features[14] = float(txn.get('amount_zscore_30d', 0))
        features[15] = float(txn.get('hour_of_day', 12))
        features[16] = 1.0 if txn.get('weekend_flag', txn.get('is_weekend', False)) else 0.0
        features[17] = float(txn.get('time_since_last_txn_min',
                                     account_history.get('hours_since_last_txn', 1) * 60))
        features[18] = float(txn.get('failed_attempts_24h', 0))
        features[19] = float(txn.get('payee_age_days', 365))
        features[20] = float(txn.get('merchant_risk_score', txn.get('mcc_risk_score', 0.3)))
        features[21] = 1.0 if txn.get('device_country_change', txn.get('ip_country_change', False)) else 0.0
        features[22] = float(txn.get('channel_risk_score', 0.3))
        features[23] = float(txn.get('session_duration_sec', 120))

        return features.tolist()
