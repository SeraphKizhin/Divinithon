from typing import Optional
from core.models import Equipment

ALLOWED_OFFHANDS = {
    "OHS": {"SHIELD", "ARROW", "SCROLL", "MD", "KNUX", "OHS"},
    "THS": {"SHIELD", "ARROW", "SCROLL", "MD", "KNUX"},
    "BOW": {"SHIELD", "ARROW", "SCROLL", "MD", "KNUX"},
    "STAFF": {"SHIELD", "ARROW", "SCROLL", "MD", "KNUX"},
    "MD": {"SHIELD", "ARROW", "SCROLL", "KNUX"},
    "KNUX" {"SHIELD", "ARROW", "SCROLL", "MD"},
}

def can_equip_offhand(mainhand: Optional[Equipment], offhand: Equipment) -> bool:
    if mainhand is None:
        return False
    
    if offhand.slot != "offhand" and not offhand.offhandable:
        return False
    
    allowed_types = ALLOWED_OFFHANDS.get(mainhand.weapon_type.set())
    return offhand.weapon_type in allowed_types