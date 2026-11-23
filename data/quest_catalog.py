import random
import time
from core.models import Monster

STANDARD_QUESTS = [
    "Explore the Whispering Woods",
    "Clear the Rat Cellar",
    "Deliver the Suspicious Parcel",
    "Hunt 5 Rowdy Goblins",
    "Recover the Lost Relic",
]

ABSURD_QUESTS = [
    {
        "title": "Get two birds with one stone",
        "duration_sec": 120,
        "completion_log": (
            "{apostle} threw a rock towards a pond out of frustration and "
            "accidentally hit two birds taking a bath."
        ),
    },
    {
        "title": "Find the end of a circular road",
        "duration_sec": 90,
        "completion_log": (
            "{apostle} tripped over a root, declared it the official finish line, "
            "and called it a day."
        ),
    },
    {
        "title": "Win a staring contest with the sun",
        "duration_sec": 100,
        "completion_log": (
            "A cloud drifted past the sun. {apostle} claimed victory by technicality "
            "while blinking furiously."
        ),
    },
    {
        "title": "Count every blade of grass in the wilds",
        "duration_sec": 150,
        "completion_log": (
            "{apostle} lost count at 47, rounded up to 'a lot', and signed off the quest."
        ),
    },
    {
        "title": "Bottle a fresh gust of wind",
        "duration_sec": 110,
        "completion_log": (
            "{apostle} slammed a cork into an empty jar and swore it feels heavier now."
        ),
    },
]


def roll_new_quest(monsters_catalog: list[Monster]) -> dict:
    """Rolls a standard, boss_hunt, or absurd quest."""
    bosses = [m.name for m in monsters_catalog if m.tier == "boss"]
    quest_types = ["standard", "absurd"]
    weights = [45, 30]

    if bosses:
        quest_types.append("boss_hunt")
        weights.append(25)

    q_type = random.choices(quest_types, weights=weights, k=1)[0]

    if q_type == "boss_hunt":
        target = random.choice(bosses)
        return {
            "type": "boss_hunt",
            "title": f"Hunt the Boss: {target}",
            "target_boss": target,
        }

    if q_type == "absurd":
        picked = random.choice(ABSURD_QUESTS)
        return {
            "type": "absurd",
            "title": picked["title"],
            "start_time": time.time(),
            "duration_sec": picked["duration_sec"],
            "completion_log": picked["completion_log"],
        }

    return {
        "type": "standard",
        "title": random.choice(STANDARD_QUESTS),
    }