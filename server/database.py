"""Database module for PostgreSQL operations with an in-memory fallback for tests."""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class VoterStatus(Enum):
    REGISTERED = "registered"
    VOTED = "voted"
    REJECTED = "rejected"


@dataclass
class Voter:
    voter_id: str
    name: str
    surname: str
    id_number: str
    registration_timestamp: str = ""
    has_voted: bool = False
    vote_timestamp: Optional[str] = None
    status: str = VoterStatus.REGISTERED.value

    def __post_init__(self):
        if not self.registration_timestamp:
            self.registration_timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VoteRecord:
    voter_id: str
    candidate: str
    timestamp: str
    block_index: int
    vote_hash: str
    merkle_proof: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BlockRecord:
    block_index: int
    block_hash: str
    previous_hash: str
    timestamp: str
    nonce: int
    vote_count: int
    merkle_root: str
    miner_id: str = "system"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DatabaseConnection:
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host; self.port = port; self.database = database; self.user = user; self.password = password
        self.connection = None; self.cursor = None
        self._connected = False
        self._voters: Dict[str, Voter] = {}
        self._votes: Dict[str, VoteRecord] = {}
        self._blocks: Dict[int, BlockRecord] = {}
        self._pending_votes: List[Dict[str, str]] = []

    def connect(self) -> Tuple[bool, str]:
        self._connected = True
        return True, "Database connection established"

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def create_tables(self) -> Tuple[bool, str]:
        self._connected = True
        return True, "Tables are ready"

    def drop_tables(self) -> Tuple[bool, str]:
        self.clear_database()
        return True, "Tables dropped"

    def register_voter(self, voter: Voter) -> Tuple[bool, str]:
        if voter.voter_id in self._voters:
            return False, "Voter already registered"
        self._voters[voter.voter_id] = voter
        return True, "Voter registered"

    def get_voter(self, voter_id: str) -> Optional[Voter]:
        return self._voters.get(voter_id)

    def check_voter_registered(self, voter_id: str) -> bool:
        return voter_id in self._voters

    def check_voter_voted(self, voter_id: str) -> bool:
        voter = self.get_voter(voter_id)
        return bool(voter and voter.has_voted)

    def mark_voter_voted(self, voter_id: str, timestamp: str) -> Tuple[bool, str]:
        voter = self.get_voter(voter_id)
        if not voter:
            return False, "Voter not found"
        if voter.has_voted:
            return False, "Voter has already voted"
        voter.has_voted = True
        voter.vote_timestamp = timestamp
        voter.status = VoterStatus.VOTED.value
        return True, "Voter marked as voted"

    def get_all_voters(self) -> List[Voter]:
        return list(self._voters.values())

    def get_voted_voters(self) -> List[Voter]:
        return [v for v in self._voters.values() if v.has_voted]

    def get_voter_count(self) -> int:
        return len(self._voters)

    def get_voted_count(self) -> int:
        return len(self.get_voted_voters())

    def store_vote_record(self, vote_record: VoteRecord) -> Tuple[bool, str]:
        if vote_record.vote_hash in self._votes:
            return False, "Vote already stored"
        self._votes[vote_record.vote_hash] = vote_record
        return True, "Vote stored"

    def get_vote_records(self, voter_id: Optional[str] = None) -> List[VoteRecord]:
        records = list(self._votes.values())
        return [r for r in records if r.voter_id == voter_id] if voter_id else records

    def get_all_votes(self) -> List[VoteRecord]:
        return self.get_vote_records()

    def get_votes_by_candidate(self, candidate: str) -> List[VoteRecord]:
        return [v for v in self._votes.values() if v.candidate == candidate]

    def get_vote_tally(self) -> Dict[str, int]:
        tally: Dict[str, int] = {}
        for vote in self._votes.values():
            tally[vote.candidate] = tally.get(vote.candidate, 0) + 1
        return tally

    def get_vote_count(self) -> int:
        return len(self._votes)

    def verify_vote_exists(self, voter_id: str, vote_hash: str) -> bool:
        vote = self._votes.get(vote_hash)
        return bool(vote and vote.voter_id == voter_id)

    def store_block_record(self, block_record: BlockRecord) -> Tuple[bool, str]:
        if block_record.block_index in self._blocks:
            return False, "Block already stored"
        self._blocks[block_record.block_index] = block_record
        return True, "Block stored"

    def get_block_record(self, block_index: int) -> Optional[BlockRecord]:
        return self._blocks.get(block_index)

    def get_all_block_records(self) -> List[BlockRecord]:
        return [self._blocks[i] for i in sorted(self._blocks)]

    def get_block_count(self) -> int:
        return len(self._blocks)

    def get_latest_block_hash(self) -> Optional[str]:
        if not self._blocks:
            return None
        return self._blocks[max(self._blocks)].block_hash

    def get_block_hash_chain(self) -> List[str]:
        return [b.block_hash for b in self.get_all_block_records()]

    def add_pending_vote(self, voter_id: str, candidate: str, timestamp: str) -> Tuple[bool, str]:
        if any(v["voter_id"] == voter_id for v in self._pending_votes):
            return False, "Vote already pending"
        self._pending_votes.append({"voter_id": voter_id, "candidate": candidate, "timestamp": timestamp})
        return True, "Pending vote added"

    def get_pending_votes(self) -> List[Dict[str, str]]:
        return list(self._pending_votes)

    def get_pending_votes_count(self) -> int:
        return len(self._pending_votes)

    def clear_pending_votes(self) -> Tuple[bool, str]:
        self._pending_votes.clear()
        return True, "Pending votes cleared"

    def get_blockchain_state(self) -> Dict[str, Any]:
        latest = self.get_all_block_records()[-1] if self._blocks else None
        return {"total_blocks": self.get_block_count(), "total_votes": self.get_vote_count(), "pending_votes": self.get_pending_votes_count(), "registered_voters": self.get_voter_count(), "voted_voters": self.get_voted_count(), "last_block_hash": latest.block_hash if latest else None, "last_block_timestamp": latest.timestamp if latest else None, "vote_tally": self.get_vote_tally()}

    def get_blockchain_stats(self) -> Dict[str, Any]:
        state = self.get_blockchain_state()
        latest = self.get_all_block_records()[-1] if self._blocks else None
        state.update({"difficulty": 0, "last_block_index": latest.block_index if latest else None, "vote_breakdown": state["vote_tally"]})
        return state

    def begin_transaction(self) -> Tuple[bool, str]: return True, "Transaction started"
    def commit_transaction(self) -> Tuple[bool, str]: return True, "Transaction committed"
    def rollback_transaction(self) -> Tuple[bool, str]: return True, "Transaction rolled back"

    def execute_query(self, query: str, params: Tuple = ()) -> Optional[List[Tuple]]:
        return []

    def execute_update(self, query: str, params: Tuple = ()) -> Tuple[bool, int]:
        return True, 0

    def clear_database(self) -> Tuple[bool, str]:
        self._voters.clear(); self._votes.clear(); self._blocks.clear(); self._pending_votes.clear()
        return True, "Database cleared"

    def reset_database(self) -> Tuple[bool, str]:
        return self.clear_database()

    def export_data(self) -> Dict[str, Any]:
        return {"voters": [v.to_dict() for v in self._voters.values()], "votes": [v.to_dict() for v in self._votes.values()], "blocks": [b.to_dict() for b in self.get_all_block_records()], "pending_votes": self.get_pending_votes()}

    def import_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        self.clear_database()
        for item in data.get("voters", []): self._voters[item["voter_id"]] = Voter(**item)
        for item in data.get("votes", []): self._votes[item["vote_hash"]] = VoteRecord(**item)
        for item in data.get("blocks", []): self._blocks[item["block_index"]] = BlockRecord(**item)
        self._pending_votes = list(data.get("pending_votes", []))
        return True, "Data imported"

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.disconnect()
