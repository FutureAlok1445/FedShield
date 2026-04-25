"""
FedShieldRegistry ABI - auto-generated from PRD Section 12.1 contract spec.
Used by polygon_client.py via web3.py to interact with the on-chain registry.
"""

FEDSHIELD_REGISTRY_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "aggregator", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "bankId", "type": "bytes32"}],
        "name": "registerBank",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "roundNumber", "type": "uint256"},
            {"internalType": "bytes32", "name": "modelHash", "type": "bytes32"},
            {"internalType": "string", "name": "modelCid", "type": "string"},
            {"internalType": "uint256", "name": "participantCount", "type": "uint256"},
            {"internalType": "uint256", "name": "poisoningEventCount", "type": "uint256"}
        ],
        "name": "finalizeRound",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "bankIdHash", "type": "bytes32"},
            {"internalType": "uint256", "name": "roundNumber", "type": "uint256"},
            {"internalType": "string", "name": "attackType", "type": "string"},
            {"internalType": "uint256", "name": "anomalyScoreE5", "type": "uint256"}
        ],
        "name": "recordPoisoningEvent",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "roundNumber", "type": "uint256"},
            {"internalType": "bytes32", "name": "claimedHash", "type": "bytes32"}
        ],
        "name": "verifyRound",
        "outputs": [
            {"internalType": "bool", "name": "valid", "type": "bool"},
            {"internalType": "bool", "name": "finalized", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "bankIdHash", "type": "bytes32"}],
        "name": "getPoisoningHistory",
        "outputs": [
            {
                "components": [
                    {"internalType": "bytes32", "name": "bankIdHash", "type": "bytes32"},
                    {"internalType": "uint256", "name": "roundNumber", "type": "uint256"},
                    {"internalType": "string", "name": "attackType", "type": "string"},
                    {"internalType": "uint256", "name": "anomalyScoreE5", "type": "uint256"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
                ],
                "internalType": "struct FedShieldRegistry.PoisoningRecord[]",
                "name": "records",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "bankIdHash", "type": "bytes32"}],
        "name": "isBankSuspended",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "poisoningEventCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "roundCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "roundNumber", "type": "uint256"},
            {"indexed": False, "name": "modelHash", "type": "bytes32"},
            {"indexed": False, "name": "participantCount", "type": "uint256"}
        ],
        "name": "RoundFinalized",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "bankIdHash", "type": "bytes32"},
            {"indexed": True, "name": "roundNumber", "type": "uint256"},
            {"indexed": False, "name": "attackType", "type": "string"}
        ],
        "name": "PoisoningDetected",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [{"indexed": True, "name": "bankId", "type": "bytes32"}],
        "name": "BankRegistered",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "bankId", "type": "bytes32"},
            {"indexed": False, "name": "totalStrikes", "type": "uint256"}
        ],
        "name": "BankSuspended",
        "type": "event"
    }
]


def get_registry_contract(web3, address):
    """Get contract instance for FedShieldRegistry."""
    return web3.eth.contract(address=address, abi=FEDSHIELD_REGISTRY_ABI)
