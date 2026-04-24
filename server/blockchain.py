"""
Enhanced blockchain module with consensus mechanism.
Implements immutable ledger for voting records with proof-of-work consensus.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from enum import Enum

try:
    from server.crypto import CryptoManager
except ImportError:
    from crypto import CryptoManager


class BlockStatus(Enum):
    """Block validation status."""
    PENDING = "pending"
    VALIDATED = "validated"
    FINALIZED = "finalized"
    REJECTED = "rejected"


@dataclass
class Vote:
    """Represents a single vote."""
    voter_id: str
    candidate: str
    timestamp: str
    vote_hash: str = ""

    def __post_init__(self) -> None:
        if not self.vote_hash:
            self.vote_hash = self.calculate_hash()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "voter_id": self.voter_id,
            "candidate": self.candidate,
            "timestamp": self.timestamp,
            "vote_hash": self.vote_hash,
        }

    def calculate_hash(self) -> str:
        return CryptoManager.generate_vote_hash(self.voter_id, self.candidate, self.timestamp)


@dataclass
class Block:
    """Represents a single block in the blockchain."""
    index: int
    timestamp: str
    votes: List[Vote] = field(default_factory=list)
    previous_hash: str = ""
    nonce: int = 0
    hash: str = ""
    merkle_root: str = ""
    miner_id: str = ""
    status: BlockStatus = BlockStatus.PENDING

    def __post_init__(self) -> None:
        if not self.merkle_root:
            self.merkle_root = CryptoManager.create_merkle_root([vote.vote_hash for vote in self.votes])
        if not self.hash:
            self.hash = self.calculate_hash()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "votes": [vote.to_dict() for vote in self.votes],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "merkle_root": self.merkle_root,
            "miner_id": self.miner_id,
            "status": self.status.value if isinstance(self.status, BlockStatus) else self.status,
        }

    def calculate_hash(self) -> str:
        return CryptoManager.hash_block_data(
            self.index,
            self.timestamp,
            [vote.to_dict() for vote in self.votes],
            self.previous_hash,
            self.nonce,
        )

    def mine_block(self, difficulty: int) -> Tuple[str, int]:
        target = "0" * difficulty
        self.merkle_root = CryptoManager.create_merkle_root([vote.vote_hash for vote in self.votes])
        self.hash = self.calculate_hash()
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
        self.status = BlockStatus.VALIDATED
        return self.hash, self.nonce

    def is_valid(self, previous_hash: str) -> bool:
        if self.previous_hash != previous_hash:
            return False
        if self.hash != self.calculate_hash():
            return False
        if not self.validate_merkle_root():
            return False
        voter_ids = [vote.voter_id for vote in self.votes]
        return len(voter_ids) == len(set(voter_ids))

    def validate_merkle_root(self) -> bool:
        expected = CryptoManager.create_merkle_root([vote.vote_hash for vote in self.votes])
        return expected == self.merkle_root

    def get_vote_count(self) -> int:
        return len(self.votes)


class Blockchain:
    """Manages the blockchain for vote recording."""

    def __init__(self, difficulty: int = 4, block_size: int = 100):
        self.chain: List[Block] = []
        self.pending_votes: List[Vote] = []
        self.difficulty = difficulty
        self.block_size = block_size
        self.mining_reward = 1
        self.voted_voters: set = set()
        self.chain_lock = None
        self.chain.append(self.create_genesis_block())

    def create_genesis_block(self) -> Block:
        block = Block(
            index=0,
            timestamp=datetime.utcnow().isoformat(),
            votes=[],
            previous_hash="0" * 64,
            miner_id="system",
            status=BlockStatus.FINALIZED,
        )
        block.mine_block(self.difficulty)
        block.status = BlockStatus.FINALIZED
        return block

    def get_latest_block(self) -> Optional[Block]:
        return self.chain[-1] if self.chain else None

    def get_block_by_index(self, index: int) -> Optional[Block]:
        for block in self.chain:
            if block.index == index:
                return block
        return None

    def add_vote(self, voter_id: str, candidate: str, timestamp: str) -> Tuple[bool, str]:
        valid, message = self.verify_vote_format(voter_id, candidate)
        if not valid:
            return False, message
        if self.is_vote_duplicate(voter_id) or self.is_vote_in_pending(voter_id):
            return False, "Voter has already voted"
        vote = Vote(voter_id=voter_id, candidate=candidate, timestamp=timestamp)
        self.pending_votes.append(vote)
        return True, vote.vote_hash

    def verify_vote_format(self, voter_id: str, candidate: str) -> Tuple[bool, str]:
        if not voter_id or not str(voter_id).strip():
            return False, "Voter ID is required"
        if not candidate or not str(candidate).strip():
            return False, "Candidate is required"
        if len(str(voter_id).strip()) > 128:
            return False, "Voter ID is too long"
        if len(str(candidate).strip()) > 255:
            return False, "Candidate name is too long"
        return True, "Vote format is valid"

    def mine_pending_votes(self, miner_id: str = "system") -> Optional[Block]:
        if not self.pending_votes:
            return None
        latest = self.get_latest_block()
        block_votes = self.pending_votes[: self.block_size]
        block = Block(
            index=len(self.chain),
            timestamp=datetime.utcnow().isoformat(),
            votes=block_votes,
            previous_hash=latest.hash if latest else "0" * 64,
            miner_id=miner_id,
        )
        block.mine_block(self.difficulty)
        ok, _ = self.validate_block(block, latest)
        if not ok:
            block.status = BlockStatus.REJECTED
            return None
        block.status = BlockStatus.FINALIZED
        self.chain.append(block)
        for vote in block_votes:
            self.voted_voters.add(vote.voter_id)
        self.pending_votes = self.pending_votes[len(block_votes):]
        return block

    def calculate_merkle_root(self, votes: List[Vote]) -> str:
        return CryptoManager.create_merkle_root([vote.vote_hash for vote in votes])

    def validate_chain(self) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not self.chain:
            return False, ["Blockchain is empty"]
        seen_voters = set()
        for index, block in enumerate(self.chain):
            previous = None if index == 0 else self.chain[index - 1]
            valid, message = self.validate_block(block, previous)
            if not valid:
                errors.append(f"Block {block.index}: {message}")
            for vote in block.votes:
                if vote.voter_id in seen_voters:
                    errors.append(f"Duplicate vote by voter {vote.voter_id}")
                seen_voters.add(vote.voter_id)
        return len(errors) == 0, errors

    def validate_block(self, block: Block, previous_block: Optional[Block] = None) -> Tuple[bool, str]:
        expected_previous = "0" * 64 if previous_block is None else previous_block.hash
        if block.previous_hash != expected_previous:
            return False, "Invalid previous hash"
        if block.hash != block.calculate_hash():
            return False, "Invalid block hash"
        if not CryptoManager.verify_proof_of_work(block.hash, self.difficulty):
            return False, "Invalid proof of work"
        if not block.validate_merkle_root():
            return False, "Invalid Merkle root"
        ids = [vote.voter_id for vote in block.votes]
        if len(ids) != len(set(ids)):
            return False, "Duplicate votes inside block"
        if previous_block is not None:
            prior_ids = {vote.voter_id for chain_block in self.chain[:block.index] for vote in chain_block.votes}
            if any(voter_id in prior_ids for voter_id in ids):
                return False, "Vote already exists in previous blocks"
        return True, "Block is valid"

    def is_vote_duplicate(self, voter_id: str) -> bool:
        return any(vote.voter_id == voter_id for block in self.chain for vote in block.votes)

    def is_vote_in_pending(self, voter_id: str) -> bool:
        return any(vote.voter_id == voter_id for vote in self.pending_votes)

    def verify_vote_inclusion(self, voter_id: str) -> Optional[Dict[str, Any]]:
        for block in self.chain:
            for idx, vote in enumerate(block.votes):
                if vote.voter_id == voter_id:
                    return {
                        "found": True,
                        "block_index": block.index,
                        "vote_hash": vote.vote_hash,
                        "timestamp": vote.timestamp,
                        "candidate": vote.candidate,
                        "merkle_proof": self.get_merkle_proof(block.index, idx),
                    }
        return None

    def get_merkle_proof(self, block_index: int, vote_index: int) -> Optional[List[str]]:
        block = self.get_block_by_index(block_index)
        if not block:
            return None
        proof = CryptoManager.get_merkle_proof([vote.vote_hash for vote in block.votes], vote_index)
        if proof is None:
            return None
        return [f"{direction}:{hash_value}" for hash_value, direction in proof]

    def get_vote_count(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for vote in self.get_all_votes():
            counts[vote.candidate] = counts.get(vote.candidate, 0) + 1
        return counts

    def get_vote_count_by_block(self, block_index: int) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for vote in self.get_votes_by_block(block_index):
            counts[vote.candidate] = counts.get(vote.candidate, 0) + 1
        return counts

    def get_all_votes(self) -> List[Vote]:
        return [vote for block in self.chain for vote in block.votes]

    def get_votes_by_block(self, block_index: int) -> List[Vote]:
        block = self.get_block_by_index(block_index)
        return list(block.votes) if block else []

    def get_block_count(self) -> int:
        return len(self.chain)

    def get_total_votes(self) -> int:
        return len(self.get_all_votes())

    def get_pending_votes_count(self) -> int:
        return len(self.pending_votes)

    def get_blockchain_stats(self) -> Dict[str, Any]:
        return {
            "total_blocks": self.get_block_count(),
            "total_votes": self.get_total_votes(),
            "pending_votes": self.get_pending_votes_count(),
            "difficulty": self.difficulty,
            "block_size": self.block_size,
            "voted_voters_count": len(self.voted_voters),
            "vote_breakdown": self.get_vote_count(),
        }

    def export_blockchain(self) -> Dict[str, Any]:
        return {
            "difficulty": self.difficulty,
            "block_size": self.block_size,
            "chain": [block.to_dict() for block in self.chain],
            "pending_votes": [vote.to_dict() for vote in self.pending_votes],
            "voted_voters": list(self.voted_voters),
        }

    def import_blockchain(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        try:
            self.difficulty = int(data.get("difficulty", self.difficulty))
            self.block_size = int(data.get("block_size", self.block_size))
            self.chain = []
            for block_data in data.get("chain", []):
                votes = [Vote(**vote_data) for vote_data in block_data.get("votes", [])]
                status_value = block_data.get("status", BlockStatus.PENDING.value)
                block = Block(
                    index=block_data["index"],
                    timestamp=block_data["timestamp"],
                    votes=votes,
                    previous_hash=block_data.get("previous_hash", ""),
                    nonce=block_data.get("nonce", 0),
                    hash=block_data.get("hash", ""),
                    merkle_root=block_data.get("merkle_root", ""),
                    miner_id=block_data.get("miner_id", ""),
                    status=BlockStatus(status_value) if status_value in BlockStatus._value2member_map_ else BlockStatus.PENDING,
                )
                self.chain.append(block)
            self.pending_votes = [Vote(**vote_data) for vote_data in data.get("pending_votes", [])]
            self.voted_voters = set(data.get("voted_voters", []))
            if not self.chain:
                self.chain.append(self.create_genesis_block())
            valid, errors = self.validate_chain()
            return (True, "Blockchain imported") if valid else (False, "; ".join(errors))
        except Exception as exc:
            return False, f"Import failed: {exc}"

    def clear_pending_votes(self) -> None:
        self.pending_votes.clear()

    def reset_blockchain(self) -> None:
        self.chain = [self.create_genesis_block()]
        self.pending_votes = []
        self.voted_voters = set()
