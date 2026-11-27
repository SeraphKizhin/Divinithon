import random
import time
from core.models import Monster
from typing import Optional

STANDARD_QUESTS = [
    "Explore the Whispering Willow",
    "Explore the Mykitiokan Farlands",
    "Scout the Northern Border",
    "Investigate the Abandoned Watchtower",
    "Map the Forgotten Trail",
    "Search the Ruins of an Old Settlement",
    "Clear the Rat Cellar",
    "Hunt 5 Rowdy Goblins",
    "Eliminate the Bandit Outpost",
    "Drive the Wolves Away",
    "Hunt the Wild Boar",
    "Defeat the Corrupted Treant",
    "Clear the Monster-Infested Cave",
    "Deliver the Suspicious Parcel",
    "Gather 10 Medicinal Herbs",
    "Collect 5 Goblin Ears",
    "Retrieve the Lost Merchant's Goods",
    "Gather Rare Mushrooms",
    "Collect 8 Pieces of Wolf Pelt",
    "Deliver Supplies to the Northern Front",
    "Recover the Lost Relic",
    "Find the Missing Caravan",
    "Investigate the Strange Footprints",
    "Recover the Stolen Family Heirloom",
    "Find the Missing Scout",
    "Retrieve the Ancient Manuscript",
    "Investigate the Abandoned Campsite",
    "Repair the Broken Watchtower",
    "Escort a Merchant Through the Wilds",
    "Protect the Village Livestock",
    "Clear the Road of Fallen Trees",
    "Deliver a Letter to a Distant Settlement",
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
    {
        "title": "Deliver a letter to yourself",
        "duration_sec": 100,
        "completion_log": (
            "{apostle} delivered the letter, opened it, and discovered a reminder "
            "to deliver the letter."
        ),
    },
    {
        "title": "Find a merchant who sells nothing",
        "duration_sec": 120,
        "completion_log": (
            "{apostle} found a merchant selling absolutely nothing and somehow "
            "spent ten minutes browsing."
        ),
    },
    {
        "title": "Return a borrowed rock",
        "duration_sec": 90,
        "completion_log": (
            "{apostle} returned the rock to its original location. The rock had no complaints."
        ),
    },
    {
        "title": "Ask five strangers for directions",
        "duration_sec": 120,
        "completion_log": (
            "{apostle} asked five strangers for directions and received six different answers."
        ),
    },
    {
        "title": "Find a suitable place to nap",
        "duration_sec": 100,
        "completion_log": (
            "{apostle} inspected several locations before falling asleep in the first one."
        ),
    },
    {
        "title": "Become the strongest person in the village",
        "duration_sec": 150,
        "completion_log": (
            "{apostle} challenged a toddler to an arm-wrestling match and won convincingly."
        ),
    },
    {
        "title": "Defeat your greatest enemy",
        "duration_sec": 120,
        "completion_log": (
            "{apostle} stared into a puddle, challenged their reflection, and declared victory."
        ),
    },
    {
        "title": "Discover a new species",
        "duration_sec": 150,
        "completion_log": (
            "{apostle} discovered a particularly strange-looking frog and immediately "
            "named it after themselves."
        ),
    },
    {
        "title": "Prove that rocks can float",
        "duration_sec": 120,
        "completion_log": (
            "{apostle} placed a rock in a bucket and watched it sink. Further research is required."
        ),
    },
    {
        "title": "Find the world's largest stick",
        "duration_sec": 150,
        "completion_log": (
            "{apostle} found a branch, declared it a stick, and refused to hear further arguments."
        ),
    },
    {
        "title": "Receive a sign from the heavens",
        "duration_sec": 100,
        "completion_log": (
            "A bird relieved itself nearby. {apostle} interpreted this as a divine message."
        ),
    },
    {
        "title": "Ask {god} for a miracle",
        "duration_sec": 90,
        "completion_log": (
            "{apostle} prayed for a miracle and successfully found a coin in their pocket."
        ),
    },
    {
        "title": "Find out whether gods need sleep",
        "duration_sec": 120,
        "completion_log": (
            "{apostle} received no answer from {god} and concluded that the deity was napping."
        ),
    },
    {
        "title": "Offer a sacrifice to the divine",
        "duration_sec": 100,
        "completion_log": (
            "{apostle} sacrificed their lunch to {god}. The stomach remains unconvinced."
        ),
    },
    {
        "title": "Establish contact with the divine",
        "duration_sec": 120,
        "completion_log": (
            "{apostle} shouted into the sky until a nearby bird responded. Close enough."
        ),
    },
    {
        "title": "Find the owner of a suspicious chicken",
        "duration_sec": 100,
        "completion_log": (
            "{apostle} found the chicken's owner. The chicken followed them anyway."
        ),
    },
    {
        "title": "Untangle a particularly stubborn rope",
        "duration_sec": 120,
        "completion_log": (
            "{apostle} untangled the rope, only to discover it was never tied in the first place."
        ),
    },
    {
        "title": "Chase away a persistent squirrel",
        "duration_sec": 90,
        "completion_log": (
            "{apostle} chased the squirrel away. It returned with two friends."
        ),
    },
    {
        "title": "Find a missing shoe",
        "duration_sec": 100,
        "completion_log": (
            "{apostle} found the missing shoe on their own foot. An embarrassing discovery."
        ),
    },
    {
        "title": "Teach a rock to roll",
        "duration_sec": 120,
        "completion_log": (
            "{apostle} pushed a rock down a hill and proudly declared themselves a teacher."
        ),
    },
    {
        "title": "Teach a rock how to swim",
        "duration_sec": 120,
        "completion_log": (
            "{apostle} tossed a pebble into a creek, watched it sink, and declared it a natural."
        ),
    },
]


def roll_new_quest(
    monsters_catalog: list[Monster],
    zone: str = "city",
    god_name: str = "The Almighty",
) -> dict:
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
            "title": picked["title"].format(god=god_name),
            "duration_sec": picked.get("duration_sec", 120),
            "start_time": time.time(),
            "completion_log": picked.get("completion_log", ""),
        }

    return {
        "type": "standard",
        "title": "Survive the Wilderness",
    }