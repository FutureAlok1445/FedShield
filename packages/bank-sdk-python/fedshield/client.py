"""FedShield API client for bank-side operations."""

import hashlib
import json
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class FedShieldClient:
    """Client for interacting with the FedShield federation server.

    Args:
        base_url: Federation server base URL (e.g. http://localhost:8000).
        api_key: Bank API key for authentication.
        bank_id: This bank's identifier.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        bank_id: str,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip('/')
        self.bank_id = bank_id
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        })

    def health(self) -> dict:
        """Check federation server health."""
        resp = self._session.get(f'{self.base_url}/health', timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_current_round(self) -> dict:
        """Get the current open federation round."""
        resp = self._session.get(f'{self.base_url}/rounds/current', timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def submit_delta(
        self,
        round_id: str,
        weight_delta: bytes,
        signature: str,
        dp_epsilon_used: float | None = None,
        local_samples_used: int | None = None,
        local_auc: float | None = None,
    ) -> dict:
        """Submit a weight delta for the current round.

        Args:
            round_id: Target round identifier.
            weight_delta: Serialized weight delta bytes.
            signature: RSA-4096 signature of the weight hash.
            dp_epsilon_used: Differential privacy epsilon applied.
            local_samples_used: Number of local training samples.
            local_auc: Local model AUC on validation set.

        Returns:
            Server response with anomaly score and trust information.
        """
        weight_hash = hashlib.sha256(weight_delta).hexdigest()
        weight_delta_cid = f'Qm{weight_hash[:44]}'  # Simulated IPFS CID

        payload = {
            'bank_id': self.bank_id,
            'weight_delta_cid': weight_delta_cid,
            'weight_hash': weight_hash,
            'signature': signature,
        }
        if dp_epsilon_used is not None:
            payload['dp_epsilon_used'] = dp_epsilon_used
        if local_samples_used is not None:
            payload['local_samples_used'] = local_samples_used
        if local_auc is not None:
            payload['local_auc'] = local_auc

        resp = self._session.post(
            f'{self.base_url}/rounds/{round_id}/submit',
            data=json.dumps(payload),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def get_trust_history(self) -> list[dict]:
        """Get this bank's trust score history across rounds."""
        resp = self._session.get(
            f'{self.base_url}/banks/{self.bank_id}/trust-history',
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def score_transaction(self, gateway_url: str, transaction: dict) -> dict:
        """Score a transaction through the API gateway.

        Args:
            gateway_url: API gateway base URL (e.g. http://localhost:3000).
            transaction: Transaction feature dictionary.

        Returns:
            Scoring response with fraud_probability, risk_tier, decision.
        """
        resp = self._session.post(
            f'{gateway_url}/v1/score/transaction',
            data=json.dumps(transaction),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()
