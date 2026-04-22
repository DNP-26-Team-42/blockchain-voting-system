# Blockchain Voting System - Implementation Guide

## Project Requirements (Variant A Analysis)

Based on Project 24 Variant A requirements:

✅ **System Must:**
1. Accept vote submissions from clients
2. Record votes immutably on a distributed ledger
3. Validate votes using a consensus mechanism
4. Prevent double voting (critical)
5. Ensure transparency - votes can be audited
6. Allow anonymous verification of vote inclusion
7. Support vote display/retrieval from centralized node
8. Log voting activities with tracking
9. Support vote verification by voters
10. Use a centralized blockchain node (unlike Variant B/C)

✅ **Deliverables:**
- PDF Report (IMRaD format) with architecture diagrams
- Working code repository with README
- Demo video (1-2 minutes)
- System demonstrating:
  - Vote logging with timestamp/hash/voter ID
  - Vote uniqueness validation (no duplicates)
  - Verification mechanism (Merkle proofs or digital receipt)
  - Consensus testing (block validation)

---

## Architecture Overview

### Components

```
┌─────────────────────────────────────────────────────────────┐
│           BLOCKCHAIN VOTING SYSTEM ARCHITECTURE             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  CLIENT LAYER                                                │
│  ├─ Client CLI (client.py)                                  │
│  └─ Network Wrapper (network.py)                            │
│       │                                                       │
│       │ TCP Socket Communication (JSON Protocol)             │
│       ▼                                                       │
│  SERVER LAYER                                                │
│  ├─ Socket Server (network.py - SocketServer)              │
│  │  ├─ Accept & handle multiple clients                     │
│  │  ├─ Route messages to handlers                           │
│  │  └─ Send responses back                                  │
│  │                                                            │
│  ├─ Voting Server (server.py - VotingServer)               │
│  │  ├─ Handle registration requests                         │
│  │  ├─ Process vote submissions                             │
│  │  ├─ Verify votes & prevent duplicates                    │
│  │  ├─ Mine blocks from pending votes                       │
│  │  ├─ Generate Merkle proofs for verification              │
│  │  └─ Server CLI for administration                        │
│  │                                                            │
│  ├─ Blockchain Engine (blockchain.py)                          │
│  │  ├─ Block management & creation                          │
│  │  ├─ Proof-of-work consensus                              │
│  │  ├─ Chain validation                                     │
│  │  ├─ Vote tracking & uniqueness                           │
│  │  ├─ Merkle tree generation                               │
│  │  └─ Statistics & analysis                                │
│  │                                                            │
│  ├─ Cryptography (crypto.py)                                 │
│  │  ├─ SHA-256 hashing                                      │
│  │  ├─ HMAC signing                                         │
│  │  ├─ Voter ID generation                                  │
│  │  ├─ Token management                                     │
│  │  ├─ Merkle proof generation & verification               │
│  │  └─ Password hashing                                     │
│  │                                                            │
│  ├─ Database Layer (database.py)                             │
│  │  ├─ PostgreSQL Connection Management                     │
│  │  ├─ Voter Registration                                   │
│  │  ├─ Vote Storage & Immutability                          │
│  │  ├─ Block Record Persistence                             │
│  │  ├─ Blockchain State Management                          │
│  │  └─ Pending Votes Pool                                   │
│  │                                                            │
│  └─ Support Modules                                          │
│     ├─ Config Loader (config.py)                            │
│     ├─ Logger Factory (logger.py)                           │
│     ├─ Exception Hierarchy (exceptions.py)                  │
│     ├─ Utility Functions (utils.py)                         │
│     └─ System Constants (constants.py)                      │
│                                                               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                        PERSISTENCE LAYER
                               │
                    ┌──────────┴──────────┐
                    │                     │
              PostgreSQL          Blockchain State
              Database            (on-disk/DB)
              - voters
              - votes
              - blocks
              - pending_votes
              - blockchain_state
```

---

## Implementation Checklist

### Phase 1: Core Blockchain ✓

- [ ] **blockchain.py - Block Class**
  - [ ] Implement `Block.__init__` with all fields
  - [ ] `calculate_hash()` - SHA-256 of block data
  - [ ] `mine_block(difficulty)` - Proof-of-work loop
    - Increment nonce
    - Calculate hash
    - Check leading zeros (difficulty)
    - Return when found
  - [ ] `is_valid(previous_hash)` - Validate PoW + structure
  - [ ] `validate_merkle_root()` - Verify Merkle tree
  - [ ] `get_vote_count()` - Count votes in block
  - [ ] `to_dict()` - Serialization for JSON/storage

- [ ] **blockchain.py - Blockchain Class**
  - [ ] `__init__` - Initialize empty chain
  - [ ] `create_genesis_block()` - Create first block (index 0, prev_hash="0"*64)
  - [ ] `get_latest_block()` - Return last block
  - [ ] `get_block_by_index(index)` - Get specific block
  - [ ] `add_vote(voter_id, candidate, timestamp)` - Add to pending pool
    - Check for duplicates
    - Create Vote object
    - Add to pending_votes list
    - Return success/failure
  - [ ] `verify_vote_format()` - Validate vote data structure
  - [ ] `mine_pending_votes(miner_id)` - Create new block if pending votes exist
    - Create Block with pending votes
    - Mine (find PoW)
    - Add to chain
    - Update voted_voters set
    - Clear pending_votes
    - Return Block or None
  - [ ] `is_vote_duplicate(voter_id)` - Check chain + pending
  - [ ] `is_vote_in_pending(voter_id)` - Check pending pool
  - [ ] `validate_chain()` - Validate entire blockchain
    - Check genesis block
    - Validate each block's PoW
    - Check hash continuity
    - Check vote uniqueness
    - Return (valid, errors)
  - [ ] `validate_block()` - Single block validation (consensus)
  - [ ] `verify_vote_inclusion()` - Find vote in chain + generate proof
  - [ ] `get_merkle_proof()` - Generate Merkle proof for specific vote
  - [ ] `calculate_merkle_root()` - Generate Merkle root from votes
  - [ ] `get_vote_count()` - Tally votes by candidate
  - [ ] `get_all_votes()` - Return all votes in chain
  - [ ] `get_votes_by_block()` - Get votes from specific block
  - [ ] `get_blockchain_stats()` - Comprehensive statistics
  - [ ] `export_blockchain()` - Serialize to dict
  - [ ] `import_blockchain()` - Deserialize from dict

### Phase 2: Cryptography ✓

- [ ] **crypto.py - CryptoManager**
  - [ ] `sha256_hash(data)` - SHA-256 implementation
  - [ ] `generate_voter_id(name, surname, id_number)` - Deterministic hash-based ID
  - [ ] `generate_random_id(length)` - Random token generation
  - [ ] `generate_signature(data, secret_key)` - HMAC-SHA256
  - [ ] `verify_signature(data, signature, secret_key)` - Constant-time compare
  - [ ] `hash_password(password, salt)` - PBKDF2 or similar
  - [ ] `verify_password(password, salted_hash)` - Compare hashes
  - [ ] `generate_voter_token()` - Create signed JWT-like token
  - [ ] `verify_voter_token()` - Validate & check expiry
  - [ ] `create_merkle_root(votes)` - Binary tree hashing
  - [ ] `create_merkle_tree(vote_hashes)` - Full tree structure
  - [ ] `get_merkle_proof()` - Generate proof for vote
  - [ ] `verify_merkle_proof()` - Validate proof
  - [ ] `hash_block_data()` - Block hash calculation
  - [ ] `verify_proof_of_work()` - Check leading zeros
  - [ ] `generate_vote_hash()` - Vote-specific hash
  - [ ] `create_vote_certificate()` - Signed receipt
  - [ ] `verify_vote_certificate()` - Validate receipt
  - [ ] `constant_time_compare()` - Timing attack prevention

### Phase 3: Database ✓

- [ ] **database.py - Dataclasses**
  - [ ] `Voter` dataclass with all fields
  - [ ] `VoteRecord` dataclass
  - [ ] `BlockRecord` dataclass
  - [ ] Implement `to_dict()` methods

- [ ] **database.py - DatabaseConnection**
  - [ ] `__init__` - Store connection parameters
  - [ ] `connect()` - psycopg2 connection
    - Test connection
    - Return (success, message)
  - [ ] `disconnect()` - Close connection
  - [ ] `is_connected()` - Check connection status
  - [ ] `create_tables()` - Execute schema.sql
  - [ ] `drop_tables()` - Clean database

  - **Voter Operations:**
  - [ ] `register_voter()` - INSERT with duplicate check
  - [ ] `get_voter()` - SELECT by voter_id
  - [ ] `check_voter_registered()` - EXISTS query
  - [ ] `check_voter_voted()` - Query has_voted field
  - [ ] `mark_voter_voted()` - UPDATE has_voted=true
  - [ ] `get_all_voters()` - SELECT * from voters
  - [ ] `get_voted_voters()` - Filter by has_voted=true
  - [ ] `get_voter_count()` - COUNT(*)
  - [ ] `get_voted_count()` - COUNT(has_voted=true)

  - **Vote Operations:**
  - [ ] `store_vote_record()` - INSERT vote immutably
  - [ ] `get_vote_records()` - SELECT votes (optional voter filter)
  - [ ] `get_all_votes()` - Get all votes
  - [ ] `get_votes_by_candidate()` - Query by candidate
  - [ ] `get_vote_tally()` - GROUP BY candidate, COUNT(*)
  - [ ] `get_vote_count()` - COUNT(*)
  - [ ] `verify_vote_exists()` - Check vote_hash in DB

  - **Block Operations:**
  - [ ] `store_block_record()` - INSERT block metadata
  - [ ] `get_block_record()` - SELECT by block_index
  - [ ] `get_all_block_records()` - SELECT * blocks
  - [ ] `get_block_count()` - COUNT(*)
  - [ ] `get_latest_block_hash()` - SELECT last block
  - [ ] `get_block_hash_chain()` - All hashes for validation

  - **Pending Votes:**
  - [ ] `add_pending_vote()` - INSERT into pending_votes
  - [ ] `get_pending_votes()` - SELECT unprocessed votes
  - [ ] `get_pending_votes_count()` - COUNT(*)
  - [ ] `clear_pending_votes()` - DELETE after mining

  - **State Management:**
  - [ ] `get_blockchain_state()` - Current state summary
  - [ ] `get_blockchain_stats()` - Comprehensive stats
  - [ ] `begin_transaction()` - START TRANSACTION
  - [ ] `commit_transaction()` - COMMIT
  - [ ] `rollback_transaction()` - ROLLBACK

  - **General:**
  - [ ] `execute_query()` - Raw SQL SELECT
  - [ ] `execute_update()` - Raw SQL INSERT/UPDATE/DELETE
  - [ ] `clear_database()` - Delete all data
  - [ ] `reset_database()` - Reset to initial state
  - [ ] `export_data()` - Serialize to dict
  - [ ] `import_data()` - Deserialize from dict
  - [ ] Context manager (`__enter__`, `__exit__`)

### Phase 4: Network & Communication ✓

- [ ] **server/network.py - NetworkMessage**
  - [ ] `__init__` - Message creation with validation
  - [ ] `_generate_message_id()` - Unique ID generation
  - [ ] `to_dict()` - Convert to dictionary
  - [ ] `to_json()` - Serialize to JSON string
  - [ ] `from_json(json_str)` - Parse JSON to message
  - [ ] `is_valid()` - Basic structure validation
  - [ ] `validate_payload()` - Type-specific validation
  - [ ] `__str__` and `__repr__` - String representations

- [ ] **server/network.py - SocketServer**
  - [ ] `__init__` - Initialize server parameters
  - [ ] `start()` - Create socket, bind, listen
    - socket.socket(AF_INET, SOCK_STREAM)
    - setsockopt for reuse
    - bind(host, port)
    - listen(backlog)
    - Threading for accept_connections()
  - [ ] `stop()` - Graceful shutdown
  - [ ] `is_running()` - Check status
  - [ ] `accept_connections()` - Main loop with threading
  - [ ] `accept_single_connection()` - One connection
  - [ ] `register_handler(msg_type, callable)` - Register handler
  - [ ] `get_handler(msg_type)` - Lookup handler
  - [ ] `handle_client()` - Per-client thread
    - Receive message loop
    - Parse → Validate → Handle
    - Send response
    - Handle disconnect
  - [ ] `handle_message()` - Route to handler
  - [ ] `send_message()` - Send JSON over socket
  - [ ] `receive_message()` - Recv & parse JSON with timeout
  - [ ] `close_client()` - Close socket safely
  - [ ] `get_active_clients_count()` - Count connections
  - [ ] `broadcast_message()` - Send to all clients
  - [ ] `shutdown()` - Cleanup

- [ ] **server/network.py - SocketClient**
  - [ ] `__init__` - Store server address
  - [ ] `connect(retry)` - Connect to server
    - socket.create_connection()
    - Retry logic if enabled
  - [ ] `connect_with_retry()` - Automatic retry
  - [ ] `disconnect()` - Close connection
  - [ ] `send_message()` - Serialize & send
  - [ ] `receive_message()` - Recv & parse with timeout
  - [ ] `send_and_receive()` - Request/response pattern
  - [ ] `is_connected()` - Check status
  - [ ] `close()` - Alias for disconnect
  - [ ] `ping()` - Connectivity check
  - [ ] Context manager support

- [ ] **client/network.py - VotingClientNetwork**
  - [ ] `__init__` - Store server address
  - [ ] `connect()` - Connect & send PING
  - [ ] `disconnect()` - Close connection
  - [ ] `register_voter()` - Send REGISTER message
  - [ ] `submit_vote()` - Send VOTE message
  - [ ] `verify_vote()` - Send VERIFY message
  - [ ] `get_results()` - Send RESULTS message
  - [ ] `get_candidates()` - Send CANDIDATES message
  - [ ] `get_server_status()` - Send STATUS message
  - [ ] `is_connected()` - Check status
  - [ ] `send_request()` - Generic request/response

### Phase 5: Server Application ✓

- [ ] **server.py - VotingServer**
  - [ ] `__init__` - Initialize components
  - [ ] `initialize_components()` - Setup blockchain, DB, network
    - Create Blockchain instance
    - Create DatabaseConnection & connect
    - Create SocketServer
  - [ ] `start_network_server()` - Start in background thread
  - [ ] `register_network_handlers()` - Register all handlers
    - register -> handle_register_voter
    - vote -> handle_vote_submission
    - verify -> handle_verify_vote
    - status -> handle_blockchain_status
    - results -> handle_get_results
  - [ ] `handle_register_voter()` - Process registration
    - Validate input
    - Generate voter_id
    - Store in DB
    - Return voter_id
  - [ ] `handle_vote_submission()` - Process vote
    - Get voter_id, candidate
    - Check already voted
    - Add to blockchain pending
    - Store in pending_votes table
    - Return vote_hash
  - [ ] `handle_verify_vote()` - Verify vote inclusion
    - Search blockchain
    - Generate Merkle proof
    - Return proof + vote details
  - [ ] `handle_get_results()` - Get vote tally
    - Get vote_count from blockchain
    - Format response
  - [ ] `handle_blockchain_status()` - Get stats
  - [ ] `mine_block()` - Trigger mining
    - Call blockchain.mine_pending_votes()
    - Store block in DB
    - Update blockchain_state
  - [ ] `validate_vote()` - Pre-submission validation
  - [ ] `shutdown()` - Graceful shutdown

  - **CLI Methods:**
  - [ ] `run_cli()` - Main CLI loop
  - [ ] `display_menu()` - Show commands
  - [ ] `cmd_status()` - Show status
  - [ ] `cmd_mine()` - Mine block
  - [ ] `cmd_view_votes()` - List all votes
  - [ ] `cmd_view_results()` - Show tally
  - [ ] `cmd_voter_info()` - List voters
  - [ ] `cmd_blockchain_info()` - Blockchain details
  - [ ] `cmd_verify_integrity()` - Validate chain
  - [ ] `cmd_help()` - Show help
  - [ ] `main()` - Entry point, load config, run server

### Phase 6: Client Application ✓

- [ ] **client.py - VotingClient**
  - [ ] `__init__` - Initialize client
  - [ ] `connect_to_server()` - Establish connection
  - [ ] `disconnect_from_server()` - Close connection
  - [ ] `is_connected()` - Check status
  - [ ] `run_cli()` - Main CLI loop
  - [ ] `display_main_menu()` - Show options
  - [ ] `menu_register_voter()` - Registration flow
    - Get name, surname, id_number
    - Send REGISTER
    - Store voter_id locally
    - Show success or error
  - [ ] `menu_submit_vote()` - Voting flow
    - Check registered
    - Get candidate choice
    - Send VOTE
    - Show receipt
  - [ ] `menu_verify_vote()` - Verification flow
    - Send VERIFY
    - Show result (found/not found)
  - [ ] `menu_view_results()` - Display tally
  - [ ] `menu_view_candidates()` - List candidates
  - [ ] `menu_server_info()` - Server status
  - [ ] `menu_my_info()` - Show stored voter info
  - [ ] `menu_help()` - Show help
  - [ ] Input getters: `get_voter_name()`, etc.
  - [ ] `display_candidates()` - Format candidate list
  - [ ] `display_results()` - Format tally
  - [ ] `save_voter_info()` - Local storage (file or memory)
  - [ ] `load_voter_info()` - Load from storage
  - [ ] `handle_server_error()` - Error display
  - [ ] `main()` - Entry point, connect, run CLI

### Phase 7: Support Modules ✓

- [ ] **config.py - ConfigLoader**
  - [ ] `__init__` - Store config path
  - [ ] `load()` - Load file + env
  - [ ] `load_from_file()` - Parse JSON
  - [ ] `load_from_env()` - Read ENV vars
  - [ ] `merge_configs()` - Overlay env on file
  - [ ] `validate_config()` - Check required fields
  - [ ] `get_default_config()` - Return defaults (done)
  - [ ] `get_*_config()` - Extract sections

- [ ] **logger.py - Logging Setup**
  - [ ] `setup_logging()` - Configure logger with handlers
  - [ ] `get_logger()` - Get named logger
  - [ ] `configure_root_logger()` - Root configuration
  - [ ] `create_log_directory()` - mkdir logs/
  - [ ] `get_log_filename()` - Generate timestamped name
  - [ ] **LoggerFactory class**
    - [ ] `configure()` - Set up factory
    - [ ] `get_logger()` - Get or create logger
    - [ ] `close_all()` - Close all handlers

- [ ] **exceptions.py - Exception Hierarchy** ✓ (structure done)
  - All exception classes defined

- [ ] **utils.py - Utility Functions** ✓ (stubs done)
  - All function stubs defined

- [ ] **constants.py - Constants** ✓ (done)
  - All constants defined

### Phase 8: Database & Infrastructure ✓

- [ ] **schema.sql - Database Schema** ✓
  - Tables created
  - Indexes defined
  - Migrations defined

- [ ] **requirements.txt** ✓
  - Dependencies specified

- [ ] **Dockerfile** ✓
  - Container image defined

- [ ] **docker-compose.yml** ✓
  - PostgreSQL service
  - Voting server service
  - Networking & volumes

- [ ] **.env.example** ✓
  - Environment template

### Phase 9: Testing

- [ ] **tests/test_blockchain.py**
  - Block creation & hashing
  - Mining & validation
  - Blockchain consensus
  - Vote tracking & uniqueness
  - Merkle tree operations

- [ ] **tests/test_database.py**
  - Connection management
  - Table creation
  - CRUD operations
  - Vote uniqueness constraints
  - State management

- [ ] **tests/test_crypto.py**
  - SHA-256 hashing
  - Signature generation & verification
  - Token management
  - Merkle proofs
  - Password hashing

- [ ] **tests/test_integration.py**
  - End-to-end voting flow
  - Duplicate prevention
  - Vote immutability
  - Network communication
  - Concurrent operations

### Phase 10: Documentation & Delivery

- [ ] **README.md** ✓
  - Project overview
  - Quick start guide
  - Commands & usage
  - Architecture diagram
  - Troubleshooting

- [ ] **PROJECT_STRUCTURE.md** ✓
  - Detailed structure
  - Module descriptions
  - Database schema
  - Implementation checklist

- [ ] **IMPLEMENTATION.md** ✓
  - This file
  - Implementation details
  - Database design
  - Network protocol
  - Testing plan

- [ ] **PDF Report (IMRaD)**
  - Introduction: Blockchain voting systems
  - Methods: Design, tools, architecture
  - Results: Implementation, testing
  - Discussion: Achievements, challenges
  - Architecture diagrams
  - Performance metrics

- [ ] **Demo Video (1-2 min)**
  - Server startup
  - Client registration
  - Vote submission
  - Vote verification
  - Results display

---

## Key Design Decisions

### 1. **Centralized Node Architecture**
- Single server manages all blockchain operations
- Simpler than peer-to-peer (Variant B)
- Suitable for organizational voting scenarios
- Database provides backup & recovery

### 2. **Proof-of-Work Consensus**
- Difficulty configurable (default 4 = 16 bits leading zeros)
- Mining verifies block validity
- Chain validation requires full computational cost
- Prevents tampering (must re-mine entire chain)

### 3. **Vote Immutability**
- Votes stored in database with constraints
- Primary key on (voter_id, block_index)
- No UPDATE/DELETE on votes
- Only INSERT allowed
- Database transaction ensures atomicity

### 4. **Double-Voting Prevention**
- In-memory voted_voters set in Blockchain
- Database has_voted flag on Voter
- Pending votes checked before acceptance
- Multiple validation layers ensure safety

### 5. **Anonymous Verification**
- Merkle proofs allow proof of inclusion without identity
- Voter provides voter_id + vote_hash
- System generates mathematical proof
- Third party can verify without revealing voter
- Perfect for ballot secrecy + transparency balance

### 6. **JSON Socket Protocol**
- Clean, human-readable message format
- version, type, timestamp, message_id fields
- payload contains operation-specific data
- Easy to extend with new message types
- Compatible with any JSON parser

### 7. **PostgreSQL Persistence**
- ACID guarantees for transaction safety
- Indexes on frequently queried columns
- Partial redundancy with blockchain state table
- Atomic operations for vote recording
- Backup/recovery capabilities

---

## Database Design Details

### Schema Relationships

```
voters (1) ──────── (M) votes
  ↑                    ↑
  │                    └──────── blocks (1)
  │
  └─────────────────────────────── pending_votes
```

### Key Constraints

**Unique Constraints:**
- `voters(voter_id)` - One voter record
- `voters(id_number)` - No duplicate registrations
- `votes(vote_hash)` - No duplicate votes
- `blocks(block_hash)` - Block uniqueness
- `votes(voter_id, block_index)` - One vote per voter per block

**Foreign Keys:**
- `votes.voter_id → voters.voter_id`
- `votes.block_index → blocks.block_index`

### Indexes for Performance

```sql
-- Voter lookups
CREATE INDEX idx_voters_id_number ON voters(id_number)

-- Vote queries
CREATE INDEX idx_votes_voter_id ON votes(voter_id)
CREATE INDEX idx_votes_candidate ON votes(candidate)
CREATE INDEX idx_votes_hash ON votes(vote_hash)
CREATE INDEX idx_votes_timestamp ON votes(timestamp)

-- Block integrity
CREATE INDEX idx_blocks_hash ON blocks(block_hash)
CREATE INDEX idx_blocks_previous_hash ON blocks(previous_hash)
```

---

## Testing Strategy

### Unit Tests (test_blockchain.py, test_crypto.py, etc.)
- Individual function/method testing
- Isolated from other components
- Mock external dependencies
- Fast execution

### Integration Tests (test_integration.py)
- Multiple components working together
- End-to-end voting flows
- Database persistence
- Network communication
- Concurrent operations

### Acceptance Criteria (from Project 24)

✅ **Vote Logging:**
- [ ] All votes logged with timestamp
- [ ] Cryptographic hash tracked
- [ ] Voter ID associated
- [ ] Immutable records

✅ **Vote Uniqueness:**
- [ ] Each voter appears once
- [ ] No duplicates possible
- [ ] Database constraints enforced
- [ ] Blockchain validation confirms

✅ **Vote Verification:**
- [ ] Merkle proof generation works
- [ ] Voters can verify offline
- [ ] Anonymous verification supported
- [ ] True vote inclusion proven

✅ **Consensus Testing:**
- [ ] Proof-of-work validates
- [ ] Block structure correct
- [ ] Chain integrity maintained
- [ ] Tampered blocks detected

---

## Implementation Order (Recommended)

1. **Start with Blockchain** (foundation)
   - Block class first
   - Then Blockchain class
   - Test locally before DB integration

2. **Implement Cryptography** (security)
   - Hashing functions
   - Merkle trees
   - Signatures & tokens

3. **Setup Database** (persistence)
   - Schema creation
   - Connection management
   - CRUD operations

4. **Create Network Layer** (communication)
   - Network message protocol
   - Socket server basics
   - Socket client

5. **Build Server Application** (main logic)
   - Integration of all components
   - Message handlers
   - CLI interface

6. **Build Client Application** (user interface)
   - Network communication
   - User input handling
  - CLI menus

7. **Write Tests** (quality assurance)
   - Unit tests
   - Integration tests
   - Acceptance testing

8. **Documentation & Demo** (delivery)
   - README setup
   - PDF report
   - Demo video

---

## Common Implementation Pitfalls to Avoid

❌ **Don't:**
- Assume votes are immutable without constraints
- Forget to check for duplicates in pending pool
- Use synchronous mining (server will block)
- Forget socket timeout handling
- Skip database transaction management
- Store sensitive data in logs
- Assume network is always reliable

✅ **Do:**
- Use database constraints + application validation
- Check both blockchain + pending votes
- Consider async/threading for mining
- Always handle timeouts and reconnects
- Use transactions for atomic operations
- Log operations, not sensitive data
- Implement retry logic with exponential backoff

---

## Performance Optimization Tips

1. **Database Indexes** - Already defined in schema.sql
2. **Connection Pooling** - Consider psycopg2 pool for production
3. **Blockchain Caching** - Cache chain in memory, persist to DB
4. **Merkle Tree Caching** - Store computed paths
5. **Batch Operations** - Insert multiple votes in single transaction
6. **Async Mining** - Don't block on PoW computation
7. **Message Compression** - For large merkle proofs

---

## Security Considerations

1. **Input Validation** - Sanitize all client input
2. **SQL Injection** - Use parameterized queries (done)
3. **Timing Attacks** - Use constant-time comparison
4. **Vote Privacy** - No plaintext passwords, use Merkle proofs
5. **Network Security** - Add TLS for production
6. **Database Backup** - Regular snapshots
7. **Access Control** - Implement if multi-user needed

---

## Deliverable Checklist

- [ ] All code complete and tested
- [ ] README.md with full documentation
- [ ] config.json example file
- [ ] Docker setup working
- [ ] Database schema in SQL file
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Server CLI fully functional
- [ ] Client CLI fully functional
- [ ] Vote verification working
- [ ] Merkle proofs implemented
- [ ] PDF report (IMRaD format)
  - [ ] Introduction
  - [ ] Methods (design + architecture)
  - [ ] Results (implementation)
  - [ ] Discussion (challenges)
  - [ ] Architecture diagrams
- [ ] Demo video (1-2 minutes)
  - [ ] Server startup
  - [ ] Client operations
  - [ ] Vote verification

---

## Resources & References

- SHA-256 Hashing: https://docs.python.org/3/library/hashlib.html
- HMAC: https://docs.python.org/3/library/hmac.html
- Socket Programming: https://docs.python.org/3/library/socket.html
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Bitcoin Proof-of-Work: https://en.wikipedia.org/wiki/Proof_of_work
- Merkle Trees: https://en.wikipedia.org/wiki/Merkle_tree
