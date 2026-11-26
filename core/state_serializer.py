import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

# Add project root to sys.path if executed directly as a script
_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from data.world_map import get_neighbors, get_node_name, get_node_zone

DEFAULT_RECENT_LOGS = 5
MAX_LOG_CHARS = 140

EQUIPMENT_SLOTS = ("mainhand", "offhand", "body", "special", "additional")


def _item_to_dict(item: Any) -> dict[str, Any] | None:
    """Equipment (dataclass or dict) -> small dict. None stays None."""
    if item is None:
        return None
    data = asdict(item) if is_dataclass(item) and not isinstance(item, type) else dict(item)
    return {
        "name": str(data.get("name", "Unknown")),
        "slot": data.get("slot"),
        "weapon_type": data.get("weapon_type"),
        "bonus": int(data.get("bonus", 0) or 0),
    }


def _serialize_equipment(equipment: dict[str, Any] | None) -> dict[str, dict | None]:
    equipment = equipment or {}
    result = {slot: _item_to_dict(equipment.get(slot)) for slot in EQUIPMENT_SLOTS}
    for slot, item in equipment.items():  # keep any extra slots added later
        if slot not in result:
            result[slot] = _item_to_dict(item)
    return result


def _serialize_inventory(inventory: dict[str, int] | None) -> list[dict[str, Any]]:
    """Stacking inventory {name: qty} -> list sorted by quantity (desc), then name."""
    rows = [
        {"name": str(name), "qty": int(qty)}
        for name, qty in (inventory or {}).items()
        if qty and int(qty) > 0
    ]
    return sorted(rows, key=lambda row: (-row["qty"], row["name"]))


def _serialize_enemy(enemy: Any) -> dict[str, Any] | None:
    if enemy is None:
        return None
    return {
        "name": str(getattr(enemy, "name", "Unknown")),
        "tier": str(getattr(enemy, "tier", "normal")),
        "level": int(getattr(enemy, "level", 1)),
        "cur_hp": int(getattr(enemy, "cur_hp", 0)),
        "max_hp": int(getattr(enemy, "max_hp", 0)),
    }


def _serialize_travel(travel: dict[str, Any] | None) -> dict[str, Any] | None:
    if not travel:
        return None
    return {
        "from": travel.get("from"),
        "from_name": get_node_name(travel.get("from", "")),
        "to": travel.get("to"),
        "to_name": get_node_name(travel.get("to", "")),
        "progress": int(travel.get("progress", 0)),
        "steps": int(travel.get("steps", 0)),
    }


def _serialize_map(node_codes: list[str], current: str, traveling: bool) -> list[dict[str, Any]]:
    nodes = []
    for code in node_codes:
        nodes.append(
            {
                "code": code,
                "name": get_node_name(code),
                "zone": get_node_zone(code),
                "neighbors": [get_node_name(n) for n in get_neighbors(code)],
                "is_current": (code == current) and not traveling,
            }
        )
    return nodes


def _recent_events(logbook: list[str] | None, count: int) -> list[str]:
    if count <= 0:
        return []
    return [str(entry)[:MAX_LOG_CHARS] for entry in (logbook or [])[-count:]]


def serialize_game_state(
    state: dict[str, Any],
    *,
    recent_logs: int = DEFAULT_RECENT_LOGS,
) -> dict[str, Any]:
    """Returns a JSON-safe snapshot of ``state`` (see module docstring for the shape)."""
    current = state.get("current_location", "NF")
    travel = state.get("travel")
    node_codes = list(state.get("map_nodes") or [current])

    return {
        "god_name": state.get("god_name"),
        "apostle": state.get("apostle"),
        "stats": {
            "level": state.get("lvl", 1),
            "exp": state.get("exp", 0),
            "exp_required": state.get("exp_req", 0),
            "cur_hp": state.get("cur_hp", 0),
            "max_hp": state.get("max_hp", 0),
            "gold": state.get("gold", 0),
            "godpower": state.get("godpower", 0),
            "monsters_defeated": state.get("monster_defeated", 0),
            "deaths": state.get("death_count", 0),
        },
        "quest": {
            "name": state.get("quest"),
            "progress_percent": state.get("quest_progress", 0),
        },
        "current_action": state.get("current_action"),
        "combat": _serialize_enemy(state.get("active_enemy")),
        "location": {
            "code": current,
            "name": get_node_name(current),
            "zone": get_node_zone(current),
            "on_the_road": bool(travel),
        },
        "travel": _serialize_travel(travel),
        "equipment": _serialize_equipment(state.get("equipment")),
        "inventory": _serialize_inventory(state.get("inventory")),
        "map": _serialize_map(node_codes, current, bool(travel)),
        "recent_events": _recent_events(state.get("logbook"), recent_logs),
    }


def game_state_to_json(
    state: dict[str, Any],
    *,
    recent_logs: int = DEFAULT_RECENT_LOGS,
    indent: int | None = None,
) -> str:
    """Serializes ``state`` straight to a JSON string."""
    return json.dumps(
        serialize_game_state(state, recent_logs=recent_logs),
        ensure_ascii=False,
        indent=indent,
    )


if __name__ == "__main__":
    from types import SimpleNamespace

    from core.models import Equipment
    from core.state import create_initial_state

    demo = create_initial_state()
    demo["equipment"]["mainhand"] = Equipment(name="Iron Sword", slot="mainhand", weapon_type="OHS", bonus=4)
    demo["inventory"] = {"Wolf Fur": 3, "Golden Apple": 1}
    demo["active_enemy"] = SimpleNamespace(name="Goblin", tier="normal", level=2, cur_hp=12, max_hp=30)
    print(game_state_to_json(demo, indent=2))
