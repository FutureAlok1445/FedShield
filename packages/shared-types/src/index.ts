// FedShield Shared Types — TypeScript type definitions for cross-service contracts.

export type HealthStatus = {
  status: string
  model_round: number
  uptime_ms: number
  current_round?: number
  last_aggregation_at?: string
}

export type BankRecord = {
  id: string
  name: string
  country_code: string
  regulator_id: string
  tier: 'standard' | 'premium' | 'anchor'
  status: 'pending' | 'active' | 'suspended'
  privacy_epsilon: number
  joined_at: string
}

export type TransactionPayload = {
  bank_id: string
  txn_ref_hash: string
  amount: number
  currency: string
  timestamp: string
  mcc: number
  is_new_device: boolean
  is_new_payee: boolean
  txn_count_1h: number
  txn_count_24h: number
  avg_txn_amount_30d: number
  amount_zscore_30d: number
  ip_country: string
  device_fingerprint: string
  mcc_is_high_risk: boolean
  velocity_ratio_1h: number
  geo_distance_km: number
  hour_of_day: number
  weekend_flag: boolean
  cross_border: boolean
  merchant_risk_score: number
  time_since_last_txn_min: number
  failed_attempts_24h: number
  payee_age_days: number
}

export type ScoreResponse = {
  fraud_probability: number
  risk_tier: 'low' | 'medium' | 'high' | 'critical'
  decision: 'allow' | 'review' | 'block'
  model_round: number
  latency_ms: number
  shap_values?: Record<string, number>
}

export type BatchScoreResponse = {
  results: ScoreResponse[]
  total: number
  high_risk_count: number
}

export type FederationRound = {
  round_id: string
  round_number: number
  status: 'open' | 'aggregating' | 'complete' | 'failed'
  expected_participants: number
  participants_received: number
  global_model_hash: string
  global_auc: number | null
  started_at: string
  completed_at: string | null
}

export type PoisoningEvent = {
  id: string
  bank_id: string
  round_number: number
  attack_type: string
  anomaly_score: number
  detection_method: string
  resolved: boolean
  detected_at: string
}

export type FraudAlert = {
  type: 'fraud_alert'
  data: {
    txn_ref_hash: string
    fraud_probability: number
    risk_tier: string
    decision: string
    scored_at: string
  }
}
