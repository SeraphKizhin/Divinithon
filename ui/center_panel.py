import streamlit as st
import html
import re
from datetime import datetime
from ui.styles import progress_bar_html, render_html
from core.llm_client import ask_apostle
from core.game_engine import execute_ai_action

IMPORTANT_MARKER = "★"
WHISPER_COST = 15

def _parse_log_line(line: str) -> tuple[str, str]:
    """Splits '[02:32] Message' or '02:32 Message' into (timestamp, message)."""
    match = re.match(r"^\[?(\d{2}:\d{2})\]?\s*(.*)$", line.strip())
    if match:
        return match.group(1), match.group(2)
    return "--:--", line.strip()


@st.dialog("Akashic Records", width="large")
def show_important_logs(state: dict) -> None:
    entries = state.get("important_logbook") or []
    if not entries:
        st.caption("Nothing worthy of legend yet. Go do something reckless.")
    else:
        log_items = []
        for entry in reversed(entries):
            cleaned = entry.replace(IMPORTANT_MARKER, "").strip()
            timestamp, msg = _parse_log_line(cleaned)
            log_items.append(
                f'<div class="div-log-entry">'
                f'<div class="div-log-time">{html.escape(timestamp)}</div>'
                f'<div class="div-log-msg">{html.escape(msg)}</div>'
                f'</div>'
            )
        st.markdown(
            f'<div class="div-log-box" style="height:420px;">{"".join(log_items)}</div>',
            unsafe_allow_html=True,
        )

    if st.button("Close", use_container_width=True, key="close_important_logs"):
        st.rerun()


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

        safe_enemy_name = html.escape(str(enemy.name))
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
        safe_action = html.escape(str(state["current_action"]))
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
        cleaned = entry.replace(IMPORTANT_MARKER, "").strip()
        timestamp, msg = _parse_log_line(cleaned)
        log_items.append(
            f'<div class="div-log-entry">'
            f'<div class="div-log-time">{html.escape(timestamp)}</div>'
            f'<div class="div-log-msg">{html.escape(msg)}</div>'
            f'</div>'
        )
    logs_html = "".join(log_items)
    godpower = max(0, min(100, int(state["godpower"])))

    with st.container(key="logbook_card_box"):
        if st.button(
            "Important",
            key="open_important_logs_btn",
            help="Show only major events: level ups, boss kills, quest completions, deaths.",
        ):
            show_important_logs(state)

        st.markdown(
            f"""
            <div class="div-card" style="margin-bottom: 0;">
              <div class="div-card-header" style="height:40px; box-sizing:border-box; display:flex; align-items:center; justify-content:center;">Logbook</div>
              <div class="div-log-box">
                {logs_html}
              </div>
              <div class="div-card-header" style="border-top: 1px solid #e0e0e0;">Power</div>
              <div class="div-card-body" style="padding-bottom: 6px;">
                <div style="display:flex; align-items:center; gap:12px;">
                  <span style="font-size:0.9rem; color:#333333; white-space:nowrap;">Godpower</span>
                  <div style="flex:1;">
                    <div class="div-bar-track" style="margin:0;">
                      <div class="div-bar-fill"
                           style="width:{godpower}%; background-color:#0044b3;"></div>
                    </div>
                  </div>
                  <span style="font-size:0.9rem; color:#333333; min-width:36px; text-align:right;">
                    {godpower}%
                  </span>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    can_whisper = godpower >= WHISPER_COST
    input_col, btn_col2 = st.columns([5, 1])
    with input_col:
        whisper_input = st.text_area(
            "Divine Whisper",
            height=68,
            label_visibility="collapsed",
            placeholder=(
                f"Whisper a divine command ({WHISPER_COST} Godpower)..."
                if can_whisper
                else f"Not enough Godpower ({godpower}/{WHISPER_COST})..."
            ),
            disabled=not can_whisper,
            key="divine_whisper_input",
        )
    with btn_col2:
        if st.button(
            f"Send (-{WHISPER_COST})",
            use_container_width=True,
            disabled=not can_whisper,
        ):
            clean_whisper = whisper_input.strip()
            if clean_whisper and state["godpower"] >= WHISPER_COST:
                now_str = datetime.now().strftime("%H:%M")
                state["godpower"] = max(0, state["godpower"] - WHISPER_COST)
                state["logbook"].append(f"[{now_str}] [Divine Whisper] {clean_whisper}")
                packet = ask_apostle(state, clean_whisper)
                if packet.dialogue:
                    apostle_name = state.get("apostle", "Apostle")
                    state["logbook"].append(f"[{now_str}] {apostle_name}: {packet.dialogue}")
                execute_ai_action(state, packet)
                st.rerun()