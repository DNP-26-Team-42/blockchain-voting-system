"""
Cryptography module for hashing, signatures, and key management.
"""

from typing import Tuple, Optional, List
import hashlib
import hmac
import json
from datetime import datetime, timedelta
import secrets
import base64


class CryptoManager:
    """Handles all cryptographic operations for the voting system."""

    @staticmethod
    def sha256_hash(data: str) -> str:
        return hashlib.sha256(str(data).encode("utf-8")).hexdigest()

    @staticmethod
    def generate_voter_id(name: str, surname: str, id_number: str) -> str:
        normalized = f"{name.strip().lower()}|{surname.strip().lower()}|{id_number.strip().upper()}"
        return CryptoManager.sha256_hash(normalized)

    @staticmethod
    def generate_random_id(length: int = 32) -> str:
        if length <= 0:
            return ""
        return secrets.token_hex((length + 1) // 2)[:length]

    @staticmethod
    def generate_signature(data: str, secret_key: str) -> str:
        return hmac.new(secret_key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).hexdigest()

    @staticmethod
    def verify_signature(data: str, signature: str, secret_key: str) -> bool:
        expected = CryptoManager.generate_signature(data, secret_key)
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def hash_password(password: str, salt: str = "") -> str:
        salt = salt or secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
        return f"{salt}${digest}"

    @staticmethod
    def verify_password(password: str, salted_hash: str) -> bool:
        try:
            salt, expected = salted_hash.split("$", 1)
        except ValueError:
            return False
        actual = CryptoManager.hash_password(password, salt).split("$", 1)[1]
        return hmac.compare_digest(actual, expected)

    @staticmethod
    def generate_voter_token(voter_id: str, secret_key: str = "", expiry_hours: int = 24) -> str:
        secret_key = secret_key or "development-secret"
        payload = {
            "voter_id": voter_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=expiry_hours)).isoformat(),
            "nonce": CryptoManager.generate_random_id(16),
        }
        raw = base64.urlsafe_b64encode(json.dumps(payload, sort_keys=True).encode()).decode()
        return f"{raw}.{CryptoManager.generate_signature(raw, secret_key)}"

    @staticmethod
    def verify_voter_token(token: str, voter_id: str, secret_key: str = "") -> Tuple[bool, str]:
        secret_key = secret_key or "development-secret"
        try:
            raw, signature = token.split(".", 1)
            if not CryptoManager.verify_signature(raw, signature, secret_key):
                return False, "Invalid token signature"
            payload = json.loads(base64.urlsafe_b64decode(raw.encode()).decode())
            if payload.get("voter_id") != voter_id:
                return False, "Token does not match voter"
            if datetime.fromisoformat(payload["expires_at"]) < datetime.utcnow():
                return False, "Token expired"
            return True, "Token valid"
        except Exception as exc:
            return False, f"Invalid token: {exc}"

    @staticmethod
    def create_merkle_root(votes: List[str]) -> str:
        root, _ = CryptoManager.create_merkle_tree(votes)
        return root

    @staticmethod
    def create_merkle_tree(vote_hashes: List[str]) -> Tuple[str, List[List[str]]]:
        if not vote_hashes:
            empty = CryptoManager.sha256_hash("")
            return empty, [[empty]]
        levels = [list(vote_hashes)]
        level = list(vote_hashes)
        while len(level) > 1:
            work = list(level)
            if len(work) % 2 == 1:
                work.append(work[-1])
            level = [CryptoManager.sha256_hash(work[i] + work[i + 1]) for i in range(0, len(work), 2)]
            levels.append(level)
        return level[0], levels

    @staticmethod
    def get_merkle_proof(vote_hashes: List[str], vote_index: int) -> Optional[List[Tuple[str, str]]]:
        if vote_index < 0 or vote_index >= len(vote_hashes):
            return None
        _, levels = CryptoManager.create_merkle_tree(vote_hashes)
        proof: List[Tuple[str, str]] = []
        index = vote_index
        for level in levels[:-1]:
            work = list(level)
            if len(work) % 2 == 1:
                work.append(work[-1])
            sibling = index + 1 if index % 2 == 0 else index - 1
            proof.append((work[sibling], "right" if index % 2 == 0 else "left"))
            index //= 2
        return proof

    @staticmethod
    def verify_merkle_proof(vote_hash: str, merkle_root: str, proof: List[Tuple[str, str]]) -> bool:
        current = vote_hash
        for sibling_hash, direction in proof:
            current = CryptoManager.sha256_hash(current + sibling_hash) if direction == "right" else CryptoManager.sha256_hash(sibling_hash + current)
        return hmac.compare_digest(current, merkle_root)

    @staticmethod
    def hash_block_data(index: int, timestamp: str, votes: List[dict], previous_hash: str, nonce: int) -> str:
        data = {"index": index, "timestamp": timestamp, "votes": votes, "previous_hash": previous_hash, "nonce": nonce}
        return CryptoManager.sha256_hash(json.dumps(data, sort_keys=True, default=str))

    @staticmethod
    def verify_proof_of_work(block_hash: str, difficulty: int) -> bool:
        return block_hash.startswith("0" * difficulty)

    @staticmethod
    def generate_vote_hash(voter_id: str, candidate: str, timestamp: str) -> str:
        data = {"voter_id": voter_id, "candidate": candidate, "timestamp": timestamp}
        return CryptoManager.sha256_hash(json.dumps(data, sort_keys=True))

    @staticmethod
    def create_vote_certificate(voter_id: str, vote_hash: str, timestamp: str, secret_key: str) -> str:
        data = {"voter_id": voter_id, "vote_hash": vote_hash, "timestamp": timestamp}
        raw = base64.urlsafe_b64encode(json.dumps(data, sort_keys=True).encode()).decode()
        return f"{raw}.{CryptoManager.generate_signature(raw, secret_key)}"

    @staticmethod
    def verify_vote_certificate(certificate: str, secret_key: str) -> Tuple[bool, dict]:
        try:
            raw, signature = certificate.split(".", 1)
            if not CryptoManager.verify_signature(raw, signature, secret_key):
                return False, {}
            return True, json.loads(base64.urlsafe_b64decode(raw.encode()).decode())
        except Exception:
            return False, {}

    @staticmethod
    def constant_time_compare(a: str, b: str) -> bool:
        return hmac.compare_digest(str(a), str(b))
