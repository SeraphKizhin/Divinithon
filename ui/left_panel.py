import streamlit as st

def render_left_column(state: dict) -> None:
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