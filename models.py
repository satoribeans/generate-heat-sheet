from typing import TypedDict, List, Dict, Any

class Swimmer(TypedDict):
    name: str
    seed_time: str
    age: str
    team: str
    rank: int
    gender: str | None

class Heat(TypedDict):
    heat_number: int
    lanes: Dict[str, Swimmer]

class Event(TypedDict):
    number: str
    name: str
    heats: List[Heat]
