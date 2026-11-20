import random
from datetime import datetime
from typing import Literal

from data.log_catalog import CITY_LOGS, IDLE_CHATTER, WILD_LOGS

LogZone = Literal["city", "wild", "idle"]


def format_log_entry(
    state: dict,
    zone: LogZone,
    event: str = "",
    *,
    item: str = "",
    qty: int = 1,
    gold: int = 0,
    enemy: str = "",
    quest: str | None = None,
) -> str:
    """Picks a random hard-coded template and returns a timestamped log line."""
    if zone == "idle":
        pool = IDLE_CHATTER
    elif zone == "city":
        pool = CITY_LOGS.get(event, CITY_LOGS["wandering"])
    elif zone == "wild":
        pool = WILD_LOGS.get(event, WILD_LOGS["wandering"])
    else:
        pool = IDLE_CHATTER

    template = random.choice(pool)
    timestamp = datetime.now().strftime("%H:%M")

    message = template.format(
        apostle=state.get("apostle", "Apostle"),
        god=state.get("god_name", "The Sky-Voice"),
        location=state.get("current_location", "Unknown"),
        quest=quest if quest is not None else state.get("quest", "Mystery Quest"),
        item=item,
        qty=qty,
        gold=gold,
        enemy=enemy,
    )
    return f"[{timestamp}] {message}"


def add_log(
    state: dict,
    zone: LogZone,
    event: str = "",
    max_entries: int = 50,
    **kwargs,
) -> str:
    """Generates a log line, appends it to state['logbook'], and trims old entries."""
    entry = format_log_entry(state, zone, event, **kwargs)
    state["logbook"].append(entry)
    if len(state["logbook"]) > max_entries:
        state["logbook"] = state["logbook"][-max_entries:]
    return entry


# Quick standalone test
if __name__ == "__main__":
    from core.state import create_initial_state

    test_state = create_initial_state()

    print(add_log(test_state, "city", "wandering"))
    print(add_log(test_state, "city", "selling", item="Goblin Ears", qty=4, gold=20))
    print(add_log(test_state, "city", "buying", item="Iron Sword", gold=50))
    print(add_log(test_state, "city", "quest_found", quest="Clear the Rat Cellar"))
    print(add_log(test_state, "city", "quest_complete", quest="Clear the Rat Cellar", gold=75))
    print(add_log(test_state, "idle"))
    print(add_log(test_state, "wild", "wandering"))
    print(add_log(test_state, "wild", "found_treasure", item="Lucky Charm", gold=15))
    print(add_log(test_state, "wild", "encounter_normal", enemy="Goblin"))
    print(add_log(test_state, "wild", "encounter_mini_boss", enemy="King Potum"))
    print(add_log(test_state, "wild", "encounter_boss", enemy="War Dragon Turba"))
    print(add_log(test_state, "wild", "quest_found", quest="Slay 5 Boars"))
    print(add_log(test_state, "wild", "quest_complete", quest="Slay 5 Boars", gold=120))