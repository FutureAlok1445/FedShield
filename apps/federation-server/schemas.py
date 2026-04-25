"""Pydantic schemas for the Federation Server API.

Matches PRD §13.2 API contracts.
"""

from typing import Optional

from pydantic import BaseModel, Field


class RoundCreateRequest(BaseModel):
    expected_participants: int = Field(..., gt=0, description='Number of banks expected to submit')


class RoundStatusResponse(BaseModel):
    round_id: str
    round_number: int = 0
    status: str = 'open'
    expected_participants: int = 0
    participants_received: int = 0
    global_model_hash: str = ''
    global_model_cid: str = ''
    chain_tx_hash: str = ''
    global_auc: Optional[float] = None
    started_at: str = ''


class SubmitDelta(BaseModel):
    bank_id: str
    weight_delta_cid: str = Field(..., description='IPFS CID of the encrypted weight delta')
    weight_hash: str = Field(..., description='SHA-256 hash of the weight delta')
    signature: str = Field(..., description='RSA-4096 signature of the weight hash')
    dp_epsilon_used: Optional[float] = None
    local_samples_used: Optional[int] = None
    local_auc: Optional[float] = None


class SubmitResponse(BaseModel):
    status: str
    anomaly_score: float = 0.0
    decision: str = 'accept'
    trust_score: float = 0.0
    received: int = 0
    flags: list[str] = []


class HealthResponse(BaseModel):
    status: str = 'ok'
    current_round: Optional[int] = None
    last_aggregation_at: Optional[str] = None


class TrustHistoryEntry(BaseModel):
    round: int
    trust_score: float
