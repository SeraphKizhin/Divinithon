from typing import Literal

ZoneType = Literal["city", "wild"]

WORLD_NODES: dict[str, dict] = {
    "NF": {
        "name": "Northern Front",
        "zone": "city",
        "label": "City",
        "x": 68,
        "y": 78,
    },
    "WW": {
        "name": "Whispering Willow",
        "zone": "wild",
        "label": "Wilderness",
        "x": 218,
        "y": 68,
    },
    "OE": {
        "name": "Open Easel",
        "zone": "city",
        "label": "Trade City",
        "x": 82,
        "y": 176,
    },
    "MF": {
        "name": "Mykitiokan Farlands",
        "zone": "wild",
        "label": "Wilderness",
        "x": 224,
        "y": 172,
    },
}

MAP_EDGES: list[tuple[str, str]] = [
    ("NF", "WW"),
    ("NF", "OE"),
    ("WW", "OE"),
    ("WW", "MF"),
    ("OE", "MF"),
]


def get_node_name(code: str) -> str:
    return WORLD_NODES.get(code, {}).get("name", code)


def get_node_zone(code: str) -> ZoneType:
    return WORLD_NODES.get(code, {}).get("zone", "wild")


def get_neighbors(code: str) -> list[str]:
    neighbors: list[str] = []
    for a, b in MAP_EDGES:
        if a == code:
            neighbors.append(b)
        elif b == code:
            neighbors.append(a)
    return neighbors