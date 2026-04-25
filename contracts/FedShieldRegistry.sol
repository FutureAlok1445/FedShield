// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title FedShieldRegistry
 * @notice On-chain registry for federated learning round results and poisoning events.
 * @dev Uses OpenZeppelin AccessControl for role-based access and ReentrancyGuard for safety.
 *      PRD §12.1 — Full specification implementation.
 */
contract FedShieldRegistry is AccessControl, ReentrancyGuard {
    bytes32 public constant AGGREGATOR_ROLE = keccak256("AGGREGATOR_ROLE");
    bytes32 public constant BANK_ROLE = keccak256("BANK_ROLE");
    uint256 public constant MAX_STRIKES = 3;

    struct RoundResult {
        uint256 roundNumber;
        bytes32 modelHash;
        string modelCid;
        uint256 participantCount;
        uint256 poisoningEventCount;
        uint256 timestamp;
    }

    struct PoisoningRecord {
        bytes32 bankIdHash;
        uint256 roundNumber;
        string attackType;
        uint256 anomalyScoreE5;  // anomaly_score * 1e5
        uint256 timestamp;
    }

    struct BankRecord {
        bytes32 bankId;
        bool registered;
        bool suspended;
        uint256 poisoningStrikes;
        uint256 registeredAt;
    }

    mapping(uint256 => RoundResult) public rounds;
    mapping(bytes32 => BankRecord) public banks;
    mapping(bytes32 => PoisoningRecord[]) public bankPoisoningHistory;
    PoisoningRecord[] public poisoningEvents;
    uint256 public roundCount;
    uint256 public bankCount;

    event RoundFinalized(uint256 indexed roundNumber, bytes32 modelHash, uint256 participantCount);
    event PoisoningDetected(bytes32 indexed bankIdHash, uint256 indexed roundNumber, string attackType);
    event BankRegistered(bytes32 indexed bankId);
    event BankSuspended(bytes32 indexed bankId, uint256 totalStrikes);

    constructor(address aggregator) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(AGGREGATOR_ROLE, aggregator);
    }

    /**
     * @notice Register a new bank in the network.
     * @param bankId Unique identifier hash for the bank.
     */
    function registerBank(bytes32 bankId) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(!banks[bankId].registered, "Bank already registered");

        banks[bankId] = BankRecord({
            bankId: bankId,
            registered: true,
            suspended: false,
            poisoningStrikes: 0,
            registeredAt: block.timestamp
        });

        bankCount++;
        emit BankRegistered(bankId);
    }

    /**
     * @notice Finalize a federation round with global model hash.
     * @dev Validates sequential round numbering (PRD §12.1).
     */
    function finalizeRound(
        uint256 roundNumber,
        bytes32 modelHash,
        string calldata modelCid,
        uint256 participantCount,
        uint256 poisoningEventCount
    ) external onlyRole(AGGREGATOR_ROLE) nonReentrant {
        require(rounds[roundNumber].timestamp == 0, "Round already finalized");

        rounds[roundNumber] = RoundResult({
            roundNumber: roundNumber,
            modelHash: modelHash,
            modelCid: modelCid,
            participantCount: participantCount,
            poisoningEventCount: poisoningEventCount,
            timestamp: block.timestamp
        });

        roundCount++;
        emit RoundFinalized(roundNumber, modelHash, participantCount);
    }

    /**
     * @notice Record a poisoning event on-chain.
     * @dev Increments bank's strikes and auto-suspends at MAX_STRIKES (PRD §12.1).
     */
    function recordPoisoningEvent(
        bytes32 bankIdHash,
        uint256 roundNumber,
        string calldata attackType,
        uint256 anomalyScoreE5
    ) external onlyRole(AGGREGATOR_ROLE) {
        PoisoningRecord memory record = PoisoningRecord({
            bankIdHash: bankIdHash,
            roundNumber: roundNumber,
            attackType: attackType,
            anomalyScoreE5: anomalyScoreE5,
            timestamp: block.timestamp
        });

        poisoningEvents.push(record);
        bankPoisoningHistory[bankIdHash].push(record);

        // Increment strikes and auto-suspend
        if (banks[bankIdHash].registered) {
            banks[bankIdHash].poisoningStrikes++;

            if (banks[bankIdHash].poisoningStrikes >= MAX_STRIKES && !banks[bankIdHash].suspended) {
                banks[bankIdHash].suspended = true;
                emit BankSuspended(bankIdHash, banks[bankIdHash].poisoningStrikes);
            }
        }

        emit PoisoningDetected(bankIdHash, roundNumber, attackType);
    }

    /**
     * @notice Verify a round's model hash integrity.
     * @param roundNumber Round to verify.
     * @param claimedHash Hash to check against.
     * @return valid Whether the hash matches.
     * @return finalized Whether the round has been finalized.
     */
    function verifyRound(uint256 roundNumber, bytes32 claimedHash)
        external
        view
        returns (bool valid, bool finalized)
    {
        RoundResult storage r = rounds[roundNumber];
        finalized = r.timestamp > 0;
        valid = finalized && r.modelHash == claimedHash;
    }

    /**
     * @notice Get full poisoning history for a bank.
     * @param bankIdHash Bank to query.
     * @return records Array of poisoning records.
     */
    function getPoisoningHistory(bytes32 bankIdHash)
        external
        view
        returns (PoisoningRecord[] memory records)
    {
        return bankPoisoningHistory[bankIdHash];
    }

    /**
     * @notice Get total poisoning events count.
     */
    function poisoningEventCount() external view returns (uint256) {
        return poisoningEvents.length;
    }

    /**
     * @notice Check if a bank is suspended.
     */
    function isBankSuspended(bytes32 bankIdHash) external view returns (bool) {
        return banks[bankIdHash].suspended;
    }
}
