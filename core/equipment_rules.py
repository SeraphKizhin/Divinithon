import random
from typing import Optional
from core.models import Equipment
from dataclasses import replace

ALLOWED_OFFHANDS = {
    "OHS": {"SHIELD", "ARROW", "SCROLL", "MD", "KNUX", "OHS"},
    "THS": set(),
    "BOW": {"SHIELD", "ARROW", "SCROLL", "MD", "KNUX"},
    "STAFF": {"SHIELD", "ARROW", "SCROLL", "MD", "KNUX"},
    "MD": {"SHIELD", "ARROW", "SCROLL", "KNUX"},
    "KNUX": {"SHIELD", "ARROW", "SCROLL", "MD"},
}

OFFHAND_DMG_TYPES = {"OHS", "MD", "ARROW", "SCROLL"}
OFFHAND_HP_TYPES = {"SHIELD", "KNUX"}

BONUS_OFFSETS = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
BONUS_WEIGHTS = [10, 15, 20, 25, 30, 35, 25, 20, 15, 10, 5]

def can_equip_offhand(mainhand: Optional[Equipment], offhand: Equipment) -> bool:
    if mainhand is None:
        return False
    allowed_types = ALLOWED_OFFHANDS.get(mainhand.weapon_type, set())
    if offhand.slot != "offhand" and not offhand.offhandable and offhand.weapon_type not in allowed_types:
        return False
    return offhand.weapon_type in allowed_types

def roll_equipment_drop(template: Equipment, apostle_lvl: int) -> Equipment:
    """Returns a fresh Equipment copy with a level-scaled bonus (lvl + [-5..+5])."""
    offset = random.choices(BONUS_OFFSETS, weights=BONUS_WEIGHTS, k=1)[0]
    rolled_bonus = max(1, apostle_lvl + offset)
    return replace(template, bonus=rolled_bonus)


def get_equipment_stats(equipment: dict[str, Optional[Equipment]]) -> dict[str, int]:
    totals = {"dmg": 0, "hp": 0}

    mainhand = equipment.get("mainhand")
    offhand = equipment.get("offhand")
    body = equipment.get("body")
    additional = equipment.get("additional")
    special = equipment.get("special")

    if mainhand:
        if mainhand.weapon_type == "THS":
            split_bonus = max(1, round(mainhand.bonus * 0.5)) if mainhand.bonus > 0 else 0
            totals["dmg"] += split_bonus
            totals["hp"] += split_bonus
        else:
            totals["dmg"] += mainhand.bonus
    if special:
        totals["dmg"] += special.bonus
    if body:
        totals["hp"] += body.bonus
    if additional:
        totals["hp"] += additional.bonus
    if offhand:
        if offhand.weapon_type in OFFHAND_DMG_TYPES:
            totals["dmg"] += offhand.bonus
        elif offhand.weapon_type in OFFHAND_HP_TYPES:
            totals["hp"] += offhand.bonus

    return totals


def _recalc_max_hp(state: dict) -> None:
    base_hp = 50 + (state["lvl"] - 1) * 15
    hp_bonus = get_equipment_stats(state["equipment"])["hp"]
    old_max = state["max_hp"]
    new_max = base_hp + hp_bonus

    state["max_hp"] = new_max
    if new_max > old_max:
        state["cur_hp"] += new_max - old_max
    state["cur_hp"] = min(state["cur_hp"], state["max_hp"])

def try_auto_equip(state: dict, new_item: Equipment, *, force: bool = False) -> bool:
    eq = state["equipment"]
    target_slot = new_item.slot

    if target_slot == "offhand":
        if not can_equip_offhand(eq["mainhand"], new_item):
            state["inventory"][new_item.name] = state["inventory"].get(new_item.name, 0) + 1
            return False

    current_item = eq.get(target_slot)

    if (
        not force
        and target_slot == "mainhand"
        and current_item is not None
        and new_item.bonus <= current_item.bonus
        and can_equip_offhand(current_item, new_item)
    ):
        cur_off = eq.get("offhand")
        if cur_off is None or new_item.bonus > cur_off.bonus:
            if cur_off is not None:
                state["inventory"][cur_off.name] = state["inventory"].get(cur_off.name, 0) + 1
            eq["offhand"] = new_item
            _recalc_max_hp(state)
            return True

    if force or current_item is None or new_item.bonus > current_item.bonus:
        old_item = current_item
        eq[target_slot] = new_item

        if target_slot == "mainhand":
            if eq["offhand"] is not None and not can_equip_offhand(new_item, eq["offhand"]):
                old_off = eq["offhand"]
                eq["offhand"] = None
                state["inventory"][old_off.name] = state["inventory"].get(old_off.name, 0) + 1

            if old_item is not None:
                cur_off = eq.get("offhand")
                if can_equip_offhand(new_item, old_item) and (
                    cur_off is None or old_item.bonus > cur_off.bonus
                ):
                    if cur_off is not None:
                        state["inventory"][cur_off.name] = state["inventory"].get(cur_off.name, 0) + 1
                    eq["offhand"] = old_item
                else:
                    state["inventory"][old_item.name] = state["inventory"].get(old_item.name, 0) + 1
        elif old_item is not None:
            state["inventory"][old_item.name] = state["inventory"].get(old_item.name, 0) + 1

        if target_slot == "body":
            _recalc_max_hp(state)

        _recalc_max_hp(state)
        return True

    state["inventory"][new_item.name] = state["inventory"].get(new_item.name, 0) + 1
    return False