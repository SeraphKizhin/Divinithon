import random
from core.models import ActiveMonster, Equipment, Monster, MonsterTier

TIER_CONFIG: dict[MonsterTier, dict] = {
    "normal": {
        "base_hp": 50,
        "spawn_weight": 75,
        "equip_start_chance": 10,
        "equip_chance_decay": 10,
        "sellable_range": (1, 2),
    },
    "mini_boss": {
        "base_hp": 120,
        "spawn_weight": 20,
        "equip_start_chance": 50,
        "equip_chance_decay": 10,
        "sellable_range": (1, 3),
    },
    "boss": {
        "base_hp": 250,
        "spawn_weight": 5,
        "equip_start_chance": 100,
        "equip_chance_decay": 20,
        "sellable_range": (2, 4),
    },
}


def calculate_monster_hp(
    tier: MonsterTier,
    apostle_lvl: int,
    hp_scale_per_lvl: float = 0.2,
) -> int:
    """
    Scales monster HP based on Apostle level.
    Level 1 uses exact base HP (50 / 120 / 250).
    Each additional level increases HP by hp_scale_per_lvl (default +20%).
    """
    base_hp = TIER_CONFIG[tier]["base_hp"]
    level_offset = max(0, apostle_lvl - 1)
    multiplier = 1.0 + (hp_scale_per_lvl * level_offset)
    return round(base_hp * multiplier)


def spawn_monster(
    apostle_lvl: int,
    monsters_catalog: list[Monster],
    hp_scale_per_lvl: float = 0.2,
) -> ActiveMonster:
    """Picks a monster tier using spawn weights, then spawns a scaled ActiveMonster."""
    available_tiers = [
        tier for tier in TIER_CONFIG
        if any(m.tier == tier for m in monsters_catalog)
    ]
    weights = [TIER_CONFIG[tier]["spawn_weight"] for tier in available_tiers]

    chosen_tier: MonsterTier = random.choices(available_tiers, weights=weights, k=1)[0]
    tier_pool = [m for m in monsters_catalog if m.tier == chosen_tier]
    template = random.choice(tier_pool)

    scaled_hp = calculate_monster_hp(chosen_tier, apostle_lvl, hp_scale_per_lvl)
    return ActiveMonster(
        name=template.name,
        tier=chosen_tier,
        max_hp=scaled_hp,
        cur_hp=scaled_hp,
        sellable_drops=template.sellable_drops,
    )


def roll_rewards(
    monster: ActiveMonster,
    equipment_catalog: list[Equipment],
) -> dict:
    """
    Rolls cascading equipment drops and monster-exclusive city-sellable loot.
    Returns {"equipment": list[Equipment], "sellables": dict[str, int]}.
    """
    cfg = TIER_CONFIG[monster.tier]

    dropped_equipment: list[Equipment] = []
    current_chance = cfg["equip_start_chance"]
    decay = cfg["equip_chance_decay"]

    while current_chance > 0 and equipment_catalog:
        if random.randint(1, 100) <= current_chance:
            dropped_equipment.append(random.choice(equipment_catalog))
            current_chance -= decay
        else:
            break

    min_qty, max_qty = cfg["sellable_range"]
    drop_count = random.randint(min_qty, max_qty)
    dropped_sellables: dict[str, int] = {}

    if monster.sellable_drops:
        picked_items = random.choices(monster.sellable_drops, k=drop_count)
        for item in picked_items:
            dropped_sellables[item.name] = dropped_sellables.get(item.name, 0) + 1

    return {
        "equipment": dropped_equipment,
        "sellables": dropped_sellables,
    }


if __name__ == "__main__":
    from data.catalog import EQUIPMENTS, MONSTERS

    for lvl in (1, 5):
        enemy = spawn_monster(apostle_lvl=lvl, monsters_catalog=MONSTERS)
        rewards = roll_rewards(enemy, EQUIPMENTS)
        print(f"Apostle Lv.{lvl} spawned: {enemy.name} ({enemy.tier}) | HP: {enemy.max_hp}")
        print(f"  Equipment drops: {[e.name for e in rewards['equipment']]}")
        print(f"  Sellable drops:  {rewards['sellables']}\n")