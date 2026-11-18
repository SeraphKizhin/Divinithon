from dataclasses import dataclass
from typing import Optional

@dataclass
class Equipment:
    name: str
    slot: str
    weapon_type: Optional[str] = None
    offhandable: bool = False
    bonus: int = 0

@dataclass
class Monster:
    name: str
    is_boss: bool = False
