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
    sell_value: int = 100

@dataclass
class Monster:
    name: str
    tier: MonsterTier = "normal"
    sellable_drops: list[Extra] = field(default_factory=list)

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
    sellable_drops: list[Extra] = field(default_factory=list)