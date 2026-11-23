import random
from dataclasses import replace
from core.models import Equipment
from data.catalog import EQUIPMENTS, MONSTERS
from data.quest_catalog import roll_new_quest

def _create_starter_equipment() -> dict[str, Equipment | None]:
    mainhand_pool = [eq for eq in EQUIPMENTS if eq.slot == "mainhand"]
    starter_mainhand = (
        replace(random.choice(mainhand_pool), bonus=1) if mainhand_pool else None
    )

    garb_template = next(
        (eq for eq in EQUIPMENTS if eq.name == "Adventurer's Garb" and eq.slot == "body"),
        Equipment("Adventurer's Garb", slot="body"),
    )
    starter_body = replace(garb_template, bonus=1)

    return {
        "mainhand": starter_mainhand,
        "offhand": None,
        "body": starter_body,
        "special": None,
        "additional": None,
    }

def create_initial_state(
    god_name: str = "Insatiable Golden Pothos",
    apostle: str = "Seraph",
    ) -> dict:
    starter_eq = _create_starter_equipment()
    starting_hp = 50 + (starter_eq["body"].bonus if starter_eq["body"] else 0)
    initial_quest = roll_new_quest(MONSTERS)
    return {
        "god_name": god_name,
        "apostle": apostle,

        "lvl": 1,
        "exp": 0,
        "exp_req": 100,
        "max_hp": starting_hp,
        "cur_hp": starting_hp,

        "quest": initial_quest["title"],
        "quest_data": initial_quest,
        "quest_progress": 0,
        "gold": 0,
        "monster_defeated": 0,
        "death_count": 0,

        "inventory": {},

        "current_action": "Awaiting divine guidance...",
        "action_progress": 0,
        "active_enemy": None,
        "logbook": [
            f"[00:00] {apostle} awakens under the gaze of {god_name}."
        ],

        "godpower": 100,

        "map_nodes": ["NF", "WW", "OE", "MF"],
        "current_location": "NF",
        "wild_stay_stacks": 0,
        "travel": None,

        "equipment": starter_eq,
    }