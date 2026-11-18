import streamlit as st

def render_center_column(state: dict) -> None:
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