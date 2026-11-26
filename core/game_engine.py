import random
import time
from datetime import datetime
from core.log_generator import add_log
from core.models import Equipment, ActiveMonster
from core.monster_engine import roll_rewards, spawn_monster, calculate_monster_exp
from data.catalog import EQUIPMENTS, EXTRA, MONSTERS, SELL_PRICE_LOOKUP
from data.world_map import get_neighbors, get_node_name, get_node_zone
from core.equipment_rules import (
    _recalc_max_hp,
    can_equip_offhand,
    get_equipment_stats,
    roll_equipment_drop,
    try_auto_equip,
)
from data.quest_catalog import roll_new_quest
from core.action_validator import VALIDATED_ACTIONS, validate_action
from core.prompts import ApostlePacket

TIER_REWARDS = {
    "normal": {"exp": 25, "quest": 20, "base_atk": 4},
    "mini_boss": {"exp": 60, "quest": 35, "base_atk": 8},
    "boss": {"exp": 150, "quest": 50, "base_atk": 13},
}
IMPORTANT_MARKER = "★"

_EQUIPMENT_BY_NAME = {eq.name.lower(): eq for eq in EQUIPMENTS}
AUTO_EVENT_INTERVAL_SEC = 30.0

def _log_raw(state: dict, message: str, max_entries: int = 50) -> None:
    timestamp = datetime.now().strftime("%H:%M")
    state["logbook"].append(f"[{timestamp}] {message}")
    if len(state["logbook"]) > max_entries:
        state["logbook"] = state["logbook"][-max_entries:]

def _log_important(state: dict, message: str) -> None:
    """Logs a message to both the rolling logbook and the permanent important log."""
    timestamp = datetime.now().strftime("%H:%M")
    entry = f"[{timestamp}] {IMPORTANT_MARKER} {message}"

    state["logbook"].append(entry)
    if len(state["logbook"]) > 50:
        state["logbook"] = state["logbook"][-50:]

    state.setdefault("important_logbook", []).append(entry)

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
        Level_up_msg = (
            f"LEVEL UP! {state['apostle']} reached Level {state['lvl']} "
            f"(Max HP: {state['max_hp']})!"
        )
        _log_important(state,Level_up_msg)


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
        gp_gain = {"normal": 3, "mini_boss": 10, "boss": 25}.get(enemy.tier, 3)
        state["godpower"] = min(100, state["godpower"] + gp_gain)

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
        kill_msg = f"{apostle} dealt {dmg_dealt} dmg and defeated {enemy.name}! (+{exp_gained} EXP){loot_text}"
        if enemy.tier in ("mini_boss", "boss"):
            _log_important(state, kill_msg)
        _log_raw(state,kill_msg)

        _grant_exp(state, exp_gained)
        state["active_enemy"] = None
        state["action_progress"] = 0
        state["current_action"] = f"Catching a breath in {get_node_name(state['current_location'])}..."
        if q_type == "boss_hunt" and state["quest_progress"] >= 100:
            _complete_quest(state, "wild")
            state["godpower"] = min(100, state["godpower"] + (20 if q_type == "boss_hunt" else 12))
        return

    raw_dmg = _get_enemy_attack(enemy)
    dmg_taken = max(1, raw_dmg)
    state["cur_hp"] = max(0, state["cur_hp"] - dmg_taken)

    if state["cur_hp"] <= 0:
        state["death_count"] += 1
        death_msg = (f"{enemy.name} landed a fatal blow ({dmg_taken} dmg)! "
                    f"{apostle} blacked out and woke up back in Northern Front.")
        _log_important(state, death_msg)
        _log_raw(state, death_msg)
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
    if state.get("quest") is None:
        _assign_new_quest(state, "city")
        return
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
    if state["gold"] >= 150:
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
        _run_window_shopping(state, is_whisper=False)

    elif event == "depart":
        neighbors = get_neighbors(state["current_location"])
        _start_travel(state, random.choice(neighbors))

    else:
        add_log(state, "city", "wandering")
        state["current_action"] = f"Strolling through {get_node_name(state['current_location'])}..."


def _handle_wild_event(state: dict) -> None:
    if state.get("quest") is None:
        _assign_new_quest(state, "wild")
        return
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


def run_game_tick(state: dict, *, force_step: bool = False) -> None:
    now = time.time()
    if state.get("active_enemy") is not None:
        _resolve_combat_tick(state)
        state["next_auto_tick_at"] = now + AUTO_EVENT_INTERVAL_SEC
        return

    is_traveling = state.get("travel") is not None
    zone = get_node_zone(state["current_location"])
    q_data = state.get("quest_data") or {}
    if zone != "city" and q_data.get("type") == "absurd":
        elapsed = now - q_data.get("start_time", now)
        duration = max(1, q_data.get("duration_sec", 120))
        state["quest_progress"] = min(100, int((elapsed / duration) * 100))

    next_tick_at = state.get("next_auto_tick_at", 0.0)
    if not force_step and now < next_tick_at:
        remaining = next_tick_at - now
        elapsed_in_cycle = max(0.0, AUTO_EVENT_INTERVAL_SEC - remaining)
        state["action_progress"] = min(99, int((elapsed_in_cycle / AUTO_EVENT_INTERVAL_SEC) * 100))
        return

    state["next_auto_tick_at"] = now + AUTO_EVENT_INTERVAL_SEC
    state["action_progress"] = 0
    state["godpower"] = min(100, state["godpower"] + 1)

    if not is_traveling and zone == "city":
        state["godpower"] = min(100, state["godpower"] + 1)
        if state["cur_hp"] < state["max_hp"]:
            state["cur_hp"] = min(state["max_hp"], state["cur_hp"] + 10)

    if not is_traveling and random.random() < 0.35:
        add_log(state, "idle")
        return

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
        if equipped:
            _log_important(
                state,
                f"Equipping {eq.name}"
            )
        bonus_loot.append(f"{eq.name} +{eq.bonus}{tag}")

    if EXTRA and random.random() < extra_chance:
        extra_item = random.choice(EXTRA)
        qty = random.randint(1, 2)
        state["inventory"][extra_item.name] = state["inventory"].get(extra_item.name, 0) + qty
        bonus_loot.append(f"{extra_item.name} x{qty}")

    if q_type == "absurd" and q_data.get("completion_log"):
        story = q_data["completion_log"].format(apostle=state["apostle"])
        loot_str = f" Bonus: {', '.join(bonus_loot)}." if bonus_loot else ""
        comquest_msg = f"QUEST COMPLETE ({state['quest']}): {story} (+{reward_gold}g){loot_str}"
        _log_important(state, comquest_msg)
        _log_raw(state,comquest_msg)
    else:
        add_log(state, zone, "quest_complete", quest=state["quest"], gold=reward_gold)
        if bonus_loot:
            _log_raw(state, f"Quest Bonus Rewards: {', '.join(bonus_loot)}.")

    new_q = roll_new_quest(MONSTERS, zone)
    state["quest"] = new_q["title"]
    state["quest_data"] = new_q
    state["quest_progress"] = 0
    add_log(state, zone, "quest_found", quest=state["quest"])
    _log_important(state, f"New quest accepted: '{state['quest']}'.")
    state["current_action"] = "Preparing for the next quest..."

def _assign_new_quest(state: dict, zone: str) -> None:
    new_q = roll_new_quest(MONSTERS, zone)
    state["quest"] = new_q["title"]
    state["quest_data"] = new_q
    state["quest_progress"] = 0
    add_log(state, zone, "quest_found", quest=state["quest"])
    _log_important(state, f"New quest accepted: '{state['quest']}'.")
    state["current_action"] = "Preparing for the new quest..."

def _consume_inventory_item(state: dict, item_name: str, qty: int = 1) -> None:
    inv = state["inventory"]
    remaining = inv.get(item_name, 0) - qty
    if remaining <= 0:
        inv.pop(item_name, None)
    else:
        inv[item_name] = remaining

def execute_ai_action(state: dict, packet: ApostlePacket) -> bool:
    action = packet.action
    target = packet.target if packet.target != "none" else None

    if action == "idle":
        return False

    if action in VALIDATED_ACTIONS:
        param = {"location": target} if action == "go_to" else {"item": target}
        verdict = validate_action(state, action, param)
        if not verdict.ok:
            _log_raw(state, f"({state['apostle']} hesitated: {verdict.reason})")
            return False

        if action == "go_to" and verdict.destination:
            _start_travel(state, verdict.destination)
            state["next_auto_tick_at"] = time.time() + AUTO_EVENT_INTERVAL_SEC
            state["action_progress"] = 0
            return True

        if action == "equip" and verdict.item and verdict.slot:
            template = _EQUIPMENT_BY_NAME.get(verdict.item.lower())
            if template is None:
                return False
            rolled = roll_equipment_drop(template, state["lvl"])
            eq = state["equipment"]
            old_item = eq.get(verdict.slot)

            _consume_inventory_item(state, verdict.item, 1)
            eq[verdict.slot] = rolled

            if old_item is not None:
                state["inventory"][old_item.name] = state["inventory"].get(old_item.name, 0) + 1

            if verdict.slot == "mainhand" and eq.get("offhand") is not None:
                if not can_equip_offhand(rolled, eq["offhand"]):
                    old_off = eq["offhand"]
                    eq["offhand"] = None
                    state["inventory"][old_off.name] = state["inventory"].get(old_off.name, 0) + 1

            _recalc_max_hp(state)
            msg = f"{state['apostle']} equipped {rolled.name} +{rolled.bonus} ({verdict.slot})."
            _log_raw(state, msg)
            _log_important(state, msg)
            state["current_action"] = f"Equipped {rolled.name}!"
            state["next_auto_tick_at"] = time.time() + AUTO_EVENT_INTERVAL_SEC
            state["action_progress"] = 0
            return True

        if action == "use_item" and verdict.item:
            _consume_inventory_item(state, verdict.item, 1)
            if "apple" in verdict.item.lower() or "potion" in verdict.item.lower():
                heal = max(15, round(state["max_hp"] * 0.35))
            else:
                heal = max(8, round(state["max_hp"] * 0.15))
            old_hp = state["cur_hp"]
            state["cur_hp"] = min(state["max_hp"], state["cur_hp"] + heal)
            gained = state["cur_hp"] - old_hp
            _log_raw(
                state,
                f"{state['apostle']} used {verdict.item} and recovered {gained} HP!",
            )
            state["current_action"] = f"Used {verdict.item}!"
            state["next_auto_tick_at"] = time.time() + AUTO_EVENT_INTERVAL_SEC
            state["action_progress"] = 0
            return True

    if action == "attack":
        if state.get("active_enemy") is None:
            return False
        _resolve_combat_tick(state)
        state["next_auto_tick_at"] = time.time() + AUTO_EVENT_INTERVAL_SEC
        state["action_progress"] = 0
        return True

    if action == "flee":
        enemy = state.get("active_enemy")
        if enemy is None:
            return False
        if random.random() < 0.70:
            _log_raw(state, f"{state['apostle']} fled from {enemy.name}!")
            state["active_enemy"] = None
            state["action_progress"] = 0
            state["current_action"] = f"Catching breath in {get_node_name(state['current_location'])}..."
        else:
            _log_raw(state, f"{state['apostle']} tried to flee from {enemy.name}, but got cornered!")
            _resolve_combat_tick(state)
        state["next_auto_tick_at"] = time.time() + AUTO_EVENT_INTERVAL_SEC
        state["action_progress"] = 0
        return True

    zone = get_node_zone(state["current_location"])
    is_traveling = state.get("travel") is not None

    if action == "rest":
        if state.get("active_enemy") is not None:
            return False
        heal = max(10, round(state["max_hp"] * 0.25))
        state["cur_hp"] = min(state["max_hp"], state["cur_hp"] + heal)
        _log_raw(state, f"{state['apostle']} took a quick breather and recovered {heal} HP.")
        state["current_action"] = "Resting..."
        state["next_auto_tick_at"] = time.time() + AUTO_EVENT_INTERVAL_SEC
        state["action_progress"] = 0
        return True

    if action == "explore":
        if state.get("active_enemy") is not None:
            return False
        state["action_progress"] = 0
        if is_traveling:
            _handle_road_event(state)
        elif zone == "city":
            add_log(state, "city", "wandering")
            state["current_action"] = f"Exploring {get_node_name(state['current_location'])}..."
        else:
            _handle_wild_event(state)
        state["next_auto_tick_at"] = time.time() + AUTO_EVENT_INTERVAL_SEC
        state["action_progress"] = 0
        return True

    if action == "sell_items":
        if is_traveling or zone != "city" or not state["inventory"]:
            return False
        item_name = target if target in state["inventory"] else random.choice(list(state["inventory"].keys()))
        qty = state["inventory"].pop(item_name)
        unit_price = SELL_PRICE_LOOKUP.get(item_name, 10)
        gold_earned = qty * unit_price
        state["gold"] += gold_earned
        add_log(state, "city", "selling", item=item_name, qty=qty, gold=gold_earned)
        state["current_action"] = "Haggling at the market..."
        state["next_auto_tick_at"] = time.time() + AUTO_EVENT_INTERVAL_SEC
        state["action_progress"] = 0
        return True

    if action == "buy_gear":
        if is_traveling or zone != "city":
            return False
        _run_window_shopping(state, is_whisper=True, target_name=target)
        state["next_auto_tick_at"] = time.time() + AUTO_EVENT_INTERVAL_SEC
        state["action_progress"] = 0
        return True

    return False

def _is_upgrade_for_apostle(state: dict, candidate: Equipment) -> bool:
    eq = state["equipment"]
    slot = candidate.slot

    if slot == "offhand":
        if not can_equip_offhand(eq.get("mainhand"), candidate):
            return False
        cur_off = eq.get("offhand")
        return cur_off is None or candidate.bonus > cur_off.bonus

    cur_item = eq.get(slot)
    if cur_item is None or candidate.bonus > cur_item.bonus:
        return True

    # Offhandable mainhand weapon check (e.g., dual-wielding OHS)
    if slot == "mainhand" and can_equip_offhand(cur_item, candidate):
        cur_off = eq.get("offhand")
        return cur_off is None or candidate.bonus > cur_off.bonus

    return False

def _run_window_shopping(
    state: dict,
    *,
    is_whisper: bool = False,
    target_name: str | None = None,
) -> bool:
    if not EQUIPMENTS:
        return False

    pool = list(EQUIPMENTS)
    chosen_templates: list[Equipment] = []

    if target_name:
        matched = [eq for eq in pool if eq.name.lower() == target_name.lower()]
        if matched:
            chosen_templates.append(matched[0])
            pool.remove(matched[0])

    sample_count = min(3 - len(chosen_templates), len(pool))
    chosen_templates.extend(random.sample(pool, k=sample_count))

    stalls: list[tuple[Equipment, int, bool, bool]] = []
    for tmpl in chosen_templates:
        rolled = roll_equipment_drop(tmpl, state["lvl"])
        cost = 150 * rolled.bonus
        is_upg = _is_upgrade_for_apostle(state, rolled)
        is_targeted = bool(target_name and rolled.name.lower() == target_name.lower())
        stalls.append((rolled, cost, is_upg, is_targeted))

    display_str = ", ".join(
        f"{eq.name} +{eq.bonus} ({cost}g{' ★' if upg else ''})"
        for eq, cost, upg, _ in stalls
    )
    _log_raw(
        state,
        f"{state['apostle']} window-shops in {get_node_name(state['current_location'])}: {display_str}.",
    )

    sorted_stalls = sorted(stalls, key=lambda x: (x[2], x[3], x[0].bonus), reverse=True)

    for eq, cost, is_upg, is_targeted in sorted_stalls:
        if state["gold"] < cost:
            continue

        if is_whisper:
            buy_chance = 1.0 if (is_upg or is_targeted) else 0.35
        else:
            buy_chance = 0.75 if is_upg else 0.15

        if random.random() < buy_chance:
            state["gold"] -= cost
            equipped = try_auto_equip(state, eq, force=not is_upg)
            tag = " [Equipped!]" if equipped else ""
            log_event = "buying" if is_upg else "buying_weaker"
            add_log(
                state,
                "city",
                log_event,
                item=f"{eq.name} +{eq.bonus}{tag}",
                gold=cost,
            )
            if equipped and is_upg:
                _log_important(
                    state,
                    f"Bought and equipped {eq.name} +{eq.bonus} ({cost}g).",
                )
            state["current_action"] = (
                f"Showing off {eq.name}..." if (equipped and not is_upg)
                else f"Equipping {eq.name}..." if equipped
                else "Inspecting newly bought gear..."
            )
            return True

    cheapest = min(cost for _, cost, _, _ in stalls)
    if state["gold"] < cheapest:
        _log_raw(state, f"{state['apostle']} sighs at the price tags and keeps walking (need at least {cheapest}g).")
    else:
        _log_raw(state, f"{state['apostle']} decides nothing on the rack is worth the gold today.")
    state["current_action"] = f"Window-shopping in {get_node_name(state['current_location'])}..."
    return False