"""
Utility functions for the voting system.
Common helpers for validation, formatting, logging, and data processing.
"""

from typing import Optional, List, Tuple
from datetime import datetime
from pathlib import Path
import logging
import re
import json
import random


def setup_logging(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def validate_voter_name(name: str) -> Tuple[bool, str]:
    if not name or not name.strip():
        return False, "Name is required"

    name = name.strip()

    if len(name) < 2:
        return False, "Name must contain at least 2 characters"

    if len(name) > 255:
        return False, "Name is too long"

    if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\s'-]+", name):
        return False, "Name may contain only letters and spaces"

    return True, "Name is valid"


def validate_voter_surname(surname: str) -> Tuple[bool, str]:
    if not surname or not surname.strip():
        return False, "Surname is required"

    surname = surname.strip()

    if len(surname) < 2:
        return False, "Surname must contain at least 2 characters"

    if len(surname) > 255:
        return False, "Surname is too long"

    if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\s'-]+", surname):
        return False, "Surname may contain only letters and spaces"

    return True, "Surname is valid"


def validate_voter_id(id_number: str) -> Tuple[bool, str]:
    if not id_number or not id_number.strip():
        return False, "Voter ID is required"

    id_number = id_number.strip()

    if len(id_number) > 50:
        return False, "Voter ID is too long"

    if not re.fullmatch(r"[A-Za-z0-9\-/]+", id_number):
        return False, "Voter ID may contain only letters, digits, hyphens and slashes"

    return True, "Voter ID is valid"


def validate_candidate_name(candidate: str) -> Tuple[bool, str]:
    if not candidate or not candidate.strip():
        return False, "Candidate name is required"

    candidate = candidate.strip()

    if len(candidate) > 255:
        return False, "Candidate name is too long"

    if not re.fullmatch(r"[A-Za-zА-Яа-яЁё0-9\s.,'-]+", candidate):
        return False, "Candidate name contains invalid characters"

    return True, "Candidate name is valid"


def validate_voter_email(email: str) -> Tuple[bool, str]:
    if not email:
        return False, "Email is required"

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.fullmatch(pattern, email.strip()):
        return False, "Invalid email format"

    return True, "Email is valid"


def validate_password(password: str, min_length: int = 8) -> Tuple[bool, str]:
    if not password:
        return False, "Password is required"

    if len(password) < min_length:
        return False, f"Password must contain at least {min_length} characters"

    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must contain at least one special character"

    return True, "Password is valid"


def sanitize_input(user_input: str, max_length: int = 255) -> str:
    if user_input is None:
        return ""

    value = str(user_input).strip()
    value = re.sub(r"[<>]", "", value)
    value = value.replace("\x00", "")
    return value[:max_length]


def is_valid_ipv4(ip: str) -> bool:
    if not ip:
        return False

    parts = ip.split(".")

    if len(parts) != 4:
        return False

    for part in parts:
        if not part.isdigit():
            return False

        number = int(part)

        if number < 0 or number > 255:
            return False

    return True


def is_valid_port(port: int) -> bool:
    return isinstance(port, int) and 1 <= port <= 65535


def is_valid_hostname(hostname: str) -> bool:
    if not hostname:
        return False

    if hostname == "localhost":
        return True

    if is_valid_ipv4(hostname):
        return True

    pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
    return bool(re.fullmatch(pattern, hostname))


def get_current_datetime() -> str:
    return datetime.utcnow().isoformat()


def get_current_timestamp_ms() -> int:
    return int(datetime.utcnow().timestamp() * 1000)


def get_current_timestamp_unix() -> float:
    return datetime.utcnow().timestamp()


def format_timestamp(dt: Optional[datetime] = None) -> str:
    dt = dt or datetime.utcnow()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(timestamp_str)
    except (TypeError, ValueError):
        return None


def timestamp_to_readable(timestamp_str: str) -> str:
    dt = parse_timestamp(timestamp_str)

    if dt is None:
        return "Invalid timestamp"

    return dt.strftime("%b %d, %Y %I:%M %p")


def get_timestamp_difference(ts1: str, ts2: str) -> Optional[float]:
    first = parse_timestamp(ts1)
    second = parse_timestamp(ts2)

    if first is None or second is None:
        return None

    return abs((second - first).total_seconds())


def format_vote_results(results: dict) -> str:
    if not results:
        return "No votes recorded."

    total = sum(results.values())
    lines = ["Voting results:", "-" * 40]

    for candidate, count in sorted(results.items(), key=lambda item: item[1], reverse=True):
        percentage = calculate_percentage(count, total)
        lines.append(f"{candidate}: {count} votes ({percentage:.2f}%)")

    lines.append("-" * 40)
    lines.append(f"Total votes: {total}")

    return "\n".join(lines)


def format_blockchain_info(blockchain_data: dict) -> str:
    if not blockchain_data:
        return "No blockchain information available."

    lines = ["Blockchain information:", "-" * 40]

    for key, value in blockchain_data.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def format_json(data: dict, indent: int = 2) -> str:
    return json.dumps(data, indent=indent, sort_keys=True, ensure_ascii=False)


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    if not headers:
        return ""

    all_rows = [headers] + rows
    widths = [
        max(len(str(row[index])) for row in all_rows)
        for index in range(len(headers))
    ]

    separator = "+".join("-" * (width + 2) for width in widths)

    def make_row(row: List[str]) -> str:
        cells = [
            f" {str(row[index]).ljust(widths[index])} "
            for index in range(len(headers))
        ]
        return "|" + "|".join(cells) + "|"

    lines = [separator, make_row(headers), separator]

    for row in rows:
        lines.append(make_row(row))

    lines.append(separator)

    return "\n".join(lines)


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    if text is None:
        return ""

    text = str(text)

    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def dict_to_json_str(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)


def json_str_to_dict(json_str: str) -> Optional[dict]:
    try:
        data = json.loads(json_str)
        return data if isinstance(data, dict) else None
    except (TypeError, json.JSONDecodeError):
        return None


def list_to_json_str(data: list) -> str:
    return json.dumps(data, ensure_ascii=False)


def json_str_to_list(json_str: str) -> Optional[list]:
    try:
        data = json.loads(json_str)
        return data if isinstance(data, list) else None
    except (TypeError, json.JSONDecodeError):
        return None


def read_json_file(file_path: str) -> Optional[dict]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def write_json_file(file_path: str, data: dict) -> Tuple[bool, str]:
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

        return True, "File written successfully"
    except OSError as error:
        return False, str(error)


def file_exists(file_path: str) -> bool:
    return Path(file_path).exists()


def create_directory(dir_path: str) -> Tuple[bool, str]:
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True, "Directory created"
    except OSError as error:
        return False, str(error)


def remove_whitespace(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def to_snake_case(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    text = text.replace("-", "_").replace(" ", "_")

    return text.lower()


def to_camel_case(text: str) -> str:
    if not text:
        return ""

    parts = text.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def capitalize_first(text: str) -> str:
    if not text:
        return ""

    return text[0].upper() + text[1:]


def calculate_percentage(value: int, total: int) -> float:
    if total == 0:
        return 0.0

    return (value / total) * 100


def get_max_value_key(data: dict) -> Optional[str]:
    if not data:
        return None

    return max(data, key=data.get)


def get_min_value_key(data: dict) -> Optional[str]:
    if not data:
        return None

    return min(data, key=data.get)


def calculate_average(values: List[float]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def generate_random_string(length: int = 32, charset: str = "abcdefghijklmnopqrstuvwxyz0123456789") -> str:
    return "".join(random.choice(charset) for _ in range(length))


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    if chunk_size <= 0:
        return []

    return [lst[index:index + chunk_size] for index in range(0, len(lst), chunk_size)]


def flatten_list(lst: List) -> List:
    result = []

    for item in lst:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)

    return result


def remove_duplicates(lst: List) -> List:
    result = []
    seen = set()

    for item in lst:
        marker = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else item

        if marker not in seen:
            seen.add(marker)
            result.append(item)

    return result


def print_section(title: str, width: int = 80) -> None:
    line = "=" * width
    print(line)
    print(title.center(width))
    print(line)


def print_table_row(cells: List[str], widths: List[int], separator: str = "|") -> None:
    formatted = [
        str(cell).ljust(widths[index])
        for index, cell in enumerate(cells)
    ]
    print(separator + separator.join(formatted) + separator)
    