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
        '<svg width="270" height="205" viewBox="0 0 290 220" xmlns="http://www.w3.org/2000/svg">'
        + "".join(lines_svg)
        + "".join(circles_svg)
        + arrow_svg
        + "</svg>"
    )

    hotspots_html: list[str] = []
    for code, info in WORLD_NODES.items():
        left_pct = (info["x"] / 290) * 100
        top_pct = (info["y"] / 220) * 100
        full_name = html.escape(info["name"])
        label = html.escape(info.get("label", ""))
        tooltip_text = f"{full_name} ({label})" if label else full_name

        if info["x"] < 90:
            h_pos = "left: 0;"
        elif info["x"] > 200:
            h_pos = "right: 0;"
        else:
            h_pos = "left: 50%; transform: translateX(-50%);"

        v_pos = "top: calc(100% + 6px);" if info["y"] < 85 else "bottom: calc(100% + 6px);"

        hotspots_html.append(
            f'<div class="div-map-hotspot" title="{tooltip_text}" '
            f'style="left:{left_pct:.2f}%; top:{top_pct:.2f}%;">'
            f'<span class="div-map-tooltip" style="{h_pos} {v_pos}">{tooltip_text}</span>'
            f'</div>'
        )

    return (
        f'<div class="div-map-wrapper">'
        f'{svg_to_img_tag(raw_svg, 270, 205)}'
        f'{"".join(hotspots_html)}'
        f'</div>'
    )


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
            <div class="div-serif" style="margin-top:6px; margin-bottom:0;">
                {loc_caption}
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