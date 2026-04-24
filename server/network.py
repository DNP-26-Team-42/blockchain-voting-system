"""Network module for socket-based communication."""
from typing import Optional, Dict, Any, Callable, Tuple
import socket, json, threading, logging, uuid
from datetime import datetime


class NetworkMessage:
    MESSAGE_TYPES = {"REGISTER":"register","VOTE":"vote","VERIFY":"verify","STATUS":"status","RESULTS":"results","CANDIDATES":"candidates","ERROR":"error","SUCCESS":"success","PING":"ping","PONG":"pong"}
    VERSION = "1.0"
    def __init__(self, msg_type: str, payload: Dict[str, Any], message_id: str = ""):
        self.type = msg_type; self.payload = payload or {}; self.message_id = message_id or self._generate_message_id(); self.timestamp = datetime.utcnow().isoformat(); self.version = self.VERSION
    @staticmethod
    def _generate_message_id() -> str: return uuid.uuid4().hex
    def to_dict(self) -> Dict[str, Any]: return {"type": self.type, "payload": self.payload, "message_id": self.message_id, "timestamp": self.timestamp, "version": self.version}
    def to_json(self) -> str: return json.dumps(self.to_dict(), sort_keys=True)
    @staticmethod
    def from_json(json_str: str) -> Optional["NetworkMessage"]:
        try:
            data = json.loads(json_str)
            msg = NetworkMessage(data.get("type", ""), data.get("payload", {}), data.get("message_id", ""))
            msg.timestamp = data.get("timestamp", msg.timestamp); msg.version = data.get("version", NetworkMessage.VERSION)
            return msg if msg.is_valid() else None
        except Exception: return None
    def is_valid(self) -> bool:
        return isinstance(self.type, str) and self.type in self.MESSAGE_TYPES.values() and isinstance(self.payload, dict) and self.version == self.VERSION
    def validate_payload(self) -> Tuple[bool, str]:
        required = {"register":["name","surname","id_number"], "vote":["voter_id","candidate"], "verify":["voter_id"]}
        for field in required.get(self.type, []):
            if field not in self.payload or self.payload[field] in (None, ""):
                return False, f"Missing field: {field}"
        return True, "Payload is valid"
    def __str__(self) -> str: return self.to_json()
    def __repr__(self) -> str: return f"NetworkMessage(type={self.type!r}, message_id={self.message_id!r})"


def _send_json(sock: socket.socket, data: str) -> None:
    raw = data.encode("utf-8")
    sock.sendall(len(raw).to_bytes(4, "big") + raw)

def _recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        part = sock.recv(size - len(chunks))
        if not part: break
        chunks.extend(part)
    return bytes(chunks)

def _receive_json(sock: socket.socket) -> Optional[str]:
    header = _recv_exact(sock, 4)
    if len(header) != 4: return None
    size = int.from_bytes(header, "big")
    data = _recv_exact(sock, size)
    return data.decode("utf-8") if data else None


class SocketServer:
    def __init__(self, host: str, port: int, timeout: int = 30):
        self.host=host; self.port=port; self.timeout=timeout; self.socket=None; self.running=False; self.handlers={}; self.active_clients={}; self.lock=threading.Lock(); self.logger=logging.getLogger(__name__); self.max_connections=100; self.buffer_size=4096
    def start(self) -> Tuple[bool, str]:
        try:
            self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM); self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); self.socket.settimeout(self.timeout); self.socket.bind((self.host,self.port)); self.socket.listen(self.max_connections); self.running=True; return True, "Server started"
        except Exception as exc: return False, str(exc)
    def stop(self) -> None:
        self.running=False
        for client in list(self.active_clients): self.close_client(client)
        if self.socket:
            try: self.socket.close()
            except OSError: pass
            self.socket=None
    def is_running(self) -> bool: return self.running
    def accept_connections(self) -> None:
        while self.running:
            item=self.accept_single_connection()
            if item: threading.Thread(target=self.handle_client, args=item, daemon=True).start()
    def accept_single_connection(self) -> Optional[Tuple[socket.socket, Tuple]]:
        try:
            if not self.socket: return None
            client, address = self.socket.accept(); client.settimeout(self.timeout)
            with self.lock: self.active_clients[client]=address
            return client, address
        except Exception: return None
    def register_handler(self, msg_type: str, handler: Callable) -> None: self.handlers[msg_type]=handler
    def get_handler(self, msg_type: str) -> Optional[Callable]: return self.handlers.get(msg_type)
    def handle_client(self, client_socket: socket.socket, client_address: Tuple) -> None:
        try:
            while self.running:
                msg=self.receive_message(client_socket)
                if msg is None: break
                response=self.handle_message(msg, client_socket)
                if response: self.send_message(client_socket, response)
        finally: self.close_client(client_socket)
    def handle_message(self, message: NetworkMessage, client_socket: socket.socket) -> Optional[NetworkMessage]:
        if message.type == "ping": return NetworkMessage("pong", {"ok": True})
        handler=self.get_handler(message.type)
        if not handler: return NetworkMessage("error", {"message": "No handler registered"})
        result=handler(message.payload)
        if isinstance(result, NetworkMessage): return result
        return NetworkMessage("success", result if isinstance(result, dict) else {"result": result})
    def send_message(self, client_socket: socket.socket, message: NetworkMessage) -> Tuple[bool, str]:
        try: _send_json(client_socket, message.to_json()); return True, "Message sent"
        except Exception as exc: return False, str(exc)
    def receive_message(self, client_socket: socket.socket) -> Optional[NetworkMessage]:
        try:
            raw=_receive_json(client_socket); return NetworkMessage.from_json(raw) if raw else None
        except Exception: return None
    def close_client(self, client_socket: socket.socket) -> None:
        with self.lock: self.active_clients.pop(client_socket, None)
        try: client_socket.close()
        except OSError: pass
    def get_active_clients_count(self) -> int: return len(self.active_clients)
    def broadcast_message(self, message: NetworkMessage, exclude_client: Optional[socket.socket] = None) -> int:
        count=0
        for client in list(self.active_clients):
            if client is not exclude_client and self.send_message(client, message)[0]: count += 1
        return count
    def shutdown(self) -> None: self.stop()


class SocketClient:
    def __init__(self, server_host: str, server_port: int, timeout: int = 30):
        self.server_host=server_host; self.server_port=server_port; self.timeout=timeout; self.socket=None; self.connected=False; self.logger=logging.getLogger(__name__); self.buffer_size=4096; self.reconnect_attempts=3; self.reconnect_delay=1
    def connect(self, retry: bool = True) -> Tuple[bool, str]:
        if retry: return self.connect_with_retry()
        try:
            self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM); self.socket.settimeout(self.timeout); self.socket.connect((self.server_host,self.server_port)); self.connected=True; return True, "Connected"
        except Exception as exc: self.connected=False; return False, str(exc)
    def connect_with_retry(self) -> Tuple[bool, str]:
        last=""
        for _ in range(self.reconnect_attempts):
            ok,msg=self.connect(False)
            if ok: return ok,msg
            last=msg
        return False,last
    def disconnect(self) -> None:
        self.connected=False
        if self.socket:
            try: self.socket.close()
            except OSError: pass
            self.socket=None
    def send_message(self, message: NetworkMessage) -> Tuple[bool, str]:
        if not self.socket or not self.connected: return False, "Not connected"
        try: _send_json(self.socket, message.to_json()); return True, "Message sent"
        except Exception as exc: self.connected=False; return False, str(exc)
    def receive_message(self) -> Optional[NetworkMessage]:
        try:
            if not self.socket: return None
            raw=_receive_json(self.socket); return NetworkMessage.from_json(raw) if raw else None
        except Exception: return None
    def send_and_receive(self, message: NetworkMessage, timeout: Optional[int] = None) -> Optional[NetworkMessage]:
        if self.socket and timeout is not None: self.socket.settimeout(timeout)
        if not self.send_message(message)[0]: return None
        return self.receive_message()
    def is_connected(self) -> bool: return self.connected
    def close(self) -> None: self.disconnect()
    def ping(self) -> bool:
        response=self.send_and_receive(NetworkMessage("ping", {}))
        return bool(response and response.type == "pong")
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.disconnect()
