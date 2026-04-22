"""
Database schema creation and migration.
PostgreSQL tables for voters, votes, blocks, and pending votes.
"""

CREATE_VOTERS_TABLE = """
CREATE TABLE IF NOT EXISTS voters (
    voter_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    id_number VARCHAR(255) NOT NULL UNIQUE,
    registration_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    has_voted BOOLEAN NOT NULL DEFAULT FALSE,
    vote_timestamp TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'registered',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_voters_id_number ON voters(id_number);
CREATE INDEX IF NOT EXISTS idx_voters_has_voted ON voters(has_voted);
"""

CREATE_VOTES_TABLE = """
CREATE TABLE IF NOT EXISTS votes (
    vote_id SERIAL PRIMARY KEY,
    voter_id VARCHAR(255) NOT NULL REFERENCES voters(voter_id),
    candidate VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    block_index INTEGER,
    vote_hash VARCHAR(64) NOT NULL UNIQUE,
    merkle_proof TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_voter_per_block UNIQUE (voter_id, block_index)
);

CREATE INDEX IF NOT EXISTS idx_votes_voter_id ON votes(voter_id);
CREATE INDEX IF NOT EXISTS idx_votes_candidate ON votes(candidate);
CREATE INDEX IF NOT EXISTS idx_votes_block_index ON votes(block_index);
CREATE INDEX IF NOT EXISTS idx_votes_timestamp ON votes(timestamp);
CREATE INDEX IF NOT EXISTS idx_votes_vote_hash ON votes(vote_hash);
"""

CREATE_BLOCKS_TABLE = """
CREATE TABLE IF NOT EXISTS blocks (
    block_index INTEGER PRIMARY KEY,
    block_hash VARCHAR(64) NOT NULL UNIQUE,
    previous_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    nonce INTEGER NOT NULL,
    vote_count INTEGER NOT NULL DEFAULT 0,
    merkle_root VARCHAR(64),
    miner_id VARCHAR(255) DEFAULT 'system',
    difficulty_level INTEGER NOT NULL DEFAULT 4,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_blocks_hash ON blocks(block_hash);
CREATE INDEX IF NOT EXISTS idx_blocks_previous_hash ON blocks(previous_hash);
CREATE INDEX IF NOT EXISTS idx_blocks_timestamp ON blocks(timestamp);
"""

CREATE_PENDING_VOTES_TABLE = """
CREATE TABLE IF NOT EXISTS pending_votes (
    pending_vote_id SERIAL PRIMARY KEY,
    voter_id VARCHAR(255) NOT NULL,
    candidate VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    received_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pending_votes_voter_id ON pending_votes(voter_id);
CREATE INDEX IF NOT EXISTS idx_pending_votes_received_at ON pending_votes(received_at);
"""

CREATE_BLOCKCHAIN_STATE_TABLE = """
CREATE TABLE IF NOT EXISTS blockchain_state (
    state_id SERIAL PRIMARY KEY,
    last_block_index INTEGER DEFAULT 0,
    last_block_hash VARCHAR(64),
    total_votes INTEGER DEFAULT 0,
    total_voters_registered INTEGER DEFAULT 0,
    total_voters_voted INTEGER DEFAULT 0,
    difficulty_level INTEGER DEFAULT 4,
    is_valid BOOLEAN DEFAULT TRUE,
    last_validation_timestamp TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_blockchain_state_last_block_index ON blockchain_state(last_block_index);
"""

# Migration scripts
INIT_BLOCKCHAIN_STATE = """
INSERT INTO blockchain_state (
    last_block_index, total_votes, total_voters_registered, total_voters_voted, difficulty_level
) VALUES (
    -1, 0, 0, 0, 4
) ON CONFLICT (state_id) DO UPDATE SET
    updated_at = CURRENT_TIMESTAMP;
"""

DROP_ALL_TABLES = """
DROP TABLE IF EXISTS pending_votes CASCADE;
DROP TABLE IF EXISTS votes CASCADE;
DROP TABLE IF EXISTS blocks CASCADE;
DROP TABLE IF EXISTS blockchain_state CASCADE;
DROP TABLE IF EXISTS voters CASCADE;
"""
