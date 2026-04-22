# Blockchain-Based Voting System - Project 24 Variant A

A centralized blockchain-based voting system implementing immutable vote recording, double-voting prevention, transparent vote verification, and consensus-based validation.

**Project**: Project 24 Variant A
**Stack**: Python, PostgreSQL, Docker, Socket Programming
**Version**: 1.0.0

## Overview

This system provides a secure, transparent voting mechanism where:
- ✅ Votes are recorded immutably on a distributed blockchain ledger
- ✅ Double-voting is cryptographically prevented
- ✅ Voters can verify their votes were counted (anonymous verification)
- ✅ Blockchain integrity is maintained through proof-of-work consensus
- ✅ Complete vote history is auditable and transparent
- ✅ Both server and client offer interactive CLI interfaces

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Blockchain Voting System                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐              ┌─────────────────────┐  │
│  │  Voting Clients  │  (Network)   │  Voting Server      │  │
│  │  (CLI)           │◄────────────►│  • Blockchain Node  │  │
│  │  • Register      │  Socket TCP  │  • Vote Validator   │  │
│  │  • Vote          │              │  • Consensus Miner  │  │
│  │  • Verify        │              │  • CLI Interface    │  │
│  └──────────────────┘              └──────────┬──────────┘  │
│                                                │              │
│                                          ┌─────▼──────────┐  │
│                                          │  PostgreSQL DB │  │
│                                          │  • Voters      │  │
│                                          │  • Votes       │  │
│                                          │  • Blocks      │  │
│                                          │  • State       │  │
│                                          └────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
blockchain-voting-system/
├── server/                      # Server application
│   ├── blockchain.py           # Block & Blockchain classes
│   ├── crypto.py               # Cryptographic operations
│   ├── database.py             # PostgreSQL interface
│   ├── network.py              # Socket communication
│   ├── server.py               # Main server with CLI
│   ├── config.py               # Configuration loader
│   ├── logger.py               # Logging setup
│   ├── constants.py            # System constants
│   ├── exceptions.py           # Custom exceptions
│   ├── utils.py                # Utility functions
│   ├── schema.sql              # Database schema
│   └── requirements.txt         # Python dependencies
│
├── client/                      # Client application
│   ├── network.py              # Socket client wrapper
│   ├── client.py               # Main client with CLI
│   └── requirements.txt         # Python dependencies
│
├── tests/                       # Test suite
│   ├── test_blockchain.py      # Blockchain tests
│   ├── test_database.py        # Database tests
│   ├── test_crypto.py          # Cryptography tests
│   └── test_integration.py     # Integration tests
│
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose orchestration
├── config.json                  # Configuration file
├── .env.example                 # Environment variables template
├── PROJECT_STRUCTURE.md         # Detailed structure documentation
└── README.md                    # This file
```

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone or navigate to project
cd blockchain-voting-system

# 2. Copy environment template
cp .env.example .env

# 3. Start server with PostgreSQL
docker-compose up -d

# 4. Verify services running
docker-compose ps

# 5. View server logs
docker-compose logs -f voting-server

# 6. Run client (from another terminal)
python client/client.py localhost 5000

# 7. Stop services
docker-compose down
```

### Option 2: Local Development

#### Setup Server

```bash
# 1. Install Python 3.11+
python3 --version

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
cd server
pip install -r requirements.txt

# 4. Setup PostgreSQL database
# Ensure PostgreSQL is running on localhost:5432
psql -U postgres -c "CREATE DATABASE voting_system;"

# 5. Initialize database schema
psql -U postgres -d voting_system -f schema.sql

# 6. Run server
python server.py config.json
```

#### Setup Client

```bash
# 1. Install dependencies
cd client
pip install -r requirements.txt

# 2. Run client (in another terminal)
python client.py localhost 5000
```

### Option 3: Environment Variables

Create `.env` file or use environment variables:

```bash
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
SERVER_TIMEOUT=30

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=voting_system
DB_USER=postgres
DB_PASSWORD=postgres

# Blockchain Configuration
BLOCKCHAIN_DIFFICULTY=4
BLOCKCHAIN_BLOCK_SIZE=100

# Logging
LOG_LEVEL=INFO
```

## Server CLI

Start server:
```bash
python server/server.py config.json
```

**Available Commands:**

| Command | Description |
|---------|-------------|
| `status` | Show blockchain and server status |
| `mine` | Mine pending votes into new block |
| `votes` | Display all votes in blockchain |
| `results` | Show vote tallies by candidate |
| `voters` | List registered voters |
| `blockchain` | Show blockchain information |
| `verify` | Verify blockchain integrity |
| `help` | Show available commands |
| `exit` | Shutdown server |

**Example:**

```
VotingServer> status
=== Server Status ===
Server Running: Yes
Server Port: 5000
Database: Connected
Blockchain Blocks: 5
Total Votes: 47
Pending Votes: 3
Registered Voters: 50
Voted Voters: 47

VotingServer> results
=== Vote Results ===
Candidate A: 20 votes (42.6%)
Candidate B: 18 votes (38.3%)
Candidate C: 9 votes (19.1%)
Total Votes: 47

VotingServer> mine
Mining block #5...
✓ Block mined successfully!
  Hash: a3f4e8d9c2b1...
  Votes included: 3
  Nonce: 12847

VotingServer> exit
Shutting down...
```

## Client CLI

Start client:
```bash
python client/client.py localhost 5000
```

**Available Commands:**

| Command | Description |
|---------|-------------|
| `register` | Register as voter |
| `vote` | Cast your vote |
| `verify` | Verify your vote |
| `results` | View election results |
| `candidates` | Show all candidates |
| `status` | Server status |
| `help` | Show help |
| `exit` | Exit |

**Example:**

```
Connected to voting server at localhost:5000

VotingClient> register
Enter your name: John
Enter your surname: Doe
Enter your ID number: ABC123456
✓ Successfully registered as voter!
Your Voter ID: 9f3e4a7b2c1d...

VotingClient> candidates
Available Candidates:
1. Candidate A
2. Candidate B
3. Candidate C

VotingClient> vote
Select candidate (1-3): 1
✓ Vote submitted successfully!
Your vote hash: f7a3c1e9...

VotingClient> verify
Verifying your vote...
✓ Vote found in blockchain!
  Voter ID: 9f3e4a7b2c1d...
  Candidate: Candidate A
  Block Index: 5
  Timestamp: 2024-04-23T10:30:45

VotingClient> results
=== Election Results ===
Candidate A: 20 votes (42.6%)
Candidate B: 18 votes (38.3%)
Candidate C: 9 votes (19.1%)
Total Votes: 47

VotingClient> exit
Disconnecting...
```

## Database Schema

### Tables

**voters**
- `voter_id` (PRIMARY KEY) - Unique voter identifier
- `name`, `surname`, `id_number` - Voter information
- `has_voted` (BOOLEAN) - Voting status
- `vote_timestamp` - When vote was cast
- `status` - Registration status

**votes**
- `vote_id` (PRIMARY KEY)
- `voter_id` (FOREIGN KEY) - Reference to voter
- `candidate` - Chosen candidate
- `timestamp` - Vote submission time
- `block_index` - Block containing this vote
- `vote_hash` - SHA-256 hash of vote
- `merkle_proof` - Merkle proof for verification

**blocks**
- `block_index` (PRIMARY KEY)
- `block_hash` - SHA-256 hash of block
- `previous_hash` - Hash of previous block
- `timestamp` - Block creation time
- `nonce` - Proof-of-work nonce
- `vote_count` - Votes in block
- `merkle_root` - Merkle root of votes
- `miner_id` - Who mined this block

**pending_votes**
- `pending_vote_id` (PRIMARY KEY)
- `voter_id` - Voter identifier
- `candidate` - Selected candidate
- `timestamp` - Submission time

**blockchain_state**
- Tracks blockchain statistics
- Last block info
- Validation state

## Cryptography

### Hash Functions
- **SHA-256**: Block hashing, vote hashing
- **HMAC**: Vote authentication and signatures

### Key Operations
1. **Voter ID Generation**: Hash of (name + surname + id_number)
2. **Vote Hash**: Hash of (voter_id + candidate + timestamp)
3. **Block Hash**: Hash of block content with proof-of-work
4. **Merkle Root**: Tree hash of all votes in block

### Vote Verification
Uses **Merkle proofs** to verify vote inclusion without full blockchain:
1. Voter provides voter_id and vote_hash
2. System generates proof path through Merkle tree
3. Voter can verify inclusion offline

## Blockchain Consensus

### Proof-of-Work
- Difficulty: Configurable leading zeros (default 4 = 16 bits)
- Mining: Iterate nonce until hash meets difficulty
- Validation: Verify hash meets proof-of-work requirement
- Immutability: Changing any vote invalidates entire chain

### Block Structure
```json
{
  "index": 5,
  "timestamp": "2024-04-23T10:30:45",
  "votes": [
    {"voter_id": "abc123", "candidate": "A", "timestamp": "2024-04-23T10:30:00"},
    {"voter_id": "def456", "candidate": "B", "timestamp": "2024-04-23T10:30:15"},
    {"voter_id": "ghi789", "candidate": "A", "timestamp": "2024-04-23T10:30:30"}
  ],
  "previous_hash": "a3f4e8d9c2b1...",
  "nonce": 12847,
  "hash": "f7a3c1e9b2d4...",
  "merkle_root": "m5n3p7q1r9s2...",
  "miner_id": "system",
  "status": "finalized"
}
```

## Security Features

✅ **Vote Immutability**: Once recorded on blockchain, votes cannot be changed
✅ **Double-Voting Prevention**: Database unique constraints + blockchain validation
✅ **Transparency**: Complete vote history auditable
✅ **Anonymous Verification**: Merkle proofs verify votes without identity
✅ **Cryptographic Integrity**: SHA-256 hashing throughout
✅ **Consensus Mechanism**: Proof-of-work validates all blocks
✅ **Transaction Atomicity**: Database transactions ensure consistency

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=server tests/

# Run specific test suite
pytest tests/test_blockchain.py
pytest tests/test_database.py
pytest tests/test_integration.py
```

## Performance Characteristics

- **Block Mining**: ~1-5 seconds per block (difficulty 4)
- **Vote Submission**: <100ms (network + database)
- **Vote Verification**: ~10ms (Merkle proof lookup)
- **Database Queries**: <50ms (indexed lookups)
- **Blockchain Validation**: ~500ms for 1000 votes

## Docker Commands

```bash
# Build image
docker build -t voting-system:latest .

# Run container
docker run -p 5000:5000 voting-system:latest

# Docker Compose
docker-compose up -d          # Start
docker-compose down           # Stop
docker-compose logs -f        # View logs
docker-compose exec voting-server bash  # Enter container

# Environment override
DB_PASSWORD=newpass docker-compose up -d
```

## Configuration

Edit `config.json`:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "timeout": 30
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
    "mining_reward": 1,
    "block_size": 100
  },
  "voting": {
    "enable_anonymous": true,
    "require_registration": true,
    "voting_duration_hours": 24
  }
}
```

## Network Protocol

### Message Format

All messages use JSON format:

```json
{
  "type": "register|vote|verify|status|results",
  "version": "1.0",
  "timestamp": "2024-04-23T10:30:45.123456",
  "message_id": "msg_abc123xyz",
  "payload": {
    "voter_id": "...",
    "candidate": "...",
    "name": "...",
    ...
  }
}
```

### Message Types

**REGISTER**: Voter registration
```json
{"type": "register", "payload": {"name": "John", "surname": "Doe", "id_number": "ABC123"}}
```

**VOTE**: Submit vote
```json
{"type": "vote", "payload": {"voter_id": "...", "candidate": "Candidate A"}}
```

**VERIFY**: Check vote inclusion
```json
{"type": "verify", "payload": {"voter_id": "..."}}
```

**STATUS**: Server status
```json
{"type": "status"}
```

**RESULTS**: Election results
```json
{"type": "results"}
```

## Troubleshooting

### PostgreSQL Connection Error
```
Error: Could not connect to database
Solution: Ensure PostgreSQL is running and credentials are correct
```

### "Address already in use" Error
```bash
# Find process on port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
# Or use different port
SERVER_PORT=5001 docker-compose up
```

### Blockchain Validation Failed
```
Error: Invalid block found in chain
Solution: Database may be corrosconabpted, run blockchain verification in server CLI
```

### Client Connection Refused
```
Error: Failed to connect to server
Solution: Verify server is running, check host/port, check firewall
```

## Future Enhancements

- [ ] Multi-node decentralized blockchain (Variant B)
- [ ] Merkle privacy features (Variant C)
- [ ] Advanced consensus protocols (RAFT)
- [ ] Web UI for voting and monitoring
- [ ] Mobile client application
- [ ] Audit logging and forensics
- [ ] Vote encryption (end-to-end)
- [ ] Automated backup and recovery
- [ ] Real-time WebSocket updates
- [ ] Admin authentication and authorization

## References

- [Bitcoin Whitepaper](https://bitcoin.org/bitcoin.pdf)
- [Merkle Trees](https://en.wikipedia.org/wiki/Merkle_tree)
- [Proof of Work](https://en.wikipedia.org/wiki/Proof_of_work)
- [Blockchain Voting Systems](https://arxiv.org/)

## License

Project 24 - Academic Use

## Support

For issues and questions, refer to project documentation or course materials.
