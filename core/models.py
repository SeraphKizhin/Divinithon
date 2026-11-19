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

@dataclass
class Extra:
    name: str
    sell_value: int

@dataclass
class ActiveMonster:
    name: str
    tier: MonsterTier
    max_hp: int
    cur_hp: int
    