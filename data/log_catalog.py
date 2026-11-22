CITY_LOGS: dict[str, list[str]] = {
    "wandering": [
        "{apostle} strolls through {location}, pretending to look important.",
        "Window-shopping in {location}. Everything is overpriced.",
        "{apostle} gets mildly lost in {location}'s back alleys and blames {god}.",
        "Taking a breather by the {location} fountain. Smells like soup and bad decisions.",
        "{apostle} watches a street juggler in {location} and briefly considers a career change.",
    ],
    "selling": [
        "Sold {item} x{qty} to a suspiciously eager merchant for {gold} Gold.",
        "Haggled furiously and dumped {item} x{qty} for {gold} Gold. Pure profit.",
        "The shopkeeper squinted at {item} x{qty}, sighed, and handed over {gold} Gold.",
        "Offloaded {item} x{qty} for {gold} Gold. My bag feels ten pounds lighter.",
    ],
    "buying": [
        "Bought {item} for {gold} Gold. Don't judge my spending habits, {god}.",
        "Splurged {gold} Gold on {item}. Surely this will keep me alive longer.",
        "Handed over {gold} Gold for {item}. The merchant's grin tells me I overpaid.",
        "Picked up {item} for {gold} Gold. Retail therapy at its finest.",
    ],
    "quest_found": [
        "Pulled a crumpled flyer off the {location} bounty board: '{quest}'.",
        "A frantic townsfolk grabbed {apostle}'s sleeve and begged for help: '{quest}'.",
        "Overheard a tavern rumor in {location}. New quest accepted: '{quest}'.",
        "Someone offered shiny coins to handle '{quest}'. {apostle} is in.",
    ],
    "quest_complete": [
        "Turned in '{quest}' at {location}! Collected {gold} Gold and a lukewarm 'thank you'.",
        "Quest '{quest}' complete! {apostle} poses heroically while pocketing {gold} Gold.",
        "Wrapped up '{quest}' in {location}. Earned {gold} Gold—not bad for a day's work.",
    ],
}

IDLE_CHATTER: list[str] = [
    "{apostle} mutters: 'Hey {god}, are you even watching, or did you fall asleep?'",
    "I swear my boots have a pebble in them, and it's definitely a test from {god}.",
    "{apostle} wonders if other Apostles get dental insurance.",
    "Talking to the sky again. The locals are starting to stare.",
    "{apostle} checks their pockets. Still no miracle gold. Typical.",
    "Dear {god}, if you're going to whisper in my head, at least make it useful.",
]

WILD_LOGS: dict[str, list[str]] = {
    "wandering": [
        "Trekking through {location}, swatting bugs and questioning life choices.",
        "{apostle} marches deeper into {location} with unearned confidence.",
        "Following a dirt trail in {location}. Nothing has tried to bite me yet.",
        "Pushing through the brush in {location}. Every twig snap sounds personal.",
    ],
    "found_treasure": [
        "Tripped over a half-buried chest in {location} and scored {item}!",
        "Spotted something shiny in the dirt—found {item} and {gold} Gold!",
        "{apostle} pried open a mossy lockbox and claimed {item}. Finders keepers.",
        "Lucky break! Stumbled onto a forgotten stash containing {item}.",
    ],
    "encounter_normal": [
        "A wild {enemy} jumps out of the bushes in {location}!",
        "{apostle} accidentally steps on a {enemy}'s tail. Combat begins!",
        "Ambushed by a grumpy {enemy}! Time to earn that EXP.",
        "A {enemy} blocks the path, looking way too confident for its own good.",
    ],
    "encounter_mini_boss": [
        "Warning! A towering {enemy} crashes onto the trail in {location}!",
        "The ground trembles—Mini-Boss {enemy} steps out, cracking its knuckles!",
        "{apostle} swallows hard. That's no regular mob—it's {enemy}!",
        "A fierce {enemy} ambushes {apostle}! Better pay attention, {god}.",
    ],
    "encounter_boss": [
        "BOSS ENCOUNTER! The sky darkens as {enemy} descends upon {location}!",
        "Boss music starts playing out of nowhere—{enemy} has appeared!",
        "Oh no. {apostle} just walked straight into {enemy}'s lair!",
        "A terrifying aura fills {location}: {enemy} stands before {apostle}!",
    ],
    "quest_found": [
        "Found a battered journal on the road in {location}. New quest: '{quest}'.",
        "A wounded traveler in {location} handed {apostle} a map: '{quest}'.",
        "Discovered a strange shrine with an engraving. Quest started: '{quest}'.",
    ],
    "quest_complete": [
        "Completed '{quest}' out in {location}! Claimed {gold} Gold for the trouble.",
        "'{quest}' is finally done! {apostle} celebrates alone in the wilderness with {gold} Gold.",
        "Against all odds, {apostle} finished '{quest}' and pocketed {gold} Gold.",
    ],
}