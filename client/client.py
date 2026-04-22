"""
Voting Client - CLI application for voter interaction.
Allows voters to register, vote, and verify their votes.
"""

import sys
import json
from typing import Optional, Dict, Any
from pathlib import Path

# from network import VotingClientNetwork


class VotingClient:
    """Voting client with CLI interface."""

    def __init__(self, server_host: str, server_port: int):
        """Initialize voting client."""
        self.server_host = server_host
        self.server_port = server_port
        self.running = True
        self.current_voter: Optional[Dict[str, str]] = None

        # self.network = VotingClientNetwork(server_host, server_port)

    def connect_to_server(self) -> bool:
        """Connect to voting server."""
        pass

    def disconnect_from_server(self) -> None:
        """Disconnect from server."""
        pass

    def is_connected(self) -> bool:
        """Check connection status."""
        pass

    def run_cli(self) -> None:
        """Run interactive CLI."""
        pass

    def display_main_menu(self) -> None:
        """Display main menu options."""
        pass

    def menu_register_voter(self) -> None:
        """Menu option: Register as a new voter."""
        pass

    def menu_submit_vote(self) -> None:
        """Menu option: Cast a vote."""
        pass

    def menu_verify_vote(self) -> None:
        """Menu option: Verify vote was recorded."""
        pass

    def menu_view_results(self) -> None:
        """Menu option: View election results."""
        pass

    def menu_view_candidates(self) -> None:
        """Menu option: View available candidates."""
        pass

    def menu_server_info(self) -> None:
        """Menu option: View server information."""
        pass

    def menu_my_info(self) -> None:
        """Menu option: View current voter info."""
        pass

    def menu_help(self) -> None:
        """Menu option: Show help."""
        pass

    def get_voter_name(self) -> str:
        """Prompt for voter name."""
        pass

    def get_voter_surname(self) -> str:
        """Prompt for voter surname."""
        pass

    def get_voter_id(self) -> str:
        """Prompt for voter ID number."""
        pass

    def get_candidate_choice(self, candidates: list) -> str:
        """Prompt user to select a candidate."""
        pass

    def display_candidates(self, candidates: list) -> None:
        """Display available candidates."""
        pass

    def display_results(self, results: Dict[str, int]) -> None:
        """Display vote results."""
        pass

    def save_voter_info(self, voter_info: Dict[str, str]) -> None:
        """Save voter info locally for verification."""
        pass

    def load_voter_info(self) -> Optional[Dict[str, str]]:
        """Load previously saved voter info."""
        pass

    def handle_server_error(self, error_message: str) -> None:
        """Handle and display server error."""
        pass


def main():
    """Main entry point for voting client."""
    if len(sys.argv) < 3:
        print("Usage: python client.py <server_host> <server_port>")
        print("Example: python client.py localhost 5000")
        sys.exit(1)

    server_host = sys.argv[1]
    try:
        server_port = int(sys.argv[2])
    except ValueError:
        print("Error: Port must be an integer")
        sys.exit(1)

    client = VotingClient(server_host, server_port)

    try:
        if not client.connect_to_server():
            print("Error: Could not connect to server")
            sys.exit(1)

        client.run_cli()

    except KeyboardInterrupt:
        print("\n\nExiting...")
        client.disconnect_from_server()
    except Exception as e:
        print(f"Error: {e}")
        client.disconnect_from_server()
        sys.exit(1)


if __name__ == "__main__":
    main()
