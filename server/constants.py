"""
Constants and configuration values for the voting system.
Centralized definitions for magic numbers and fixed values.
"""

# ============ SYSTEM CONSTANTS ============

SYSTEM_NAME = "Blockchain-Based Voting System"
SYSTEM_VERSION = "1.0.0"
SYSTEM_AUTHOR = "Voting System Development Team"

# ============ BLOCKCHAIN CONSTANTS ============

DEFAULT_DIFFICULTY = 4
DEFAULT_BLOCK_SIZE = 100
DEFAULT_MINING_REWARD = 1
GENESIS_BLOCK_INDEX = 0
GENESIS_BLOCK_HASH = "0" * 64

# Proof of Work - number of leading zeros required (difficulty * 4 bits)
PoW_BASE_DIFFICULTY = 4

# ============ NETWORK CONSTANTS ============

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 5000
DEFAULT_TIMEOUT = 30
DEFAULT_BUFFER_SIZE = 4096
MAX_CONNECTIONS = 100
SOCKET_BACKLOG = 5

# ============ DATABASE CONSTANTS ============

DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = 5432
DEFAULT_DB_NAME = "voting_system"
DEFAULT_DB_USER = "postgres"
DEFAULT_DB_PASSWORD = "postgres"

# Connection pool settings
DB_POOL_MIN_SIZE = 1
DB_POOL_MAX_SIZE = 10
DB_CONNECTION_TIMEOUT = 10

# ============ VOTER VALIDATION CONSTANTS ============

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 255

MIN_SURNAME_LENGTH = 2
MAX_SURNAME_LENGTH = 255

MIN_ID_NUMBER_LENGTH = 5
MAX_ID_NUMBER_LENGTH = 50

MIN_CANDIDATE_LENGTH = 1
MAX_CANDIDATE_LENGTH = 255

# ============ MESSAGE PROTOCOL CONSTANTS ============

MESSAGE_VERSION = "1.0"
MESSAGE_ENCODING = "utf-8"

# Message types
MSG_REGISTER = "register"
MSG_VOTE = "vote"
MSG_VERIFY = "verify"
MSG_STATUS = "status"
MSG_RESULTS = "results"
MSG_CANDIDATES = "candidates"
MSG_ERROR = "error"
MSG_SUCCESS = "success"
MSG_PING = "ping"
MSG_PONG = "pong"

# ============ ERROR CODES ============

ERROR_SUCCESS = 0
ERROR_INVALID_INPUT = 1
ERROR_VOTER_NOT_FOUND = 2
ERROR_VOTER_ALREADY_VOTED = 3
ERROR_DUPLICATE_VOTER = 4
ERROR_DATABASE_ERROR = 5
ERROR_BLOCKCHAIN_ERROR = 6
ERROR_NETWORK_ERROR = 7
ERROR_AUTHENTICATION_FAILED = 8
ERROR_VOTE_NOT_FOUND = 9
ERROR_INVALID_CANDIDATE = 10
ERROR_SERVER_ERROR = 500

# ============ TIMESTAMP CONSTANTS ============

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
TIMESTAMP_FORMAT_ISO = "%Y-%m-%dT%H:%M:%S.%f"
TIMESTAMP_FORMAT_READABLE = "%B %d, %Y %I:%M %p"

# Token expiry time
TOKEN_EXPIRY_HOURS = 24
TOKEN_EXPIRY_SECONDS = TOKEN_EXPIRY_HOURS * 3600

# ============ CRYPTOGRAPHY CONSTANTS ============

HASH_ALGORITHM = "sha256"
HMAC_ALGORITHM = "sha256"

# Password hashing
PBKDF2_ITERATIONS = 100000
SALT_LENGTH = 32

# ============ LOGGING CONSTANTS ============

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"

# ============ STATUS CODES ============

STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_REGISTERED = "registered"
STATUS_VOTED = "voted"
STATUS_REJECTED = "rejected"

# ============ MERKLE TREE CONSTANTS ============

MERKLE_HASH_ALGORITHM = "sha256"
MERKLE_TREE_JOIN_CHARACTER = ""

# ============ VALIDATION PATTERNS ============

# Regex patterns for validation
PATTERN_VOTER_ID = r"^[A-Z0-9\-/]{5,50}$"
PATTERN_NAME = r"^[a-zA-Z\s]{2,255}$"
PATTERN_EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PATTERN_IPV4 = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"

# ============ DISPLAY CONSTANTS ============

# Terminal colors
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"

# ============ FILE PATHS ============

CONFIG_FILE_DEFAULT = "config.json"
LOG_DIR = "logs"
DATA_DIR = "data"
SCHEMA_FILE = "schema.sql"

# ============ PAGINATION & LIMITS ============

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000
DEFAULT_QUERY_LIMIT = 100
MAX_QUERY_LIMIT = 10000

# ============ FEATURE FLAGS ============

ENABLE_ANONYMOUS_VOTING = True
REQUIRE_VOTER_REGISTRATION = True
ENABLE_VOTER_VERIFICATION = True
ENABLE_MERKLE_PROOF_VERIFICATION = True
ENABLE_LOGGING = True
ENABLE_PERSISTENCE = True
