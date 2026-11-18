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