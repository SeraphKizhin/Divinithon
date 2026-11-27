# Divinithon

An AI-powered Zero-Player RPG (ZPG) built with **Streamlit**. An automated text-based RPG loop runs in the background while you play as a weakened deity guiding your stubborn, comedic mortal Apostle through natural-language **"Divine Whispers"** powered by an LLM agent.

## Live Links
- **Trello Board:** [View Project Board](https://trello.com/b/lyevzKWq/divinithon)
- **Game Data (Google Sheet):** [View Equipment & Monsters Sheet](https://docs.google.com/spreadsheets/d/1t-H755kepdq32KBuS9Hk5aniY1BuIQDL9mOXJba8RJY/edit?usp=sharing)
- **Live App:** [Play Here](https://divinithon-game.streamlit.app/)

---

## Features

- **Hybrid Zero-Player Game Loop:** Automated timer ticks drive exploration, travel, quests, loot drops, and turn-based combat math deterministically—saving API tokens for player interactions.
- **Agentic Divine Whispers:** Type free-form commands (e.g., *"Run away!"*, *"Head to Whispering Willow"*, *"Hurry up!"*, *"Heal"*) that are translated by an LLM into validated game engine actions (`attack`, `flee`, `go_to`, `use_item`, `equip`, `buy_gear`, `sell_items`, `heal`, `hurry`, `explore`, `rest`, `idle`).
- **Godpower & Clarity System:** Every whisper consumes Godpower, which regenerates through town rest, monster kills, and completed quests[cite: 5]. Lower Godpower degrades how clearly the Apostle hears you, causing hilarious misinterpretations.
- **Dynamic World & Economy:** Travel across 4 connected nodes (**Northern Front**, **Open Easel**, **Whispering Willow**, and **Mykitiokan Farlands**) on an interactive SVG map, battle Normal, Mini-Boss, and Boss monsters, window-shop at city markets, and collect level-scaled gear.
- **Interactive Dashboard & Akashic Records:** Single-screen 3-column UI featuring dynamic zone landscape banners, a color-coded Logbook, and an **Akashic Records** modal for milestone events.
- **Multi-Layer Prompt Defense:** Protects the agent against jailbreaks and prompt injections using pre-API regex heuristics, delimiter sanitization, in-world data fencing, hardened system guardrails, and deterministic post-LLM state validation.

---

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
