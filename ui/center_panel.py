import streamlit as st
import html
import re
from ui.styles import progress_bar_html

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
    
    action_text = html.escape(str(state["current_action"]))
    action_html = f"""
    <div class="div-card">
      <div class="div-card-header">Current Action</div>
      <div class="div-card-body" style="padding-top:10px; padding-bottom:10px;">
        <div class="div-serif">{action_text}</div>
        {progress_bar_html(state['action_progress'], "#f4d04e")}
      </div>
    </div>
    """
    st.markdown(action_html, unsafe_allow_html=True)

    log_items = []
    for entry in state["logbook"]:
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
        oracle_input = st.text_area(
            "Oracle Whisper",
            height=68,
            label_visibility="collapsed",
            placeholder="Whisper a divine command to your Apostle...",
            key="oracle_whisper_input",
        )
    with btn_col:
        if st.button("Send", use_container_width=True):
            if oracle_input.strip():
                state["logbook"].append(f"[00:00] [Divine Whisper] {oracle_input.strip()}")
                state["godpower"] = max(0, state["godpower"] - 10)
                st.rerun()