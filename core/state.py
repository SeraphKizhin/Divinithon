def create_initial_state(
    god_name: str = "Insatiable Golden Pothos",
    apostle: str = "Seraph",
    ) -> dict:
    """Returns a fresh game_state dictionary for a new session."""
    return {
        "god_name": god_name,
        "apostle": apostle,

        "lvl": 1,
        "exp": 0,
        "exp_req": 100,
        "max_hp": 50,
        "cur_hp": 50,

        "quest": "Explore the Whispering Woods",
        "quest_progress": 0,
        "gold": 0,
        "monster_defeated": 0,
        "death_count": 0,

        "inventory": {},

        "current_action": "Awaiting divine guidance...",
        "action_progress": 0,
        "logbook": [
            f"[00:00] {apostle} awakens under the gaze of {god_name}."
        ],

        "godpower": 100,

        "map_nodes": ["NF", "EP", "OE", "MF"],
        "current_location": "NF",

        "equipment": {
            "mainhand": None,
            "offhand": None,
            "body": None,
            "special": None,
            "additional": None,
        },
    }