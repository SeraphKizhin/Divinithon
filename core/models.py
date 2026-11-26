from dataclasses import dataclass, field
from typing import Optional, Literal

MonsterTier = Literal["normal", "mini_boss", "boss"]

@dataclass
class Extra:
    name: str
    sell_value: int

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
    hp_mult: float = 1.0
    dmg_mult: float = 1.0

@dataclass
class ActiveMonster:
    name: str
    tier: MonsterTier
    level: int
    max_hp: int
    cur_hp: int
    sellable_drops: list[Extra] = field(default_factory=list)
    dmg_mult: float = 1.0