import json
from pathlib import Path

YARD = json.loads((Path(__file__).parent.parent / "data" / "yard.json").read_text())
DECISIONS = ["ACT", "READ_BACK", "ASK_AGAIN"]


def has_lookalike(unit: str, trailers: list[str]) -> bool:
    return any(t != unit and sorted(t) == sorted(unit) for t in trailers)


def decide(cmd: dict | None, yard: dict = YARD) -> str:
    if not cmd or not cmd.get("action") or not cmd.get("unit"):
        return "ASK_AGAIN"
    if cmd["unit"] not in yard["trailers"]:
        return "ASK_AGAIN"
    if cmd["action"] == "move":
        to = cmd.get("to")
        if not to:
            return "ASK_AGAIN"
        if yard["doors"].get(to) == "busy":
            return "ASK_AGAIN"
    if cmd["action"] == "status":
        return "ACT"
    if cmd["action"] == "release":
        return "READ_BACK"
    if has_lookalike(cmd["unit"], yard["trailers"]):
        return "READ_BACK"
    return "ACT"
