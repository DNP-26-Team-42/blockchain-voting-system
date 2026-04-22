# Blockchain-Based Voting System - Project Structure

## Overview
A centralized blockchain-based voting system implementing:
- Immutable vote recording on a distributed ledger
- Consensus mechanism for vote validation
- Prevention of double voting
- Transparency and voter verification
- CLI interfaces for both server and client

## Directory Structure

```
blockchain-voting-system/
├── server/
│   ├── blockchain.py       # Block and Blockchain classes
│   ├── crypto.py          # Cryptographic functions
│   ├── database.py        # PostgreSQL database operations
│   ├── network.py         # Socket server and communication
│   ├── server.py          # Main server with CLI
│   ├── utils.py           # Utility functions
│   ├── requirements.txt    # Python dependencies
│   └── data/              # Data files
├── client/
│   ├── network.py         # Socket client communication
│   ├── client.py          # Main client with CLI
│   └── requirements.txt    # Python dependencies
├── config.json            # Server configuration
└── README.md              # Project documentation
```

## Core Modules

### Server Side

#### `server/blockchain.py`
**Classes:**
- `Block`: Represents a single block containing votes
  - `calculate_hash()`: SHA-256 hash calculation
  - `mine_block()`: Proof-of-work mining
  - `is_valid()`: Block validation

- `Blockchain`: Manages the vote ledger
  - `create_genesis_block()`: Initialize blockchain
  - `add_vote()`: Add pending vote
  - `mine_pending_votes()`: Create new block from pending votes
  - `validate_chain()`: Ensure blockchain integrity
  - `is_vote_duplicate()`: Prevent double voting
  - `verify_vote_inclusion()`: Voter verification method
  - `get_vote_count()`: Tally votes by candidate

#### `server/crypto.py`
**Class:** `CryptoManager`
- `sha256_hash()`: Hash data securely
- `generate_voter_id()`: Create unique voter identifier
- `generate_signature()`: HMAC signing
- `verify_signature()`: Signature validation
- `hash_password()`: Secure password hashing
- `generate_voter_token()`: Authentication tokens
- `verify_voter_token()`: Token validation
- `create_merkle_root()`: Merkle tree for vote batches

#### `server/database.py`
**Classes:**
- `Voter`: Dataclass for voter information
- `VoteRecord`: Dataclass for vote storage
- `DatabaseConnection`: PostgreSQL operations
  - `connect()`: Establish database connection
  - `create_tables()`: Initialize schema
  - `register_voter()`: Add new voter
  - `mark_voter_voted()`: Track voting
  - `store_vote_record()`: Persist votes
  - `get_blockchain_state()`: Retrieve current state
  - `execute_query()`: Raw SQL execution

#### `server/network.py`
**Classes:**
- `NetworkMessage`: Request/response envelope
  - `to_json()`: Serialize message
  - `from_json()`: Deserialize message
  - `is_valid()`: Message validation

- `SocketServer`: TCP socket server
  - `start()`: Begin listening
  - `accept_connections()`: Handle client connections
  - `register_handler()`: Add message handlers
  - `handle_client()`: Process client requests
  - `send_message()`: Send to client
  - `receive_message()`: Receive from client

- `SocketClient`: Client connection wrapper (for testing)

#### `server/server.py`
**Class:** `VotingServer`
- `initialize_components()`: Setup blockchain, database, network
- `start_network_server()`: Launch socket server
- `handle_register_voter()`: Process registration
- `handle_vote_submission()`: Process vote
- `handle_verify_vote()`: Verify vote inclusion
- `handle_get_results()`: Return tallies
- `validate_vote()`: Check vote validity
- `mine_block()`: Create new block
- **CLI Methods:**
  - `cmd_status()`: Server/blockchain status
  - `cmd_mine()`: Mine pending votes
  - `cmd_view_votes()`: List all votes
  - `cmd_view_results()`: Show vote totals
  - `cmd_verify_integrity()`: Validate blockchain

#### `server/utils.py`
- `setup_logging()`: Logger configuration
- `validate_voter_name()`: Input validation
- `validate_candidate_name()`: Input validation
- `format_timestamp()`: Timestamp handling
- `sanitize_input()`: Security sanitization
- `format_vote_results()`: Display formatting
- `format_blockchain_info()`: Blockchain formatting

### Client Side

#### `client/network.py`
**Class:** `VotingClientNetwork`
- `connect()`: Connect to server
- `disconnect()`: Close connection
- `register_voter()`: Send registration
- `submit_vote()`: Submit vote
- `verify_vote()`: Verify vote recorded
- `get_results()`: Fetch election results
- `get_candidates()`: Get candidate list
- `is_connected()`: Check connectivity

#### `client/client.py`
**Class:** `VotingClient`
- `connect_to_server()`: Establish connection
- `run_cli()`: Interactive interface
- **Menu Methods:**
  - `menu_register_voter()`: Registration flow
  - `menu_submit_vote()`: Voting flow
  - `menu_verify_vote()`: Verification flow
  - `menu_view_results()`: Results display
  - `menu_view_candidates()`: Show candidates
  - `save_voter_info()`: Local persistence
  - `load_voter_info()`: Local retrieval

## Configuration

`config.json` contains:
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000
  },
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "voting_system",
    "user": "postgres",
    "password": "postgres"
  },
  "blockchain": {
    "difficulty": 4,
    "mining_reward": 1
  }
}
```

## Message Protocol

Client-server communication uses JSON messages:

```json
{
  "type": "register|vote|verify|results|status",
  "payload": {
    "voter_id": "...",
    "candidate": "...",
    "timestamp": "..."
  }
}
```

## Database Schema

**voters table:**
- voter_id (PRIMARY KEY)
- name, surname, id_number
- has_voted (BOOLEAN)
- vote_timestamp (TIMESTAMP)

**votes table:**
- voter_id (FOREIGN KEY)
- candidate
- timestamp
- block_index
- vote_hash

**blocks table:**
- block_index (PRIMARY KEY)
- block_hash
- previous_hash
- timestamp
- vote_count

## Security Features

1. **Cryptography**
   - SHA-256 hashing for block integrity
   - HMAC signatures for authentication
   - Voter tokens for session management

2. **Blockchain Validation**
   - Proof-of-work mining
   - Chain validation
   - Duplicate vote prevention

3. **Database**
   - Transactional operations
   - Voter registration tracking
   - Vote immutability

## Running the System

### Server
```bash
cd server
pip install -r requirements.txt
python server.py ../config.json
```

### Client
```bash
cd client
pip install -r requirements.txt
python client.py localhost 5000
```

## Implementation Checklist

- [ ] Implement Block class with hashing and mining
- [ ] Implement Blockchain class with consensus
- [ ] Implement CryptoManager with all crypto functions
- [ ] Implement DatabaseConnection with PostgreSQL
- [ ] Implement SocketServer for connections
- [ ] Implement SocketClient for testing
- [ ] Implement VotingServer with handlers
- [ ] Implement VotingClient CLI
- [ ] Create database schema
- [ ] Test vote submission flow
- [ ] Test vote verification
- [ ] Test blockchain integrity
- [ ] Test duplicate prevention
- [ ] Docker deployment setup
