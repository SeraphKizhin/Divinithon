import random
import time
from core.models import Monster
from typing import Optional

STANDARD_QUESTS = [
    "Explore the Whispering Willow",
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


def roll_new_quest(monsters_catalog: list[Monster], zone: str = "city") -> dict:
    if zone == "city":
        quest_type = random.choices(["standard", "boss_hunt"], weights=[70, 30], k=1)[0]

        if quest_type == "boss_hunt":
            bosses = [m.name for m in monsters_catalog if m.tier == "boss"]
            if bosses:
                target_boss = random.choice(bosses)
                return {
                    "type": "boss_hunt",
                    "title": f"Slay {target_boss}",
                    "target_boss": target_boss,
                }

        title = random.choice(STANDARD_QUESTS) if STANDARD_QUESTS else "Patrol the Border"
        return {
            "type": "standard",
            "title": title,
        }

    if ABSURD_QUESTS:
        picked = random.choice(ABSURD_QUESTS)
        return {
            "type": "absurd",
            "title": picked["title"],
            "duration_sec": picked.get("duration_sec", 120),
            "start_time": time.time(),
            "completion_log": picked.get("completion_log", ""),
        }

    return {
        "type": "standard",
        "title": "Survive the Wilderness",
    }