import random
import time
from datetime import datetime
from core.log_generator import add_log
from core.models import ActiveMonster
from core.monster_engine import roll_rewards, spawn_monster, calculate_monster_exp
from data.catalog import EQUIPMENTS, EXTRA, MONSTERS, SELL_PRICE_LOOKUP
from data.world_map import get_neighbors, get_node_name, get_node_zone
from core.equipment_rules import (
    get_equipment_stats,
    roll_equipment_drop,
    try_auto_equip,
)
from data.quest_catalog import roll_new_quest

TIER_REWARDS = {
    "normal": {"exp": 25, "quest": 20, "base_atk": 4},
    "mini_boss": {"exp": 60, "quest": 35, "base_atk": 8},
    "boss": {"exp": 150, "quest": 50, "base_atk": 13},
}


def _log_raw(state: dict, message: str, max_entries: int = 50) -> None:
    timestamp = datetime.now().strftime("%H:%M")
    state["logbook"].append(f"[{timestamp}] {message}")
    if len(state["logbook"]) > max_entries:
        state["logbook"] = state["logbook"][-max_entries:]


def _get_apostle_attack(state: dict) -> int:
    dmg_bonus = get_equipment_stats(state["equipment"])["dmg"]
    base = 10 + (state["lvl"] * 3) + dmg_bonus
    return max(1, round(base * random.uniform(0.85, 1.15)))


def _get_enemy_attack(enemy: ActiveMonster) -> int:
    base = TIER_REWARDS[enemy.tier]["base_atk"] + (enemy.level * 2)
    return max(1, round(base * enemy.dmg_mult * random.uniform(0.8, 1.2)))


def _grant_exp(state: dict, amount: int) -> None:
    state["exp"] += amount
    while state["exp"] >= state["exp_req"]:
        state["exp"] -= state["exp_req"]
        state["lvl"] += 1
        state["exp_req"] = round(state["exp_req"] * 1.4)
        body_hp = get_equipment_stats(state["equipment"])["hp"]
        state["max_hp"] = 50 + (state["lvl"] - 1) * 15 + body_hp
        state["cur_hp"] = state["max_hp"]
        _log_raw(
            state,
            f"LEVEL UP! {state['apostle']} reached Level {state['lvl']} "
            f"(Max HP: {state['max_hp']})!",
        )


def _resolve_combat_tick(state: dict) -> None:
    enemy: ActiveMonster = state["active_enemy"]
    apostle = state["apostle"]

    dmg_dealt = _get_apostle_attack(state)
    enemy.cur_hp = max(0, enemy.cur_hp - dmg_dealt)

    if enemy.cur_hp <= 0:
        state["monster_defeated"] += 1
        tier_cfg = TIER_REWARDS[enemy.tier]
        q_data = state.get("quest_data", {"type": "standard"})
        q_type = q_data.get("type", "standard")

        if q_type == "boss_hunt":
            if enemy.name == q_data.get("target_boss"):
                state["quest_progress"] = 100
        elif q_type == "standard":
            state["quest_progress"] = min(100, state["quest_progress"] + tier_cfg["quest"])

        rewards = roll_rewards(enemy, EQUIPMENTS, apostle_lvl=state["lvl"])
        loot_names: list[str] = []

        for item_name, qty in rewards["sellables"].items():
            state["inventory"][item_name] = state["inventory"].get(item_name, 0) + qty
            loot_names.append(f"{item_name} x{qty}")

        for eq in rewards["equipment"]:
            equipped = try_auto_equip(state, eq)
            tag = " [Equipped!]" if equipped else ""
            loot_names.append(f"{eq.name} +{eq.bonus}{tag}")

        loot_text = f" Looted: {', '.join(loot_names)}." if loot_names else ""
        exp_gained = calculate_monster_exp(enemy.tier, enemy.level)
        _log_raw(
            state,
            f"{apostle} dealt {dmg_dealt} dmg and defeated {enemy.name}! "
            f"(+{exp_gained} EXP){loot_text}",
        )

        _grant_exp(state, exp_gained)
        state["active_enemy"] = None
        state["action_progress"] = 0
        state["current_action"] = f"Catching a breath in {get_node_name(state['current_location'])}..."
        if q_type == "boss_hunt" and state["quest_progress"] >= 100:
            _complete_quest(state, "wild")
        return

    raw_dmg = _get_enemy_attack(enemy)
    dmg_taken = max(1, raw_dmg)
    state["cur_hp"] = max(0, state["cur_hp"] - dmg_taken)

    if state["cur_hp"] <= 0:
        state["death_count"] += 1
        _log_raw(
            state,
            f"{enemy.name} landed a fatal blow ({dmg_taken} dmg)! "
            f"{apostle} blacked out and woke up back in Northern Front.",
        )
        state["active_enemy"] = None
        state["travel"] = None
        state["current_location"] = "NF"
        state["wild_stay_stacks"] = 0
        state["cur_hp"] = state["max_hp"]
        state["action_progress"] = 0
        state["current_action"] = "Recovering in Northern Front..."
        return

    _log_raw(
        state,
        f"{apostle} hits {enemy.name} for {dmg_dealt} dmg! "
        f"{enemy.name} strikes back for {dmg_taken} dmg.",
    )
    state["current_action"] = f"Fighting {enemy.name}!"


def _handle_city_event(state: dict) -> None:
    if state["quest_progress"] >= 100:
        _complete_quest(state, "city")
        return

    if state.get("quest_data", {}).get("type") == "absurd":
        wild_neighbors = [n for n in get_neighbors(state["current_location"]) if get_node_zone(n) != "city"]
        if wild_neighbors:
            _start_travel(state, random.choice(wild_neighbors))
            return

    choices = ["wandering", "wandering"]
    if state["inventory"]:
        choices.extend(["selling", "selling"])
    if state["gold"] >= 50:
        choices.append("buying")
    if random.random() < 0.30:
        choices.append("depart")

    event = random.choice(choices)

    if event == "selling":
        item_name = random.choice(list(state["inventory"].keys()))
        qty = state["inventory"].pop(item_name)
        unit_price = SELL_PRICE_LOOKUP.get(item_name, 10)
        gold_earned = qty * unit_price
        state["gold"] += gold_earned
        add_log(state, "city", "selling", item=item_name, qty=qty, gold=gold_earned)
        state["current_action"] = "Haggling at the market..."

    elif event == "buying":
        if EQUIPMENTS:
            template = random.choice(EQUIPMENTS)
            bought_eq = roll_equipment_drop(template, state["lvl"])
            cost = random.randint(25, min(100, state["gold"]))
            state["gold"] -= cost
            equipped = try_auto_equip(state, bought_eq)
            tag = " [Equipped!]" if equipped else ""
            add_log(
                state,
                "city",
                "buying",
                item=f"{bought_eq.name} +{bought_eq.bonus}{tag}",
                gold=cost,
            )
            state["current_action"] = (
                f"Equipping {bought_eq.name}..." if equipped else "Inspecting newly bought gear..."
            )
        else:
            item = "Health Potion"
            cost = random.randint(25, min(100, state["gold"]))
            state["gold"] -= cost
            state["inventory"][item] = state["inventory"].get(item, 0) + 1
            add_log(state, "city", "buying", item=item, gold=cost)
            state["current_action"] = "Inspecting newly bought gear..."

    elif event == "depart":
        neighbors = get_neighbors(state["current_location"])
        _start_travel(state, random.choice(neighbors))

    else:
        add_log(state, "city", "wandering")
        state["current_action"] = f"Strolling through {get_node_name(state['current_location'])}..."


def _handle_wild_event(state: dict) -> None:
    q_data = state.get("quest_data", {"type": "standard"})

    if q_data.get("type") == "absurd":
        elapsed = time.time() - q_data.get("start_time", time.time())
        duration = max(1, q_data.get("duration_sec", 120))
        state["quest_progress"] = min(100, int((elapsed / duration) * 100))

    if state["quest_progress"] >= 100:
        _complete_quest(state, "wild")
        return

    roll = random.random()

    if roll < 0.25:
        state["wild_stay_stacks"] = state.get("wild_stay_stacks", 0) + 1
        add_log(state, "wild", "wandering")
        if q_data.get("type") == "standard":
            state["quest_progress"] = min(100, state["quest_progress"] + 15)
        state["current_action"] = f"Exploring {get_node_name(state['current_location'])}..."

    elif roll < 0.38:
        state["wild_stay_stacks"] = state.get("wild_stay_stacks", 0) + 1
        item = random.choice(["Potum Silver Coin", "Golden Apple", "Colon Leaf", "Wolf Fur"])
        gold_found = random.randint(5, 25)
        state["gold"] += gold_found
        state["inventory"][item] = state["inventory"].get(item, 0) + 1
        add_log(state, "wild", "found_treasure", item=item, gold=gold_found)
        state["current_action"] = "Stuffing loot into the backpack..."

    elif roll < 0.88:
        stacks = state.get("wild_stay_stacks", 0)
        enemy = spawn_monster(
            apostle_lvl=state["lvl"],
            monsters_catalog=MONSTERS,
            wild_stay_stacks=stacks,
        )
        if (
            q_data.get("type") == "boss_hunt"
            and enemy.tier == "boss"
            and random.random() < 0.60
        ):
            target_pool = [m for m in MONSTERS if m.name == q_data.get("target_boss")]
            if target_pool:
                enemy = spawn_monster(state["lvl"], target_pool, wild_stay_stacks=stacks)
        state["active_enemy"] = enemy

        if enemy.tier in ("mini_boss", "boss"):
            state["wild_stay_stacks"] = 0
        else:
            state["wild_stay_stacks"] = stacks + 1

        event_key = f"encounter_{enemy.tier}"
        add_log(state, "wild", event_key, enemy=enemy.name)
        state["current_action"] = f"Fighting {enemy.name}!"

    else:
        neighbors = get_neighbors(state["current_location"])
        if q_data.get("type") == "absurd":
            wild_neighbors = [n for n in neighbors if get_node_zone(n) != "city"]
            if wild_neighbors:
                _start_travel(state, random.choice(wild_neighbors))
            else:
                add_log(state, "wild", "wandering")
                state["current_action"] = f"Refusing to go to town until '{state['quest']}' is done..."
        else:
            _start_travel(state, random.choice(neighbors))


def run_game_tick(state: dict) -> None:
    state["godpower"] = min(100, state["godpower"] + 2)

    if state.get("active_enemy") is not None:
        _resolve_combat_tick(state)
        return

    is_traveling = state.get("travel") is not None
    zone = get_node_zone(state["current_location"])
    q_data = state.get("quest_data", {})
    if zone != "city" and q_data.get("type") == "absurd":
        elapsed = time.time() - q_data.get("start_time", time.time())
        duration = max(1, q_data.get("duration_sec", 120))
        state["quest_progress"] = min(100, int((elapsed / duration) * 100))

    if not is_traveling and zone == "city" and state["cur_hp"] < state["max_hp"]:
        state["cur_hp"] = min(state["max_hp"], state["cur_hp"] + 10)

    state["action_progress"] += 50

    if state["action_progress"] < 100:
        if random.random() < 0.45:
            add_log(state, "idle")
        return

    state["action_progress"] = 0
    if is_traveling:
        _handle_road_event(state)
    elif zone == "city":
        _handle_city_event(state)
    else:
        _handle_wild_event(state)

def _start_travel(state: dict, destination: str, steps: int = 3) -> None:
    """Puts the Apostle onto the road between current_location and destination."""
    origin = state["current_location"]
    state["travel"] = {
        "from": origin,
        "to": destination,
        "progress": 0,
        "steps": steps,
    }
    state["wild_stay_stacks"] = 0
    state["current_action"] = f"Traveling to {get_node_name(destination)}..."
    _log_raw(
        state,
        f"{state['apostle']} sets out on the road from "
        f"{get_node_name(origin)} toward {get_node_name(destination)}.",
    )


def _handle_road_event(state: dict) -> None:
    """Advances the Apostle one step along the road, with a chance of wild encounters."""
    travel = state["travel"]
    travel["progress"] += 1

    if travel["progress"] >= travel["steps"]:
        dest = travel["to"]
        state["current_location"] = dest
        state["travel"] = None
        state["wild_stay_stacks"] = 0
        dest_zone = get_node_zone(dest)
        state["current_action"] = f"Arrived at {get_node_name(dest)}!"
        _log_raw(state, f"{state['apostle']} arrives at {get_node_name(dest)}.")
        add_log(state, dest_zone, "wandering")
        return

    dest_name = get_node_name(travel["to"])
    if random.random() < 0.50:
        stacks = state.get("wild_stay_stacks", 0)
        enemy = spawn_monster(
            apostle_lvl=state["lvl"],
            monsters_catalog=MONSTERS,
            wild_stay_stacks=stacks,
        )
        state["active_enemy"] = enemy
        if enemy.tier in ("mini_boss", "boss"):
            state["wild_stay_stacks"] = 0
        else:
            state["wild_stay_stacks"] = stacks + 1

        add_log(state, "wild", f"encounter_{enemy.tier}", enemy=enemy.name)
        state["current_action"] = f"Ambushed on the road by {enemy.name}!"
    else:
        _log_raw(
            state,
            f"{state['apostle']} marches along the road toward {dest_name} "
            f"({travel['progress']}/{travel['steps']}).",
        )
        state["current_action"] = f"Walking to {dest_name}..."

def _complete_quest(state: dict, zone: str) -> None:
    q_data = state.get("quest_data", {"type": "standard"})
    q_type = q_data.get("type", "standard")

    if q_type == "boss_hunt":
        reward_gold = random.randint(120, 220)
        equip_chance = 0.75
        extra_chance = 0.80
    else:
        reward_gold = random.randint(40, 120)
        equip_chance = 0.35
        extra_chance = 0.60

    state["gold"] += reward_gold
    bonus_loot: list[str] = []

    if EQUIPMENTS and random.random() < equip_chance:
        eq = roll_equipment_drop(random.choice(EQUIPMENTS), state["lvl"])
        equipped = try_auto_equip(state, eq)
        tag = " [Equipped!]" if equipped else ""
        bonus_loot.append(f"{eq.name} +{eq.bonus}{tag}")

    if EXTRA and random.random() < extra_chance:
        extra_item = random.choice(EXTRA)
        qty = random.randint(1, 2)
        state["inventory"][extra_item.name] = state["inventory"].get(extra_item.name, 0) + qty
        bonus_loot.append(f"{extra_item.name} x{qty}")

    if q_type == "absurd" and q_data.get("completion_log"):
        story = q_data["completion_log"].format(apostle=state["apostle"])
        loot_str = f" Bonus: {', '.join(bonus_loot)}." if bonus_loot else ""
        _log_raw(
            state,
            f"QUEST COMPLETE ({state['quest']}): {story} (+{reward_gold}g){loot_str}",
        )
    else:
        add_log(state, zone, "quest_complete", quest=state["quest"], gold=reward_gold)
        if bonus_loot:
            _log_raw(state, f"Quest Bonus Rewards: {', '.join(bonus_loot)}.")

    new_q = roll_new_quest(MONSTERS)
    state["quest"] = new_q["title"]
    state["quest_data"] = new_q
    state["quest_progress"] = 0
    add_log(state, zone, "quest_found", quest=state["quest"])
    state["current_action"] = "Preparing for the next quest..."