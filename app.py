import streamlit as st

st.set_page_config(
    page_title="Divinithon Dashboard", 
    layout="wide"
)

# INITIALIZATION OF GAME STATE (run once)
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        
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