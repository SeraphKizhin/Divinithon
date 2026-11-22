import streamlit as st
from ui.creation_page import render_creation_page
from ui.left_panel import render_left_column
from ui.center_panel import render_center_column
from ui.right_panel import render_right_column
from ui.styles import inject_custom_css
from core.game_engine import run_game_tick

st.set_page_config(
    page_title="Divinithon Dashboard", 
    layout="wide"
)
inject_custom_css()

# INITIALIZATION OF GAME STATE (run once)
if not st.session_state.get("logged_in", False):
    render_creation_page()
    st.stop()

if "is_paused" not in st.session_state:
    st.session_state.is_paused = False

state = st.session_state.game_state

header_left, btn_pause, btn_step, btn_logout = st.columns([5, 1, 1, 1])
with header_left:
    st.markdown(
        f"<h3 style='margin:0; color:#333333;'>Divinithon &mdash; {state['god_name']}</h3>",
        unsafe_allow_html=True,
    )
with btn_pause:
    label = "Resume" if st.session_state.is_paused else "Pause"
    if st.button(label, use_container_width=True):
        st.session_state.is_paused = not st.session_state.is_paused
        st.rerun()
with btn_step:
    if st.button("Next Tick", use_container_width=True):
        run_game_tick(state)
        st.rerun()
with btn_logout:
    if st.button("Log Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

tick_interval = None if st.session_state.is_paused else 3

@st.fragment(run_every=tick_interval)
def render_live_dashboard() -> None:
    if not st.session_state.is_paused:
        run_game_tick(state)

    col_left, col_center, col_right = st.columns([1, 1.9, 1], gap="medium")

    with col_left:
        render_left_column(state)
    with col_center:
        render_center_column(state)
    with col_right:
        render_right_column(state)


render_live_dashboard()