/**
 * FedShield — ML Inference Runner
 *
 * Computes fraud probability from transaction features.
 * In production, this would load a LightGBM ONNX model.
 * Currently uses a feature-weighted heuristic that produces
 * realistic scores for demo purposes.
 */

// Feature weights matching the 24 canonical features from fedshield/features.py
const FEATURE_WEIGHTS = {
  amount: 0.05,
  currency_risk_score: 0.08,
  mcc: 0.0, // Categorical
  mcc_is_high_risk: 0.12,
  is_new_device: 0.18,
  is_new_payee: 0.15,
  device_fingerprint_hash: 0.0,
  ip_country_match: -0.10, // Negative weight (lower risk if match)
  geo_distance_km: 0.005,
  cross_border: 0.14,
  txn_count_1h: 0.12,
  txn_count_24h: 0.08,
  velocity_ratio_1h: 0.15,
  avg_txn_amount_30d: 0.02,
  amount_zscore_30d: 0.20,
  hour_of_day: 0.01,
  weekend_flag: 0.05,
  time_since_last_txn_min: -0.001,
  failed_attempts_24h: 0.25,
  payee_age_days: -0.002,
  merchant_risk_score: 0.15,
  device_country_change: 0.22,
  graph_centrality_score: 0.15, // Evaluates network topology via Graph Neural Network
  session_duration_sec: -0.001,
}

const BASE_SCORE = 0.08

function sigmoid(x) {
  return 1 / (1 + Math.exp(-x))
}

/**
 * Run inference on a transaction feature vector.
 * @param {object|null} modelData - Reserved for ONNX model (not yet loaded).
 * @param {object} features - Transaction features matching PRD §10.1 spec.
 * @returns {{ score: number, confidence: number, latency_ms: number, shap_values: object }}
 */
export async function runInference(modelData, features) {
  const startTime = performance.now()

  // Compute weighted score from available features
  let logit = 0
  const shapValues = {}

  for (const [feature, weight] of Object.entries(FEATURE_WEIGHTS)) {
    let value = features[feature]
    if (value === undefined || value === null) continue

    // Normalize booleans
    if (typeof value === 'boolean') value = value ? 1 : 0

    const contribution = Number(value) * weight
    logit += contribution
    shapValues[feature] = Math.round(contribution * 1000) / 1000
  }

  const score = sigmoid(logit - 1.5 + BASE_SCORE)
  const latencyMs = Math.round((performance.now() - startTime) * 100) / 100

  return {
    score: Math.round(score * 100000) / 100000,
    confidence: Math.min(0.99, 0.7 + Math.abs(score - 0.5) * 0.4),
    latency_ms: Math.max(1, latencyMs),
    shap_values: shapValues,
  }
}
