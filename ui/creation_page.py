import streamlit as st
from core.state import create_initial_state

def render_creation_page() -> None:
    _, col_center, _ = st.columns([1, 1.5, 1])

    with col_center:
        st.title("Divinithon")
        st.caption("Awaken your divinity and name the mortal who will carry your will.")
        st.divider()

        with st.form("creation_form"):
            god_name = st.text_input(
                "God Name",
                placeholder="e.g., Insatiable Golden Pothos",
                max_chars=40,
            )
            apostle_name = st.text_input(
                "Apostle Name",
                placeholder="e.g., Seraph",
                max_chars=30,
            )

            submitted = st.form_submit_button(
                "Begin Journey",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                clean_god = god_name.strip()
                clean_apostle = apostle_name.strip()

                if not clean_god or not clean_apostle:
                    st.error("Please enter both a God Name and an Apostle Name.")
                else:
                    st.session_state.game_state = create_initial_state(
                        god_name=clean_god,
                        apostle=clean_apostle,
                    )
                    st.session_state.logged_in = True
                    st.rerun