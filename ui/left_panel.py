import streamlit as st
import html
from ui.styles import progress_bar_html

AVATAR_SVG = """
<div style="display:flex; justify-content:center; margin: 4px 0 14px 0;">
<svg width="78" height="78" viewBox="0 0 100 100" fill="#262626" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="30" r="19"/>
  <path d="M18 86 C18 62, 32 54, 50 54 C68 54, 82 62, 82 86 Z"/>
</svg>
</div>
"""

def render_left_column(state: dict) -> None:
    exp_pct = (state["exp"] / state["exp_req"] * 100) if state["exp_req"] > 0 else 0
    hp_pct = (state["cur_hp"] / state["max_hp"] * 100) if state["max_hp"] > 0 else 0
    quest_pct = state["quest_progress"]

    apostle_name = html.escape(str(state["apostle"]))
    quest_text = html.escape(str(state["quest"]))

    apostle_html = f"""
    <div class="div-card">
      <div class="div-card-header">Apostle</div>
      <div class="div-card-body">
        {AVATAR_SVG}
        <div class="div-row">
          <span class="div-label">Name</span>
          <span class="div-value">{apostle_name}</span>
        </div>
        <div class="div-row">
          <span class="div-label">Level</span>
          <span class="div-value">{state['lvl']}</span>
        </div>
        {progress_bar_html(exp_pct, "#f4d04e")}
        <div class="div-row">
          <span class="div-label">Health</span>
          <span class="div-value">{state['cur_hp']}/{state['max_hp']}</span>
        </div>
        {progress_bar_html(hp_pct, "#12b84c")}
        <div class="div-row" style="margin-bottom:2px;">
          <span class="div-label">Quest</span>
        </div>
        <div class="div-serif">&ldquo;{quest_text}&rdquo;</div>
        {progress_bar_html(quest_pct, "#f6b7c1")}
        <div class="div-row">
          <span class="div-label">Gold</span>
          <span class="div-value">{state['gold']}</span>
        </div>
        <div class="div-row">
          <span class="div-label">Monster Defeated</span>
          <span class="div-value">{state['monster_defeated']}</span>
        </div>
        <div class="div-row" style="margin-bottom:0;">
          <span class="div-label">Death Count</span>
          <span class="div-value">{state['death_count']}</span>
        </div>
      </div>
    </div>
    """
    st.markdown(apostle_html, unsafe_allow_html=True)

    if not state["inventory"]:
        inv_rows = '<div style="color:#888888; font-size:0.88rem;">Inventory is empty.</div>'
    else:
        inv_rows = "".join(
            f'<div class="div-row">'
            f'<span>{html.escape(str(item))}</span>'
            f'<span>x{qty}</span>'
            f'</div>'
            for item, qty in state["inventory"].items()
        )

    inventory_html = f"""
    <div class="div-card">
      <div class="div-card-header">Inventory</div>
      <div class="div-card-body" style="min-height: 290px;">
        {inv_rows}
      </div>
    </div>
    """
    st.markdown(inventory_html, unsafe_allow_html=True)