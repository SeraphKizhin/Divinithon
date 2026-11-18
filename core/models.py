from dataclasses import dataclass
from typing import Optional

MonsterTier = Literal["normal", "mini_boss", "boss"]

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
    tier: MonsterTier = "normal"
