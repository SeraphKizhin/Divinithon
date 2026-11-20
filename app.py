import streamlit as st
from ui.creation_page import render_creation_page
from ui.left_panel import render_left_column
from ui.center_panel import render_center_column
from ui.right_panel import render_right_column

st.set_page_config(
    page_title="Divinithon Dashboard", 
    layout="wide"
)

# INITIALIZATION OF GAME STATE (run once)
if not st.session_state.get("logged_in", False):
    render_creation_page()
    st.stop()

state = st.session_state.game_state

header_left, header_right = st.columns([5, 1])
with header_left:
    st.title(f"Divinithon — {state['god_name']}")
with header_right:
    st.write("")  # Vertical alignment spacer
    if st.button("Log Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.divider()

col_left, col_center, col_right = st.columns([1, 1.5, 1])

# LEFT COLUMN: Apostle & Resources
with col_left:
    render_left_column(state)

# CENTER COLUMN: Action & Logbook
with col_center:
    render_center_column(state)

# RIGHT COLUMN: Map & Gear
with col_right:
    render_right_column(state)