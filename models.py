from typing import TypedDict, Dict, List, Optional

class Swimmer(TypedDict):
    name: str
    seed_time: str
    age: str
    team: str
    rank: int
    gender: Optional[str]

class Heat(TypedDict):
    heat_number: int
    lanes: Dict[str, Swimmer]

class Event(TypedDict):
    number: str
    name: str
    swimmers: List[Swimmer]   # ONLY parser uses this
    heats: List[Heat]         # everything else uses this
