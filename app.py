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

# LEFT COLUMN: Apostle & Resources
with col_left:
    st.header("Apostle & Resources")
    
    st.subheader("Apostle Profile")
    st.write(f"**Name:** {state['apostle']} | **Level:** {state['lvl']}")

    hp_ratio = max(0.0, min(1.0, state["cur_hp"] / state["max_hp"]))
    st.progress(
        hp_ratio,
        text=f"HP: {state['cur_hp']}/{state['max_hp']}"
    )

    exp_ratio = max(0.0, min(1.0, state["exp"] / state["exp_req"]))
    st.progress(
        exp_ratio, 
        text=f"EXP: {state['exp']}/{state['exp_req']}"
    )

    st.write(
        f"**Gold:** {state['gold']} \n "
        f"**Monsters Defeated:** {state['monster_defeated']} \n "
        f"**Death Count:** {state['death_count']}"
    )
    
    st.divider()
    
    st.subheader("Inventory")
    if not state["inventory"]:
        st.caption("Inventory is empty.")
    else:
        for item, qty in state["inventory"].items():
            st.write(f"`[{item} x{qty}]`")

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