import sys

def info(msg: str) -> None:
    print(f"[INFO] {msg}")

def success(msg: str) -> None:
    print(f"[SUCCESS] {msg}")

def warn(msg: str) -> None:
    print(f"[WARN] {msg}")

def caution(msg: str) -> None:
    print(f"[CAUTION] {msg}")

def debug(msg: str) -> None:
    print(f"[DEBUG] {msg}")

def error(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)

def banner(text: str) -> None:
    line = "=" * (len(text) + 4)
    print(f"\n{line}\n| {text} |\n{line}\n")
