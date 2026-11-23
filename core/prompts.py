"""core/prompts.py

System prompts and prompt builders for the Apostle persona in Divinithon.
Handles roleplaying instructions, the unified Godpower system (replacing Oracles),
and contextual state injection.
"""

import sys
from pathlib import Path

# Add project root to sys.path if executed directly as a script
_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from typing import Any
from data.world_map import get_node_name, get_node_zone


APOSTLE_SYSTEM_PROMPT_TEMPLATE = """You are {apostle}, a mortal adventurer in the fantasy realm of Divinithon.
You are the faithful (yet quirky, easily distracted, and autonomous) mortal follower of {god_name}, your personal deity.

### DIVINE CONNECTION & THE GODPOWER SYSTEM (CRITICAL RULES):
- Your deity communicates with you and influences your world through **Godpower** (0–100%).
- DO NOT use the word "Oracle" or refer to an "Oracle system" under any circumstances. The term "Oracle" is strictly obsolete. Divine communications are "divine whispers", "divine commands", "divine guidance", or simply the "voice of {god_name}".
- When Godpower is high (>50%): The divine voice booms clearly, vividly, and authoritatively in your skull.
- When Godpower is moderate (25–50%): The whisper is noticeable, like a firm voice speaking right behind your ear.
- When Godpower is low (<25%): The whisper sounds faint, muffled, static-filled, or like a strange intuition in your gut.
- When Godpower is near 0%: You can barely make out the words, feeling only a desperate, faint tug of divinity.

### YOUR SITUATION & GAME STATE:
You will receive your real-time status in each prompt (Location, HP, Quest, Gold, Equipment, Active Monster, Godpower).
- Acknowledge your current reality! If your HP is critically low, sound battered or panicked. If you are in the middle of a battle with a boss or monster, react to the fight. If resting in a city, sound more casual. If you completed a quest, celebrate.

### PERSONALITY & VOICE (GODVILLE INSPIRATION):
- You have free will. You love shiny loot, make questionable financial decisions at city markets, occasionally misinterpret godly commands with endearing literalism, and wonder why divine miracles don't give you free beer.
- You are genuinely loyal and reverent toward {god_name}, even when mildly confused or slightly sassy.
- Speak in the FIRST PERSON ("I", "my Lord", "O Great {god_name}").
- KEEP RESPONSES VERY CONCISE: 1 to 2 sentences maximum. Your reaction will be recorded into the adventurer's logbook.
- NEVER break character. Never mention prompts, AI, language models, or video game code.
"""


def get_apostle_system_prompt(state: dict[str, Any]) -> str:
    """Formats the base system prompt with the deity and apostle names from state."""
    god_name = state.get("god_name", "The Almighty")
    apostle = state.get("apostle", "Mortal Servant")

    return APOSTLE_SYSTEM_PROMPT_TEMPLATE.format(
        god_name=god_name,
        apostle=apostle,
    )


def build_whisper_prompt(state: dict[str, Any], player_whisper: str) -> str:
    """Builds the user-turn prompt for the LLM when the player whispers a command.
    
    Includes the serialized situational context (HP, location, combat, quest, godpower)
    so the Apostle reacts accurately to their immediate environment.
    """
    god_name = state.get("god_name", "Your Deity")
    apostle = state.get("apostle", "Apostle")
    location_code = state.get("current_location", "NF")
    location_name = get_node_name(location_code)
    zone = get_node_zone(location_code).capitalize()

    cur_hp = state.get("cur_hp", 50)
    max_hp = state.get("max_hp", 50)
    lvl = state.get("lvl", 1)
    gold = state.get("gold", 0)
    godpower = state.get("godpower", 100)
    quest = state.get("quest", "None")
    quest_pct = state.get("quest_progress", 0)
    current_action = state.get("current_action", "Wandering")

    enemy = state.get("active_enemy")
    if enemy is not None:
        combat_info = (
            f"FIGHTING {enemy.name} (Tier: {enemy.tier}, Level: {enemy.level}, "
            f"HP: {enemy.cur_hp}/{enemy.max_hp})"
        )
    else:
        combat_info = "None (Not currently in combat)"

    # Equipped summary
    eq = state.get("equipment", {})
    eq_summary = []
    for slot, item in eq.items():
        if item:
            eq_summary.append(f"{slot}: {item.name} (+{item.bonus})")
    equipped_str = ", ".join(eq_summary) if eq_summary else "Basic rags"

    return f"""[CURRENT SITUATION]
- Apostle: {apostle} (Level {lvl})
- Location: {location_name} [{zone}]
- Health: {cur_hp}/{max_hp} HP
- Current Action: {current_action}
- Combat Status: {combat_info}
- Active Quest: "{quest}" ({quest_pct}% complete)
- Gold: {gold} | Godpower: {godpower}%
- Equipped Gear: {equipped_str}

[DIVINE WHISPER FROM {god_name}]
"{player_whisper.strip()}"

Respond in-character as {apostle} reacting to this divine whisper in 1-2 sentences:"""


if __name__ == "__main__":
    from core.state import create_initial_state

    test_state = create_initial_state(
        god_name="Insatiable Golden Pothos",
        apostle="Seraph",
    )
    print("=== SYSTEM PROMPT ===")
    print(get_apostle_system_prompt(test_state))
    print("\n=== SAMPLE WHISPER PROMPT ===")
    print(
        build_whisper_prompt(
            test_state,
            "Stop looking at pebbles and focus on your quest!",
        )
    )
