import streamlit as st
from typing import Optional
from core.models import Equipment

def format_equip(slot_item):
    if slot_item is None:
        return "Empty (+0)"
    return f"{slot_item['name']} (+{slot_item['bonus']})"

def render_right_column(state: dict) -> None:
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