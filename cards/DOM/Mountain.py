from enumeratedTypes import *
from combatFunctions import *
from gameElements import *
from gameActions import *


class Mountain(Card):
    def __init__(self, game, player, key):
        super(Mountain, self).__init__(game, player, key)

        # AA: {T}: Add {U}

        # C: {T}
        c1 = ({}, [[tap, self]])
        # End

        # E: Add {U}
        e1 = [
            [addMana, self.controller, Color.RED, 1]
        ]
        # End

        r1 = f"{{T}}: Add {{R}}."
        a1 = ActivatedAbility(game, self, r1, c1, e1, allowedZones={Zone.FIELD}, isManaAbility=True)
        # End

        self.printed = {
            "name": "Mountain",
            "power": 0,
            "toughness": 0,
            "abilities": [a1],
            "types": {Supertype.BASIC, Type.LAND, Subtype.MOUNTAIN},
            "colors": {Color.COLORLESS}
        }

        self.update()
