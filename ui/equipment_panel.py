"""
equipment_panel.py — Multi-Theme RPG Equipment Panel for Divinithon
===========================================================================
Renders the bottom-right Equipment card with 5 gear slots (Mainhand, Offhand,
Body, Special, Additional) in 5 selectable fantasy/RPG aesthetic designs.

Features:
- Fixes the iframe clipping/trimming bug with box-sizing and calibrated heights.
- Interactive in-app theme selector to preview and compare 5 distinct RPG styles.
- Pure HTML/CSS rendered inside components.v1.html for 100% style isolation.

Usage:
    from ui.equipment_panel import render_equipment_panel
    render_equipment_panel(state)
"""

import streamlit.components.v1 as components
import streamlit as st
from typing import Optional

# ---------------------------------------------------------------------------
# Slot definitions: (state_key, icon, display_label)
# ---------------------------------------------------------------------------
EQUIPMENT_SLOTS: tuple[tuple[str, str, str], ...] = (
    ("mainhand",   "🗡️", "Mainhand"),
    ("offhand",    "🛡️", "Offhand"),
    ("body",       "⛓️", "Body"),
    ("special",    "🔮", "Special"),
    ("additional", "💍", "Additional"),
)

# ---------------------------------------------------------------------------
# 5 Distinct Visual Themes
# ---------------------------------------------------------------------------
THEMES: dict[str, dict] = {
    "1. Medieval Parchment (Aged Scroll)": {
        "header_title": "⚜ Equipment ⚜",
        "css": """
        body { 
            margin: 0; 
            padding: 2px;
            font-family: Georgia, 'Times New Roman', serif; 
            box-sizing: border-box;
            background: transparent;
        }
        * { box-sizing: border-box; }
        
        .eq-panel-wrapper {
            background: #e3cf9c;
            border: 4px double #6b4423;
            border-radius: 8px;
            padding: 14px 16px;
            box-shadow: inset 0 0 25px rgba(90, 50, 10, 0.45), 0 4px 12px rgba(0,0,0,0.3);
        }
        .eq-title-bar {
            text-align: center;
            padding-bottom: 8px;
            border-bottom: 2px solid #6b4423;
            margin-bottom: 6px;
        }
        .eq-title-text {
            font-size: 16px;
            font-weight: 700;
            color: #2b1d0e;
            letter-spacing: 4px;
            text-transform: uppercase;
        }
        .eq-slot {
            background: rgba(255, 244, 214, 0.55);
            border: 1px solid #7c532b;
            border-left: 4px solid #4a2f14;
            border-radius: 5px;
            padding: 8px 12px;
            margin-top: 8px;
        }
        .eq-slot-dimmed {
            opacity: 0.6;
            border-style: dashed;
            background: rgba(255, 244, 214, 0.25);
        }
        .eq-slot-lbl {
            font-size: 11px;
            font-weight: 700;
            color: #4a2f14;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 4px;
        }
        .eq-item-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        .eq-item-name {
            font-size: 14px;
            font-weight: 600;
            color: #2b1d0e;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            flex: 1;
        }
        .eq-item-name-empty {
            font-style: italic;
            color: #7b6644;
            font-weight: 400;
        }
        .eq-stat {
            font-family: Georgia, serif;
            font-weight: 700;
            font-size: 13.5px;
            color: #fce8bd;
            background: #8b1a1a;
            border: 1px solid #571010;
            border-radius: 50%;
            width: 34px;
            height: 34px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .eq-stat-dim {
            color: #7b6644;
            background: transparent;
            border: 1px dashed #7b6644;
            box-shadow: none;
        }
        """
    },

    "2. Celestial Astral (Divine Gold & Void)": {
        "header_title": "✦ Celestial Reliquary ✦",
        "css": """
        body { 
            margin: 0; 
            padding: 2px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: transparent;
        }
        * { box-sizing: border-box; }

        .eq-panel-wrapper {
            background: radial-gradient(circle at 50% 0%, #171b33 0%, #0c0e1a 100%);
            border: 1px solid #373e68;
            border-top: 3px solid #d4af37;
            border-radius: 10px;
            padding: 14px 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), inset 0 0 15px rgba(212, 175, 55, 0.08);
        }
        .eq-title-bar {
            text-align: center;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(212, 175, 55, 0.35);
            margin-bottom: 6px;
        }
        .eq-title-text {
            font-size: 14px;
            font-weight: 700;
            color: #f7e7a9;
            letter-spacing: 3px;
            text-transform: uppercase;
            text-shadow: 0 0 10px rgba(247, 231, 169, 0.4);
        }
        .eq-slot {
            background: rgba(27, 32, 60, 0.65);
            border: 1px solid #2b335c;
            border-left: 3px solid #9d8137;
            border-radius: 6px;
            padding: 8px 12px;
            margin-top: 8px;
        }
        .eq-slot-dimmed {
            opacity: 0.5;
            border-left-color: #43496a;
            background: rgba(20, 24, 45, 0.4);
        }
        .eq-slot-lbl {
            font-size: 11px;
            font-weight: 700;
            color: #c4b5fd;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 4px;
        }
        .eq-item-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        .eq-item-name {
            font-size: 13.5px;
            font-weight: 500;
            color: #f1f2fa;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            flex: 1;
        }
        .eq-item-name-empty {
            font-style: italic;
            color: #697096;
            font-weight: 400;
        }
        .eq-stat {
            font-family: "Courier New", monospace;
            font-weight: 700;
            font-size: 13px;
            color: #ffd966;
            background: rgba(212, 175, 55, 0.18);
            border: 1px solid #d4af37;
            border-radius: 6px;
            padding: 3px 8px;
            flex-shrink: 0;
            text-shadow: 0 0 6px rgba(255, 217, 102, 0.4);
        }
        .eq-stat-dim {
            color: #697096;
            background: rgba(43, 51, 92, 0.3);
            border-color: #3e4670;
            text-shadow: none;
        }
        """
    },

    "3. Gothic Obsidian (Bloodstone Runes)": {
        "header_title": "❖ Crypt Armory ❖",
        "css": """
        body { 
            margin: 0; 
            padding: 2px;
            font-family: 'Cinzel', 'Palatino', serif;
            background: transparent;
        }
        * { box-sizing: border-box; }

        .eq-panel-wrapper {
            background: #101114;
            border: 2px solid #38191d;
            border-radius: 6px;
            padding: 14px 16px;
            box-shadow: inset 0 0 30px rgba(70, 10, 18, 0.4), 0 4px 16px rgba(0,0,0,0.7);
        }
        .eq-title-bar {
            text-align: center;
            padding-bottom: 8px;
            border-bottom: 2px solid #5e1d24;
            margin-bottom: 6px;
        }
        .eq-title-text {
            font-size: 15px;
            font-weight: 700;
            color: #e6a8ad;
            letter-spacing: 3.5px;
            text-transform: uppercase;
        }
        .eq-slot {
            background: #17181f;
            border: 1px solid #2e1d22;
            border-left: 4px solid #8f2631;
            border-radius: 4px;
            padding: 8px 12px;
            margin-top: 8px;
        }
        .eq-slot-dimmed {
            opacity: 0.55;
            border-left-color: #3b2024;
            border-style: dotted;
        }
        .eq-slot-lbl {
            font-size: 11px;
            font-weight: 700;
            color: #cf6679;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 4px;
        }
        .eq-item-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        .eq-item-name {
            font-size: 13.5px;
            color: #e5e5ea;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            flex: 1;
        }
        .eq-item-name-empty {
            font-style: italic;
            color: #635759;
        }
        .eq-stat {
            font-family: monospace;
            font-weight: 700;
            font-size: 13px;
            color: #ffb4be;
            background: #471118;
            border: 1px solid #801e2b;
            border-radius: 4px;
            padding: 3px 8px;
            flex-shrink: 0;
            box-shadow: 0 0 8px rgba(180, 30, 50, 0.3);
        }
        .eq-stat-dim {
            color: #635759;
            background: #201a1c;
            border-color: #36292c;
            box-shadow: none;
        }
        """
    },

    "4. Arcane Grimoire (Mana Crystals & Violet)": {
        "header_title": "⚡ Arcane Inventory ⚡",
        "css": """
        body { 
            margin: 0; 
            padding: 2px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: transparent;
        }
        * { box-sizing: border-box; }

        .eq-panel-wrapper {
            background: linear-gradient(170deg, #18122B 0%, #0d0a1a 100%);
            border: 1px solid #3F2E56;
            border-top: 3px solid #00F0FF;
            border-radius: 10px;
            padding: 14px 16px;
            box-shadow: inset 0 0 20px rgba(0, 240, 255, 0.08), 0 4px 16px rgba(0,0,0,0.5);
        }
        .eq-title-bar {
            text-align: center;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(0, 240, 255, 0.3);
            margin-bottom: 6px;
        }
        .eq-title-text {
            font-size: 14px;
            font-weight: 700;
            color: #00F0FF;
            letter-spacing: 3px;
            text-transform: uppercase;
            text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
        }
        .eq-slot {
            background: rgba(36, 27, 61, 0.5);
            border: 1px solid #3d2f5a;
            border-radius: 6px;
            padding: 8px 12px;
            margin-top: 8px;
        }
        .eq-slot-dimmed {
            opacity: 0.5;
            background: rgba(22, 17, 38, 0.4);
        }
        .eq-slot-lbl {
            font-size: 11px;
            font-weight: 700;
            color: #d8b4fe;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 4px;
        }
        .eq-item-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        .eq-item-name {
            font-size: 13.5px;
            color: #F1F0F5;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            flex: 1;
        }
        .eq-item-name-empty {
            font-style: italic;
            color: #726786;
        }
        .eq-stat {
            font-family: monospace;
            font-weight: 700;
            font-size: 13px;
            color: #00F0FF;
            background: rgba(0, 240, 255, 0.12);
            border: 1px solid #00F0FF;
            border-radius: 12px;
            padding: 2px 9px;
            flex-shrink: 0;
            text-shadow: 0 0 5px rgba(0, 240, 255, 0.4);
        }
        .eq-stat-dim {
            color: #726786;
            background: transparent;
            border-color: #4a3e63;
            text-shadow: none;
        }
        """
    },

    "5. Ironclad Forge (Dwarven Steel & Brass)": {
        "header_title": "🛡 War Gear & Arsenal 🛡",
        "css": """
        body { 
            margin: 0; 
            padding: 2px;
            font-family: 'Verdana', sans-serif;
            background: transparent;
        }
        * { box-sizing: border-box; }

        .eq-panel-wrapper {
            background: #20232a;
            border: 2px solid #484f5d;
            border-top: 4px solid #b87333;
            border-radius: 6px;
            padding: 14px 16px;
            box-shadow: inset 0 0 15px rgba(0,0,0,0.5), 0 4px 12px rgba(0,0,0,0.4);
        }
        .eq-title-bar {
            text-align: center;
            padding-bottom: 8px;
            border-bottom: 2px solid #5a422d;
            margin-bottom: 6px;
        }
        .eq-title-text {
            font-size: 14px;
            font-weight: 700;
            color: #e5b382;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .eq-slot {
            background: #2b2f38;
            border: 1px solid #3c424f;
            border-left: 4px solid #b87333;
            border-radius: 4px;
            padding: 8px 12px;
            margin-top: 8px;
        }
        .eq-slot-dimmed {
            opacity: 0.55;
            border-left-color: #555d6e;
        }
        .eq-slot-lbl {
            font-size: 10.5px;
            font-weight: 700;
            color: #baa287;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 4px;
        }
        .eq-item-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        .eq-item-name {
            font-size: 13.5px;
            font-weight: 600;
            color: #eceff4;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            flex: 1;
        }
        .eq-item-name-empty {
            font-style: italic;
            color: #717887;
            font-weight: 400;
        }
        .eq-stat {
            font-family: monospace;
            font-weight: 700;
            font-size: 13.5px;
            color: #20232a;
            background: #d49b42;
            border-radius: 4px;
            padding: 2px 8px;
            flex-shrink: 0;
        }
        .eq-stat-dim {
            color: #717887;
            background: #393e4a;
        }
        """
    },
}


def _slot_html(icon: str, label: str, item_name: Optional[str], bonus: int) -> str:
    """Returns the HTML string for one equipment slot card."""
    is_empty = item_name is None
    card_cls = "eq-slot eq-slot-dimmed" if is_empty else "eq-slot"
    name_cls = "eq-item-name eq-item-name-empty" if is_empty else "eq-item-name"
    stat_cls = "eq-stat eq-stat-dim" if is_empty else "eq-stat"
    name_text = "— Empty —" if is_empty else item_name

    return (
        f'<div class="{card_cls}">'
        f'  <div class="eq-slot-lbl">{icon} {label}</div>'
        f'  <div class="eq-item-row">'
        f'    <span class="{name_cls}">{name_text}</span>'
        f'    <span class="{stat_cls}">+{bonus}</span>'
        f'  </div>'
        f'</div>'
    )


def render_equipment_panel(state: dict) -> None:
    """
    Renders the Equipment panel inside the current Streamlit column.
    Provides a theme selector allowing the user to test 5 distinct visual designs.
    """
    # Interactive Theme Selector
    theme_names = list(THEMES.keys())
    chosen_theme = st.selectbox(
        "Style Variant",
        theme_names,
        index=0,
        label_visibility="collapsed",
        key="equipment_panel_theme_choice"
    )

    theme_data = THEMES[chosen_theme]
    equipment = state.get("equipment", {})

    cards_html = []
    for key, icon, label in EQUIPMENT_SLOTS:
        slot_data = equipment.get(key)
        if slot_data is not None:
            cards_html.append(_slot_html(icon, label, slot_data.get("name"), slot_data.get("bonus", 0)))
        else:
            cards_html.append(_slot_html(icon, label, None, 0))

    full_html = (
        f"<style>{theme_data['css']}</style>"
        f'<div class="eq-panel-wrapper">'
        f'  <div class="eq-title-bar">'
        f'    <span class="eq-title-text">{theme_data["header_title"]}</span>'
        f'  </div>'
        + "".join(cards_html)
        + '</div>'
    )

    # Generous height to prevent bottom trimming of the "Additional" slot
    # 5 slots * 62px + title (45px) + padding/margins + safety buffer
    panel_height = 490
    components.html(full_html, height=panel_height, scrolling=False)
