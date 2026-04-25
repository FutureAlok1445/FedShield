"""Feature extraction pipeline per PRD §10.1 — 24 engineered features."""

import numpy as np


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


def extract_features(transaction: dict) -> np.ndarray:
    """Extract 24 features from a raw transaction dict.

    Args:
        transaction: Raw transaction payload from bank.

    Returns:
        numpy array of shape (24,) with engineered features.
    """
    features = np.zeros(len(FEATURE_NAMES), dtype=np.float64)

    features[0] = float(transaction.get('amount', 0))
    features[1] = 0.5  # Default currency risk
    features[2] = float(transaction.get('mcc', 0))
    features[3] = 1.0 if transaction.get('mcc', 0) in HIGH_RISK_MCCS else 0.0
    features[4] = 1.0 if transaction.get('is_new_device', False) else 0.0
    features[5] = 1.0 if transaction.get('is_new_payee', False) else 0.0
    features[6] = hash(transaction.get('device_fingerprint', '')) % 1000000 / 1000000
    features[7] = 1.0 if transaction.get('ip_country', 'IN') == transaction.get('billing_country', 'IN') else 0.0
    features[8] = float(transaction.get('geo_distance_km', 0))
    features[9] = 1.0 if transaction.get('cross_border', False) else 0.0
    features[10] = float(transaction.get('txn_count_1h', 0))
    features[11] = float(transaction.get('txn_count_24h', 0))
    features[12] = float(transaction.get('velocity_ratio_1h', 1.0))
    features[13] = float(transaction.get('avg_txn_amount_30d', 0))
    features[14] = float(transaction.get('amount_zscore_30d', 0))
    features[15] = float(transaction.get('hour_of_day', 12))
    features[16] = 1.0 if transaction.get('weekend_flag', False) else 0.0
    features[17] = float(transaction.get('time_since_last_txn_min', 60))
    features[18] = float(transaction.get('failed_attempts_24h', 0))
    features[19] = float(transaction.get('payee_age_days', 365))
    features[20] = float(transaction.get('merchant_risk_score', 0.3))
    features[21] = 1.0 if transaction.get('device_country_change', False) else 0.0
    features[22] = float(transaction.get('channel_risk_score', 0.3))
    features[23] = float(transaction.get('session_duration_sec', 120))

    return features
