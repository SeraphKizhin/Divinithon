import random
import math
from core.models import ActiveMonster, Equipment, Monster, MonsterTier
from core.equipment_rules import roll_equipment_drop

TIER_CONFIG: dict[MonsterTier, dict] = {
    "normal": {
        "base_hp": 50,
        "spawn_weight": 75,
        "level_mult_range": (0.625, 1.25),
        "equip_start_chance": 10,
        "equip_chance_decay": 10,
        "sellable_range": (1, 2),
    },
    "mini_boss": {
        "base_hp": 120,
        "spawn_weight": 20,
        "level_mult_range": (1.0, 1.5),
        "equip_start_chance": 50,
        "equip_chance_decay": 10,
        "sellable_range": (1, 3),
    },
    "boss": {
        "base_hp": 250,
        "spawn_weight": 5,
        "level_mult_range": (1.25, 1.75),
        "equip_start_chance": 100,
        "equip_chance_decay": 20,
        "sellable_range": (2, 4),
    },
}

BASE_EXP_BY_TIER: dict[MonsterTier, int] = {
    "normal": 25,
    "mini_boss": 60,
    "boss": 150,
}

WILD_LVL_BONUS_PER_STACK = 1
WILD_MINIBOSS_WEIGHT_PER_STACK = 5
WILD_BOSS_WEIGHT_PER_STACK = 3

def calculate_monster_hp(
    tier: MonsterTier,
    monster_lvl: int,
    hp_mult: float = 1.0,
    hp_scale_per_lvl: float = 0.2,
) -> int:
    base_hp = TIER_CONFIG[tier]["base_hp"]
    level_offset = max(0, monster_lvl - 1)
    multiplier = 1.0 + (hp_scale_per_lvl * level_offset)
    return max(1, round(base_hp * multiplier * hp_mult))

def spawn_monster(
    apostle_lvl: int,
    monsters_catalog: list[Monster],
    wild_stay_stacks: int = 0,
    hp_scale_per_lvl: float = 0.2,
) -> ActiveMonster:
    available_tiers: list[MonsterTier] = [
        tier for tier in TIER_CONFIG
        if any(m.tier == tier for m in monsters_catalog)
    ]
    weights = get_scaled_spawn_weights(available_tiers, wild_stay_stacks)

    chosen_tier: MonsterTier = random.choices(available_tiers, weights=weights, k=1)[0]
    tier_pool = [m for m in monsters_catalog if m.tier == chosen_tier]
    template = random.choice(tier_pool)

    enemy_lvl = calculate_enemy_level(chosen_tier, apostle_lvl, wild_stay_stacks)
    scaled_hp = calculate_monster_hp(
        chosen_tier,
        enemy_lvl,
        hp_mult=template.hp_mult,
        hp_scale_per_lvl=hp_scale_per_lvl,
    )
    return ActiveMonster(
        name=template.name,
        tier=chosen_tier,
        level=enemy_lvl,
        max_hp=scaled_hp,
        cur_hp=scaled_hp,
        sellable_drops=template.sellable_drops,
        dmg_mult=template.dmg_mult,
    )

def roll_rewards(
    monster: ActiveMonster,
    equipment_catalog: list[Equipment],
    apostle_lvl: int = 1,
) -> dict:
    cfg = TIER_CONFIG[monster.tier]

    dropped_equipment: list[Equipment] = []
    current_chance = cfg["equip_start_chance"]
    decay = cfg["equip_chance_decay"]

    while current_chance > 0 and equipment_catalog:
        if random.randint(1, 100) <= current_chance:
            template = random.choice(equipment_catalog)
            dropped_equipment.append(roll_equipment_drop(template, apostle_lvl))
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

def calculate_enemy_level(
    tier: MonsterTier,
    apostle_lvl: int,
    wild_stay_stacks: int = 0,
) -> int:
    min_mult, max_mult = TIER_CONFIG[tier]["level_mult_range"]
    min_lvl = max(1, round(apostle_lvl * min_mult))
    max_lvl = max(min_lvl, math.ceil(apostle_lvl * max_mult))

    level_bonus = wild_stay_stacks * WILD_LVL_BONUS_PER_STACK
    return random.randint(min_lvl, max_lvl) + level_bonus

def get_scaled_spawn_weights(
    available_tiers: list[MonsterTier],
    wild_stay_stacks: int = 0,
) -> list[int]:
    weights: list[int] = []
    for tier in available_tiers:
        base_w = TIER_CONFIG[tier]["spawn_weight"]
        if tier == "mini_boss":
            w = base_w + (wild_stay_stacks * WILD_MINIBOSS_WEIGHT_PER_STACK)
        elif tier == "boss":
            w = base_w + (wild_stay_stacks * WILD_BOSS_WEIGHT_PER_STACK)
        else:
            # Reduce normal weight as threat escalates, keeping a small floor
            reduction = wild_stay_stacks * (
                WILD_MINIBOSS_WEIGHT_PER_STACK + WILD_BOSS_WEIGHT_PER_STACK
            )
            w = max(10, base_w - reduction)
        weights.append(w)
    return weights

if __name__ == "__main__":
    from data.catalog import MONSTERS

    print("=== Apostle Lv.40 | 0 stacks (default) ===")
    for _ in range(5):
        e = spawn_monster(40, MONSTERS, wild_stay_stacks=0)
        print(f"  [{e.tier:9}] {e.name} — Lv.{e.level} (HP: {e.max_hp})")

    print("\n=== Apostle Lv.40 | 8 stacks (lingering in wild) ===")
    for _ in range(5):
        e = spawn_monster(40, MONSTERS, wild_stay_stacks=8)
        print(f"  [{e.tier:9}] {e.name} — Lv.{e.level} (HP: {e.max_hp})")

def calculate_monster_exp(
    tier: MonsterTier,
    monster_lvl: int,
    exp_scale_per_lvl: float = 0.25,
) -> int:
    """Scales EXP yield based on monster tier and rolled level."""
    base_exp = BASE_EXP_BY_TIER[tier]
    level_offset = max(0, monster_lvl - 1)
    multiplier = 1.0 + (exp_scale_per_lvl * level_offset)
    return round(base_exp * multiplier)