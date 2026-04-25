import axios from 'axios'

/**
 * FedShield Node.js SDK — Bank-side client for transaction scoring and federation API.
 */
export class FedShieldClient {
  #baseUrl
  #gatewayUrl
  #apiKey
  #bankId

  /**
   * @param {Object} config
   * @param {string} config.baseUrl - Federation server URL
   * @param {string} config.gatewayUrl - API gateway URL
   * @param {string} config.apiKey - Bank API key
   * @param {string} config.bankId - Bank identifier
   */
  constructor({ baseUrl, gatewayUrl, apiKey, bankId }) {
    this.#baseUrl = baseUrl.replace(/\/$/, '')
    this.#gatewayUrl = gatewayUrl.replace(/\/$/, '')
    this.#apiKey = apiKey
    this.#bankId = bankId
  }

  #headers() {
    return {
      Authorization: `Bearer ${this.#apiKey}`,
      'Content-Type': 'application/json',
    }
  }

  /** Check API gateway health */
  async health() {
    const { data } = await axios.get(`${this.#gatewayUrl}/v1/health`)
    return data
  }

  /** Score a single transaction */
  async scoreTransaction(transaction, { explain = false } = {}) {
    const url = `${this.#gatewayUrl}/v1/score/transaction${explain ? '?explain=true' : ''}`
    const { data } = await axios.post(url, transaction, { headers: this.#headers() })
    return data
  }

  /** Score a batch of transactions (max 10,000) */
  async scoreBatch(transactions) {
    const { data } = await axios.post(
      `${this.#gatewayUrl}/v1/score/batch`,
      { transactions },
      { headers: this.#headers() }
    )
    return data
  }

  /** Get SHAP explanation for a transaction */
  async explain(txnRefHash) {
    const { data } = await axios.get(
      `${this.#gatewayUrl}/v1/score/explain/${txnRefHash}`,
      { headers: this.#headers() }
    )
    return data
  }

  /** Get current federation round status */
  async getCurrentRound() {
    const { data } = await axios.get(`${this.#baseUrl}/rounds/current`, {
      headers: this.#headers(),
    })
    return data
  }

  /** Get this bank's trust score history */
  async getTrustHistory() {
    const { data } = await axios.get(
      `${this.#baseUrl}/banks/${this.#bankId}/trust-history`,
      { headers: this.#headers() }
    )
    return data
  }
}

/** Legacy function — kept for backwards compatibility */
export async function fetchBankConfig(bankId) {
  const response = await axios.get(`/api/banks/${bankId}`)
  return response.data
}

export default FedShieldClient
