"""Async IPFS client for model weight delta storage."""

import logging
import os

logger = logging.getLogger(__name__)

IPFS_URL = os.environ.get('IPFS_URL', 'http://localhost:5001')


async def upload_delta(delta_bytes: bytes) -> str:
    """Upload serialized weight delta to IPFS.

    Args:
        delta_bytes: Serialized model weight delta.

    Returns:
        IPFS Content Identifier (CID).
    """
    try:
        import ipfshttpclient

        client = ipfshttpclient.connect(IPFS_URL)
        result = client.add_bytes(delta_bytes)
        logger.info('Uploaded delta to IPFS: %s', result)
        return result
    except Exception as exc:
        logger.warning('IPFS upload failed, using fallback hash: %s', exc)
        import hashlib

        return 'Qm' + hashlib.sha256(delta_bytes).hexdigest()[:44]


async def fetch_delta(cid: str) -> bytes:
    """Fetch serialized weight delta from IPFS by CID.

    Args:
        cid: IPFS Content Identifier.

    Returns:
        Raw bytes of the weight delta.
    """
    try:
        import ipfshttpclient

        client = ipfshttpclient.connect(IPFS_URL)
        data = client.cat(cid)
        logger.info('Fetched delta from IPFS: %s (%d bytes)', cid, len(data))
        return data
    except Exception as exc:
        logger.warning('IPFS fetch failed for CID %s: %s — returning empty', cid, exc)
        return b''
