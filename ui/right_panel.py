import streamlit as st
from typing import Optional
from core.models import Equipment
import html
from ui.styles import render_html, svg_to_img_tag

def _build_map_svg(current_location: str) -> str:
    nodes = {
        "NF": (48, 45),
        "EP": (212, 118),
        "MF": (68, 198),
        "OE": (160, 295),
    }

    circles_svg = []
    for code, (cx, cy) in nodes.items():
        is_current = code == current_location
        stroke = "#0055cc" if is_current else "#888888"
        stroke_w = "2.5" if is_current else "1.2"
        fill = "#eef5ff" if is_current else "#ffffff"
        circles_svg.append(
            f'<circle cx="{cx}" cy="{cy}" r="22" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}"/>'
            f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="600" fill="#222222">{code}</text>'
        )

    raw_svg = f"""
    <svg width="250" height="335" viewBox="0 0 250 335" xmlns="http://www.w3.org/2000/svg">
      <path d="M 68 48 C 140 38, 210 55, 212 96" fill="none" stroke="#111111" stroke-width="2.2"/>
      <path d="M 55 66 C 85 110, 115 135, 190 122" fill="none" stroke="#111111" stroke-width="2.2"/>
      <path d="M 122 128 C 98 145, 80 160, 72 176" fill="none" stroke="#111111" stroke-width="2.2"/>
      <path d="M 212 140 C 218 195, 185 190, 168 210 C 155 225, 160 250, 160 273" fill="none" stroke="#111111" stroke-width="2.2"/>
      <path d="M 54 216 C 25 275, 45 330, 138 302" fill="none" stroke="#111111" stroke-width="2.2"/>
      <polygon points="108,45 96,39 99,45 96,51" fill="#0066ff"/>
      {''.join(circles_svg)}
    </svg>
    """
    return f'<div style="display:flex; justify-content:center; padding: 6px 0;">{svg_to_img_tag(raw_svg, 250, 335)}</div>'


def _format_equip_parts(slot_item: Optional[Equipment]) -> tuple[str, str]:
    if slot_item is None:
        return "Empty", "+0"
    return html.escape(slot_item.name), f"+{slot_item.bonus}"


def render_right_column(state: dict) -> None:
    map_html = f"""
    <div class="div-card">
      <div class="div-card-header">Map</div>
      <div class="div-card-body" style="padding: 8px;">
        {_build_map_svg(state['current_location'])}
      </div>
    </div>
    """
    render_html(map_html)

    slots = [
        ("Mainhand", state["equipment"]["mainhand"]),
        ("Offhand", state["equipment"]["offhand"]),
        ("Body", state["equipment"]["body"]),
        ("Special", state["equipment"]["special"]),
        ("Additional", state["equipment"]["additional"]),
    ]

    slot_blocks = []
    for label, item in slots:
        item_name, bonus_str = _format_equip_parts(item)
        slot_blocks.append(
            f'<div class="div-equip-slot">'
            f'<div class="div-equip-title">{label}</div>'
            f'<div class="div-row" style="margin-bottom:0;">'
            f'<span>{item_name}</span>'
            f'<span>{bonus_str}</span>'
            f'</div>'
            f'</div>'
        )

    equip_html = f"""
    <div class="div-card">
      <div class="div-card-header">Equipment</div>
      <div class="div-card-body">
        {''.join(slot_blocks)}
      </div>
    </div>
    """
    render_html(equip_html)