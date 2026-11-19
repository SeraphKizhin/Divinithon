import streamlit as st
from core.state import create_initial_state
from ui.left_panel import render_left_column
from ui.center_panel import render_center_column
from ui.right_panel import render_right_column

st.set_page_config(
    page_title="Divinithon Dashboard", 
    layout="wide"
)

# INITIALIZATION OF GAME STATE (run once)
if "game_state" not in st.session_state:
    st.session_state.game_state = create_initial_state()

state = st.session_state.game_state

st.title(f"Divinithon — {state['god_name']}")
st.divider()

col_left, col_center, col_right = st.columns([1, 1.5, 1])

# LEFT COLUMN: Apostle & Resources
with col_left:
    render_left_column

# CENTER COLUMN: Action & Logbook
with col_center:
    render_center_column

# RIGHT COLUMN: Map & Gear
with col_right:
    render_right_column
    