import streamlit as st
import html
import re
from datetime import datetime
from ui.styles import progress_bar_html, render_html

def _parse_log_line(line: str) -> tuple[str, str]:
    """Splits '[02:32] Message' or '02:32 Message' into (timestamp, message)."""
    match = re.match(r"^\[?(\d{2}:\d{2})\]?\s*(.*)$", line.strip())
    if match:
        return match.group(1), match.group(2)
    return "--:--", line.strip()

def render_center_column(state: dict) -> None:
    landscape_html = f"""
    <div class="div-card">
      <div class="div-card-header">&nbsp;</div>
      <div class="div-card-body">
        <div style="
          height: 145px;
          border-radius: 10px;
          background: linear-gradient(180deg, #dff1ff 0%, #f2f9ff 100%);
          border: 1px dashed #b8d4ea;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #5b7a94;
          font-size: 0.95rem;
        ">
          [Landscape Placeholder &mdash; Location: {html.escape(str(state['current_location']))}]
        </div>
      </div>
    </div>
    """
    st.markdown(landscape_html, unsafe_allow_html=True)
    
    enemy = state.get("active_enemy")
    if enemy is not None:
        enemy_hp_pct = max(0.0, min(100.0, (enemy.cur_hp / enemy.max_hp) * 100))
        tier_badge = ""
        if enemy.tier == "boss":
            tier_badge = " [BOSS]"
        elif enemy.tier == "mini_boss":
            tier_badge = " [Mini-Boss]"

        action_html = f"""
        <div class="div-card">
            <div class="div-card-header">In Combat</div>
            <div class="div-card-body">
                {progress_bar_html(enemy_hp_pct, "#e04f4f")}
                <div class="div-serif" style="margin-top:4px; margin-bottom:0;">
                    <strong>{enemy.name}{tier_badge}</strong> &bull; Lv. {enemy.level} &bull; {enemy_hp_pct:.0f}%
                </div>
            </div>
        </div>
        """
    else:
        action_html = f"""
        <div class="div-card">
            <div class="div-card-header">Current Action</div>
            <div class="div-card-body">
                <div class="div-serif">{state["current_action"]}</div>
                {progress_bar_html(state["action_progress"], "#f0c43c")}
            </div>
        </div>
        """
    render_html(action_html)

    log_items = []
    for entry in reversed(state["logbook"]):
        timestamp, msg = _parse_log_line(entry)
        log_items.append(
            f'<div class="div-log-entry">'
            f'<div class="div-log-time">{html.escape(timestamp)}</div>'
            f'<div class="div-log-msg">{html.escape(msg)}</div>'
            f'</div>'
        )
    logs_html = "".join(log_items)
    
    godpower = max(0, min(100, int(state["godpower"])))
    logbook_and_power_html = f"""
    <div class="div-card" style="margin-bottom: 8px;">
      <div class="div-card-header">Logbook</div>
      <div class="div-log-box">
        {logs_html}
      </div>
      <div class="div-card-header" style="border-top: 1px solid #e0e0e0;">Power</div>
      <div class="div-card-body" style="padding-bottom: 6px;">
        <div style="display:flex; align-items:center; gap:12px;">
          <span style="font-size:0.9rem; color:#333333; white-space:nowrap;">Godpower</span>
          <div style="flex:1;">
            <div class="div-bar-track" style="margin:0;">
              <div class="div-bar-fill" style="width:{godpower}%; background-color:#0044b3;"></div>
            </div>
          </div>
          <span style="font-size:0.9rem; color:#333333; min-width:36px; text-align:right;">{godpower}%</span>
        </div>
      </div>
    </div>
    """
    st.markdown(logbook_and_power_html, unsafe_allow_html=True)

    input_col, btn_col = st.columns([5, 1])
    with input_col:
        whisper_input = st.text_area(
            "Divine Whisper",
            height=68,
            label_visibility="collapsed",
            placeholder="Whisper a divine command to your Apostle...",
            key="divine_whisper_input",
        )
    with btn_col:
        if st.button("Send", use_container_width=True):
            if whisper_input.strip():
                now_str = datetime.now().strftime("%H:%M")
                state["logbook"].append(f"[{now_str}] [Divine Whisper] {whisper_input.strip()}")
                state["godpower"] = max(0, state["godpower"] - 10)
                st.rerun()