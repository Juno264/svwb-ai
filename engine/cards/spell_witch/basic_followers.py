# Basic Spell Witch followers for rotation format

from svwb_ai.engine.cards.base import FollowerCard, SpellCard, AmuletCard


# Followers
class AirJinn(FollowerCard):
    def __init__(self):
        super().__init__(
            card_id="air_jinn",
            name="Air Jinn",
            cost=1,
            attack=1,
            hp=1
        )


class KingElephant(FollowerCard):
    def __init__(self):
        super().__init__(
            card_id="king_elephant",
            name="King Elephant",
            cost=4,
            attack=4,
            hp=4
        )


class HighSorcerer(FollowerCard):
    def __init__(self):
        super().__init__(
            card_id="high_sorcerer",
            name="High Sorcerer",
            cost=3,
            attack=2,
            hp=3
        )
        # This card would have fanfare or spell boost effects


class VeilWitch(FollowerCard):
    def __init__(self):
        super().__init__(
            card_id="veil_witch",
            name="Veil Witch",
            cost=2,
            attack=1,
            hp=2
        )


# Spells
class Flame(SpellCard):
    def __init__(self):
        super().__init__(
            card_id="flame",
            name="Flame",
            cost=1
        )


class Frostbolt(SpellCard):
    def __init__(self):
        super().__init__(
            card_id="frostbolt",
            name="Frostbolt",
            cost=2
        )


class MassSpell(SpellCard):
    def __init__(self):
        super().__init__(
            card_id="mass_spell",
            name="Mass Spell",
            cost=6
        )


# Amulets
class SpellBurst(AmuletCard):
    def __init__(self):
        super().__init__(
            card_id="spell_burst",
            name="Spell Burst",
            cost=3,
            countdown=1
        )


def get_all_cards():
    """Return all available cards"""
    return [
        AirJinn(),
        KingElephant(),
        HighSorcerer(),
        VeilWitch(),
        Flame(),
        Frostbolt(),
        MassSpell(),
        SpellBurst(),
    ]
