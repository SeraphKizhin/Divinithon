import streamlit as st
import html
from typing import Optional
from core.models import Equipment
from ui.styles import render_html, svg_to_img_tag
from data.world_map import MAP_EDGES, WORLD_NODES

def _build_map_svg(current_location: str, travel: Optional[dict] = None) -> str:
    lines_svg: list[str] = []
    active_edge = {travel["from"], travel["to"]} if travel else set()

    for a, b in MAP_EDGES:
        na, nb = WORLD_NODES[a], WORLD_NODES[b]
        is_active_road = bool(travel) and {a, b} == active_edge
        stroke = "#2b7de9" if is_active_road else "#b5b5b5"
        stroke_w = "3.5" if is_active_road else "2"
        lines_svg.append(
            f'<line x1="{na["x"]}" y1="{na["y"]}" x2="{nb["x"]}" y2="{nb["y"]}" '
            f'stroke="{stroke}" stroke-width="{stroke_w}" />'
        )

    circles_svg: list[str] = []
    arrow_svg = ""

    for code, info in WORLD_NODES.items():
        cx, cy = info["x"], info["y"]
        is_current = (travel is None) and (code == current_location)
        is_city = info["zone"] == "city"

        if is_current:
            fill = "#d9ecff"
            stroke = "#2b7de9"
            stroke_w = "2.5"
        elif is_city:
            fill = "#f3efe6"
            stroke = "#888888"
            stroke_w = "1.5"
        else:
            fill = "#eef3ea"
            stroke = "#888888"
            stroke_w = "1.5"

        circles_svg.append(
            f'<circle cx="{cx}" cy="{cy}" r="22" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" />'
            f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="600" fill="#222222">{code}</text>'
        )

        if is_current:
            tip_y = cy - 26
            base_y = cy - 42
            stem_top = cy - 50
            arrow_svg = (
                f'<line x1="{cx}" y1="{stem_top}" x2="{cx}" y2="{base_y + 4}" '
                f'stroke="#2b7de9" stroke-width="3" stroke-linecap="round" />'
                f'<polygon points="{cx - 7},{base_y + 2} {cx + 7},{base_y + 2} {cx},{tip_y}" '
                f'fill="#2b7de9" />'
            )

    if travel is not None:
        orig = WORLD_NODES[travel["from"]]
        dest = WORLD_NODES[travel["to"]]
        steps = max(1, travel.get("steps", 3))
        t = (travel.get("progress", 0) + 1) / (steps + 1)
        ax = orig["x"] + (dest["x"] - orig["x"]) * t
        ay = orig["y"] + (dest["y"] - orig["y"]) * t

        tip_y = ay - 7
        base_y = ay - 22
        stem_top = ay - 30
        arrow_svg = (
            f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="5" fill="#2b7de9" stroke="#ffffff" stroke-width="1.5" />'
            f'<line x1="{ax:.1f}" y1="{stem_top:.1f}" x2="{ax:.1f}" y2="{base_y + 4:.1f}" '
            f'stroke="#2b7de9" stroke-width="3" stroke-linecap="round" />'
            f'<polygon points="{ax - 7:.1f},{base_y + 2:.1f} {ax + 7:.1f},{base_y + 2:.1f} {ax:.1f},{tip_y:.1f}" '
            f'fill="#2b7de9" />'
        )

    raw_svg = (
        '<svg width="270" height="220" viewBox="0 0 290 220" xmlns="http://www.w3.org/2000/svg">'
        + "".join(lines_svg)
        + "".join(circles_svg)
        + arrow_svg
        + "</svg>"
    )
    return f'<div style="display:flex; justify-content:center; padding:4px 0;">{svg_to_img_tag(raw_svg, 270, 220)}</div>'


def render_right_column(state: dict) -> None:
    loc_code = state.get("current_location", "NF")
    travel = state.get("travel")

    if travel is not None:
        orig_name = WORLD_NODES[travel["from"]]["name"]
        dest_name = WORLD_NODES[travel["to"]]["name"]
        loc_caption = f"<strong>On the Road:</strong> {orig_name} &rarr; {dest_name}"
    else:
        loc_info = WORLD_NODES.get(loc_code, {"name": loc_code, "label": "Unknown"})
        loc_caption = f'<strong>{loc_info["name"]}</strong> ({loc_info["label"]})'

    map_html = f"""
    <div class="div-card">
        <div class="div-card-header">Map</div>
        <div class="div-card-body">
            {_build_map_svg(loc_code, travel)}
            <div class="div-serif" style="margin-top:6px;">
                {loc_caption}
            </div>
            <div style="font-size:0.75rem; color:#666666; text-align:center; line-height:1.5;">
                NF: Northern Front &bull; OE: Open Easel<br>
                WW: Whispering Willow &bull; MF: Mykitiokan Farlands
            </div>
        </div>
    </div>
    """
    render_html(map_html)

    eq = state["equipment"]
    slots = [
        ("Mainhand", eq["mainhand"]),
        ("Offhand", eq["offhand"]),
        ("Body", eq["body"]),
        ("Special", eq["special"]),
        ("Additional", eq["additional"]),
    ]

    slots_html = ""
    for label, item in slots:
        item_name, bonus_str = _format_equip_parts(item)
        slots_html += f"""
        <div class="div-equip-slot">
            <div class="div-equip-title">{label}</div>
            <div class="div-row" style="margin-bottom:0;">
                <span class="div-value">{item_name}</span>
                <span class="div-value" style="font-weight:600;">{bonus_str}</span>
            </div>
        </div>
        """

    equip_html = f"""
    <div class="div-card">
        <div class="div-card-header">Equipment</div>
        <div class="div-card-body">{slots_html}</div>
    </div>
    """
    render_html(equip_html)


def _format_equip_parts(slot_item: Optional[Equipment]) -> tuple[str, str]:
    if slot_item is None:
        return "Empty", ""
    return html.escape(slot_item.name), f"+{slot_item.bonus}"