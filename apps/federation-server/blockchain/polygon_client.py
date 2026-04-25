"""Polygon blockchain client for on-chain model audit anchoring."""

import json
import logging
import os

logger = logging.getLogger(__name__)

POLYGON_RPC_URL = os.environ.get('POLYGON_RPC_URL', 'https://rpc-mumbai.maticvigil.com')
CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS', '')
AGGREGATOR_PRIVATE_KEY = os.environ.get('AGGREGATOR_PRIVATE_KEY', '')


def _get_web3():
    """Lazy-load web3 connection."""
    try:
        from web3 import Web3

        return Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
    except ImportError:
        logger.warning('web3 not installed — blockchain features disabled')
        return None


def publish_model_hash(hash_value: str, round_number: int = 0, participant_count: int = 0) -> dict:
    """Publish global model hash to Polygon for immutable audit.

    Args:
        hash_value: SHA-256 hash of the global model.
        round_number: Federation round number.
        participant_count: Number of banks that participated.

    Returns:
        Dict with tx_hash and status.
    """
    w3 = _get_web3()
    if not w3 or not CONTRACT_ADDRESS or not AGGREGATOR_PRIVATE_KEY:
        logger.warning('Blockchain not configured — skipping on-chain publish for hash %s', hash_value)
        return {
            'status': 'skipped',
            'reason': 'blockchain not configured',
            'hash': hash_value,
        }

    try:
        from web3 import Web3

        from blockchain.contracts import get_registry_contract

        contract = get_registry_contract(w3, Web3.to_checksum_address(CONTRACT_ADDRESS))
        account = w3.eth.account.from_key(AGGREGATOR_PRIVATE_KEY)
        nonce = w3.eth.get_transaction_count(account.address)

        tx = contract.functions.finalizeRound(
            round_number,
            bytes.fromhex(hash_value[:64]) if len(hash_value) >= 64 else hash_value.encode(),
            '',  # CID
            participant_count,
            0,  # poisoning event count
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, AGGREGATOR_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        logger.info('Published round %d to Polygon: %s', round_number, tx_hash.hex())
        return {
            'status': 'submitted',
            'tx_hash': tx_hash.hex(),
            'round_number': round_number,
        }
    except Exception as exc:
        logger.error('Failed to publish to Polygon: %s', exc)
        return {
            'status': 'failed',
            'error': str(exc),
            'hash': hash_value,
        }


def record_poisoning_event(
    bank_id: str,
    round_number: int,
    attack_type: str,
    anomaly_score: float,
) -> dict:
    """Record a poisoning event on-chain."""
    w3 = _get_web3()
    if not w3 or not CONTRACT_ADDRESS or not AGGREGATOR_PRIVATE_KEY:
        logger.warning('Blockchain not configured — skipping poisoning record')
        return {'status': 'skipped'}

    try:
        from web3 import Web3

        from blockchain.contracts import get_registry_contract

        contract = get_registry_contract(w3, Web3.to_checksum_address(CONTRACT_ADDRESS))
        account = w3.eth.account.from_key(AGGREGATOR_PRIVATE_KEY)
        nonce = w3.eth.get_transaction_count(account.address)

        tx = contract.functions.recordPoisoningEvent(
            bank_id.encode()[:32],
            round_number,
            attack_type,
            int(anomaly_score * 100000),
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 150000,
            'gasPrice': w3.eth.gas_price,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, AGGREGATOR_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return {'status': 'submitted', 'tx_hash': tx_hash.hex()}
    except Exception as exc:
        logger.error('Failed to record poisoning event: %s', exc)
        return {'status': 'failed', 'error': str(exc)}
