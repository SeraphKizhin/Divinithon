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


st.title("Divinithon")
st.divider()

col_left, col_center, col_right = st.columns([1, 1.5, 1])

# LEFT COLUMN: Apostle & Resources
with col_left:
    

# CENTER COLUMN: Action & Logbook
with col_center:
    

# RIGHT COLUMN: Map & Gear
with col_right:
    