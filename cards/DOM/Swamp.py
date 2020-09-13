from enumeratedTypes import *
from combatFunctions import *
from gameElements import *
from gameActions import *


class Swamp(Card):
    def __init__(self, game, player, key):
        super(Swamp, self).__init__(game, player, key)

        # AA: {T}: Add {B}

        # C: {T}
        c1 = ({}, [[tap, self]])
        # End

        # E: Add {B}
        e1 = [
            [addMana, self.controller, Color.BLACK, 1]
        ]
        # End

        r1 = f"{{T}}: Add {{B}}."
        a1 = ActivatedAbility(game, self, r1, c1, e1, allowedZones={Zone.FIELD}, isManaAbility=True)
        # End

        self.printed = {
            "name": "Swamp",
            "power": 0,
            "toughness": 0,
            "abilities": [a1],
            "types": {Supertype.BASIC, Type.LAND, Subtype.SWAMP},
            "colors": {Color.COLORLESS}
        }

        self.update()
