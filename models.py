from dataclasses import dataclass

@dataclass
class Swimmer:
    name: str
    age: str
    team: str
    seed_time: str
    rank: int
    gender: str | None = None

@dataclass
class Event:
    number: str
    name: str
    swimmers: list
