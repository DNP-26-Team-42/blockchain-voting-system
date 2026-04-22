"""
Custom exceptions for the voting system.
Handles errors at various layers: blockchain, database, network, voting.
"""


class VotingSystemError(Exception):
    """Base exception for voting system."""
    pass


# ============ BLOCKCHAIN EXCEPTIONS ============

class BlockchainError(VotingSystemError):
    """Base exception for blockchain-related errors."""
    pass


class InvalidBlockError(BlockchainError):
    """Block failed validation (PoW, hash, structure)."""
    pass


class InvalidChainError(BlockchainError):
    """Blockchain validation failed (broken chain, duplicate votes)."""
    pass


class GenesisBlockError(BlockchainError):
    """Error creating genesis block."""
    pass


class MiningError(BlockchainError):
    """Error during block mining (PoW computation)."""
    pass


class DuplicateVoteError(BlockchainError):
    """Voter has already voted."""
    pass


class VoteNotInBlockchainError(BlockchainError):
    """Vote not found in blockchain."""
    pass


# ============ DATABASE EXCEPTIONS ============

class DatabaseError(VotingSystemError):
    """Base exception for database-related errors."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Failed to connect to database."""
    pass


class DatabaseQueryError(DatabaseError):
    """SQL query execution failed."""
    pass


class VoterNotFoundError(DatabaseError):
    """Voter registration not found."""
    pass


class VoterAlreadyExistsError(DatabaseError):
    """Voter already registered."""
    pass


class VoterAlreadyVotedError(DatabaseError):
    """Voter has already cast their vote."""
    pass


class VoteStorageError(DatabaseError):
    """Failed to store vote in database."""
    pass


class BlockStorageError(DatabaseError):
    """Failed to store block in database."""
    pass


# ============ NETWORK EXCEPTIONS ============

class NetworkError(VotingSystemError):
    """Base exception for network-related errors."""
    pass


class ServerError(NetworkError):
    """Server operation failed."""
    pass


class ClientConnectionError(NetworkError):
    """Failed to connect to server."""
    pass


class MessageFormatError(NetworkError):
    """Invalid message format or structure."""
    pass


class MessageTypeError(NetworkError):
    """Unknown or unsupported message type."""
    pass


class MessageValidationError(NetworkError):
    """Message validation failed."""
    pass


class TimeoutError(NetworkError):
    """Network operation timeout."""
    pass


# ============ VOTING EXCEPTIONS ============

class VotingError(VotingSystemError):
    """Base exception for voting-related errors."""
    pass


class InvalidVoteError(VotingError):
    """Vote format or content is invalid."""
    pass


class VotingNotEnabledError(VotingError):
    """Voting is not currently enabled."""
    pass


class InvalidCandidateError(VotingError):
    """Specified candidate does not exist."""
    pass


class InvalidVoterError(VotingError):
    """Voter ID or information is invalid."""
    pass


# ============ CRYPTOGRAPHY EXCEPTIONS ============

class CryptoError(VotingSystemError):
    """Base exception for cryptography operations."""
    pass


class SignatureVerificationError(CryptoError):
    """Signature verification failed."""
    pass


class TokenVerificationError(CryptoError):
    """Token verification failed."""
    pass


class MerkleProofError(CryptoError):
    """Merkle proof generation or verification failed."""
    pass


# ============ VALIDATION EXCEPTIONS ============

class ValidationError(VotingSystemError):
    """Base exception for input validation."""
    pass


class InvalidInputError(ValidationError):
    """Input validation failed."""
    pass


class MissingFieldError(ValidationError):
    """Required field is missing."""
    pass


class InvalidFormatError(ValidationError):
    """Input format is invalid."""
    pass


# ============ CONFIGURATION EXCEPTIONS ============

class ConfigError(VotingSystemError):
    """Base exception for configuration issues."""
    pass


class ConfigurationError(ConfigError):
    """Configuration loading or parsing failed."""
    pass


class MissingConfigError(ConfigError):
    """Required configuration is missing."""
    pass
