import streamlit as st
from ui.equipment_panel import render_equipment_panel


def render_right_column(state: dict) -> None:
    st.subheader("Node Map")
    node_display = []
    for node in state["map_nodes"]:
        if node == state["current_location"]:
            node_display.append(f"**`[{node}] (Current)`**")
        else:
            node_display.append(f"`[{node}]`")
    st.write(" ➔ ".join(node_display))

    st.divider()

    # ── Equipment Panel (celestial dark-fantasy card) ──
    render_equipment_panel(state)