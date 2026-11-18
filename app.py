import streamlit as st

st.set_page_config(
    page_title="Divinithon Dashboard", 
    layout="wide"
)

st.title("Divinithon")
st.divider()

col_left, col_center, col_right = st.columns([1, 1.5, 1])

# LEFT COLUMN: Apostle & Resources
with col_left:
    st.header("Apostle & Resources")
    
    st.subheader("Apostle Profile")
    st.write("**Name:** Sir Clumsy-a-Lot | **Level:** 1")
    st.progress(
        80, 
        text="Health Bar: 40/50"
    )
    st.progress(
        30, 
        text="Quest Progress: 30%"
    )
    st.write("**Gold:** 150 | **Monsters Defeated:** 12 | **Death Count:** 2")
    
    st.divider()
    
    st.subheader("Inventory")
    st.write("`[Goblin Ears x4]`")
    st.write("`[Wolf Pelt x3]`")
    st.write("`[Health Potion x1]`")

# CENTER COLUMN: Action & Logbook
with col_center:
    st.header("Action & Logbook")
    
    st.info("[Landscape Image Placeholder]")
    st.progress(
        60, 
        text="Current Action: Walking through the forest...."
    )
    
    st.text_area(
        "Logbook",
        "[02:40] Left the village.\n[02:43] Walking in these forests...\n[02:45] Ambushed by a Goblin!",
        height=250,
        disabled=True,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.subheader("Power Panel")
    st.progress(
        75, 
        text="Godpower: 75%"
    )
    
    oracle_input = st.text_input(
        "Oracle Whisper", 
        label_visibility="collapsed", 
        placeholder="Type your divine command here..."
    )
    if st.button(
        "SEND", 
        type="primary"
    ):
        st.success("Command sent!")

# RIGHT COLUMN: Map & Gear
with col_right:
    st.header("Map & Gear")
    
    st.subheader("Node Map")
    st.write("`[NF]` ➔ **`[EP] (Current)`** ➔ `[OE]` ➔ `[MF]`")
    
    st.divider()
    
    st.subheader("Equipment")
    st.write("**Mainhand:** +12")
    st.write("**Offhand:** +5")
    st.write("**Body:** +20")
    st.write("**Special:** +0")
    st.write("**Additional:** +2")