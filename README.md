# Divinithon

An AI-powered Zero-Player RPG (ZPG) built with **Streamlit**[cite: 3]. An automated text-based RPG loop runs in the background while you play as a weakened deity guiding your stubborn, comedic mortal Apostle through natural-language **"Divine Whispers"** powered by an LLM agent[cite: 6, 8, 9].

## Live Links
- **Trello Board:** [View Project Board](https://trello.com/b/lyevzKWq/divinithon)
- **Game Data (Google Sheet):** [View Equipment & Monsters Sheet](https://docs.google.com/spreadsheets/d/1t-H755kepdq32KBuS9Hk5aniY1BuIQDL9mOXJba8RJY/edit?usp=sharing)
- **Live App:** *[Play Here](https://divinithon-game.streamlit.app/)

---

## Features

- **Hybrid Zero-Player Game Loop:** Automated timer ticks drive exploration, travel, quests, loot drops, and turn-based combat math deterministically—saving API tokens for player interactions[cite: 3, 4, 8].
- **Agentic Divine Whispers:** Type free-form commands (e.g., *"Run away!"*, *"Head to Whispering Willow"*, *"Hurry up!"*, *"Heal"*) that are translated by an LLM into validated game engine actions (`attack`, `flee`, `go_to`, `use_item`, `equip`, `buy_gear`, `sell_items`, `heal`, `hurry`, `explore`, `rest`, `idle`)[cite: 4, 5, 9].
- **Godpower & Clarity System:** Every whisper consumes Godpower, which regenerates through town rest, monster kills, and completed quests[cite: 5]. Lower Godpower degrades how clearly the Apostle hears you, causing hilarious misinterpretations[cite: 13].
- **Dynamic World & Economy:** Travel across 4 connected nodes (**Northern Front**, **Open Easel**, **Whispering Willow**, and **Mykitiokan Farlands**) on an interactive SVG map, battle Normal, Mini-Boss, and Boss monsters, window-shop at city markets, and collect level-scaled gear[cite: 4, 7, 12].
- **Interactive Dashboard & Akashic Records:** Single-screen 3-column UI featuring dynamic zone landscape banners, a color-coded Logbook, and an **Akashic Records** modal for milestone events[cite: 3, 4, 13].
- **Multi-Layer Prompt Defense:** Protects the agent against jailbreaks and prompt injections using pre-API regex heuristics, delimiter sanitization, in-world data fencing, hardened system guardrails, and deterministic post-LLM state validation[cite: 9, 13].

---

## Project Structure

```text
divinithon/
├── app.py                     # Main Streamlit entry point & 3-column dashboard layout
├── requirements.txt           # Python dependencies
├── .env.example               # Template for required environment variables
├── assets/                    # Zone & road landscape banners (NF, OE, WW, MF, road)
├── core/
│   ├── state.py               # Initial session state & Apostle/Deity defaults
│   ├── models.py              # Dataclasses for Equipment, Monsters, and SellableItems
│   ├── game_engine.py         # Automated tick loop, combat, travel, economy & AI action bridge
│   ├── monster_engine.py      # Tier spawn weights, level HP/EXP scaling & cascading loot rolls
│   ├── equipment_rules.py     # Bonus rolling, offhand compatibility & auto-equip logic
│   ├── log_generator.py       # Timestamped procedural log formatting
│   └── prompts.py             # Engineered system prompt, injection defense & JSON parser
├── data/
│   ├── catalog.py             # Equipments, monsters, sellable loot & price lookup tables
│   ├── log_catalog.py         # Procedural city, wild, and idle chatter templates
│   ├── quest_catalog.py       # Standard, boss-hunt, and absurd quest generators
│   └── world_map.py           # World nodes, zone types, coordinates & graph edges
├── services/
│   └── ai_oracle.py           # OpenAI-compatible LLM client wrapper
└── ui/
    ├── login_page.py          # Deity & Apostle naming screen
    ├── left_panel.py          # Apostle stats, active quest, Gold, counters & inventory
    ├── center_panel.py        # Landscape banner, action bar, color-coded Logbook & Whisper input
    ├── right_panel.py         # Interactive SVG node map & 5-slot equipment view
    └── styles.py              # Custom CSS cards, progress bars & cached base64 image loader
```

## Local Setup & Run Instructions

```bash
git clone [https://github.com/SeraphKizhin/Divinithon.git](https://github.com/SeraphKizhin/Divinithon.git)
cd divinithon
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```
- Create a .env file in the root divinithon/ directory (do not commit this file to GitHub) and add your API credentials:
```bash
AI_API_KEY=your_api_key_here
AI_BASE_URL=[https://aiki-labs.up.railway.app/api/v1](https://aiki-labs.up.railway.app/api/v1)
AI_MODEL=gpt-6-luna
```
- then Run it
```bash
streamlit run app.py
