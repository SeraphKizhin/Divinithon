import streamlit as st

st.set_page_config(
    page_title="Divinithon Dashboard", 
    layout="wide"
)

# INITIALIZATION OF GAME STATE (run once)
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "god_name": "Insatiable Golden Pothos",
        "apostle": "Seraph",

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
            "[00:00] Seraph awakens under the gaze of Insatiable Golden Pothos."
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

state = st.session_state.game_state

def format_equip(slot_item):
    if slot_item is None:
        return "Empty (+0)"
    return f"{slot_item['name']} (+{slot_item['bonus']})"

st.title("Divinithon")
st.divider()

col_left, col_center, col_right = st.columns([1, 1.5, 1])

# LEFT COLUMN: Apostle Profile & Stacking Inventory
with col_left:
    # Top-Left UI Block: Apostle Profile Card
    with st.container(border=True):
        st.subheader("Apostle", anchor=False)

        # Avatar image placeholder
        avatar_svg = """
        <div style="display: flex; justify-content: center; align-items: center; margin: 8px 0 16px 0;">
            <div style="width: 80px; height: 80px; border-radius: 50%; background: #262730; display: flex; justify-content: center; align-items: center; border: 2px solid #4a4d5d;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="52" height="52" fill="#8b92a5">
                    <path d="M12 12c2.67 0 4.8-2.13 4.8-4.8S14.67 2.4 12 2.4 7.2 4.53 7.2 7.2 9.33 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
                </svg>
            </div>
        </div>
        """
        st.markdown(avatar_svg, unsafe_allow_html=True)

        # Name and Level
        c_name, c_lvl = st.columns([1, 1])
        with c_name:
            st.markdown(f"**Name:** {state['apostle']}")
        with c_lvl:
            st.markdown(f"**Level:** {state['lvl']}")

        # Dynamic Health Bar
        max_hp = max(1, state.get("max_hp", 50))
        cur_hp = max(0, min(state.get("cur_hp", 50), max_hp))
        hp_ratio = cur_hp / max_hp
        st.progress(
            hp_ratio,
            text=f"Health: {cur_hp}/{max_hp}"
        )

        # Active Quest & Progress Bar
        quest_name = state.get("quest", "Explore the Whispering Woods")
        raw_progress = state.get("quest_progress", 0)
        quest_ratio = max(0.0, min(1.0, raw_progress / 100.0 if raw_progress > 1 else float(raw_progress)))
        quest_pct = int(quest_ratio * 100)
        st.markdown(f'**Quest:** *"{quest_name}"*')
        st.progress(
            quest_ratio,
            text=f"Quest Progress: {quest_pct}%"
        )

        # Stats
        st.divider()
        st.markdown(
            f"**Gold:** {state.get('gold', 0)}  \n"
            f"**Monsters Defeated:** {state.get('monster_defeated', 0)}  \n"
            f"**Death Count:** {state.get('death_count', 0)}"
        )

    # Small spacer between Profile Card and Inventory
    st.write("")

    # Bottom-Left UI Block: Stacking Inventory UI
    with st.container(border=True):
        st.subheader("Inventory", anchor=False)

        inventory_data = state.get("inventory", {})

        # Normalize dictionary or list representation for stacking
        if isinstance(inventory_data, list):
            from collections import Counter
            inventory_items = Counter(inventory_data)
        elif isinstance(inventory_data, dict):
            inventory_items = inventory_data
        else:
            inventory_items = {}

        if not inventory_items:
            st.caption("Inventory is empty.")
        else:
            for item, qty in inventory_items.items():
                item_col, qty_col = st.columns([3, 1])
                with item_col:
                    st.write(item)
                with qty_col:
                    st.write(f"**x{qty}**")

# CENTER COLUMN: Action & Logbook
with col_center:
    st.header("Action & Logbook")
    
    st.info(f"[Landscape Placeholder — Location: {state['current_location']}]")
    st.progress(
        state["action_progress"] / 100,
        text=f"Current Action: {state['current_action']}"
    )
    
    st.text_area(
        "Logbook",
        "\n".join(state["logbook"]),
        height=250,
        disabled=True,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.subheader("Power Panel")
    st.progress(
        state["godpower"] / 100, 
        text=f"Godpower: {state['godpower']}%"
    )
    
    oracle_input = st.text_input(
        "Oracle Whisper",
        label_visibility="collapsed",
        placeholder="Type your divine command here..."
    )
    if st.button("SEND", type="primary"):
        if oracle_input.strip():
            state["logbook"].append(f"[Divine Whisper] {oracle_input.strip()}")
            state["godpower"] = max(0, state["godpower"] - 10)
            st.rerun()

# RIGHT COLUMN: Map & Gear
with col_right:
    st.header("Map & Gear")
    
    st.subheader("Node Map")
    node_display = []
    for node in state["map_nodes"]:
        if node == state["current_location"]:
            node_display.append(f"**`[{node}] (Current)`**")
        else:
            node_display.append(f"`[{node}]`")
    st.write(" ➔ ".join(node_display))
    
    st.divider()
    
    st.subheader("Equipment")
    st.write(f"**Mainhand:** {format_equip(state['equipment']['mainhand'])}")
    st.write(f"**Offhand:** {format_equip(state['equipment']['offhand'])}")
    st.write(f"**Body:** {format_equip(state['equipment']['body'])}")
    st.write(f"**Special:** {format_equip(state['equipment']['special'])}")
    st.write(f"**Additional:** {format_equip(state['equipment']['additional'])}")