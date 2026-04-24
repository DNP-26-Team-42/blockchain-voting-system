"""
Main server module for the voting system.
Handles client requests, blockchain operations and database interaction.
"""

from typing import Dict, Any, Tuple
import threading
import logging

from server.network import SocketServer, NetworkMessage
from server.blockchain import Blockchain
from server.database import DatabaseManager
from server.config import ConfigLoader
from server.logger import setup_logging


class VotingServer:
    """Main voting server class."""

    def __init__(self, config_path: str = "config.json"):
        self.config_loader = ConfigLoader(config_path)
        success, config = self.config_loader.load()

        if not success:
            raise RuntimeError("Failed to load configuration")

        self.config = config

        # logger
        log_file = config["logging"].get("file")
        log_level = getattr(logging, config["logging"].get("level", "INFO"))
        self.logger = setup_logging(__name__, log_file, log_level)

        # blockchain + db
        self.blockchain = Blockchain(
            difficulty=config["blockchain"]["difficulty"],
            max_votes_per_block=config["blockchain"]["block_size"],
        )

        self.database = DatabaseManager()

        # network
        self.server = SocketServer(
            config["server"]["host"],
            config["server"]["port"],
            config["server"]["timeout"]
        )

        self._register_handlers()

    def _register_handlers(self) -> None:
        self.server.register_handler("register", self.handle_register)
        self.server.register_handler("vote", self.handle_vote)
        self.server.register_handler("verify", self.handle_verify)
        self.server.register_handler("results", self.handle_results)
        self.server.register_handler("status", self.handle_status)
        self.server.register_handler("candidates", self.handle_candidates)

    def start(self) -> Tuple[bool, str]:
        ok, msg = self.server.start()

        if not ok:
            return ok, msg

        thread = threading.Thread(target=self.server.accept_connections, daemon=True)
        thread.start()

        self.logger.info("Server started")

        return True, "Server running"

    def stop(self) -> None:
        self.server.stop()
        self.database.close()
        self.logger.info("Server stopped")

    # ================= HANDLERS =================

    def handle_register(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        name = payload.get("name")
        surname = payload.get("surname")
        id_number = payload.get("id_number")

        if not all([name, surname, id_number]):
            return {"error": "Missing registration fields"}

        from server.crypto import CryptoManager

        voter_id = CryptoManager.generate_voter_id(name, surname, id_number)
        token = CryptoManager.generate_voter_token(voter_id)

        success, message = self.database.register_voter(
            voter_id,
            f"{name} {surname}",
            token
        )

        if not success:
            return {"error": message}

        return {
            "voter_id": voter_id,
            "token": token
        }

    def handle_vote(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        voter_id = payload.get("voter_id")
        candidate = payload.get("candidate")
        token = payload.get("token")

        if not all([voter_id, candidate, token]):
            return {"error": "Missing vote fields"}

        from server.crypto import CryptoManager

        valid, msg = CryptoManager.verify_voter_token(token, voter_id)

        if not valid:
            return {"error": msg}

        voter = self.database.get_voter(voter_id)

        if not voter:
            return {"error": "Voter not registered"}

        if voter["has_voted"]:
            return {"error": "Already voted"}

        success, vote_hash = self.blockchain.add_vote(voter_id, candidate)

        if not success:
            return {"error": vote_hash}

        vote = self.blockchain.pending_votes[-1]

        self.database.save_vote(
            vote.vote_hash,
            vote.voter_id,
            vote.candidate,
            vote.timestamp
        )

        self.database.mark_voter_as_voted(voter_id)

        return {"vote_hash": vote.vote_hash}

    def handle_verify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        vote_hash = payload.get("vote_hash")

        if not vote_hash:
            return {"error": "Missing vote_hash"}

        valid, message = self.blockchain.verify_vote(vote_hash)

        return {
            "valid": valid,
            "message": message
        }

    def handle_results(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "results": self.blockchain.get_results()
        }

    def handle_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        valid, _ = self.blockchain.is_chain_valid()

        return {
            "status": "ok" if valid else "error",
            "blocks": len(self.blockchain.chain),
            "pending_votes": len(self.blockchain.pending_votes)
        }

    def handle_candidates(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        results = self.blockchain.get_results()
        return {"candidates": list(results.keys())}


def main():
    server = VotingServer()
    ok, msg = server.start()

    if not ok:
        print("Failed to start:", msg)
        return

    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()