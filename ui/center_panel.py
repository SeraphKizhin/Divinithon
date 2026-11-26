import streamlit as st
import html
import re
from datetime import datetime
from ui.styles import progress_bar_html, render_html
from core.llm_client import ask_apostle
from core.game_engine import execute_ai_action

IMPORTANT_MARKER = "★"
WHISPER_COST = 15

HURRY_KEYWORDS = ("hurry", "faster", "quick", "chop chop", "speed up", "move it")
HEAL_KEYWORDS = ("heal", "cure", "mend", "restore hp", "full hp", "revitalize")
HEAL_COST = 10

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
        apostle_name = str(state.get("apostle", "Apostle"))
        log_items = []
        for entry in reversed(entries):
            cleaned = entry.replace(IMPORTANT_MARKER, "").strip()
            timestamp, msg = _parse_log_line(cleaned)
            color, is_bold = _get_log_color(msg, apostle_name)
            weight = "font-weight:600;" if is_bold else ""
            log_items.append(
                f'<div class="div-log-entry">'
                f'<div class="div-log-time">{html.escape(timestamp)}</div>'
                f'<div class="div-log-msg" style="color:{color}; {weight}">{html.escape(msg)}</div>'
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

    apostle_name = str(state.get("apostle", "Apostle"))
    log_items = []
    prev_was_whisper = False

    for entry in state["logbook"]:
        cleaned = entry.replace(IMPORTANT_MARKER, "").strip()
        timestamp, msg = _parse_log_line(cleaned)
        is_whisper = msg.startswith("[Divine Whisper]")
        is_reply = prev_was_whisper and msg.startswith(f"{apostle_name}:")

        color, is_bold = _get_log_color(msg, apostle_name, is_whisper_reply=is_reply)
        weight = "font-weight:600;" if is_bold else ""

        log_items.append(
            f'<div class="div-log-entry">'
            f'<div class="div-log-time">{html.escape(timestamp)}</div>'
            f'<div class="div-log-msg" style="color:{color}; {weight}">{html.escape(msg)}</div>'
            f'</div>'
        )
        prev_was_whisper = is_whisper

    logs_html = "".join(reversed(log_items))
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
    is_heal_text = any(kw in whisper_input.lower() for kw in HEAL_KEYWORDS)
    can_send_now = godpower >= (HEAL_COST if is_heal_text else WHISPER_COST)

    with btn_col2:
        if st.button(
            f"Send (-{WHISPER_COST})",
            use_container_width=True,
            disabled=not can_send_now,
        ):
            clean_whisper = whisper_input.strip()
            is_heal_cmd = any(kw in clean_whisper.lower() for kw in HEAL_KEYWORDS)
            required_gp = HEAL_COST if is_heal_cmd else WHISPER_COST

            if clean_whisper and state["godpower"] >= required_gp:
                now_str = datetime.now().strftime("%H:%M")
                if not is_heal_cmd:
                    state["godpower"] = max(0, state["godpower"] - WHISPER_COST)

                state["logbook"].append(f"[{now_str}] [Divine Whisper] {clean_whisper}")
                packet = ask_apostle(state, clean_whisper)

                if (
                    packet.action == "idle"
                    and state.get("dead_until") is None
                    and is_heal_cmd
                ):
                    packet.action = "heal"
                    packet.target = "none"
                elif (
                    packet.action == "idle"
                    and state.get("active_enemy") is None
                    and state.get("dead_until") is None
                    and any(kw in clean_whisper.lower() for kw in HURRY_KEYWORDS)
                ):
                    packet.action = "hurry"
                    packet.target = "none"
                if packet.action == "heal" and not is_heal_cmd:
                    state["godpower"] = min(100, state["godpower"] + WHISPER_COST)

                if packet.dialogue:
                    apostle_name = state.get("apostle", "Apostle")
                    state["logbook"].append(f"[{now_str}] {apostle_name}: {packet.dialogue}")
                execute_ai_action(state, packet)
                st.rerun()

def _get_log_color(msg: str, apostle_name: str, is_whisper_reply: bool = False) -> tuple[str, bool]:
    lower = msg.lower()

    if msg.startswith("[Divine Whisper]"):
        return "#0044b3", True  
    if is_whisper_reply or (apostle_name and msg.startswith(f"{apostle_name}:")):
        return "#2b7de9", False 

    combat_keywords = (
        "dmg", "defeated", "fatal blow", "ambushed", "jumps out",
        "combat begins", "boss encounter", "boss music", "fled from",
        "tried to flee", "blocks the path", "crashes onto the trail",
        "steps out, cracking", "walked straight into", "stands before",
    )
    if any(k in lower for k in combat_keywords):
        return "#c62828", False 

    quest_keywords = (
        "quest complete", "new quest", "quest started", "bounty board",
        "begged for help", "handed ", "engraving", "turned in '",
        "wrapped up '", "completed '", "is finally done", "finished '",
        "quest bonus rewards",
    )
    if any(k in lower for k in quest_keywords):
        return "#c2185b", False  

    trade_keywords = (
        "window-shops", "bought", "splurged", "handed over", "picked up",
        "blew ", "spent ", "sold ", "haggled", "offloaded", "shopkeeper",
        "price tags", "worth the gold",
    )
    if any(k in lower for k in trade_keywords):
        return "#b27b00", False  

    return "#333333", False  