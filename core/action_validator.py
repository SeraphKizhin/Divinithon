from dataclasses import dataclass
from typing import Any, Optional

from core.equipment_rules import can_equip_offhand
from core.models import Equipment
from data.catalog import EQUIPMENTS
from data.world_map import WORLD_NODES, get_neighbors, get_node_name

# Fallback only; the real list is read from state["equipment"] when available.
DEFAULT_SLOTS = ("mainhand", "offhand", "body", "special", "additional")

_EQUIPMENT_BY_NAME: dict[str, Equipment] = {eq.name.lower(): eq for eq in EQUIPMENTS}


@dataclass(frozen=True)
class ValidationResult:
    """Verdict for one action.

    ok:     True if the action may be executed.
    reason: short, plain-language explanation, safe to narrate in character.
    item:   canonical inventory name of the matched item (when found).
    slot:   canonical equipment slot (equip only, when resolved).
    destination: canonical node code (go_to only, when resolved).
    action: canonical action name (set by validate_action; None for a null action).
    """

    ok: bool
    reason: str = ""
    item: Optional[str] = None
    slot: Optional[str] = None
    destination: Optional[str] = None
    action: Optional[str] = None

    def __bool__(self) -> bool:
        return self.ok


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _fail(
    reason: str,
    item: Optional[str] = None,
    slot: Optional[str] = None,
    destination: Optional[str] = None,
) -> ValidationResult:
    return ValidationResult(False, reason, item, slot, destination)


def _find_inventory_key(inventory: dict[str, int], item_name: str) -> Optional[str]:
    """Case- and whitespace-insensitive lookup; returns the real inventory key."""
    wanted = " ".join(item_name.split()).lower()
    for key in inventory:
        if " ".join(str(key).split()).lower() == wanted:
            return key
    return None


def _normalize_slot(slot: str) -> str:
    """'Main Hand', 'main_hand', 'MAINHAND' -> 'mainhand'."""
    return "".join(ch for ch in slot.lower() if ch.isalnum())


def _valid_slots(state: dict[str, Any]) -> tuple[str, ...]:
    equipment = state.get("equipment")
    if isinstance(equipment, dict) and equipment:
        return tuple(equipment.keys())
    return DEFAULT_SLOTS


def _describe_inventory_hint(inventory: dict[str, int], limit: int = 5) -> str:
    owned = [name for name, qty in inventory.items() if isinstance(qty, int) and qty > 0]
    if not owned:
        return "The pack is empty."
    shown = ", ".join(owned[:limit])
    more = f" (and {len(owned) - limit} more)" if len(owned) > limit else ""
    return f"The pack holds: {shown}{more}."


# --------------------------------------------------------------------------- #
# use_item
# --------------------------------------------------------------------------- #

def validate_use_item(state: dict[str, Any], item_name: Any, qty: Any = 1) -> ValidationResult:
    """Checks that the Apostle actually carries `qty` of `item_name`.

    Rejects: bad/empty name, bad quantity, item not in the inventory,
    or fewer copies held than requested.
    """
    if not isinstance(item_name, str) or not item_name.strip():
        return _fail("No item was named.")
    if isinstance(qty, bool) or not isinstance(qty, int) or qty < 1:
        return _fail("The quantity must be a whole number of at least 1.")

    inventory = state.get("inventory") or {}
    key = _find_inventory_key(inventory, item_name)
    held = inventory.get(key, 0) if key is not None else 0

    if key is None or not isinstance(held, int) or held < 1:
        return _fail(f"There is no '{item_name.strip()}' in the pack. {_describe_inventory_hint(inventory)}")

    if held < qty:
        return _fail(f"Only {held} x {key} in the pack, but {qty} were asked for.", item=key)

    return ValidationResult(True, f"{qty} x {key} can be used.", item=key)


# --------------------------------------------------------------------------- #
# equip
# --------------------------------------------------------------------------- #

def validate_equip(state: dict[str, Any], item_name: Any, slot: Any = None) -> ValidationResult:
    """Checks that `item_name` can be equipped into `slot`.

    If `slot` is None, the item's own catalog slot is used.

    Rejects: bad/empty name, item not in the inventory, item that is not gear,
    unknown slot, slot that does not fit the item, and offhand choices that
    break the mainhand/offhand compatibility rules.
    """
    if not isinstance(item_name, str) or not item_name.strip():
        return _fail("No item was named.")

    inventory = state.get("inventory") or {}
    key = _find_inventory_key(inventory, item_name)
    held = inventory.get(key, 0) if key is not None else 0
    if key is None or not isinstance(held, int) or held < 1:
        return _fail(f"There is no '{item_name.strip()}' in the pack to equip. {_describe_inventory_hint(inventory)}")

    template = _EQUIPMENT_BY_NAME.get(key.lower())
    if template is None:
        return _fail(f"{key} is not something that can be worn or wielded.", item=key)

    valid_slots = _valid_slots(state)
    if slot is None:
        target = template.slot
    elif isinstance(slot, str) and slot.strip():
        target = _normalize_slot(slot)
        if target not in valid_slots:
            return _fail(f"'{slot.strip()}' is not an equipment slot. Valid slots: {', '.join(valid_slots)}.", item=key)
    else:
        return _fail("The slot must be a non-empty name.", item=key)

    if target not in valid_slots:
        return _fail(f"{key} belongs to a slot ('{target}') this Apostle does not have.", item=key)

    # A slot fits if it is the item's own slot, or if a one-handed item
    # (offhandable=True) is being placed in the offhand slot.
    fits = template.slot == target or (target == "offhand" and template.offhandable)
    if not fits:
        return _fail(f"{key} is {template.slot} gear and cannot go in the {target} slot.", item=key, slot=target)

    if target == "offhand":
        mainhand = (state.get("equipment") or {}).get("mainhand")
        if mainhand is None:
            return _fail(f"{key} needs a mainhand weapon first, and the hands are empty.", item=key, slot=target)
        if not can_equip_offhand(mainhand, template):
            mh_name = mainhand["name"] if isinstance(mainhand, dict) else mainhand.name
            return _fail(f"{key} cannot be paired with {mh_name} in the offhand.", item=key, slot=target)

    return ValidationResult(True, f"{key} can be equipped in the {target} slot.", item=key, slot=target)


# --------------------------------------------------------------------------- #
# go_to
# --------------------------------------------------------------------------- #

def _resolve_node(text: str) -> Optional[str]:
    """Node code ('nf') or full name ('Northern Front') -> canonical code, else None."""
    wanted = _normalize_slot(text)  # same cleanup: lowercase, letters/digits only
    for code, info in WORLD_NODES.items():
        if wanted == _normalize_slot(code) or wanted == _normalize_slot(info["name"]):
            return code
    return None


def _node_list(codes: list[str]) -> str:
    return ", ".join(f"{get_node_name(c)} ({c})" for c in codes)


def validate_go_to(state: dict[str, Any], location_name: Any) -> ValidationResult:
    """Checks that the Apostle may walk to `location_name` right now.

    Accepts a node code ("NF") or a full name ("Northern Front"), any casing.

    Rejects, in this order: bad/empty name, unknown place, Apostle already on
    the road, Apostle in combat, destination equals the current location, and
    destination not directly connected to the current location by MAP_EDGES.
    """
    if not isinstance(location_name, str) or not location_name.strip():
        return _fail("No destination was named.")

    dest = _resolve_node(location_name)
    if dest is None:
        return _fail(f"'{location_name.strip()}' is not a place in this realm. Known places: {_node_list(list(WORLD_NODES))}.")

    travel = state.get("travel")
    if travel:
        going_to = travel.get("to") if isinstance(travel, dict) else None
        where = f" to {get_node_name(going_to)}" if going_to else ""
        return _fail(f"The Apostle is already on the road{where} and cannot change course mid-journey.", destination=dest)

    if state.get("active_enemy") is not None:
        return _fail("The Apostle is in the middle of a fight and cannot simply walk away.", destination=dest)

    current = state.get("current_location")
    if current not in WORLD_NODES:
        return _fail("The Apostle's current location is unknown, so no route can be checked.", destination=dest)

    if dest == current:
        return _fail(f"The Apostle is already in {get_node_name(current)}.", destination=dest)

    neighbors = get_neighbors(current)
    if dest not in neighbors:
        return _fail(
            f"{get_node_name(dest)} is not directly connected to {get_node_name(current)}. "
            f"Reachable from here: {_node_list(neighbors)}.",
            destination=dest,
        )

    return ValidationResult(True, f"{get_node_name(dest)} is one road away from {get_node_name(current)}.", destination=dest)


# --------------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------------- #

VALIDATED_ACTIONS = ("go_to", "use_item", "equip")
_NULL_NAMES = ("", "null", "none")


def _with_action(result: ValidationResult, action: str) -> ValidationResult:
    return ValidationResult(result.ok, result.reason, result.item, result.slot, result.destination, action)


def validate_action(state: dict[str, Any], name: Any, param: Any = None) -> ValidationResult:
    """Routes an AI action to the right validator.

    name:  "go_to", "use_item" or "equip" (casing, spaces and hyphens are
           forgiven: "Use Item" -> "use_item"). None / "null" means the AI chose
           no action, which is always fine and is returned as ok with action=None.
    param: a string (the location or item name), or a dict for extra detail:
             go_to    {"location": "NF"}
             use_item {"item": "Wolf Fur", "qty": 2}
             equip    {"item": "Buckler", "slot": "offhand"}

    Any other action name is rejected, because this module has no rules for it
    (attack and flee, for example, are not covered here).
    """
    if name is None:
        return ValidationResult(True, "No action to validate.")
    if not isinstance(name, str):
        return _fail("The action name must be text.")

    action = "_".join(name.strip().lower().replace("-", " ").split())
    if action in _NULL_NAMES:
        return ValidationResult(True, "No action to validate.")
    if action not in VALIDATED_ACTIONS:
        return _fail(f"'{name.strip()}' is not an action this validator knows. Known actions: {', '.join(VALIDATED_ACTIONS)}.")

    if isinstance(param, str):
        fields: dict[str, Any] = {}
        main = param
    elif isinstance(param, dict):
        fields = param
        main = param.get("location") if action == "go_to" else param.get("item")
    else:
        return _with_action(_fail(f"{action} needs a name as its parameter."), action)

    if action == "go_to":
        result = validate_go_to(state, main)
    elif action == "use_item":
        result = validate_use_item(state, main, fields.get("qty", 1))
    else:  # equip
        result = validate_equip(state, main, fields.get("slot"))
    return _with_action(result, action)